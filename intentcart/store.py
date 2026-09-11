"""SQLite product state: CAS writes, idempotency, consent, and observable tool effects."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import secrets
import sqlite3
import time
from pathlib import Path

from .domain import Problem, CartEdit, Constraints, initial_state, view_state, validate, edit_cart, apply_user_message
from .catalog import get_product


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as c:
            c.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, csrf TEXT NOT NULL, version INTEGER NOT NULL, state TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS receipts(sid TEXT, key TEXT, digest TEXT NOT NULL, effect_version INTEGER NOT NULL, result TEXT, PRIMARY KEY(sid,key));
            CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, sid TEXT, role TEXT, text TEXT);
            CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, sid TEXT, request_id TEXT, driver TEXT, status TEXT, metrics TEXT, UNIQUE(sid,request_id));
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, sid TEXT, run_id TEXT, kind TEXT, payload TEXT, utc REAL);
            CREATE TABLE IF NOT EXISTS confirmations(token TEXT PRIMARY KEY, sid TEXT, version INTEGER, expires REAL);
            CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, sid TEXT, snapshot TEXT, utc REAL);
            PRAGMA user_version=1;
            ''')

    @contextmanager
    def connection(self, transaction=False):
        c = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        c.row_factory = sqlite3.Row
        try:
            if transaction:
                c.execute('BEGIN IMMEDIATE')
            yield c
            if transaction:
                c.commit()
        except Exception:
            if transaction:
                c.rollback()
            raise
        finally:
            c.close()

    def create_session(self):
        sid, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with self.connection(True) as c:
            c.execute('INSERT INTO sessions VALUES(?,?,0,?)', (sid, csrf, encoded(initial_state())))
        return sid, csrf

    def session(self, sid):
        with self.connection() as c:
            row = c.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
        if row is None:
            raise Problem('SESSION_MISSING', '請重新載入以建立購物工作階段。', 401)
        return dict(row)

    def _load(self, c, sid):
        row = c.execute('SELECT * FROM sessions WHERE id=?', (sid,)).fetchone()
        if row is None:
            raise Problem('SESSION_MISSING', 'Session not found.', 401)
        return json.loads(row['state']), row['version']

    def _save(self, c, sid, state, version):
        c.execute('UPDATE sessions SET state=?,version=? WHERE id=?', (encoded(state), version, sid))  # effect:write

    def state(self, sid, reconcile=False):
        with self.connection(True) as c:
            s, version = self._load(c, sid)
            if reconcile:
                s['reconcile_required'] = False
                self._save(c, sid, s, version)
            return view_state(s, version)

    def raw_state(self, sid):
        row = self.session(sid)
        return json.loads(row['state']), row['version']

    def messages(self, sid):
        with self.connection() as c:
            return [dict(r) for r in c.execute('SELECT role,text FROM messages WHERE sid=? ORDER BY id', (sid,))]

    def begin_run(self, sid, text, request_id, driver):
        run_id = secrets.token_hex(12)
        with self.connection(True) as c:
            if c.execute('SELECT 1 FROM runs WHERE sid=? AND request_id=?', (sid, request_id)).fetchone():
                raise Problem('DUPLICATE_RUN', '這次訊息已處理或正在處理；請讀取最新狀態，勿重送。')
            s, version = self._load(c, sid)
            updated, facts = apply_user_message(s, text)
            self._save(c, sid, updated, version + 1)
            c.execute('INSERT INTO messages(sid,role,text) VALUES(?,?,?)', (sid, 'user', text))
            c.execute('INSERT INTO runs VALUES(?,?,?,?,?,?)', (run_id, sid, request_id, driver, 'running', '{}'))
        self.event(sid, run_id, 'user_facts', dict(facts=facts, version=version + 1))
        return run_id

    def finish_run(self, sid, run_id, message, status, metrics):
        with self.connection(True) as c:
            c.execute('UPDATE runs SET status=?,metrics=? WHERE id=? AND sid=?', (status, encoded(metrics), run_id, sid))
            c.execute('INSERT INTO messages(sid,role,text) VALUES(?,?,?)', (sid, 'assistant', message))

    def event(self, sid, run_id, kind, payload):
        with self.connection(True) as c:
            c.execute('INSERT INTO events(sid,run_id,kind,payload,utc) VALUES(?,?,?,?,?)', (sid, run_id, kind, encoded(payload), time.time()))

    def trace(self, sid):
        with self.connection() as c:
            events = [dict(r) for r in c.execute('SELECT id,run_id,kind,payload,utc FROM events WHERE sid=? ORDER BY id', (sid,))]
            runs = [dict(r) for r in c.execute('SELECT id,driver,status,metrics FROM runs WHERE sid=? ORDER BY rowid', (sid,))]
        for e in events:
            e['payload'] = json.loads(e['payload'])
        for r in runs:
            r['metrics'] = json.loads(r['metrics'])
        return dict(runs=runs, events=events)

    def _change(self, sid, expected, key, actor, operation, data, transition):
        digest = hashlib.sha256(encoded([actor, operation, data]).encode()).hexdigest()
        uncertain = False
        with self.connection(True) as c:
            s, version = self._load(c, sid)
            if actor == 'agent' and s['reconcile_required']:  # guard:reconcile
                raise Problem('RECONCILE_REQUIRED', '前次操作結果不確定；先讀取最新購物車。')
            old = c.execute('SELECT * FROM receipts WHERE sid=? AND key=?', (sid, key)).fetchone()
            if old:
                if old['digest'] != digest:  # guard:idempotency
                    raise Problem('IDEMPOTENCY_CONFLICT', '同一操作 ID 不能用於不同內容。')
                return dict(state=view_state(s, version), replayed=True, effect_version=old['effect_version'])
            if expected != version:  # guard:version
                raise Problem('STALE_STATE', '購物車已改變；請先重新讀取再調整。', current_version=version)
            updated = transition(s)
            if actor == 'agent' and s['fault'] == 'write_timeout':
                updated['fault'] = None
                updated['reconcile_required'] = True
                uncertain = True
            self._save(c, sid, updated, version + 1)
            c.execute('INSERT INTO receipts VALUES(?,?,?,?,NULL)', (sid, key, digest, version + 1))
            result = dict(state=view_state(updated, version + 1), replayed=False, effect_version=version + 1)
        if uncertain:
            raise Problem('UNKNOWN_EFFECT', '模擬：寫入後連線中斷。結果未知，必須重新讀取。', 503)
        return result

    def edit(self, sid, edit: CartEdit, actor='user'):
        return self._change(sid, edit.expected_version, edit.request_id, actor, 'edit',
                            edit.model_dump(exclude={'expected_version', 'request_id'}),
                            lambda s: edit_cart(s, edit, actor))

    def constraints(self, sid, values: Constraints, expected, key):
        def change(s):
            s['constraints'] = values.model_dump()
            return s
        return self._change(sid, expected, key, 'user', 'constraints', values.model_dump(), change)

    def require_items(self, sid, needs, expected, key):
        """The model may add inferred essentials, not relax existing hard facts."""
        def change(s):
            s['constraints']['needs'] = sorted((set(s['constraints']['needs']) | set(needs)) - set(s['constraints']['owned']))
            return s
        return self._change(sid, expected, key, 'agent', 'requirements', needs, change)

    def inject_fault(self, sid, fault, variant_id=None):
        with self.connection(True) as c:
            s, version = self._load(c, sid)
            if fault == 'stock':
                if get_product(variant_id) is None:
                    raise Problem('UNKNOWN_VARIANT', 'Unknown fixture variant.', 422)
                s['stock_overrides'][variant_id] = 0
            elif fault == 'unknown_fee':
                s['fee_cents'] = None
            elif fault == 'restore_fee':
                s['fee_cents'] = 0
            elif fault == 'write_timeout':
                s['fault'] = 'write_timeout'
            else:
                raise Problem('UNKNOWN_FAULT', 'Unknown experiment.', 422)
            self._save(c, sid, s, version + 1)
        self.event(sid, None, 'environment_fault', dict(fault=fault, variant_id=variant_id))
        return self.state(sid)

    def preview_checkout(self, sid):
        with self.connection(True) as c:
            s, version = self._load(c, sid)
            verdict = validate(s)
            if not verdict['ready']:
                raise Problem('NOT_READY', '尚有未解決條件，不能結帳。', issues=verdict['issues'])
            token = secrets.token_urlsafe(32)
            c.execute('INSERT INTO confirmations VALUES(?,?,?,?)', (token, sid, version, time.time() + 300))
        return dict(confirmation_token=token, version=version, state=view_state(s, version), simulated=True)

    def checkout(self, sid, token, expected, key, actor='user'):
        if actor != 'user':  # guard:checkout
            raise Problem('USER_CONTROL_ONLY', 'Agent 沒有下單權限。', 403)
        with self.connection(True) as c:
            s, version = self._load(c, sid)
            digest = hashlib.sha256(encoded(['checkout', token, expected]).encode()).hexdigest()
            prior = c.execute('SELECT * FROM receipts WHERE sid=? AND key=?', (sid, key)).fetchone()
            if prior:
                if prior['digest'] != digest:
                    raise Problem('IDEMPOTENCY_CONFLICT', '操作 ID 已被其他請求使用。')
                return json.loads(prior['result'])
            confirmation = c.execute('SELECT * FROM confirmations WHERE token=? AND sid=?', (token, sid)).fetchone()
            if not confirmation or confirmation['expires'] < time.time() or confirmation['version'] != version or expected != version:  # guard:confirmation
                raise Problem('STALE_CONFIRMATION', '確認內容已改變或過期，請重新檢查訂單。')
            if not validate(s)['ready']:
                raise Problem('NOT_READY', '購物車不再符合條件。')
            order = dict(id='SIM-' + secrets.token_hex(5).upper(), snapshot=view_state(s, version), simulated=True)
            c.execute('INSERT INTO orders VALUES(?,?,?,?)', (order['id'], sid, encoded(order['snapshot']), time.time()))
            s['cart'] = {}
            self._save(c, sid, s, version + 1)
            c.execute('DELETE FROM confirmations WHERE sid=?', (sid,))
            c.execute('INSERT INTO receipts VALUES(?,?,?,?,?)', (sid, key, digest, version + 1, encoded(order)))
        return order

    def orders(self, sid):
        with self.connection() as c:
            return [dict(id=r['id'], snapshot=json.loads(r['snapshot']), utc=r['utc'], simulated=True)
                    for r in c.execute('SELECT * FROM orders WHERE sid=? ORDER BY utc', (sid,))]

    def apply_plan(self, sid, items, expected, key):
        from .domain import plan_cart
        return self._change(sid, expected, key, 'agent', 'plan', [i.model_dump() for i in items], lambda s: plan_cart(s, items))
