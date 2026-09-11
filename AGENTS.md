# Agent entrypoint

IntentCart uses **AI-Native Development Practice** for repository development. This file is a small entrypoint, not a custom harness or an Agent Continuity bootstrap.

## Read before acting

1. [PROJECT_STATE.md](PROJECT_STATE.md): current authorization, phase, decisions, and evidence status.
2. [Product brief](docs/PRODUCT_BRIEF.md): scope and behavioral boundaries.
3. [Development practice](docs/DEVELOPMENT.md): phase gates and verification requirements.
4. [Research plan](docs/RESEARCH_PLAN.md): what the prototype must eventually demonstrate.

The latest explicit owner instruction governs the assignment. Reconcile conflicting or outdated project state before changing scope. A proposed roadmap never grants execution permission.

## Current boundary

At this documentation baseline, the owner has authorized **documentation only** and explicitly asked not to begin development. Until that instruction is explicitly superseded, do not scaffold the app, install project dependencies, implement features, create executable tests or evaluation runners, add CI workflows, provision infrastructure, or deploy. Do not treat "continue" without a clear assignment as permission to start the entire roadmap.

Planning documents describe intended behavior; do not report their existence as implemented capabilities. Stack, provider, data fixtures, and deployment decisions are not finalized.

## When implementation is authorized

- Work phase by phase within the authorized scope. Use native tools first; delegate bounded work only when helpful.
- Main Agent owns integration and the proceed / repair / blocked decision after verification. Sub-agent completion is not acceptance evidence.
- Keep chat and manual shopping operations on the same authoritative product state.
- Preserve explicit user choices and constraints. No shopping-agent order submission or payment authority.
- Verify actual tool effects and final state; distinguish intended, implemented, and verified behavior.
- Follow the behavioral and mutation gates in the development document. Missing or stale evidence is not a pass.
- Use coherent commits and the repository's authorized PR / squash-merge workflow; do not commit every small edit or equate implementation with merge or deployment.

Keep development-environment databases, task leases, session logs, credentials, and Agent Continuity runtime outside the checkout. Product data and product task state are a separate concern and may later be implemented in the application through normal reviewed changes.
