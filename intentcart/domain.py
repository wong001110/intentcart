"""Authoritative commerce rules. The model can propose actions, not change policy."""
from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt
from .catalog import get_product

KINDS = ('light', 'microphone', 'stand', 'accessory')
WORDS = {'light': r'燈|灯|\blight(?:ing)?\b', 'microphone': r'麥克風|麦克风|收音|microphone|\bmic\b|audio',
         'stand': r'支架|腳架|脚架|\bstand\b|\btripod\b', 'accessory': r'配件|accessor(?:y|ies)'}


class Problem(Exception):
    def __init__(self, code: str, message: str, status: int = 409, **details):
        super().__init__(message)
        self.code, self.message, self.status, self.details = code, message, status, details

    def as_dict(self):
        return dict(code=self.code, message=self.message, **self.details)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class CartEdit(StrictModel):
    operation: Literal['add', 'replace', 'remove', 'quantity', 'lock', 'unlock']
    variant_id: str = Field(min_length=1, max_length=100)
    target_id: str | None = Field(default=None, max_length=100)
    quantity: StrictInt = Field(default=1, ge=1, le=5)
    expected_version: StrictInt = Field(ge=0)
    request_id: str = Field(min_length=8, max_length=100, pattern=r'^[A-Za-z0-9_-]+$')


class Constraints(StrictModel):
    budget_cents: StrictInt | None = Field(default=None, ge=100, le=10000000)
    needs: list[Literal['light', 'microphone', 'stand', 'accessory']] = Field(default_factory=list, max_length=4)
    owned: list[Literal['light', 'microphone', 'stand', 'accessory']] = Field(default_factory=list, max_length=4)
    device_port: Literal['unknown', 'usb-c', 'lightning'] = 'unknown'
    desk_only: bool = True
    preferred_color: Literal['any', 'ivory', 'sage', 'black'] = 'any'


def initial_state():
    return dict(constraints=Constraints().model_dump(), cart={}, excluded=[], stock_overrides={},
                fee_cents=0, fault=None, reconcile_required=False)


def total_cents(state):
    return sum(get_product(k)['price_cents'] * v['quantity'] for k, v in state['cart'].items())


def stock_of(state, p):
    return state['stock_overrides'].get(p['id'], p['stock'])


def validate(state):
    issues = []
    c = state['constraints']
    products = [(get_product(k), v) for k, v in state['cart'].items()]
    if not products:
        issues.append(dict(code='EMPTY_CART', message='購物車還沒有商品。'))
    present = {p['kind'] for p, _ in products if p}
    for kind in set(c['needs']) - set(c['owned']) - present:
        issues.append(dict(code='MISSING_KIND', kind=kind, message=f'尚缺 {kind}。'))
    families = {p['family_id'] for p, _ in products if p}
    for p, item in products:
        if p is None:
            issues.append(dict(code='UNKNOWN_VARIANT', message='商品規格不存在。'))
            continue
        details = dict(variant_id=p['id'])
        if stock_of(state, p) < item['quantity']:  # guard:stock
            issues.append(dict(code='OUT_OF_STOCK', message='所選規格庫存不足。', **details))
        if p['kind'] in c['owned']:  # guard:owned
            issues.append(dict(code='ALREADY_OWNED', message='你已擁有這類物品；請先確認是否需要重複購買。', **details))
        if p['kind'] == 'microphone':
            if c['device_port'] == 'unknown' or p['port'] == 'unknown':  # guard:unknown
                issues.append(dict(code='UNKNOWN_COMPATIBILITY', message='請確認手機接口，不能將未知規格視為相容。', **details))
            elif p['port'] != c['device_port']:  # guard:compatibility
                issues.append(dict(code='INCOMPATIBLE', message='麥克風接口與已確認裝置不符。', **details))
        if c['desk_only'] and not p['desk_fit']:
            issues.append(dict(code='NOT_DESK_FIT', message='商品不適合目前的桌面限制。', **details))
        for family in p['requires']:
            if family not in families:  # guard:dependency
                issues.append(dict(code='MISSING_ACCESSORY', required_family=family, message='缺少必要配件。', **details))
    subtotal = total_cents(state)
    fee = state['fee_cents']
    total = subtotal + fee if fee is not None else None
    if fee is None:  # guard:fee
        issues.append(dict(code='UNKNOWN_FEE', message='費用尚未確認；不能宣稱符合最終預算。'))
    if c['budget_cents'] is not None and (total if total is not None else subtotal) > c['budget_cents']:  # guard:budget
        issues.append(dict(code='OVER_BUDGET', message='目前方案超出你設定的硬性預算。'))
    return dict(ready=not issues, issues=issues, subtotal_cents=subtotal, fee_cents=fee,
                total_cents=total, fee_scope='All synthetic prices include fees; no real payment.')


