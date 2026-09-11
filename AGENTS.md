# Agent entrypoint

IntentCart uses **AI-Native Development Practice**. Read `PROJECT_STATE.md`, `docs/PRODUCT_BRIEF.md`, `docs/DEVELOPMENT.md`, and `docs/RESEARCH_PLAN.md` before changing scope.

The owner explicitly authorized phase-by-phase implementation through the MVP on 2026-09-11, superseding the earlier documentation-only stop. This does not authorize automatic merge, deployment, paid provider calls, real shopping, or unrelated roadmap work. Latest explicit owner instructions prevail over historical status.

## Working rules

- Native tools first; bounded delegation only where helpful. Main Agent owns integration and proceed / repair / blocked decisions.
- One authoritative product state for chat and manual shopping. Never turn product views into selections.
- Preserve user constraints, locks, explicit removals and concrete variants. The agent never gets order/payment authority or generic HTTP/browser/execution tools.
- Use coherent phase/outcome commits. Normal delivery is a scoped PR; squash merge only when separately authorized and required gates pass.
- Test actual persisted effects, negative cases, stale versions and uncertain writes. Run relevant targeted mutation checks; coverage alone is not acceptance.
- Separate deterministic demo, mocked protocol tests and real-model evidence. Missing/stale/blocked evidence is not a pass.
- Self-review is not independent review. Keep unavailable review and browser/model checks open, rather than changing policy to declare completion.
- Keep credentials and anonymous session data out of source and public evidence. Do not require private model reasoning.

## Commands

`python -m pytest -q`; `python scripts/mutate.py`; `python scripts/browser_test.py`.
For control evaluations: `python scripts/evaluate.py --driver demo` or `--driver baseline`.
Real evaluation requires owner-provided configuration and an explicit `--allow-live` cost opt-in.

The repository must build and test without Agent Continuity. Any development-environment SQLite, checkpoint, scope ledger or helper belongs outside the entire worktree. The application's `var/intentcart.sqlite` is separate **product data**, not coding-agent continuity.
