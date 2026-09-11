# AI-Native Development Practice

## Authority and purpose

IntentCart uses the owner's **AI-Native Development Practice** as its coding and delivery method. This is distinct from the runtime shopping agent under study.

**Current instruction: documentation only; do not start implementation.** See [PROJECT_STATE.md](../PROJECT_STATE.md). The rules below govern future authorized work, not permission to begin it.

## Native-first, with explicit boundaries

Use the coding environment's existing planning, tools, delegation, review, tracing, and repository capabilities first. Add custom orchestration only for a demonstrated gap. Do not recreate a harness, phase engine, or session-memory system just because the product contains an agent.

Maintain a small set of documents for scope, state, material decisions, and verification. Avoid exhaustive pre-written implementation instructions. Adapt implementation details to the actual environment and findings without silently changing product contracts.

## Responsibilities

The owner defines product direction, authorizes the working scope, and decides genuinely material changes. Main Agent owns integration, scope control, evidence review, and the decision to proceed, repair, or mark work blocked.

Sub-agents are optional and receive bounded tasks with explicit inputs, boundaries, and expected evidence. A delegated agent's completion message does not establish correctness. Do not claim a separate reviewer or parallel verification ran when the environment did not provide one.

After implementation is authorized, ordinary reversible choices inside that scope need not trigger repeated approval requests. Scope expansion, real spending or ordering, sensitive account access, destructive changes, publication outside the authorized repository work, and deployment beyond granted permission require owner involvement.

## Phase loop

For each authorized phase:

1. Define the outcome, exclusions, affected contracts, risks, and acceptance evidence before editing.
2. Implement a coherent slice using native tools; use bounded delegation where useful.
3. Run the relevant checks and inspect real state changes, not only returned prose.
4. Perform independent verification of the change, with negative and boundary cases. Label self-review separately; it is not independent review.
5. Main Agent evaluates evidence and records **proceed**, **repair**, or **blocked**. Only proceed when required gates pass.
6. Publish coherent changes and update project state with actual delivery and evidence. Implementation, verification, PR creation, merge, and deployment are distinct milestones.

Suggested work states are `TODO -> IN_PROGRESS -> IMPLEMENTED -> VERIFYING -> VERIFIED`, with `BLOCKED` and `DEFERRED` as explicit alternatives. Unknown, missing, or stale evidence must not be represented as verified. If independent verification is required but unavailable, keep that gate open rather than relabeling self-review.

## Verification and mutation gate

Write behavior tests from the contract, including the happy path, negative cases, boundaries, and invariants. Every explicit behavior rule should have at least one test demonstrated to kill a relevant mutation; coverage alone does not meet this requirement.

For critical rules, plan mutations such as removing a budget guard, reversing a lock check, selecting a wrong variant, skipping a state write, accepting a stale update, retrying without reconciliation, or exposing order submission to the shopping agent. Actually run the applicable mutation tooling once implementation exists.

A meaningful surviving mutant is a gap to repair, not a green result. An equivalent or non-applicable mutant requires recorded justification and review rather than silent exclusion. Keep not-run mutation work visible. At this documentation-only stage there are no implemented rules, tests, mutation runner, or mutation results.

Verification should establish that UI events, agent tool calls, application state, and user-visible outcomes agree. A passing unit test alone does not prove an end-to-end shopping task or a real external integration.

## Evidence discipline

Record the tested commit, environment, fixture/scenario version, relevant model/provider settings, actual command or run identifier, tool events, state before/after, observed result, and limitations. Retain initial failures and subsequent repairs where they explain what changed.

Tests of deterministic commerce rules and evaluations of stochastic agent behavior are separate evidence. Preserve failed agent runs and report repeated-run outcomes, not a hand-picked demo. Claims are limited to the environment actually exercised.

Do not store credentials or sensitive user data in logs. Observable tool actions, results, and concise user-facing explanations are sufficient; private chain-of-thought is not a required artifact.

## Commit and publication discipline

Use coherent phase- or outcome-level commits, not a commit for every small edit. Future implementation should normally go through a scoped PR with the evidence needed for that change and a squash merge when merge is authorized. Do not bypass repository checks or infer deployment permission from a merge.

Documentation-only initialization of an empty repository is a separate bootstrap activity. It does not start the implementation roadmap or imply product verification. Review and report documentation checks honestly as documentation checks.

## Project state versus Agent Continuity

Repository documentation owns product scope, architecture decisions, delivery phases, review rules, and project status. The repository must remain understandable without a particular coding environment's memory.

Agent Continuity, if separately used for a bounded assignment, is optional environment-side assistance. Keep its SQLite database, leases, event ledger, session records, mappings, checkpoints, and helper runtime outside the checkout. Do not add continuity state directories, required runtime scripts, package hooks, CI jobs, or symlinks to this repository as a development prerequisite.

The minimal root `AGENTS.md` only points to repository instructions; it does not require continuity infrastructure. Future application persistence for IntentCart's shopping tasks and cart is **product state**, not development-session continuity, and should be designed through normal implementation review.

## Current stop condition

Finish the documentation update and stop. Do not scaffold a project, choose and install a stack, run an implementation spike, add executable tests, configure CI, or deploy until the owner explicitly authorizes development.
