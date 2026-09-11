"""Single-origin, loopback-first research server. Never exposes payment/ordering to tools."""
import asyncio
import json
import os
from pathlib import Path
import secrets
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from .agent import Config, run_turn
from .catalog import search_products, get_product, FIXTURE_VERSION
from .domain import StrictModel, CartEdit, Constraints, Problem
from .store import Store


class Chat(StrictModel):
    message: str = Field(min_length=1, max_length=2000)
    request_id: str = Field(min_length=8, max_length=100, pattern=r'^[A-Za-z0-9_-]+$')


class ConstraintUpdate(StrictModel):
    constraints: Constraints
    expected_version: int = Field(ge=0, strict=True)
    request_id: str = Field(min_length=8, max_length=100)


class Fault(StrictModel):
    fault: Literal['stock', 'unknown_fee', 'restore_fee', 'write_timeout']
    variant_id: str | None = Field(default=None, max_length=100)


class Confirmation(StrictModel):
    confirmation_token: str = Field(min_length=16, max_length=100)
    expected_version: int = Field(ge=0, strict=True)
    request_id: str = Field(min_length=8, max_length=100)


def create_app(db_path=None, config=None, provider=None):
    config = config or Config.from_env()
    store = Store(db_path or os.getenv('INTENTCART_DB_PATH', 'var/intentcart.sqlite'))
    app = FastAPI(title='IntentCart Research API', docs_url=None, redoc_url=None)
    app.state.store, app.state.config = store, config
    running = set()
    app.state.running = running
    web = Path(__file__).resolve().parents[1] / 'web'

    @app.middleware('http')
    async def headers(request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        if request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.exception_handler(Problem)
    async def problem_handler(request, exc):
        return JSONResponse({'error': exc.as_dict()}, status_code=exc.status)

    def identify(request):
        sid = request.cookies.get('intentcart_session', '')
        store.session(sid)
        return sid

    def authorize(request):
        sid = identify(request)
        origin = request.headers.get('origin')
        if origin and origin.rstrip('/') != str(request.base_url).rstrip('/'):
            raise Problem('ORIGIN_REJECTED', '只接受此網站內的操作。', 403)
        token = request.headers.get('x-csrf-token', '')
        if not secrets.compare_digest(token, store.session(sid)['csrf']):
            raise Problem('CSRF_REJECTED', '操作驗證失效，請重新載入。', 403)
        return sid

    @app.get('/api/health')
    def health():
        return dict(status='ok', fixture=FIXTURE_VERSION, driver=config.driver, simulated=True)

    @app.get('/api/state')
    def state(request: Request):
        try:
            sid = identify(request)
            csrf = store.session(sid)['csrf']
        except Problem:
            sid, csrf = store.create_session()
        response = JSONResponse(dict(state=store.state(sid), csrf=csrf, messages=store.messages(sid),
                                     config=config.public(), orders=store.orders(sid)))
        response.set_cookie('intentcart_session', sid, httponly=True, samesite='strict',
                            secure=request.url.scheme == 'https', max_age=604800)
        return response

    @app.get('/api/catalog')
    def catalog(request: Request, query: str = '', kind: str | None = None):
        sid = identify(request)
        if len(query) > 100:
            raise Problem('QUERY_TOO_LONG', '搜尋文字過長。', 422)
        raw, _ = store.raw_state(sid)
        return dict(products=search_products(query, kind=kind, stock=raw['stock_overrides']), fixture=FIXTURE_VERSION)

    @app.get('/api/products/{variant_id}')
    def product(variant_id: str, request: Request):
        sid = identify(request)
        item = get_product(variant_id)
        if item is None:
            raise Problem('UNKNOWN_VARIANT', '商品不存在。', 404)
        raw, _ = store.raw_state(sid)
        item['stock'] = raw['stock_overrides'].get(item['id'], item['stock'])
        return item

    @app.post('/api/cart')
    def cart(body: CartEdit, request: Request):
        return store.edit(authorize(request), body, actor='user')

    @app.post('/api/constraints')
    def constraints(body: ConstraintUpdate, request: Request):
        return store.constraints(authorize(request), body.constraints, body.expected_version, body.request_id)

    @app.post('/api/chat')
    async def chat(body: Chat, request: Request):
        sid = authorize(request)
        if not body.message.strip():
            raise Problem('EMPTY_MESSAGE', '請輸入需求。', 422)
        if sid in running:
            raise Problem('RUN_IN_PROGRESS', '目前正在處理上一則訊息；你仍可手動修改購物車。')
        run_id = store.begin_run(sid, body.message.strip(), body.request_id, config.driver)
        running.add(sid)

        async def stream():
            generator = run_turn(store, sid, run_id, config, provider=provider)
            try:
                async for event in generator:
                    yield json.dumps(event, ensure_ascii=False) + '\n'
                    await asyncio.sleep(0)
            finally:
                await generator.aclose()
                running.discard(sid)
        return StreamingResponse(stream(), media_type='application/x-ndjson', headers={'X-Accel-Buffering': 'no'})

    @app.post('/api/experiments')
    def experiment(body: Fault, request: Request):
        return dict(state=store.inject_fault(authorize(request), body.fault, body.variant_id))

    @app.post('/api/checkout/preview')
    def checkout_preview(request: Request):
        return store.preview_checkout(authorize(request))

    @app.post('/api/checkout/confirm')
    def checkout_confirm(body: Confirmation, request: Request):
        # Identity comes from the human session, never an agent-supplied actor field.
        sid = authorize(request)
        if sid in running:
            raise Problem('RUN_IN_PROGRESS', '請等目前採購準備結束，再重新確認下單。')
        return store.checkout(sid, body.confirmation_token, body.expected_version, body.request_id, actor='user')

    @app.get('/api/trace')
    def trace(request: Request):
        return store.trace(identify(request))

    @app.get('/api/export')
    def export(request: Request):
        sid = identify(request)
        return dict(fixture=FIXTURE_VERSION, config=config.public(), state=store.state(sid),
                    messages=store.messages(sid), trace=store.trace(sid), orders=store.orders(sid))

    app.mount('/static', StaticFiles(directory=web), name='static')

    @app.get('/')
    def home():
        return FileResponse(web / 'index.html')

    return app
