# AI-Native Development Practice

## Authority

The owner authorized execution through the research MVP on 2026-09-11, superseding the documentation-only pause. Scope remains the product brief. Implementation is not automatic permission to merge, deploy, spend, access sensitive accounts or build the rest of a roadmap.

Use native planning, tools, delegation, tracing, verification and repository capabilities first. Add custom coordination only for a demonstrated gap. Keep project scope, status, decisions and evidence in a small set of normal documents, not a custom phase engine.

Main Agent owns integration and proceed / repair / blocked decisions. Bounded sub-agents are optional; a completion message is not verification. Ordinary reversible choices within the assignment do not require repeated approval. Scope expansion, irreversible effects and externally consequential actions require actual authority.

## Phase loop and unchanged gates

1. Define outcome, exclusions, affected contracts, risks and acceptance evidence before editing.
2. Implement a coherent slice using native tools.
3. Verify actual state changes, including negative and boundary cases.
4. Perform independent verification. Label implementer self-review separately; it is not independent review or separate-model signoff.
5. Evaluate proceed / repair / blocked. Only treat required gates as passed when their evidence exists. Unavailable required review stays open, not waived by relabeling.
6. Publish coherent changes and update project state with actual delivery and limitations. Local changes, commits, PRs, merges and deployments are separate milestones.

Where an unavailable external verification leaves a gate open, report an implementation candidate, not a fully verified release. Independent executable work may be retained without misrepresenting blocked acceptance as a passed phase. The current report records all such open gates.

## Verification and mutation gate

Write behavioral tests from the contracts: happy paths, negative cases, boundaries and invariants. Every explicit behavior rule needs a test demonstrated to kill a relevant mutation; coverage alone is insufficient. Critical examples include budget removal, wrong variants, reversed lock checks, skipped writes, stale updates, blind retries and unauthorized order submission.

Actually execute applicable mutation tooling. Surviving meaningful mutants require repair; equivalent/non-applicable cases need justification and review. Not-run work stays visible. The targeted runner is not a proof that every possible mutation or model behavior has been covered. Current live-model and independent-review gaps remain open.

Check UI events, API/tool results, saved state and visible outcomes together. Unit tests and mock provider responses do not prove live model behavior or a real browser/HTTP flow. A blocked browser is not permission to bypass managed browser policy.

## Evidence

Identify source revisions/hashes, environment, fixture/scenario version, provider settings, actual commands, tool effects, state before/after and limitations. Preserve failed agent/control runs. Separate deterministic commerce checks, mock protocol tests, offline DOM rendering, browser E2E and live-model evaluations.

Do not persist credentials, sensitive transcripts or private chain-of-thought. Public project evidence uses synthetic inputs. Self-review, independent review and unperformed review remain distinct.

## Commits and repository boundary

Commit coherent outcomes or phases, not each small edit. Deliver through a scoped PR with evidence; squash merge only after explicit authorization and required gates. Never force-rewrite shared history or infer deployment permission.

The repository must build and test without Agent Continuity. Its optional environment-side SQLite, scope mappings, events, private checkpoints and helper runtime remain outside the entire checkout. Do not add a mandatory continuity manifest, package hook, CI job or bootstrap dependency. Product SQLite state is a separate application concern.

Maintain README, product brief, architecture, research plan and project state for facts contributors need. Do not copy a private coding-session ledger into product documentation.