def view_state(state, version):
    result = deepcopy(state)
    result.pop('fault', None)
    result.pop('reconcile_required', None)
    result['version'] = version
    result['items'] = [dict(product=get_product(k), **v, stock=stock_of(state, get_product(k)))
                       for k, v in state['cart'].items()]
    result['validation'] = validate(state)
    return result


def edit_cart(state, edit: CartEdit, actor: str):
    """Pure transition. Store performs CAS, idempotency, and atomic persistence."""
    s = deepcopy(state)
    cart = s['cart']
    p = get_product(edit.variant_id)
    if p is None:  # guard:variant
        raise Problem('UNKNOWN_VARIANT', '請選擇確實存在的商品規格。', 422)
    target = edit.target_id if edit.operation == 'replace' else edit.variant_id
    old = cart.get(target)
    if actor == 'agent' and edit.operation in ('lock', 'unlock'):
        raise Problem('USER_CONTROL_ONLY', '只有使用者可以變更保留決定。', 403)
    if edit.operation != 'add' and old is None:
        raise Problem('NOT_IN_CART', '此商品已不在購物車；請重新讀取。')
    if actor == 'agent' and old and old['locked']:  # guard:lock
        if edit.operation != 'add' or edit.quantity != old['quantity']:
            raise Problem('LOCKED', '保留的選擇不能由 agent 改動。')
    if edit.operation in ('add', 'replace', 'quantity'):
        if actor == 'agent' and edit.variant_id in s['excluded']:  # guard:exclusion
            raise Problem('EXPLICITLY_REMOVED', '使用者已移除此商品，不能擅自加回。')
        if actor == 'user' and edit.variant_id in s['excluded']:
            s['excluded'].remove(edit.variant_id)
        if edit.operation == 'replace':
            if edit.variant_id != target and edit.variant_id in cart:
                raise Problem('DUPLICATE_TARGET', '替換目標已在購物車中。')
            del cart[target]
            if actor == 'user' and target != edit.variant_id and target not in s['excluded']:
                s['excluded'].append(target)
        cart[edit.variant_id] = dict(quantity=edit.quantity, locked=(actor == 'user') or bool(old and old['locked']), source=actor)
    elif edit.operation == 'remove':
        del cart[target]
        if actor == 'user' and target not in s['excluded']:
            s['excluded'].append(target)
    else:
        cart[target]['locked'] = edit.operation == 'lock'
    if edit.operation in ('add', 'replace', 'quantity'):
        problems = validate(s)['issues']
        blocking = [i for i in problems if i['code'] not in ('EMPTY_CART', 'MISSING_KIND', 'MISSING_ACCESSORY', 'UNKNOWN_FEE')]
        if blocking:
            raise Problem('INVALID_CART_EDIT', blocking[0]['message'], issues=blocking)
    return s


