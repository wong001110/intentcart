# IntentCart

**Tell it what you need. Make the final call.**

An agentic shopping research prototype that turns user intent into a validated cart through conversation and manual browsing, while leaving checkout to the user.

> **Status: planning / documentation only.** Implementation has not started. There is no runnable application, deployed demo, or measured agent performance yet. The capabilities below describe the intended prototype, not delivered features. Development must wait for explicit owner authorization.

## What this project investigates

Can an agent turn an incomplete, changing shopping request into a valid cart by choosing and using tools, responding to environmental feedback, and preserving the user's decisions?

IntentCart is a research portfolio project, not an attempt to compete with general-purpose shopping assistants or build a production marketplace. The initial environment will be an owned shopping website with a controlled product catalog and cart. Cross-commerce search and third-party checkout automation are outside the initial scope.

The goal is to demonstrate **task completion, not just conversational recommendations**: actual product lookup, actual cart mutations, independently checkable constraints, and recovery when requirements or availability change.

## Intended experience

1. Describe a goal and constraints in natural language. The agent asks only for missing information that materially affects suitability.
2. The agent searches, selects, checks, and prepares a cart without asking the user to approve every ordinary preparation step.
3. Browse products directly at any time. Chat and manual actions update the same shopping state; explicit choices and locked items remain respected.
4. Change the budget, replace an item, or encounter unavailable stock. The agent repairs affected parts rather than restarting the entire task.
5. Review the prepared cart and submit the order yourself. The prototype will use clearly labeled simulated checkout; the shopping agent will not have order-submission or payment authority.

A useful outcome can also be buying less, using an item the user already owns, or explaining why no valid solution exists.

## A running example

> "I want to record talking-head videos at a small desk. I already have a phone and stand. Find lighting and audio equipment within RM300."
>
> Later: "Keep the light. Reduce the total budget to RM250."

The research challenge is to identify necessary compatibility questions, avoid buying another stand, select a valid combination, preserve the locked light, and adapt the remaining selection. A stock change or failed cart operation should trigger evidence-based recovery, not a scripted success message.

This is an illustrative scenario. The initial product category and catalog size are still proposals, not finalized implementation decisions.

## What must be demonstrated

| Capability | Observable evidence |
| --- | --- |
| Intent understanding | Hard constraints, preferences, owned items, and unresolved information are distinguished. |
| Autonomous tool use | Searches and subsequent actions respond to returned data rather than a fixed dialogue script. |
| Constraint handling | Cart validity is checked against concrete variants, quantities, budget, availability, and known compatibility rules. |
| Shared state | Manual selections, locks, and chat-driven changes are reflected in one authoritative cart. |
| Recovery and restraint | Failures and changes are handled without duplicate additions, silent constraint relaxation, or false completion claims. |
| Human control | Only the user can perform final simulated order submission. |

Synthetic products and simulated transactions are acceptable. Fake tool execution, fabricated stock, and unsupported claims of success are not.

## Interface direction

Conversation-first, not conversation-only. Start with a simple conversation surface, contextual product cards, and an expandable cart. Let users browse, replace, remove, and lock products directly.

Show one primary recommendation by default; alternatives and comparisons appear when useful. Prefer a small set of stable, typed UI components over arbitrary generated frontend code. Earlier concept boards are exploratory illustrations, not a requirement for a permanent three-column dashboard, cross-platform shopping, or a finalized visual design.

## Development approach

IntentCart will use **AI-Native Development Practice**:

- Native-first tooling, with custom coordination added only for demonstrated gaps.
- A Main Agent owns scope, integration, verification decisions, and phase progression; bounded sub-agent work is optional.
- Phase-by-phase implementation, review, behavioral verification, and mutation-sensitive tests before progressing.
- Small, maintained project documentation and commit-linked evidence, rather than an elaborate custom development harness.

This is the coding and delivery method. It is distinct from the runtime shopping agent being studied. Agent Continuity is optional environment-side assistance, not a repository dependency or the project's development method.

**A roadmap is not permission to execute it.** The current assignment is documentation only.

## Project documents

| Document | Purpose |
| --- | --- |
| [Project state](PROJECT_STATE.md) | Current authorization, delivered state, proposed phases, and unresolved decisions. |
| [Product brief](docs/PRODUCT_BRIEF.md) | Scope, user experience, behavioral requirements, and system boundaries. |
| [Research plan](docs/RESEARCH_PLAN.md) | Planned scenarios, state-based evaluation, comparison design, and evidence limits. |
| [Development practice](docs/DEVELOPMENT.md) | Native-first delivery, phase gates, verification, mutation testing, and commit discipline. |
| [Agent entrypoint](AGENTS.md) | Minimal instructions for future coding agents. |

## Not decided or implemented yet

The technology stack, model/provider, product fixtures, persistence implementation, test tooling, visual system, and deployment target remain undecided. No setup commands or performance claims are provided because the application and experiments do not exist yet.
