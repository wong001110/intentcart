# Project state

Updated: **2026-09-11**

## Authorization and actual delivery

| Field | Current state |
| --- | --- |
| Assignment | Implement the agreed IntentCart research MVP, phase by phase, with coherent commits. |
| Authorization | Owner explicitly superseded the documentation-only pause. |
| Development method | AI-Native Development Practice; optional external Agent Continuity v0.4.0. |
| Application | Runnable MVP candidate: storefront, product state, commerce rules, live adapter/tool loop, controls and research runners. |
| Automated verification | 69 domain/API/mock-protocol/oracle tests passed; targeted mutations executed. See evidence. |
| Real model evaluation | **BLOCKED / NOT_RUN**: no configured provider credentials or terminal DNS in the implementing environment. |
| Networked browser E2E | **BLOCKED** by managed Chromium policy at loopback navigation. Test runner retained; policy not changed. |
| Visual inspection | Offline fixture-based DOM rendering inspected at desktop/mobile sizes; not browser/API integration evidence. |
| Independent review | **NOT_PERFORMED**. Implementer self-review and automated tests are not separate reviewer signoff. |
| Delivery target | Scoped implementation PR. Publication, merge and deployment are distinct milestones. |
| Merge / deployment | Not authorized by the implementation request; not performed. |

The program can be run locally in deterministic demo mode. A configurable real tool-calling model path exists, but its correctness with a real provider and its shopping performance have not been verified. **Do not label this a fully validated agent MVP until the open gates are satisfied.**

## Phase outcomes

| Phase | Implemented work | Gate state |
| --- | --- | --- |
| P1 — Commerce contracts | 40 synthetic variants, authoritative SQLite cart, compatibility/budget/stock rules, locks, versions, idempotency, human-only simulated checkout. | Automated core checks passed; no independent reviewer signoff. |
| P2 — Shopping interface and tools | Conversation/browse UI, shared cart, clarification tool, bounded live tool loop, explicit offline drivers, traces and fault injection. | API and mock protocol checks passed. Browser E2E and real-provider checks blocked. |
| P3 — Evaluation and handoff | 20-case repeatable suite, independent state oracle, mutation runner, browser runner, setup/architecture/evidence docs. | Controls executed with all failures retained. Real-model comparison and independent review remain open. |

These are implementation milestones, not retroactive waivers of phase verification. Work that could be completed without unavailable services was delivered; open acceptance conditions remain blocked rather than marked passed.

## Finalized MVP decisions

Python 3.11+ with FastAPI, SQLite, and native browser ES modules/CSS. One local single-worker server, one session-scoped task/cart, Traditional Chinese UI with limited Chinese/English fact extraction. Single-agent Chat Completions tool-calling adapter; no custom general-purpose harness. All values are synthetic MYR, inclusive of simulated fees, except explicit unknown-fee fault cases.

The default `demo` is not an LLM. `baseline` is the same deterministic selection policy with one execution attempt; `demo` allows bounded recovery retries. Live performance cannot be inferred from their comparison. Configuration and claim limits are in the README and research plan.

## Material open items

1. Configure a real supported model, then run development and held-out evaluations without tuning on held-out failures. Preserve every outcome and provider configuration.
2. Run the supplied real browser test in a policy-permitted local environment; fix any observed UI/HTTP integration failures.
3. Obtain the required independent implementation review and resolve material findings before calling review complete or merging.
4. Known scope limits include conservative fact extraction, category-level owned items, deterministic accessory-repair failure, process-local run ownership, and no production auth/deployment.

Project requirements and limitations live in normal documents, not in a private development state store. Any external continuity record only tracks the current coding assignment and cannot grant further permissions.
