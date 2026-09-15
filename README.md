# IntentCart

**Tell it what you need. Make the final call.**

A conversation-first shopping research prototype: an agent prepares a real, persisted cart in a **synthetic** catalog; the user browses, changes selections, and submits the final **simulated** order.

> **Status: runnable MVP candidate, not a validated agent-performance claim.** The storefront, commerce service, model adapter, tool loop and evaluation runners are implemented. Automated domain/API/protocol checks ran. Real-model evaluation, networked browser E2E, and independent review remain open. See [project state](PROJECT_STATE.md) and [evidence](docs/EVIDENCE.md).

## What you can do

Describe a desk-recording goal in Traditional Chinese or English, give a budget, and identify equipment already owned. Browse 40 synthetic variants, inspect specifications without changing the cart, manually replace or lock a choice, revise constraints, and inspect actual tool actions. Fault controls can change stock, make fees unknown, or simulate a write that succeeded but timed out. Only the user can confirm the simulated order.

Chat and manual controls share the same SQLite-backed product state. Versions reject stale writes; request IDs prevent duplicate effects; an uncertain write requires reconciliation. Locks, concrete variants, known compatibility, stock, dependencies and hard budgets are enforced outside the model prompt.

**This is not cross-merchant shopping, real payment, a deployed service, or proof that an LLM solves every task.** All prices are MYR fixtures inclusive of simulated fees. No product rating or merchant claim is real.

## Run locally

Python **3.11+**. Tested in Python 3.13.5. No Node build step or cloud account is needed for offline mode.

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn intentcart.api:create_app --factory --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. The default **demo** driver is a transparent deterministic control, **not an LLM**. The mode is displayed in the UI, API, traces, and reports. Product state lives in `var/intentcart.sqlite`; use `INTENTCART_DB_PATH` for a different local file. Do not run multiple Uvicorn workers: this prototype's active-run ownership is process-local.

Try:

> 我需要桌面燈和麥克風，預算 RM300，已有支架。
>
> 我的手機是 USB-C。
>
> 保留燈，預算改成 RM180。

The first request should prepare the safe portion and ask for the missing interface. Directly selected products are automatically protected; use the visible unlock control to release that choice.

## Connect a real model

The live driver uses an OpenAI-compatible **Chat Completions tool-calling** endpoint. Select a model that supports that API shape. Provider/model compatibility and task quality must be tested; no default model performance is implied.

```bash
# Copy .env.example to .env, then set these values in .env:
INTENTCART_DRIVER=live
INTENTCART_API_BASE=https://api.deepseek.com
export INTENTCART_API_KEY=YOUR_PROVIDER_KEY
INTENTCART_MODEL=deepseek-v4-flash
INTENTCART_MAX_ROUNDS=6
INTENTCART_MAX_TOOLS=12
python -m uvicorn intentcart.api:create_app --factory --host 127.0.0.1 --port 8000
```

Copy `.env.example` to `.env`; the local server accepts only the documented `INTENTCART_DRIVER`, `INTENTCART_API_BASE`, `INTENTCART_API_KEY`, `INTENTCART_MODEL`, `INTENTCART_MAX_ROUNDS`, `INTENTCART_MAX_TOOLS`, and `INTENTCART_DB_PATH` keys from that file. Live defaults are six model rounds and 12 tool calls; use the two limits to trade completeness for speed and cost. `.env` is ignored by Git, and explicitly set system environment variables take precedence, which keeps CI and temporary provider overrides possible. Keys stay server-side; never commit them. Live mode fails configuration rather than silently falling back to demo. Provider usage may incur charges.

The model chooses searches, inspections, clarifications and cart proposals. It has no general network, browser, execution, checkout or payment tool. A host-generated summary reports the actual saved cart; model final prose is retained separately as unverified research output. `ask_user` preserves material model questions in the conversation.

For a longer live conversation, the server sends the model the eight newest saved messages plus a compact, host-derived reference to older **user** messages. It never stores model reasoning or tool payloads in that memory. The reference is visibly labelled in the chat, supplied as untrusted user data, and cannot override the current request or the saved cart, budget, permissions, and compatibility facts. This keeps context bounded without adding a separate summarization-model call or provider cost.

## Verify and evaluate

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/mutate.py
python -m playwright install chromium
python scripts/browser_test.py
python scripts/evaluate.py --driver demo --output artifacts/evaluation-demo.json
python scripts/evaluate.py --driver baseline --output artifacts/evaluation-baseline.json
# Explicitly opt into potentially billable model calls:
python scripts/evaluate.py --driver live --allow-live --output artifacts/evaluation-live.json
```

`CHROMIUM_PATH` may point to an existing browser. The browser runner starts and stops a temporary loopback server and DB. It exits **2** when the environment blocks verification, **1** on test failure, and **0** only on success. Do not disable managed browser policies to make it pass.

The evaluation suite has 20 cases, three repeats by default, and declared development/held-out splits. Every result, including failures, records tool effects and state. Deterministic repetitions validate the machinery; they do not measure stochastic model reliability. The split is not a completed blind holdout experiment.

## Boundaries and known limitations

Hard facts are extracted with a small, inspectable bilingual grammar, not unlimited language understanding. Unsupported paraphrases, quantities, device-name inference and complex hardware compatibility need clarification or explicit controls. Owned items are category-level; there is no long-term user profile. The bounded conversation reference is session-scoped context, not a profile, and is cleared with the chat. Deterministic controls cannot repair every accessory dependency. The live agent's ability to do better is **not yet measured**.

This is loopback-first research software, not an Internet-hardened multi-user shop. There is no production identity system, global rate limiting, distributed run ownership, payment gateway, merchant integration, or deployment. A browser session has an HttpOnly cookie and CSRF checks, but clearing cookies loses access to that anonymous session. SQLite persists state, not a resumable in-flight model process.

## Development

**AI-Native Development Practice**: native-first tools, bounded phases, coherent commits, behavioral/mutation evidence and explicit review gates. The owner's current authorization covers implementation through the MVP, not automatic merge or deployment. Agent Continuity may track the coding assignment **outside the checkout**; it is not a product dependency.

| Document | Purpose |
| --- | --- |
| [Project state](PROJECT_STATE.md) | Actual implementation and verification status |
| [Product brief](docs/PRODUCT_BRIEF.md) | Behavioral contracts and exclusions |
| [Architecture](docs/ARCHITECTURE.md) | State, tools, trust boundaries and stack decisions |
| [Research plan](docs/RESEARCH_PLAN.md) | Scenarios, controls, oracle and claim limits |
| [Evidence](docs/EVIDENCE.md) | Executed results, failures and unverified gates |
| [Development](docs/DEVELOPMENT.md) | Phase, mutation and review policy |
| [Agent entrypoint](AGENTS.md) | Minimal contributor instructions |
