"""Protocol tests use explicitly fake model responses. They are NOT LLM evaluations."""
import asyncio
import json
import pytest
import httpx
from intentcart.agent import Config, Tools, LiveProvider, run_turn, tool_schemas
from intentcart.catalog import get_product
from intentcart.domain import Constraints, CartEdit, Problem
from intentcart.store import Store

TEXT = '我需要燈和麥克風，預算 RM300，手機是 USB-C，已經有支架。'


@pytest.fixture
def context(tmp_path):
    store = Store(tmp_path / 'agent.sqlite')
    sid, _ = store.create_session()
    return store, sid


def collect(store, sid, driver='demo', text=TEXT, provider=None, config=None):
    config = config or Config(driver=driver)
    run = store.begin_run(sid, text, f'request-{len(store.messages(sid))}-long', driver)
    async def go():
        return [event async for event in run_turn(store, sid, run, config, provider)]
    return asyncio.run(go())


def fake_call(name, args, identity='tool-1'):
    return dict(role='assistant',content=None,tool_calls=[dict(id=identity,type='function',function=dict(name=name,arguments=json.dumps(args)))])


def test_demo_is_labelled_and_uses_real_tools_and_cart(context):
    store, sid = context
    events = collect(store, sid)
    assert events[0]['type'] == 'progress'
    done = events[-1]
    assert done['state']['validation']['ready']
    assert done['metrics']['driver'] == 'demo'
    assert done['metrics']['model_evidence'] is False
    assert store.orders(sid) == []
    names = [e['name'] for e in events if e['type'] == 'tool']
    assert {'search_catalog','apply_plan','inspect_task','validate_cart'} <= set(names)
    assert store.state(sid)['cart']


def test_missing_port_prepares_safe_part_then_asks(context):
    events = collect(*context, text='需要燈和麥克風，預算 RM300。')
    state = events[-1]['state']
    assert not state['validation']['ready']
    assert any(i['product']['kind'] == 'light' for i in state['items'])
    assert not any(i['product']['kind'] == 'microphone' for i in state['items'])
    assert 'USB-C' in events[-1]['message']
    events = collect(*context, text='我的手機是 USB-C。')
    assert events[-1]['state']['validation']['ready']


def test_locked_light_preserved_after_budget_revision(context):
    store, sid = context
    collect(store, sid)
    lamp = next(pid for pid in store.state(sid)['cart'] if get_product(pid)['kind'] == 'light')
    events = collect(store, sid, text='保留燈，預算改成 RM180。')
    state = events[-1]['state']
    assert state['cart'][lamp]['locked']
    assert state['validation']['ready']
    assert state['validation']['total_cents'] <= 18000


def test_out_of_stock_repair_only_changes_affected_kind(context):
    store, sid = context
    collect(store, sid)
    before = store.state(sid)
    mic = next(pid for pid in before['cart'] if get_product(pid)['kind'] == 'microphone')
    lamp = next(pid for pid in before['cart'] if get_product(pid)['kind'] == 'light')
    store.inject_fault(sid, 'stock', mic)
    after = collect(store, sid, text='請依照原本需求繼續準備。')[-1]['state']
    assert after['validation']['ready']
    assert lamp in after['cart']
    assert mic not in after['cart']


def test_locked_out_of_stock_stops_instead_of_replacing(context):
    store, sid = context
    collect(store, sid)
    lamp = next(pid for pid in store.state(sid)['cart'] if get_product(pid)['kind'] == 'light')
    store.edit(sid, CartEdit(operation='lock', variant_id=lamp, expected_version=store.state(sid)['version'], request_id='user-keep-lamp'), actor='user')
    store.inject_fault(sid, 'stock', lamp)
    event = collect(store, sid, text='請繼續準備。')[-1]
    assert not event['state']['validation']['ready']
    assert lamp in event['state']['cart']
    assert '不能結帳' in event['message']


