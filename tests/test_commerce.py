import json
import secrets
import sqlite3
import pytest
from pydantic import ValidationError
from intentcart.domain import CartEdit, Constraints, Problem, extract_facts
from intentcart.catalog import PRODUCTS, get_product
from intentcart.store import Store

LIGHT = 'dawn-ivory'
MIC = 'clip-black-usb-c'


@pytest.fixture
def shop(tmp_path):
    store = Store(tmp_path / 'shop.sqlite')
    sid, _ = store.create_session()
    c = Constraints(budget_cents=30000, needs=['light', 'microphone'], device_port='usb-c', owned=['stand'])
    store.constraints(sid, c, 0, 'initial-facts')
    return store, sid


def edit(store, sid, pid=LIGHT, operation='add', actor='agent', **kwargs):
    args = dict(variant_id=pid, operation=operation, expected_version=store.state(sid)['version'], request_id=secrets.token_hex(8))
    args.update(kwargs)
    return store.edit(sid, CartEdit(**args), actor)


def ready(store, sid):
    edit(store, sid)
    edit(store, sid, MIC)


def issue(exc, code):
    assert any(i['code'] == code for i in exc.value.details.get('issues', []))


def test_fixture_ids_are_concrete_unique_and_synthetic():
    assert len(PRODUCTS) == 40
    assert len({p['id'] for p in PRODUCTS}) == len(PRODUCTS)
    assert all(p['synthetic'] and isinstance(p['price_cents'], int) for p in PRODUCTS)


def test_write_is_persisted_and_read_back(shop):
    store, sid = shop
    edit(store, sid)
    reopened = Store(store.path)
    assert reopened.state(sid)['cart'][LIGHT]['quantity'] == 1
    assert not reopened.state(sid)['validation']['ready']


def test_ready_totals_and_human_order(shop):
    store, sid = shop
    ready(store, sid)
    assert store.state(sid)['validation']['total_cents'] == 16800
    assert store.state(sid)['validation']['ready']
    assert store.orders(sid) == []
    preview = store.preview_checkout(sid)
    order = store.checkout(sid, preview['confirmation_token'], preview['version'], 'human-confirm')
    assert order['simulated'] is True
    assert order['snapshot']['validation']['ready']
    assert not store.state(sid)['cart']
    assert len(store.orders(sid)) == 1
    assert store.checkout(sid, preview['confirmation_token'], preview['version'], 'human-confirm')['id'] == order['id']
    assert len(store.orders(sid)) == 1


def test_budget_is_a_hard_guard(shop):
    store, sid = shop
    c = Constraints(budget_cents=5000, needs=['light'])
    store.constraints(sid, c, store.state(sid)['version'], 'set-small-budget')
    with pytest.raises(Problem) as exc:
        edit(store, sid)
    issue(exc, 'OVER_BUDGET')
    assert store.state(sid)['cart'] == {}


@pytest.mark.parametrize('pid,code', [
    ('retired-black-usb-c', 'OUT_OF_STOCK'),
    ('clip-black-lightning', 'INCOMPATIBLE'),
    ('mystery-black-unknown', 'UNKNOWN_COMPATIBILITY'),
    ('angle-ivory', 'ALREADY_OWNED'),
    ('floor-ivory', 'NOT_DESK_FIT'),
])
def test_unfit_variants_are_rejected(shop, pid, code):
    with pytest.raises(Problem) as exc:
        edit(*shop, pid)
    issue(exc, code)


def test_missing_port_stays_unknown(shop):
    store, sid = shop
    c = Constraints(needs=['microphone'])
    store.constraints(sid, c, store.state(sid)['version'], 'unknown-device')
    with pytest.raises(Problem) as exc:
        edit(store, sid, MIC)
    issue(exc, 'UNKNOWN_COMPATIBILITY')


def test_dependency_is_not_optional(shop):
    store, sid = shop
    edit(store, sid)
    edit(store, sid, 'pro-black-usb-c')
    assert any(i['code'] == 'MISSING_ACCESSORY' for i in store.state(sid)['validation']['issues'])
    with pytest.raises(Problem):
        store.preview_checkout(sid)
    edit(store, sid, 'power-ivory')
    assert store.state(sid)['validation']['ready']


def test_unknown_fee_not_zero(shop):
    store, sid = shop
    ready(store, sid)
    store.inject_fault(sid, 'unknown_fee')
    state = store.state(sid)
    assert state['validation']['total_cents'] is None
    assert not state['validation']['ready']
    assert any(i['code'] == 'UNKNOWN_FEE' for i in state['validation']['issues'])


def test_unknown_variant_is_not_fuzzy_matched(shop):
    with pytest.raises(Problem) as exc:
        edit(*shop, 'dawn')
    assert exc.value.code == 'UNKNOWN_VARIANT'