def extract_facts(text):
    """Conservative, inspectable input guard, NOT a substitute for LLM understanding.

    Only explicit amounts/ports/possession and a small bilingual domain lexicon are
    committed here. Remaining preferences and ambiguity are left to the real model.
    The UI exposes editable facts. Unsupported paraphrases remain a research limit.
    """
    patch = {}
    # A hard-cap update must name the user's budget, not merely describe a product price.
    amounts = re.findall(r'(?:預算|预算|最多|不超過|不超过|(?:my\s+)?budget)\s*(?:改成|改為|改为|to|is|of|:|：)?\s*(?:RM|MYR)?\s*(\d+(?:\.\d{1,2})?)', text, re.I)
    if amounts:
        value = int(Decimal(amounts[-1]) * 100)
        if 100 <= value <= 10000000:
            patch['budget_cents'] = value
    # Negated/uncertain interface mentions are not affirmative hardware facts.
    port_text = re.sub(r'(?:不是|不是用|不確定|不确定|not|not sure|isn.t)\s*(?:USB[- ]?C|Type[- ]?C|lightning)', '', text, flags=re.I)
    if re.search(r'USB[- ]?C|Type[- ]?C', port_text, re.I):
        patch['device_port'] = 'usb-c'
    elif re.search(r'lightning', port_text, re.I):
        patch['device_port'] = 'lightning'
    own = re.findall(r'(?:already have|already own|i own|已有|已經有|已经有|我有)\s*([^。.;，,\n]+)', text, re.I)
    if own:
        patch['owned'] = [k for k, pattern in WORDS.items() if any(re.search(pattern, phrase, re.I) for phrase in own)]
    kinds = [k for k, pattern in WORDS.items() if re.search(pattern, text, re.I)]
    if not {'light', 'microphone'}.intersection(kinds) and re.search(r'拍片|拍影片|錄影|录影|record.*video|talking.head', text, re.I):
        kinds = ['light', 'microphone', 'stand']
    if kinds:
        patch['needs'] = kinds
    for color, pattern in [('ivory', r'米白|象牙|ivory'), ('sage', r'綠色|绿色|sage'), ('black', r'黑色|black')]:
        if re.search(pattern, text, re.I):
            patch['preferred_color'] = color
    return patch


def apply_user_message(state, text):
    s = deepcopy(state)
    patch = extract_facts(text)
    for k, value in patch.items():
        if k == 'needs':
            if not s['constraints']['needs']:
                s['constraints'][k] = value
        elif k == 'owned':
            s['constraints'][k] = sorted(set(s['constraints'][k]) | set(value))
        else:
            s['constraints'][k] = value
    for kind, pattern in WORDS.items():
        keep = re.search(r'(?:保留|keep|lock)\s*(?:這個|这个|the\s+)?(?:' + pattern + ')|(?:' + pattern + r')\s*保留', text, re.I)
        unlock = re.search(r'(?:解鎖|解锁|unlock)\s*(?:the\s+)?(?:' + pattern + ')', text, re.I)
        remove = re.search(r'(?:不要|不需要|remove|no longer need)\s*(?:the\s+)?(?:' + pattern + ')', text, re.I)
        for pid in list(s['cart']):
            if get_product(pid)['kind'] == kind:
                if remove:
                    del s['cart'][pid]
                    if pid not in s['excluded']:
                        s['excluded'].append(pid)
                elif unlock:
                    s['cart'][pid]['locked'] = False
                elif keep:
                    s['cart'][pid]['locked'] = True
        if remove and kind in s['constraints']['needs']:
            s['constraints']['needs'].remove(kind)
    s['constraints']['needs'] = [k for k in s['constraints']['needs'] if k not in s['constraints']['owned']]
    return s, patch


class PlanItem(StrictModel):
    variant_id: str = Field(min_length=1, max_length=100)
    quantity: StrictInt = Field(default=1, ge=1, le=5)


def plan_cart(state, items):
    s = deepcopy(state)
    new = {}
    for item in items:
        pid = item.variant_id
        if get_product(pid) is None:
            raise Problem('UNKNOWN_VARIANT', '指定的商品規格不存在。', 422)
        if pid in new:
            raise Problem('DUPLICATE_VARIANT', '方案中每個規格只能出現一次。', 422)
        if pid in s['excluded']:
            raise Problem('EXPLICITLY_REMOVED', '不能把使用者移除的商品加回。')
        previous = s['cart'].get(pid)
        new[pid] = dict(quantity=item.quantity, locked=bool(previous and previous['locked']),
                        source=previous['source'] if previous else 'agent')
    for pid, previous in s['cart'].items():
        if previous['locked'] and (pid not in new or new[pid]['quantity'] != previous['quantity']):  # guard:plan-lock
            raise Problem('LOCKED', '方案必須保留使用者鎖定的商品與數量。')
    s['cart'] = new
    blocking = [i for i in validate(s)['issues'] if i['code'] not in ('EMPTY_CART', 'MISSING_KIND', 'MISSING_ACCESSORY', 'UNKNOWN_FEE')]
    if blocking:
        raise Problem('INVALID_PLAN', blocking[0]['message'], issues=blocking)
    return s