def test_uncertain_effect_is_followed_by_read_then_repair(context):
    store, sid = context
    store.inject_fault(sid, 'write_timeout')
    events = collect(store, sid)
    calls = [e for e in events if e['type'] == 'tool']
    uncertain = next(i for i, e in enumerate(calls) if e['result'].get('error', {}).get('code') == 'UNKNOWN_EFFECT')
    assert calls[uncertain + 1]['name'] == 'inspect_task'
    assert events[-1]['state']['validation']['ready']
    assert all(i['quantity'] == 1 for i in events[-1]['state']['items'])


def test_no_feasible_cart_is_not_reported_ready(context):
    last = collect(*context, text='我需要燈和麥克風，預算 RM20，USB-C。')[-1]
    assert not last['state']['validation']['ready']
    assert last['state']['cart'] == {}
    assert '不能結帳' in last['message']


def test_gateway_never_exposes_checkout_or_generic_execution(context):
    store, sid = context
    tools = Tools(store, sid, 'malicious-test')
    for name in ['checkout','submit_order','http','browser','exec','set_budget','eval']:
        result = tools.call(name, {'actor':'user'})
        assert result['error']['code'] == 'TOOL_NOT_ALLOWED'
    assert store.orders(sid) == []
    assert not {'checkout','http','exec'} & {t['function']['name'] for t in tool_schemas()}


def test_tool_arguments_cannot_escalate_authority_or_budget(context):
    store, sid = context
    tools = Tools(store, sid, 'argument-test')
    result = tools.call('require_items', {'needs': [], 'budget_cents':999999, 'expected_version':0,'request_id':'attack-budget'})
    assert result['error']['code'] == 'INVALID_ARGUMENTS'
    result = tools.call('edit_cart', {'operation':'unlock','variant_id':'dawn-ivory','expected_version':0,'request_id':'attack-lock','actor':'user'})
    assert result['error']['code'] == 'INVALID_ARGUMENTS'


def test_no_silent_live_fallback(monkeypatch):
    monkeypatch.setenv('INTENTCART_DRIVER','live')
    monkeypatch.delenv('INTENTCART_API_KEY', raising=False)
    monkeypatch.delenv('INTENTCART_MODEL', raising=False)
    with pytest.raises(ValueError, match='no silent demo fallback'):
        Config.from_env()


def test_provider_endpoint_validation(monkeypatch):
    monkeypatch.setenv('INTENTCART_DRIVER','demo')
    for base in ['http://example.com/v1','https://user:password@example.com/v1','https://example.com/v1?key=secret']:
        monkeypatch.setenv('INTENTCART_API_BASE',base)
        with pytest.raises(ValueError):
            Config.from_env()


def test_live_adapter_protocol_against_mock_transport(context):
    store, sid = context
    seen = []
    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        assert 'tools' in body
        assert request.headers['authorization'] == 'Bearer canary-private-key'
        last = body['messages'][-1]
        if last['role'] == 'user':
            answer = fake_call('inspect_task', {})
        elif last.get('tool_call_id') == 'tool-1':
            state = json.loads(last['content'])['value']
            answer = fake_call('apply_plan', dict(items=[{'variant_id':'dawn-ivory'},{'variant_id':'clip-black-usb-c'}], expected_version=state['version'],request_id='model-cart-plan'), 'tool-2')
        else:
            answer = dict(role='assistant',content='Prepared, not purchased.')
        return httpx.Response(200,json={'choices':[{'message':answer}],'usage':{'prompt_tokens':20,'completion_tokens':8}})
    config = Config(driver='live',api_key='canary-private-key',model='mock-not-a-real-model')
    provider = LiveProvider(config,httpx.MockTransport(handler))
    events = collect(store, sid, driver='live',provider=provider,config=config)
    assert events[-1]['state']['validation']['ready']
    assert events[-1]['metrics']['usage']['prompt_tokens'] == 60
    assert len(seen) == 3
    assert 'canary-private-key' not in json.dumps(store.trace(sid))
    # This is protocol evidence using a mocked transport, not a measured model result.


