# Product brief

**Status: intended behavior, not implemented functionality.** Current execution authorization is recorded in [PROJECT_STATE.md](../PROJECT_STATE.md).

## Purpose and boundary

IntentCart is a controlled shopping environment for investigating whether a shopping agent can translate incomplete, changing needs into a valid, user-owned cart. It is a research portfolio prototype; business competition, merchant acquisition, and exhaustive commerce functionality are not its current objectives.

The first environment is an owned website with a controlled catalog and cart. Synthetic products and simulated checkout are acceptable, provided they are labeled honestly. Product queries, stock responses, cart mutations, and validation outcomes must still operate on actual application state rather than canned conversation outcomes.

The agent prepares; the user decides and submits. Spending less, reusing existing equipment, or declining to propose an invalid purchase can be correct outcomes.

## Intended user journey

A user states a goal, budget, and any important constraints or owned items. The agent resolves material uncertainty, searches products, chooses concrete variants and quantities, validates the combination, and prepares the cart. The user can browse, select, lock, remove, or replace products directly at any point. Subsequent agent work uses those changes rather than maintaining a separate conversational cart.

When requirements or stock change, preserve valid work and repair affected selections. Hand off a clear cart summary for user-triggered simulated order submission. Do not claim that preparing the cart has completed the purchase.

## Behavioral requirements

| ID | Required behavior | Observable failure to prevent |
| --- | --- | --- |
| R1 — Interpret | Separate hard constraints, soft preferences, owned items, and unknowns. | Inventing a device specification or treating a preference as permission to exceed budget. |
| R2 — Clarify selectively | Ask for missing information that materially changes suitability; proceed with safe, reversible preparation where possible. | A long mandatory questionnaire or a guess that could make a purchase unsuitable. |
| R3 — Act on feedback | Choose searches and subsequent actions from the request and actual tool results. | A fixed script that produces the same success story regardless of returned data. |
| R4 — Validate | Check concrete variants, quantities, known compatibility rules, availability, budget, and missing essentials. | Treating absent compatibility data as confirmation or ignoring required accessories. |
| R5 — Mutate real state | Read back relevant cart effects; distinguish attempts from confirmed results. | Saying an item was added when the tool failed or the cart is unchanged. |
| R6 — Preserve decisions | Keep one authoritative shopping state and respect explicit selections, locks, removals, and constraint updates. | Overwriting a user edit with a stale agent result or inferring a selection merely from a product view. |
| R7 — Recover | Reconcile uncertain effects before retrying; repair only affected selections and revalidate dependencies. | Duplicate additions after a timeout, silent substitutions, or restarting valid parts of the cart. |
| R8 — Admit infeasibility | Explain conflicting constraints or insufficient evidence; request a decision when relaxation is necessary. | Fabricating a suitable product or silently exceeding a hard limit. |
| R9 — Preserve checkout control | Allow only the user to submit the final simulated order through an enforced boundary. | A shopping-agent tool or generic action path creating an order or triggering payment. |

## State and trust rules

These are product contracts, not a finalized schema or stack choice:

- Distinguish a product family, a purchasable variant, quantity, and the concrete offer used for the cart.
- Record constraints, owned items, selected items, locks, unresolved questions, known costs, and the latest authoritative cart state.
- Viewing a product is not selecting it. Selecting it is not permission to submit an order.
- A locked item stays locked until the user explicitly changes that decision. If it becomes unavailable or incompatible, surface the conflict rather than silently replacing it.
- A hard budget cannot be relaxed by the agent. Unknown fees or specifications must remain unknown, not become zero or a fabricated compatible value.
- For the initial controlled environment, explicitly define whether synthetic prices include all fees. A fully validated budget claim requires the stated cost scope to be known.
- Cart changes must detect stale state and uncertain previous effects. The exact transaction/version/idempotency design is deferred to implementation.
- Product descriptions and other catalog text are untrusted data, not instructions that can change tool permissions or user constraints.
- Enforce user-only order submission outside the model prompt. Do not expose a general HTTP, browser, or execution capability that can bypass that boundary.

## UI direction

Keep the interface small: a conversation surface, contextual product cards, an expandable cart, and a browse view. One main recommendation is the default; expose alternatives or side-by-side comparisons only when they help the user's decision.

Direct controls should handle simple actions such as selecting a variant, removing an item, replacing a product, or locking a choice. Do not turn a few clicks into an unnecessarily long conversation. Show concise task progress and relevant uncertainty, not an unrestricted internal reasoning transcript.

Use known components with typed data and actions. Product discovery, browsing, and chat share one shopping state. The specific desktop/mobile layout and visual identity remain undecided. The brainstorming boards are not binding pixel specifications or proof of implemented features.

## Initial scope and exclusions

**Planned initial scope:** one controlled product domain; a small catalog; one shopping task and cart; a real tool-using agent loop; necessary clarification; manual browsing; concrete cart edits; constraint validation; dynamic repair; visible task/action evidence; and user-triggered simulated checkout.

**Not required initially:** cross-merchant search, real marketplace accounts, browser automation, real payments, delivery operations, seller administration, subscriptions, loyalty schemes, 3D spatial shopping, extensive long-term personalization, multi-agent swarms, arbitrary UI code generation, or a custom general-purpose agent harness.

The phone-recording accessory example, catalog size, and individual tools are planning aids. Choose final fixtures and implementation contracts during an authorized feasibility phase, not by presenting these proposals as already accepted code-level decisions.