def test_quantity_bounds_and_extra_fields():
    for q in [0, -1, 6, True, 1.1, '2']:
        with pytest.raises(ValidationError):
            CartEdit(operation='add', variant_id=LIGHT, quantity=q, expected_version=0, request_id='test-quantity')
    with pytest.raises(ValidationError):
        CartEdit(operation='add', variant_id=LIGHT, expected_version=0, request_id='test-extra', actor='user')


def test_user_add_is_a_protected_selection(shop):
    store, sid = shop
    edit(store, sid, actor='user')
    assert store.state(sid)['cart'][LIGHT]['locked']
    for operation in ['remove', 'quantity', 'unlock']:
        with pytest.raises(Problem):
            edit(store, sid, operation=operation, quantity=2)
    with pytest.raises(Problem):
        edit(store, sid, 'pocket-ivory', 'replace', target_id=LIGHT)
    assert LIGHT in store.state(sid)['cart']


def test_lock_can_be_released_only_by_user(shop):
    store, sid = shop
    edit(store, sid, actor='user')
    edit(store, sid, operation='unlock', actor='user')
    edit(store, sid, 'pocket-ivory', 'replace', target_id=LIGHT)
    assert LIGHT not in store.state(sid)['cart']


def test_manual_removal_does_not_return(shop):
    store, sid = shop
    edit(store, sid)
    edit(store, sid, operation='remove', actor='user')
    with pytest.raises(Problem) as exc:
        edit(store, sid)
    assert exc.value.code == 'EXPLICITLY_REMOVED'
    edit(store, sid, actor='user')
    assert LIGHT in store.state(sid)['cart']


def test_stale_agent_cannot_overwrite_user(shop):
    store, sid = shop
    version = store.state(sid)['version']
    edit(store, sid, actor='user')
    with pytest.raises(Problem) as exc:
        edit(store, sid, MIC, expected_version=version)
    assert exc.value.code == 'STALE_STATE'
    assert MIC not in store.state(sid)['cart']


def test_idempotency_binds_content_and_does_not_duplicate(shop):
    store, sid = shop
    version = store.state(sid)['version']
    edit(store, sid, request_id='same-request', expected_version=version)
    result = edit(store, sid, request_id='same-request', expected_version=version)
    assert result['replayed']
    assert result['state']['cart'][LIGHT]['quantity'] == 1
    with pytest.raises(Problem) as exc:
        edit(store, sid, MIC, request_id='same-request')
    assert exc.value.code == 'IDEMPOTENCY_CONFLICT'


def test_timeout_requires_reconciliation_and_preserves_single_effect(shop):
    store, sid = shop
    store.inject_fault(sid, 'write_timeout')
    with pytest.raises(Problem) as exc:
        edit(store, sid, request_id='uncertain-write')
    assert exc.value.code == 'UNKNOWN_EFFECT'
    with pytest.raises(Problem) as exc:
        edit(store, sid, MIC)
    assert exc.value.code == 'RECONCILE_REQUIRED'
    snapshot = store.state(sid, reconcile=True)
    assert snapshot['cart'][LIGHT]['quantity'] == 1
    edit(store, sid, request_id='uncertain-write')
    assert store.state(sid)['cart'][LIGHT]['quantity'] == 1


def test_locked_stock_failure_is_visible_not_replaced(shop):
    store, sid = shop
    ready(store, sid)
    edit(store, sid, operation='lock', actor='user')
    store.inject_fault(sid, 'stock', LIGHT)
    assert not store.state(sid)['validation']['ready']
    with pytest.raises(Problem) as exc:
        edit(store, sid, 'pocket-ivory', 'replace', target_id=LIGHT)
    assert exc.value.code == 'LOCKED'


def test_confirmation_bound_to_exact_cart_version(shop):
    store, sid = shop
    ready(store, sid)
    preview = store.preview_checkout(sid)
    edit(store, sid, operation='lock', actor='user')
    with pytest.raises(Problem) as exc:
        store.checkout(sid, preview['confirmation_token'], store.state(sid)['version'], 'stale-confirm')
    assert exc.value.code == 'STALE_CONFIRMATION'
    assert store.orders(sid) == []


def test_confirmation_expiry_and_wrong_session(shop):
    store, sid = shop
    ready(store, sid)
    p = store.preview_checkout(sid)
    other, _ = store.create_session()
    with pytest.raises(Problem):
        store.checkout(other, p['confirmation_token'], p['version'], 'other-confirm')
    with store.connection(True) as c:
        c.execute('UPDATE confirmations SET expires=0')
    with pytest.raises(Problem):
        store.checkout(sid, p['confirmation_token'], p['version'], 'expired-confirm')