def test_provider_error_does_not_leak_key_or_fabricate_completion(context):
    config = Config(driver='live',api_key='private-canary',model='mock')
    provider = LiveProvider(config,httpx.MockTransport(lambda r:httpx.Response(401,text='private-canary')))
    events = collect(*context, driver='live',provider=provider,config=config)
    assert events[-1]['metrics']['failure']['code'] == 'PROVIDER_ERROR'
    assert 'private-canary' not in json.dumps(events)
    assert not events[-1]['state']['validation']['ready']


def test_malformed_tool_call_cannot_mutate(context):
    class BadJSON:
        def __init__(self): self.n = 0
        async def complete(self, messages):
            self.n += 1
            return (dict(role='assistant',content=None,tool_calls=[dict(id='bad',function=dict(name='apply_plan',arguments='{broken'))]) if self.n == 1 else dict(role='assistant',content='I added everything!')), {}
    events = collect(*context, driver='live',provider=BadJSON(),config=Config(driver='live'))
    assert events[-1]['state']['cart'] == {}
    assert any(e.get('result',{}).get('error',{}).get('code') == 'INVALID_TOOL_JSON' for e in events)
    assert 'I added everything' not in events[-1]['message']


def test_loop_limits_do_not_claim_success(context):
    class Forever:
        async def complete(self,messages): return fake_call('inspect_task',{}), {}
    result = collect(*context,driver='live',provider=Forever(),config=Config(driver='live',max_rounds=2))[-1]
    assert result['metrics']['failure']['code'] == 'STEP_LIMIT'
    assert result['metrics']['tool_calls'] == 2


def test_live_manual_race_rejects_stale_then_replans(context):
    store, sid = context
    class RacingFake:
        def __init__(self): self.n=0;self.version=0
        async def complete(self,messages):
            self.n+=1
            if self.n==1:return fake_call('inspect_task',{}),{}
            if self.n==2:
                self.version=json.loads(messages[-1]['content'])['value']['version']
                store.edit(sid,CartEdit(operation='add',variant_id='dawn-sage',expected_version=self.version,request_id='human-racing-edit'),actor='user')
                return fake_call('apply_plan',{'items':[{'variant_id':'dawn-ivory'},{'variant_id':'clip-black-usb-c'}],'expected_version':self.version,'request_id':'stale-model-plan'}),{}
            if self.n==3:
                assert json.loads(messages[-1]['content'])['error']['code']=='STALE_STATE'
                return fake_call('inspect_task',{}),{}
            if self.n==4:
                s=json.loads(messages[-1]['content'])['value']
                return fake_call('apply_plan',{'items':[{'variant_id':'dawn-sage'},{'variant_id':'clip-black-usb-c'}],'expected_version':s['version'],'request_id':'reconciled-plan'}),{}
            return dict(role='assistant',content='Prepared.'),{}
    events=collect(store,sid,driver='live',provider=RacingFake(),config=Config(driver='live'))
    assert events[-1]['state']['cart']['dawn-sage']['locked']
    assert 'dawn-ivory' not in events[-1]['state']['cart']
    assert events[-1]['state']['validation']['ready']


def test_model_clarification_is_visible_without_mutating_user_constraints(context):
    class Asking:
        def __init__(self): self.n=0
        async def complete(self,messages):
            self.n+=1
            return (fake_call('ask_user',{'question':'你想同時為幾個人收音？'}) if self.n==1 else dict(role='assistant',content='Waiting')),{}
    result=collect(*context,driver='live',provider=Asking(),config=Config(driver='live'))[-1]
    assert '幾個人收音' in result['message']
    assert result['state']['cart']=={}
    assert result['state']['constraints']['budget_cents']==30000
