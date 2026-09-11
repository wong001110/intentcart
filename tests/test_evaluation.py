"""Checks for the research oracle itself, not new agent-performance claims."""
from copy import deepcopy
import json
from pathlib import Path
from scripts.evaluate import oracle
from intentcart.domain import initial_state,view_state


def test_suite_keeps_complete_splits_and_stable_ids():
    suite=json.loads((Path(__file__).resolve().parents[1]/'evals/scenarios.json').read_text())
    assert len(suite['scenarios'])==20
    assert len({s['id'] for s in suite['scenarios']})==20
    assert sum(s['split']=='held_out' for s in suite['scenarios'])==8
    assert all(s['steps'] and s['oracle']['expect'] in ('ready','conflict','clarify') for s in suite['scenarios'])


def test_oracle_rejects_false_readiness_independently():
    state=view_state(initial_state(),0)
    state['validation']['ready']=True
    faults=oracle(state,{'expect':'ready','kinds':['light'],'cap':30000},{},{'events':[]},'Everything is fine')
    assert {'empty_cart','missing_kind','budget'}<=set(faults)


def test_oracle_rejects_stock_and_bad_port_even_if_report_says_ready():
    raw=initial_state();raw['constraints']['device_port']='usb-c'
    raw['cart']={'clip-black-lightning':{'quantity':1,'locked':False,'source':'agent'}}
    raw['stock_overrides']['clip-black-lightning']=0
    state=view_state(raw,1);state['validation']['ready']=True
    faults=oracle(state,{'expect':'ready','kinds':['microphone'],'port':'usb-c'},{},{'events':[]},'Done')
    assert {'stock','compatibility','wrong_requested_port'}<=set(faults)
