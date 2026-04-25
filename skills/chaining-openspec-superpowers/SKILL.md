---
name: chaining-openspec-superpowers
description: Use when starting or resuming a feature that needs both openspec business specs and superpowers technical design with subagent execution - orchestrates openspec (proposal + specs) and superpowers (design + plan + subagent dispatch) end-to-end.
---

# Chaining OpenSpec with Superpowers

## Overview

Drive a feature from business spec to implemented code by delegating to existing skills: **openspec owns proposal + specs**, **superpowers owns design + plan + subagent execution**. This skill only orchestrates — it never reimplements the steps.

**Core principle:** Business intent belongs in openspec (capability deltas, scenarios, validation). Technical design and execution belong in superpowers (thorough designs, bite-sized plans, fresh-subagent-per-task dispatch).

## When to Use

- User wants to build a feature that deserves both a formal spec and a thorough technical design.
- A change already exists in `openspec/changes/` and the user wants to continue/finish it.
- User asks to "spec then ship" or explicitly invokes this skill by name.

**When NOT to use:**
- Single-file fixes or trivial tweaks. Skip the ceremony — just edit.
- Exploratory spikes where no one will read the spec later.
- Documentation-only changes.

## Announce on entry

> "Using chaining-openspec-superpowers. Resuming at step N: <step name>."

Always run state detection first and tell the user where you're starting.

## Orchestration

```
1. Setup (first-run per project)
2. Create change
3. Fill proposal + specs (HARD GATE: openspec validate)
4. Technical design (superpowers:brainstorming, design only)
5. Implementation plan (superpowers:writing-plans)
6. Execute (superpowers:subagent-driven-development)
7. Archive
```

## State Detection

Always run this before taking any action:

1. If no `<change-name>` argument: ask the user which change (or that they want to start a new one).
2. If change directory does not exist → go to step 1 (setup) then step 2 (create).
3. Otherwise run `openspec status --change <name> --json` and parse.

Resume at the first incomplete step:

| Condition | Resume at |
|---|---|
| Change directory missing | Step 1 → Step 2 |
| proposal.md missing/incomplete | Step 3 |
| specs/ missing/incomplete | Step 3 |
| `openspec validate <name>` fails | **HARD GATE — stop, surface errors, do not proceed** |
| `.superpowers/design.md` missing | Step 4 |
| `.superpowers/plan.md` missing | Step 5 |
| Plan tasks incomplete | Step 6 |
| All tasks complete, not archived | Step 7 |
| Archived | Nothing to do |

## Step 1 — Setup (only before creating a new change)

Skip this step entirely if the change already exists on disk — the schema is only needed at `openspec new change` time.

Check for the project-local schema:

```bash
openspec schema which openspec-superpowers
```

Exit code 0 means it exists; exit code 1 means create it:

```bash
openspec schema init openspec-superpowers --artifacts proposal,specs
```

This schema omits `design` and `tasks` — those responsibilities move to superpowers.

## Step 2 — Create change

Invoke the **openspec-new-change** skill. Pass the change name and schema:

```bash
openspec new change <name> --schema openspec-superpowers
```

## Step 3 — Fill proposal + specs

Invoke the **openspec-continue-change** skill to walk each artifact. Loop until all artifacts show complete in `openspec status`.

After each artifact, run:

```bash
openspec validate <name>
```

**HARD GATE:** If validate fails, stop the whole chain. Surface the errors and ask the user to fix. Do NOT proceed to step 4 with failing specs — the whole point of using openspec is that specs are locked before technical design.

## Step 4 — Technical design

Invoke **superpowers:brainstorming** with this preset context (pass as skill args):

```
Requirements are already captured in openspec/changes/<name>/specs/.
Read those files first. Skip all requirements-gathering questions —
the WHAT is locked. Focus exclusively on the HOW: technical design,
architecture, components, data flow, testing strategy.

Save the design to: openspec/changes/<name>/.superpowers/design.md
```

Create the `.superpowers/` directory if it doesn't exist.

**About the step 4 → step 5 chain:** `superpowers:brainstorming`'s terminal state is invoking `superpowers:writing-plans` automatically. Include the plan location preset in the step 4 args so it carries through:

```
...design/plan instructions as above...

When you transition to writing-plans, save the plan to:
openspec/changes/<name>/.superpowers/plan.md
```

Then do NOT invoke `superpowers:writing-plans` a second time — brainstorming already did it. Just verify the plan file exists at the expected path before moving to step 6.

## Step 5 — Implementation plan (only if step 4 did not chain)

Run this step only if `.superpowers/plan.md` is still missing after step 4 completes (e.g., brainstorming was interrupted before handing off). Otherwise skip.

Invoke **superpowers:writing-plans** with:

```
Save plan to: openspec/changes/<name>/.superpowers/plan.md
```

## Step 6 — Execute

Invoke **superpowers:subagent-driven-development** with the plan path AND the model-triage preset below:

```
Plan file: openspec/changes/<name>/.superpowers/plan.md

Apply the Model Triage rules from chaining-openspec-superpowers when
dispatching each subagent. Pass the chosen model explicitly via the
Task tool's `model:` parameter — do NOT inherit from the parent.
Never default to Opus for implementer or spec-reviewer roles.
```

