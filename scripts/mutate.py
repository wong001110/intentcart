"""Targeted fault mutations. Killed means the named behavior test failed, not syntax failure."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TEST_ENV = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
MUTATIONS = [
 ('budget', 'domain.py', "if c['budget_cents'] is not None and (total if total is not None else subtotal) > c['budget_cents']:", 'if False:', 'test_budget_is_a_hard_guard'),
 ('stock', 'domain.py', "if stock_of(state, p) < item['quantity']:", 'if False:', 'test_unfit_variants_are_rejected'),
 ('owned', 'domain.py', "if p['kind'] in c['owned']:", 'if False:', 'test_unfit_variants_are_rejected'),
 ('unknown-spec', 'domain.py', "if c['device_port'] == 'unknown' or p['port'] == 'unknown':", 'if False:', 'test_missing_port_stays_unknown'),
 ('compatibility', 'domain.py', "elif p['port'] != c['device_port']:", 'elif False:', 'test_unfit_variants_are_rejected'),
 ('dependency', 'domain.py', "if family not in families:", 'if False:', 'test_dependency_is_not_optional'),
 ('unknown-fee', 'domain.py', 'if fee is None:', 'if False:', 'test_unknown_fee_not_zero'),
 ('lock', 'domain.py', "if actor == 'agent' and old and old['locked']:", 'if False:', 'test_user_add_is_a_protected_selection'),
 ('excluded', 'domain.py', "if actor == 'agent' and edit.variant_id in s['excluded']:", 'if False:', 'test_manual_removal_does_not_return'),
 ('quantity', 'domain.py', 'quantity: StrictInt = Field(default=1, ge=1, le=5)\n    expected_version', 'quantity: StrictInt = Field(default=1, ge=1, le=500)\n    expected_version', 'test_quantity_bounds_and_extra_fields'),
 ('explicit-budget', 'domain.py', 'patch[\'budget_cents\'] = value', "patch['budget_cents'] = value + 1", 'test_explicit_budget_parser'),
 ('version', 'store.py', 'if expected != version:', 'if False:', 'test_stale_agent_cannot_overwrite_user'),
 ('idempotency', 'store.py', "if old['digest'] != digest:", 'if False:', 'test_idempotency_binds_content_and_does_not_duplicate'),
 ('reconcile', 'store.py', "if actor == 'agent' and s['reconcile_required']:", 'if False:', 'test_timeout_requires_reconciliation_and_preserves_single_effect'),
 ('checkout-authority', 'store.py', "if actor != 'user':", 'if False:', 'test_agent_cannot_order_even_with_a_valid_confirmation'),
 ('confirmation', 'store.py', "if not confirmation or confirmation['expires'] < time.time() or confirmation['version'] != version or expected != version:", 'if False:', 'test_confirmation_bound_to_exact_cart_version'),
 ('lost-write', 'store.py', "c.execute('UPDATE sessions SET state=?,version=? WHERE id=?', (encoded(state), version, sid))", 'pass', 'test_write_is_persisted_and_read_back'),
 ('required-items', 'store.py', "(set(s['constraints']['needs']) | set(needs))", 'set(needs)', 'test_model_cannot_remove_existing_requirements'),
 ('plan-lock', 'domain.py', "if previous['locked'] and (pid not in new or new[pid]['quantity'] != previous['quantity']):", 'if False:', 'test_atomic_plan_preserves_locked_variants'),
 ('plan-exclusion', 'domain.py', "if pid in s['excluded']:", 'if False:', 'test_atomic_plan_rejects_duplicates_exclusions_and_bad_ids'),
 ('plan-duplicate', 'domain.py', 'if pid in new:', 'if False:', 'test_atomic_plan_rejects_duplicates_exclusions_and_bad_ids'),
 ('csrf', 'api.py', "if not secrets.compare_digest(token, store.session(sid)['csrf']):", 'if False:', 'test_api.py::test_csrf_and_cross_origin_rejected'),
 ('origin', 'api.py', "if origin and origin.rstrip('/') != str(request.base_url).rstrip('/'):", 'if False:', 'test_api.py::test_csrf_and_cross_origin_rejected'),
 ('demo-label', 'agent.py', "model_evidence=config.driver == 'live'", 'model_evidence=True', 'test_agent.py::test_demo_is_labelled_and_uses_real_tools_and_cart'),
 ('generic-intent', 'domain.py', "kinds = ['light', 'microphone', 'stand']", "kinds = ['stand']", 'test_generic_recording_request_infers_essentials_but_not_owned_stand'),

]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='artifacts/mutations.json')
    args = parser.parse_args()
    baseline = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests'], cwd=ROOT, env=TEST_ENV, capture_output=True, text=True)
    if baseline.returncode:
        print(baseline.stdout, baseline.stderr)
        raise SystemExit('Baseline failed; mutation results would be meaningless.')
    results = []
    for name, filename, before, after, target in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix='intentcart-mutant-') as tmp:
            scratch = Path(tmp)
            shutil.copytree(ROOT / 'intentcart', scratch / 'intentcart', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(ROOT / 'tests', scratch / 'tests', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(ROOT / 'web', scratch / 'web')
            file = scratch / 'intentcart' / filename
            source = file.read_text()
            if source.count(before) != 1:
                raise SystemExit(f'Ambiguous mutation {name}')
            changed = source.replace(before, after, 1)
            compile(changed, str(file), 'exec')
            file.write_text(changed)
            run = subprocess.run([sys.executable, '-m', 'pytest', '-q', (f'tests/{target}' if '::' in target else f'tests/test_commerce.py::{target}')], cwd=scratch, env=TEST_ENV, capture_output=True, text=True, timeout=25)
            status = 'killed' if run.returncode == 1 and 'failed' in run.stdout else ('survived' if run.returncode == 0 else 'error')
            results.append(dict(name=name, file=f'intentcart/{filename}', target=target, status=status, output=run.stdout))
            print(f'{name}: {status}', flush=True)
    report = dict(kind='targeted deterministic mutations, not model evaluation', total=len(results),
                  killed=sum(r['status'] == 'killed' for r in results), results=results,
                  source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'intentcart').glob('*.py'))})
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    if report['killed'] != report['total']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
