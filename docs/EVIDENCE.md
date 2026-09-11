# Evidence and limitations

Recorded 2026-09-11. **MVP candidate, not a fully verified research result.**

## What actually ran

| Check | Observed outcome | Claim boundary |
| --- | --- | --- |
| `python -m pytest -q` | **69 passed** | Commerce, SQLite, API, loop/protocol, and evaluation-oracle tests. Model responses in protocol tests are explicitly mocked. |
| `python scripts/mutate.py` | **25/25 targeted mutants killed** | Compiled mutations cause the named behavioral tests to fail. This is not exhaustive mutation coverage or independent review. |
| `node --check web/app.js` and `web/art.js` | Passed | JavaScript syntax only. |
| `python scripts/evaluate.py --driver demo --repeats 3` | **57/60** | Deterministic adaptive control; **not an LLM**. |
| `python scripts/evaluate.py --driver baseline --repeats 3` | **54/60** | Deterministic fixed-flow control; **not an LLM**. |
| Live provider evaluation | **BLOCKED; zero real provider runs** | No provider credentials were available; terminal DNS was also unavailable. No live-provider or model-quality claim. |
| `python scripts/browser_test.py` | **BLOCKED** | Managed Chromium rejected loopback navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`. No browser-to-HTTP-to-database success claim. |
| Offline DOM previews | Rendered desktop, browse, and mobile views | Original UI code with a read-only bootstrap fixture; no live API connection. Illustrates layout, not integrated shopping behavior. |
| Independent implementation review | **NOT PERFORMED** | Implementing-agent self-review does not satisfy this gate. |
| CI, deployment, merge | **NOT PERFORMED** | Local tests are not CI. Implementation does not grant merge or deployment authority. |

A final successful test rerun does not erase earlier failures. Raw evaluation outputs retain every failed run. The reproducible source fingerprints are in [source-sha256.json](evidence/source-sha256.json); a compact factual summary is in [summary.json](evidence/summary.json).

The evaluation reports also record the actual local execution commit and hashes of the six runtime modules. Publication through GitHub's Git-data API creates different commit identities while preserving source bytes. Match the source hashes; do not rewrite a historical test record to pretend it executed at a later publication commit.

## Failures retained, not hidden

- **S08, necessary accessory:** both deterministic controls fail all three repeats when the user selects the Pro microphone that requires the power accessory. The validator correctly blocks checkout, but the control planner does not add the dependency. Safe refusal is not counted as success on this feasible task.
- **S06, uncertain write:** the fixed flow fails all three repeats because it does not perform the required readback after `UNKNOWN_EFFECT`. The adaptive deterministic control does reconcile. A ready-looking cart is insufficient if the required recovery behavior did not occur.

Twenty scenario definitions were run three times for each control. Twelve are marked development and eight held-out. The author could read all definitions: these are protocol partitions, **not a blinded or independently administered holdout**. Repeated deterministic runs do not measure stochastic model reliability. There is no basis yet to claim an agent success rate, superiority over a model-matched baseline, or arbitrary shopping competence.

## Observable boundaries

Persisted cart contents, exact variants, quantities, known costs, stock, explicit selections, and simulated order records are checked independently of model prose. The evaluation oracle does not call the application's commerce validator as its only success test. It can accept multiple valid carts.

The `model_evidence` field in runtime configuration/metrics indicates the selected driver, **not that a run has been externally verified**. A mock transport may exercise the live adapter with that mode flag; such tests remain protocol tests. Use run provenance, provider identity, and actual responses to classify evidence. The default UI explicitly identifies its deterministic demo mode.

External descriptions are data, not authority. Tools have no generic network/browser/execution action and no order tool. Human checkout uses a separate route with session/CSRF, a short-lived version-bound confirmation, and an active-run guard. This is defense-in-depth for a local research prototype, not a claim of production security certification.

## Still required before full MVP acceptance

1. Run the actual browser integration test in an environment that permits local navigation; inspect desktop/mobile UI and fix any failures.
2. Configure an authorized tool-capable provider, run real tasks and repeated evaluations with full failed-run retention, and assess the live model's ability to repair dependencies, handle paraphrases, and resist untrusted catalog instructions.
3. Obtain independent review of the implementation and evidence. Extend targeted mutations wherever that review finds an uncovered material behavior rule.

Known scope limits remain: one synthetic domain, conservative bilingual extraction of hard facts, category-level owned items, bounded search/tool budgets, single-worker execution, no durable in-flight model-job recovery, no real payments, no cross-merchant operation, and no production account/abuse-management layer. User-originated settings are editable; unsupported natural-language constraint updates must not be silently described as fully understood.

These open gates are not waived. The runnable candidate and research tooling can be reviewed without mistaking them for a completed real-model experiment.
