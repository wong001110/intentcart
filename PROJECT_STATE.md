# Project state

Updated: **2026-09-11**

## Current authorization and delivery

| Field | Current state |
| --- | --- |
| Assignment | Document the agreed IntentCart direction; do not begin development. |
| Delivery phase | P0: documentation baseline. |
| Allowed work | Repository documentation and planning updates. |
| Implementation authorization | **NOT_AUTHORIZED** until the owner explicitly starts implementation. |
| Application implementation | **NOT_STARTED**. |
| Executable tests / experiments | **NOT_RUN**; no application or evaluation runner exists. |
| Product verification | **NOT_VERIFIED**. |
| Independent implementation review | Not performed; no implementation exists. |
| Deployment | None. |
| Technology and model selection | Undecided. |

The documentation baseline consists of the README, product brief, research plan, development practice, this state record, and the minimal agent entrypoint. These are planning artifacts, not evidence that the shopping agent works.

## Confirmed direction

- Name: **IntentCart**. Repository: `wong001110/intentcart`.
- Purpose: a research portfolio project that demonstrates whether an agent can handle user shopping requests, not a competitive-marketplace exercise.
- Initial setting: an owned shopping website and cart; cross-commerce operation is not needed to validate the initial research question.
- Interaction: conversation-first, with manual product browsing and selection preserved.
- Product state: chat and direct user actions share the same cart and explicit selections.
- Autonomy: the agent performs ordinary shopping preparation within the request; the user retains final order submission.
- Capability focus: intent understanding, useful clarification, tool use, constraint handling, actual cart updates, and recovery after changes or failures.
- Development method: **AI-Native Development Practice**, not a repository-managed Agent Continuity runtime.
- Current boundary: document now, implement later only after explicit authorization.

## Planning proposals, not finalized decisions

A single product domain with tens of synthetic products is the proposed starting scope. Desk-based phone-recording accessories, RM-denominated examples, roughly 40–60 products, and approximately 20 scenarios with three runs each are illustrative planning values. They are not a frozen catalog, dataset, or release contract.

A single shopping agent is the proposed baseline. Multi-agent orchestration is not needed merely to label the product agentic. The runtime provider, stack, persistence design, test runner, UI design, locale coverage, and deployment target remain open.

The concept illustrations discussed during brainstorming are visual references only. Any cross-platform copy, external-checkout wording, placeholder ratings, or dense dashboard layout in those illustrations does not override the product brief. This initial prototype uses its own catalog/cart and a clearly labeled user-triggered simulated checkout.

## Proposed phases

All phases after P0 are **NOT_STARTED / NOT_AUTHORIZED** at this baseline. Once the owner authorizes a defined implementation scope, Main Agent may progress within that scope only after the relevant gates pass; the phase list itself is not an instruction to execute.

| Phase | Proposed outcome | Exit evidence required before progressing |
| --- | --- | --- |
| P0 — Definition | Scope, research question, delivery rules, and pause boundary are documented. | Consistent documentation; no product-readiness claim. |
| P1 — Feasibility and contracts | Select a viable stack/provider and prove the smallest tool/state boundary; define fixtures and measurable behavioral contracts. | Actual feasibility checks, decision rationale, reproducible environment, and explicit known gaps. |
| P2 — End-to-end slice | One real agent loop searches and prepares a cart; browsing shares that state; user-only simulated checkout works. | End-to-end and negative-path evidence, boundary tests, mutation gate, and independent verification. |
| P3 — Change and recovery | Preserve locks, handle revised requests, reconcile stale/manual edits, and recover from stock or tool failures. | Adversarial scenarios and state assertions, mutation evidence, and independent verification. |
| P4 — Evaluation and portfolio | Run repeated and held-out scenarios against a meaningful baseline; report outcomes and limitations. | Reproducible run records, complete results including failures, and a bounded case study. |

Main Agent can simplify or revise these proposed phase boundaries when implementation starts, provided the research scope and verification obligations are preserved and changes are recorded. Do not create a detailed multi-phase harness before a product need exists.

## Next permissible action

Clarify or refine these documents. Starting P1, choosing a stack through an executable spike, creating fixtures, and building the application require a subsequent explicit implementation instruction.

## State maintenance

Update this file when authorization, phase outcome, material decisions, blockers, or evidence change. Keep detailed product requirements in [PRODUCT_BRIEF.md](docs/PRODUCT_BRIEF.md), evaluation design in [RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md), and delivery policy in [DEVELOPMENT.md](docs/DEVELOPMENT.md). Do not duplicate a development-session ledger here.
