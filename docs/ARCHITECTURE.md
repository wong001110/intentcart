# Architecture and decisions

## Small runnable boundary

`web/` is a native ES-module/CSS storefront served by FastAPI. `intentcart/api.py` provides same-origin session endpoints and NDJSON progress. `agent.py` owns a bounded provider/tool loop; `domain.py` owns pure rules; `store.py` owns SQLite transactions, state versions and receipts; `catalog.py` supplies 40 synthetic variants.

Python/FastAPI/SQLite were chosen because the execution environment could run and test them without downloading a frontend toolchain. This is a scoped research decision, not a claim that other stacks are inferior. There is no frontend build or external asset dependency. Run one worker on loopback; deployment was not part of this assignment.

## Authority and state

A server-generated HttpOnly/SameSite session binds the cart and traces. Mutations require CSRF validation; an Origin header, when present, must match. Model tools are bound to that session internally. Neither actor nor session ID is accepted from tool arguments.

All commerce updates use `BEGIN IMMEDIATE`, compare the expected version, validate the transition and record a content-bound idempotency receipt. `apply_plan` changes the complete proposal atomically and retains locks. An injected write-timeout commits, then reports an unknown effect; the next model mutation is blocked until `inspect_task` reconciles.

The browser rejects older snapshots, and manual edits remain available while a model waits. Final order confirmation is refused during an active model run, preventing late preparation from repopulating a just-ordered cart. Confirmation tokens expire and bind the cart revision; the order is immutable and explicitly simulated.

## Model versus deterministic code

The live model chooses tools, searches and repairs. It can add inferred essential categories but cannot relax hard budgets, owned items, known ports, locks or exclusions. A conservative bilingual user-text extractor records supported explicit facts; unsupported forms require the editable fact controls or clarification. This extractor is not an LLM and its limitations are not hidden.

`ask_user` exposes material model questions. `validate_plan` reports actual rule outcomes. The final success summary is generated from saved state; raw model prose is retained separately as unverified output. Provider-specific reasoning/signature fields may be forwarded in memory for protocol continuity but are not persisted.

Long conversations use a bounded two-layer context. SQLite remains the authority for cart and constraint state. When more than eight conversation messages exist, `store.py` persists a host-derived reference for the older portion: its covered range, lightweight topics, selected normalized user excerpts, and a snapshot of verified constraints. The model receives that block as a labelled `user` message, never as system policy; the system prompt says it is untrusted and non-authoritative. No model-generated summary, model reasoning, or tool payload is retained in this layer. `/api/state` and the chat UI expose the reference so the user can inspect it, and session reset removes it.

`demo` and `baseline` are non-LLM controls. Both use the same catalog, validator and deterministic selection policy. Demo permits three bounded recovery attempts; baseline makes one. Neither automatically handles every dependency. They are useful for UI and test infrastructure, not a substitute for real-model evaluation.

## Recovery, trust and limits

Persisted product state survives a process restart; an in-flight model call does not. The active-run set is process-local, so multi-worker execution is unsupported. Browser cookies are anonymous access handles, not production user accounts. There are no production quotas, role management, distributed leases, live stock or real billing.

No key is sent to the browser, trace or Git. For local development, the server loads only an allowlist of documented `INTENTCART_*` entries from a Git-ignored root `.env`; process environment variables take precedence. Remote providers require HTTPS; the development-only HTTP exception accepts literal loopback IP addresses only. No payment/tool escalation route exists in the model gateway. Product descriptions cannot alter schemas or server permissions. These boundaries reduce exposure; they do not constitute a general prompt-injection security proof.

Development Agent Continuity stays outside the checkout and is not required to run any of the above.
