import json
import pytest
from fastapi.testclient import TestClient
from intentcart.api import create_app
from intentcart.agent import Config


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path/'api.sqlite',Config())) as c:
        data=c.get('/api/state').json()
        c.headers['x-csrf-token']=data['csrf']
        yield c


def run(c, text='需要燈和麥克風，預算 RM300，USB-C。', request_id='request-for-chat', language='zh'):
    response=c.post('/api/chat',json={'message':text,'request_id':request_id,'language':language})
    assert response.status_code==200,response.text
    return [json.loads(line) for line in response.text.splitlines()]


def test_bootstrap_no_secret_state_leak(client):
    response=client.get('/api/state')
    assert response.status_code==200
    assert 'HttpOnly' in response.headers['set-cookie']
    assert 'SameSite=strict' in response.headers['set-cookie']
    assert response.headers['cache-control']=='no-store'
    assert 'csrf' not in response.json()['state']
    assert 'api_key' not in json.dumps(response.json()['config'])
    assert response.json()['memory'] is None


def test_english_chat_request_returns_english_host_summary(client):
    events = run(client, 'I need a desk light and microphone. My budget is RM300 and my phone uses USB-C.', 'english-request', 'en')
    assert events[0]['message'] == 'Checking your request and saved cart…'
    assert 'Your cart is ready:' in events[-1]['message']


def test_csrf_and_cross_origin_rejected(client):
    body={'message':'hello','request_id':'csrf-request-id'}
    assert client.post('/api/chat',json=body,headers={'x-csrf-token':'wrong'}).status_code==403
    assert client.post('/api/chat',json=body,headers={'origin':'https://attacker.invalid'}).status_code==403


def test_http_shared_cart_checkout_and_refresh(client):
    events=run(client)
    assert events[0]['type']=='progress'
    assert events[-1]['state']['validation']['ready']
    s=client.get('/api/state').json()['state']
    pid=s['items'][0]['product']['id']
    r=client.post('/api/cart',json={'operation':'lock','variant_id':pid,'expected_version':s['version'],'request_id':'manual-lock-api'})
    assert r.status_code==200
    assert r.json()['state']['cart'][pid]['locked']
    p=client.post('/api/checkout/preview',json={}).json()
    assert client.get('/api/state').json()['orders']==[]
    order=client.post('/api/checkout/confirm',json={'confirmation_token':p['confirmation_token'],'expected_version':p['version'],'request_id':'confirm-api-order'})
    assert order.status_code==200,order.text
    assert order.json()['simulated']
    assert len(client.get('/api/state').json()['orders'])==1


def test_duplicate_chat_not_rerun(client):
    run(client)
    response=client.post('/api/chat',json={'message':'same','request_id':'request-for-chat'})
    assert response.status_code==409
    assert response.json()['error']['code']=='DUPLICATE_RUN'


def test_reset_starts_a_fresh_session_without_erasing_prior_evidence(client):
    run(client)
    old_sid=client.cookies.get('intentcart_session')
    response=client.post('/api/session/reset',json={})
    assert response.status_code==200
    fresh=response.json()
    assert fresh['state']['cart']=={}
    assert fresh['messages']==[]
    assert fresh['memory'] is None
    assert fresh['orders']==[]
    assert client.cookies.get('intentcart_session') != old_sid
    assert client.app.state.store.messages(old_sid)


def test_reset_rejects_an_active_agent_run(client):
    sid=client.cookies.get('intentcart_session')
    client.app.state.running.add(sid)
    response=client.post('/api/session/reset',json={})
    assert response.status_code==409
    assert response.json()['error']['code']=='RUN_IN_PROGRESS'
    client.app.state.running.remove(sid)


def test_catalog_view_never_adds(client):
    before=client.get('/api/state').json()['state']
    assert len(client.get('/api/catalog').json()['products'])==40
    assert client.get('/api/products/dawn-ivory').status_code==200
    assert client.get('/api/products/missing').status_code==404
    assert client.get('/api/state').json()['state']==before


def test_direct_actor_injection_not_accepted(client):
    assert client.post('/api/cart',json={'operation':'add','variant_id':'dawn-ivory','expected_version':0,'request_id':'bad-actor-input','actor':'agent'}).status_code==422
    assert client.post('/api/checkout/confirm',json={'confirmation_token':'a'*40,'expected_version':0,'request_id':'bad-confirmation','actor':'user'}).status_code==422


def test_faults_and_traces_are_real_and_session_scoped(client):
    run(client)
    s=client.get('/api/state').json()['state']
    pid=s['items'][0]['product']['id']
    response=client.post('/api/experiments',json={'fault':'stock','variant_id':pid})
    assert response.status_code==200
    assert not response.json()['state']['validation']['ready']
    trace=client.get('/api/export').json()
    assert trace['trace']['events']
    assert trace['config']['driver']=='demo'
    assert 'csrf' not in json.dumps(trace)
    assert 'intentcart_session' not in json.dumps(trace)
    other=TestClient(client.app)
    new=other.get('/api/state').json()
    assert not new['state']['cart']
    assert not other.get('/api/trace').json()['events']


def test_whitespace_and_oversized_messages_rejected(client):
    assert client.post('/api/chat',json={'message':'   ','request_id':'empty-request'}).status_code==422
    assert client.post('/api/chat',json={'message':'x'*2001,'request_id':'large-request'}).status_code==422


def test_serves_own_scripts_and_csp(client):
    response=client.get('/')
    assert response.status_code==200
    assert 'IntentCart' in response.text
    assert 'recommendations.css' in response.text
    assert 'conversation-memory' in response.text
    assert "script-src 'self'" in response.headers['content-security-policy']
    app_script=client.get('/static/app.js')
    assert app_script.status_code==200
    assert 'recommendationStarts' in app_script.text
    assert 'renderMemory' in app_script.text
    assert "$('memory-body').textContent" in app_script.text
    assert 'request_id:uid(),language' in app_script.text
    assert 'Respond only in English' not in app_script.text
    assert client.get('/static/style.css').status_code==200
    assert client.get('/static/recommendations.css').status_code==200


def test_checkout_cannot_race_an_active_agent_run(client):
    run(client)
    preview=client.post('/api/checkout/preview',json={}).json()
    body={'confirmation_token':preview['confirmation_token'],'expected_version':preview['version'],'request_id':'human-checkout-race'}
    sid=client.cookies.get('intentcart_session')
    client.app.state.running.add(sid)
    response=client.post('/api/checkout/confirm',json=body)
    assert response.status_code==409
    assert response.json()['error']['code']=='RUN_IN_PROGRESS'
    assert not client.get('/api/state').json()['orders']
    client.app.state.running.remove(sid)
    assert client.post('/api/checkout/confirm',json=body).status_code==200