The subagent-driven-development skill will then dispatch fresh subagents per task with its own two-stage review, but each `Task` call MUST include an explicit `model:` per the triage rules below.

### Model Triage

Default to **Sonnet** for implementers. Use the signal table to move up to Opus or down to Haiku. Score each signal, then apply the dominance rule.

| Signal | Lean Haiku | Lean Sonnet | Lean Opus |
|---|---|---|---|
| **Spec clarity** | Acceptance criteria concrete and testable | Some interpretation needed | Ambiguous, design judgment required |
| **File scope** | 1 file, isolated | 2–4 files, known boundaries | Cross-cutting, unknown blast radius |
| **Pattern reuse** | Mirrors existing pattern in codebase | Adapts a pattern with small variations | New pattern, no precedent |
| **External knowledge** | Stdlib / well-known idioms only | Familiar framework APIs | Unfamiliar library, protocol, or domain |
| **Failure cost** | Local — wrong code obvious in tests | Moderate — could leak through review | High — security, data loss, concurrency |
| **State/concurrency** | Pure functions, no I/O | Sync I/O, simple state | Async, locks, ordering, distributed |
| **Test type** | Unit tests obvious from spec | Some integration setup | Tests themselves require design |

**Dominance rule (not averaging):**
- All signals lean Haiku → **Haiku** (`model: haiku`)
- Any signal leans Opus → **Opus** (`model: opus`)
- Otherwise → **Sonnet** (`model: sonnet`)

**Hard overrides (these win regardless of signals):**
- **Spec compliance reviewer → always `model: sonnet`** (verification, not generation)
- **Code quality reviewer → always `model: opus`** (deep judgment pays off here)
- **Final whole-implementation reviewer → always `model: opus`**
- **Implementer returns `BLOCKED` for reasoning reasons → upgrade one tier (haiku→sonnet, sonnet→opus) and re-dispatch.** A `BLOCKED` for missing context is NOT a tier upgrade — provide context and re-dispatch with the same model.

**When announcing a dispatch, state the chosen model and the dominant signal that drove it**, e.g. _"Dispatching implementer for Task 3 on Sonnet (default — multi-file integration, no Opus signals)."_ This makes triage decisions auditable.

## Step 7 — Archive

**First: re-run validate.** Specs or artifacts may have drifted during implementation:

```bash
openspec validate <name>
```

If validate fails, stop and fix before archiving.

**Then: handle schema compatibility.** The schema name is already in the `openspec status --change <name> --json` output you ran during state detection — read `schemaName` from that (no `jq` needed, just parse the JSON).

- If `schemaName` is `openspec-superpowers`: archive directly.
- If `schemaName` is `spec-driven` (or any schema that requires `design`/`tasks`): write one-line pointer stubs first so `openspec validate` passes:

  `openspec/changes/<name>/design.md`:
  ```markdown
  # Design

  See .superpowers/design.md
  ```

  `openspec/changes/<name>/tasks.md`:
  ```markdown
  # Tasks

  See .superpowers/plan.md
  ```

Only write the stubs if the files do not already exist. Then:

```bash
openspec archive <name>
```

## Delegation Reference

| Step | Delegate skill | Must be present |
|---|---|---|
| 2 | `openspec-new-change` | openspec plugin |
| 3 | `openspec-continue-change` | openspec plugin |
| 4 | `superpowers:brainstorming` | superpowers plugin |
| 5 | `superpowers:writing-plans` | superpowers plugin |
| 6 | `superpowers:subagent-driven-development` | superpowers plugin |

If any delegate skill is missing, stop and tell the user which plugin to install. Do not try to recreate the step inline.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Invoking `superpowers:brainstorming` without the "specs already locked" preset — it re-asks requirements questions | Always include the preset in step 4; point brainstorming at `openspec/changes/<name>/specs/` |
| Skipping the `openspec validate` gate because "specs look fine" | Never skip. The whole value of openspec is that archive validates — if validate fails now, it fails at archive too |
| Archiving a `spec-driven` change without writing the stub pointers | Check schema first. If not `openspec-superpowers`, write the stubs |
| Reimplementing a step inline instead of delegating | If a delegate is missing, stop and tell the user. Never reinvent |
| Skipping state detection and restarting from step 1 | Always run `openspec status --json` first; resume at the right step |
| Dispatching implementer/spec-reviewer subagents without an explicit `model:` parameter — they silently inherit Opus from the parent | Apply the Model Triage table for every dispatch; Sonnet is the default, Haiku for trivial mechanical tasks, Opus reserved for code-quality review and complex/cross-cutting work |

## Red Flags — Stop and Recheck

- About to call `openspec archive` without running `openspec validate` first.
- About to call step 4 without reading `openspec/changes/<name>/specs/` yourself.
- About to ask brainstorming requirements-gathering questions when specs already exist.
- About to write `.superpowers/design.md` outside the change directory.
- About to dispatch a subagent without an explicit `model:` parameter (silently inherits Opus).
- About to dispatch the implementer on Opus when no Opus signal from the triage table fired.

All of these mean: stop, re-read this skill, and resume at the correct step.
