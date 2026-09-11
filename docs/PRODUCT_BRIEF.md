# Product brief

IntentCart is a controlled shopping environment for investigating whether a tool-using agent can turn incomplete, changing needs into a valid, user-owned cart. It is a research portfolio prototype, not a competitive marketplace. See the actual implementation and verification status in `../PROJECT_STATE.md`.

## Core journey

The user states a goal, budget, owned items and constraints. The agent resolves material uncertainty, searches concrete variants, validates a combination and prepares the cart. The user can browse, choose, replace, lock, remove or revise conditions directly. Both paths operate on the same state. Only the user confirms the final simulated order.

Synthetic products and transactions are acceptable; canned tool outcomes are not. Buying less, reusing equipment, or correctly declining an infeasible request can be successful outcomes.

## Behavioral contracts

| ID | Required behavior | Failure to prevent |
| --- | --- | --- |
| R1 — Interpret | Separate hard facts, preferences, owned items and unknowns. | Fabricating a device specification or treating preference as budget authority. |
| R2 — Clarify selectively | Ask material questions; prepare safe reversible portions where possible. | Unsupported compatibility claims or a needless mandatory questionnaire. |
| R3 — Act on feedback | Choose subsequent actions from actual tool results. | A fixed script misrepresented as a model-driven agent. |
| R4 — Validate | Check concrete variants, quantities, compatibility, availability, budget and dependencies. | Treating unknown as compatible, fees as zero, or omitting essentials. |
| R5 — Mutate real state | Read back effects and distinguish attempts from confirmed state. | Claiming an add after a failed tool call. |
| R6 — Preserve decisions | Shared authoritative state; explicit locks, replacements, removals and facts persist. | Stale overwrite or a product view becoming a selection. |
| R7 — Recover | Reconcile uncertain effects before retry; preserve unaffected selections. | Duplicate effects, silent substitutions or unnecessary resets. |
| R8 — Admit infeasibility | Surface conflicts and insufficient evidence. | Inventing a valid result or silently relaxing constraints. |
| R9 — Preserve checkout control | Enforce user-only simulated submission outside the prompt. | Agent tools or generic execution creating orders. |

## State and trust

A family is not a purchasable variant. Quantities are bounded integers, costs are integer MYR cents, and all synthetic fee assumptions are explicit. Unknown fees prevent readiness. Existing owned categories should not be bought again without a direct user change.

Manual additions/replacements are protected selections. Locks only change through user controls or explicit supported user statements. If a locked item becomes invalid, surface the conflict rather than replacing it. Manual replacements/removals exclude the old variant from autonomous re-addition.

Versions reject stale changes; bound request IDs prevent repeated side effects. Uncertain writes require a state read before another agent mutation. Checkout confirmation is short-lived and bound to the exact cart version. Submission waits until any active preparation run ends.

Catalog text is untrusted data. There is no model-accessible generic HTTP, browser, file execution, checkout or payment tool. User/API identity never comes from a model-supplied actor field.

## Interface and scope

Conversation first, not conversation only. A simple conversation surface, contextual controls, an expandable/shared cart, browsing and details are enough. Display mode, uncertainty and observable tool effects rather than private reasoning. Use stable UI components, not arbitrary generated UI code.

The MVP uses one synthetic desk-recording domain, 40 variants, local persistence, a single live-model adapter, deterministic controls, session-scoped fault injection and user-triggered simulated checkout. Cross-merchant search, real accounts/payments, seller administration, delivery, 3D spatial shopping, long-term profiles, distributed swarms and a custom development harness are excluded.

The concept boards are exploratory, not fixed pixel specifications, real marketplace integrations or verification evidence. Implementation and evaluation limitations must remain visible in the project state and evidence report.
