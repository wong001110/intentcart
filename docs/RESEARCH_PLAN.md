# Research plan

## Question

Can a tool-using shopping agent translate incomplete, changing user intent into a valid cart, preserve explicit choices, recover from changes/failures, and leave submission to the user?

The evaluation unit is the entire system: model, tools, state, validation and UI. Do not attribute deterministic guardrails to model intelligence. Synthetic catalog/checkout is acceptable; fabricated tool execution is not.

## Implemented protocol

`evals/scenarios.json` version `intentcart-eval-v1` contains 20 cases: 12 development and 8 declared held-out cases. Default repetitions: 3. The runner records every input, intervention, tool argument/result, final state, oracle failures, elapsed time and reported token usage. Source and suite hashes identify the actual artifacts. Failures remain in the output and produce a nonzero exit status.

Case families cover clear intent, missing port, follow-up clarification, revised budgets/locks, stock changes, uncertain writes, manual selection, required accessory repair, infeasibility, untrusted catalog instructions, checkout authority, view-only behavior, English wording, Lightning, unknown hardware, locked stock, unknown/restored fees, removals and an indirect filming goal.

Held-out is a declared split for a future frozen-model/prompt experiment, not a claim that these cases were hidden from the implementation author. No blind real-model holdout has run. Before a formal live comparison, freeze code/prompt/configuration, select fresh paraphrases or a separately held dataset, and do not tune on held-out outcomes.

## State-based oracle

`oracle` in `scripts/evaluate.py` does not call the commerce validator or trust agent prose. It independently checks concrete quantities, total, required kinds/families, requested budget/port, stock, owned items, preserved selections and recorded actions. It also checks the service readiness flag for agreement. Multiple valid carts are acceptable; exact IDs are required only for explicit user choices.

For underspecified tasks, safe partial preparation plus a material clarification is expected. For intentionally infeasible tasks, no false-ready result is allowed. Feasible cases cannot pass by habitual refusal. Checkout must remain absent before an explicit human action. The oracle has its own tests; that is not proof the oracle has no omissions.

## Controls and live mode

Both deterministic controls use the same catalog, tool schemas, validator and selection policy. `baseline` makes one preparation attempt; `demo` permits up to three retries after stale/uncertain effects. Their reported differences test recovery infrastructure, not LLM intelligence. Both share a known limitation: automatic accessory-dependency planning is incomplete.

The live driver lets a real configured model choose tool calls and react to feedback, with limits of 10 model rounds and 30 tools. `--allow-live` is required because calls may incur charges. Missing configuration blocks execution; it never substitutes demo. Model selection and provider/task compatibility remain unverified until actual runs.

A meaningful future agent-versus-fixed-flow comparison must use the same task/intervention schedule and disclose comparable resource limits and actual usage. Do not weaken the control to manufacture an advantage. Equivalent or better control results are legitimate outcomes.

## Metrics and artifacts

Primary: final task success by the scenario oracle. Retain hard-constraint rejections, stale attempts, duplicate effects, attempted privilege escalation, recovery outcome and infeasibility/clarification handling. Log all repetitions, tool count, latency and available provider token usage. Cost is not inferred from tokens without a verified price/configuration.

The initial control runs and their failures are summarized in `EVIDENCE.md`. Full reports are generated under ignored `artifacts/`, and the handoff evidence archive retains the executed reports. These deterministic repetitions are not an estimate of stochastic model reliability.

## Claim boundary

Results apply only to this synthetic environment. They do not establish arbitrary-web shopping, real merchant integration, payment safety, general product expertise, commercial viability, or universal prompt-injection resistance. Real-model performance, networked browser integration and independent implementation review remain open.

The portfolio should show a complete task, a failure/recovery example, all repeated results and explicit limits. The project is valuable when it identifies where the agent fails or deterministic controls are necessary, not only when a demo succeeds.