def test_agent_cannot_order_even_with_a_valid_confirmation(shop):
    store, sid = shop
    ready(store, sid)
    preview = store.preview_checkout(sid)
    with pytest.raises(Problem) as exc:
        store.checkout(sid, preview['confirmation_token'], preview['version'], 'agent-attempt', actor='agent')
    assert exc.value.code == 'USER_CONTROL_ONLY'
    assert store.orders(sid) == []


def test_empty_cart_not_ready(shop):
    assert not shop[0].state(shop[1])['validation']['ready']
    with pytest.raises(Problem):
        shop[0].preview_checkout(shop[1])


@pytest.mark.parametrize('text,amount', [('預算 RM300', 30000), ('預算改成 RM250', 25000), ('Budget to RM250.50', 25050), ('A product costs RM200', None)])
def test_explicit_budget_parser(text, amount):
    assert extract_facts(text).get('budget_cents') == amount


def test_no_inferred_port_from_phone_name():
    assert 'device_port' not in extract_facts('I have an iPhone 15')
    assert extract_facts('I need a microphone with Lightning')['needs'] == ['microphone']


def test_message_preserves_locked_light_on_budget_change(shop):
    store, sid = shop
    ready(store, sid)
    store.begin_run(sid, '燈保留，預算改成 RM150', 'new-budget-request', 'test')
    state = store.state(sid)
    assert state['cart'][LIGHT]['locked']
    assert state['constraints']['budget_cents'] == 15000
    assert any(i['code'] == 'OVER_BUDGET' for i in state['validation']['issues'])


def test_model_cannot_remove_existing_requirements(shop):
    store, sid = shop
    result = store.require_items(sid, [], store.state(sid)['version'], 'requirements-edit')
    assert result['state']['constraints']['needs'] == ['light', 'microphone']


def test_reads_do_not_select_products(shop):
    store, sid = shop
    before = store.state(sid)
    get_product(LIGHT)
    get_product(MIC)
    assert store.state(sid) == before


def test_sessions_are_isolated(shop):
    store, sid = shop
    other, _ = store.create_session()
    edit(store, sid)
    assert not store.state(other)['cart']
    assert not store.orders(other)
    assert not store.trace(other)['events']


def test_atomic_plan_preserves_locked_variants(shop):
    from intentcart.domain import PlanItem
    store, sid = shop
    edit(store, sid, actor='user')
    with pytest.raises(Problem) as exc:
        store.apply_plan(sid, [PlanItem(variant_id=MIC)], store.state(sid)['version'], 'plan-missing-lock')
    assert exc.value.code == 'LOCKED'
    assert LIGHT in store.state(sid)['cart']


def test_atomic_plan_rejects_duplicates_exclusions_and_bad_ids(shop):
    from intentcart.domain import PlanItem
    store, sid = shop
    for ids, code in [([LIGHT, LIGHT], 'DUPLICATE_VARIANT'), (['imaginary-product'], 'UNKNOWN_VARIANT')]:
        with pytest.raises(Problem) as exc:
            store.apply_plan(sid, [PlanItem(variant_id=x) for x in ids], store.state(sid)['version'], secrets.token_hex(8))
        assert exc.value.code == code
    edit(store, sid)
    edit(store, sid, operation='remove', actor='user')
    with pytest.raises(Problem) as exc:
        store.apply_plan(sid, [PlanItem(variant_id=LIGHT)], store.state(sid)['version'], 'plan-excluded-id')
    assert exc.value.code == 'EXPLICITLY_REMOVED'


def test_generic_recording_request_infers_essentials_but_not_owned_stand(shop):
    store, sid = shop
    other, _ = store.create_session()
    store.begin_run(other, '我想用手機拍片，預算 RM300。已經有手機和支架。', 'generic-request', 'test')
    c = store.state(other)['constraints']
    assert c['needs'] == ['light', 'microphone']
    assert c['owned'] == ['stand']
    assert c['device_port'] == 'unknown'


def test_manual_replacement_excludes_old_variant(shop):
    store,sid=shop
    edit(store,sid)
    edit(store,sid,'dawn-sage',operation='replace',target_id=LIGHT,actor='user')
    with pytest.raises(Problem) as exc: edit(store,sid,LIGHT)
    assert exc.value.code=='EXPLICITLY_REMOVED'


def test_negated_interface_is_not_an_affirmative_fact():
    assert 'device_port' not in extract_facts('不是 USB-C，我不確定接口。')
    assert 'device_port' not in extract_facts('It is not Lightning.')
    assert extract_facts('不是 Lightning，是 USB-C。')['device_port']=='usb-c'
