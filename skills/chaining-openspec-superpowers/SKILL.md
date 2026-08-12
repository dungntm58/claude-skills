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
0. Prerequisites (install missing dependencies)
1. Setup (first-run per project)
2. Create change
3. Fill proposal + specs (HARD GATE: openspec validate)
4. Technical design (superpowers:brainstorming, design only) (HARD GATE: user reviews design.md)
5. Implementation plan (superpowers:writing-plans) (HARD GATE: user reviews plan.md)
6. Execute (superpowers:subagent-driven-development — spec-compliance review only)
7. Simplify (/simplify — one quality/cleanup pass; all requirements implemented)
8. Archive
```

## Step 0 — Prerequisites

The plugin's `SessionStart` hook (`hooks/check-deps.sh`) already nags the user about missing `openspec` CLI / `superpowers` plugin at session start. So just verify here:

```bash
command -v openspec >/dev/null && [ -d .claude/skills/openspec-new-change ]
```

If `openspec` CLI present but project skills missing, run:

```bash
openspec init --tools claude
```

If anything else missing, point user to the SessionStart hook output. Do not proceed to Step 1 until all green.

## State Detection

Run after Step 0 passes. Always run this before taking any orchestration action:

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
| `.superpowers/plan.md` missing | Step 5 — confirm design was reviewed first |
| Plan tasks incomplete | Step 6 — confirm plan was reviewed first |
| All tasks complete, not simplified/archived | Step 7 (simplify) → Step 8 (archive) |
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

Write the design in normal prose. DO NOT apply caveman/compression —
the design is the human review artifact and must stay thorough,
comprehensive, and explanatory. Diagrams, trade-off discussion, and
rationale all belong here.
```

Create the `.superpowers/` directory if it doesn't exist.

**Break the brainstorming → writing-plans auto-chain.** `superpowers:brainstorming` will normally hand off to `superpowers:writing-plans` in the same session, which means plan generation inherits the parent (usually Opus). Plan generation is mostly mechanical (locked design → TDD steps + code blocks) and should run on Sonnet. Add this to the step 4 args:

```
STOP after writing design.md. Do NOT chain into writing-plans —
plan generation is dispatched separately on a cheaper model.
```

**HARD GATE — design review.** After design.md is written, STOP. Do NOT proceed to Step 5. Tell the user:

> "Design written to `openspec/changes/<name>/.superpowers/design.md`. Review it. Reply to approve, or give changes. Plan generation waits for your go-ahead."

The user needs time to read the design — it is the human review artifact. Only proceed to Step 5 after the user explicitly approves. If they request changes, revise design.md and re-surface the gate. Do not interpret silence, a new unrelated message, or "looks fine" mid-sentence as approval — wait for a clear go-ahead.

## Step 5 — Implementation plan (threshold fan-out; only after design approved)

**Precondition:** the Step 4 design-review gate passed — the user explicitly approved design.md. If resuming in a fresh session at this step (design.md exists, plan.md missing), confirm with the user that the design was reviewed before dispatching. Do not auto-run.

### 5.0 — Decide fan-out width

Plan-writing scales with scope. One sonnet writer for a large plan risks output-limit truncation (hence the incremental-write guard) and runs serial. Above a threshold, fan out by spec requirement — one sub-plan file per requirement, indexed by `plan.md`.

Count spec capabilities — the `## Requirement` blocks:

```bash
grep -rc '^## Requirement' openspec/changes/<name>/specs/ | awk -F: '{s+=$2} END {print s}'
```

Let `R` = that count.

| `R` | Path | Why |
|---|---|---|
| ≤ 6 | **5.A single writer** | One sonnet writer handles ≤6 coarse Tasks without truncation and is already coherent; below this, fan-out coordination outweighs the parallel gain. |
| > 6 | **5.B fan-out + index** | Single writer would run long / risk output-limit truncation. Parallelize by requirement; `plan.md` indexes the sub-plans. |

Also take 5.B regardless of `R` if the design names many files per requirement and a single-writer plan would obviously blow the output limit (size, not just count, is the real trigger).

Announce path + width before dispatching, e.g. _"7 requirements → fan-out: 1 plan-writer per requirement + index."_

### 5.A — Single writer (R ≤ 6)

Dispatch `superpowers:writing-plans` in a fresh `Task` with `model: sonnet` (design + specs as context, not your conversation history). **Use the 5.A dispatch template in `references/step5-dispatch.md`.**

The template enforces these rules — keep them whatever you do:
- **Granularity:** 1 Task = 1 spec `## Requirement` / vertical slice; MAY touch many files via the `Files:` block (Create/Modify/Test); ≤2 Tasks per requirement; ~15–30 min subagent runtime. Worked right/wrong example in the reference file.
- **Terse write-style**, **NO placeholders / "TBD"**, **full code blocks** for every file touched (signatures, DDL, payloads, test cases verbatim inside Step blocks).
- **Incremental write** (Sonnet output-limit guard): first Write = header only, then one Edit-append per Task. Never one big Write. Never echo plan content.
- Return path + Task count only.

**Hard override (5.A):** if the design contains genuinely novel architecture (no precedent in repo, new concurrency model, new protocol), upgrade plan writing to `model: opus`. Default Sonnet, escalate only on the same signals from the Step 6 Model Triage table.

When announcing the dispatch, state the chosen model: _"Dispatching plan writer on Sonnet (default — design is locked, plan generation is mechanical)."_

### 5.B — Fan-out + index (R > 6)

ONE parallel batch of writers → coordinator writes an index. One barrier, not three: no serial foundations pre-stage, no whole-plan rewrite at the end. Each writer's file IS the durable sub-plan for its Task; `plan.md` is a thin index pointing at them.

**One copy per Task (the rule the rest of 5.B follows from):** a Task's content lives in exactly one file — its sub-plan. `plan.md` holds pointers, never content. That keeps the Step-C sync scoped to the sub-plans that actually conflict, and lets a Step 6 implementer read its own Task's file instead of a whole-plan blob.

**Output-isolation rule (non-negotiable):** every writer writes its OWN file `openspec/changes/<name>/.superpowers/plan-task-NN.md`. NEVER point two subagents at the same file — concurrent writes clobber. The coordinator owns `plan.md` (the index) and is the only writer of it.

**Step A — Coordinator prep (you, inline, before dispatching — cheap, no subagent).** You already hold design.md and the specs. Do the ordering/numbering yourself so the writers emit final-form blocks and the index is trivial to build:

1. **Order requirements by dependency** per design.md.
2. **Assign each a global Task number** in that order. Foundations (if any) is Task 1.
3. **Extract the shared-file paths** from design.md (the shared schema / services / types are already named there). This is the shared-files list — you do NOT need a foundations subagent to produce it.

**Step B — Single parallel batch (foundations writer + all requirement writers in ONE message).** Foundations is a peer in the batch, NOT a prerequisite — requirement writers reference shared-file PATHS (from Step A), not Task 1's output, so nothing waits on it.

- **Foundations writer (only if shared scaffolding exists):** writes the shared SHELL only — schema/migrations, shared service-class skeleton (constructor + shared private helpers), shared types → `plan-task-01.md` as `### Task 1`. Does NOT write per-requirement methods; each requirement writer ADDS its methods to the shared class via a `Files: Modify` entry. No shared scaffolding → skip it, pass "none" as the shared-files list.
- **Requirement writers:** one subagent per `## Requirement`, each emitting its FINAL-FORM `### Task N` block (global number from Step A) → `plan-task-NN.md` (`NN` = that global number, zero-padded).
- **Model — sonnet ceiling.** Design.md is LOCKED; writing the plan is translation, not architecture, so writers do NOT need opus. Default `sonnet`; drop to `haiku` only for trivially mechanical requirements. Never opus or fable here — a heavy-reasoning writer just stalls the whole parallel batch behind the slowest agent. (Genuine novel-concurrency judgment lives in Step C reconciliation, not in writing.) Announce model per requirement.
- **Context:** full specs + full design.md + the shared-files list from Step A (so the writer references those files, never redefines them) + the writer's assigned global Task number.
- Reuse 5.A's content rules: granularity (1 Task per requirement, may touch many files via the `Files:` block), terse write-style, NO placeholders, full code blocks, return path only. The write *mechanic* differs (one sub-plan file, final-form numbered heading) — do NOT carry over 5.A's plan.md header / incremental-append sequence.

**Use the 5.B Step-B writer template in `references/step5-dispatch.md`** (also the basis for the foundations writer).

**Step C — Index + sync (you, inline; subagent ONLY on real conflict).** Sub-plans are already final-form and globally numbered, so there is nothing to assemble: they stay exactly as written and are never merged into one file, copied into `plan.md`, or deleted. Your only outputs here are the index and, if two sub-plans collide, the sync.

**C1 — Read each sub-plan's `Files:` block.** One pass; you need it for both the index and the overlap check.

**C2 — Write the index to `openspec/changes/<name>/.superpowers/plan.md`** (you write it; no subagent). Index only — never copy Task content into it:

```markdown
# Plan — <change-name>

<N> tasks, one sub-plan each. Execute in Task order. Each sub-plan is
self-contained: Files: block + test-first Steps with full code.
Shared files (owned by Task 1): <paths from Step A, or "none">

| Task | Sub-plan | Requirement | Files touched | Depends on |
|---|---|---|---|---|
| 1 | `plan-task-01.md` | Shared scaffolding | `src/db/schema.ts` | — |
| 2 | `plan-task-02.md` | <requirement title> | `src/foo.ts`, `test/foo.test.ts` | 1 |
```

**C3 — Sync overlapping sub-plans.** The ONE coherence check: do two sub-plans `Modify` the same file at overlapping ranges?

- **No** → done. Index + sub-plans are the plan.
- **Yes** → dispatch ONE sync subagent (**5.B Step-C template in `references/step5-dispatch.md`**) scoped to ONLY the conflicting Modify blocks — merge or sequence them + note the dependency in the dependent Task. Re-read design.md for concurrency / shared-state flags first → `sonnet` default, `opus` if flagged (this is the one place reconciliation judgment justifies opus). It edits those blocks **in the conflicting `plan-task-NN.md` files in place** — never the index, never a non-conflicting sub-plan, never a re-emitted whole plan. When it returns, update the index's **Depends on** column with any sequencing it introduced.

**HARD GATE — plan review.** After the plan is written, STOP. Do NOT proceed to Step 6. Tell the user:

> 5.A: "Plan written to `openspec/changes/<name>/.superpowers/plan.md` — <N> tasks. Review it. Reply to approve, or give changes. Execution waits for your go-ahead."
>
> 5.B: "Plan index at `openspec/changes/<name>/.superpowers/plan.md` — <N> tasks, one sub-plan each (`plan-task-NN.md`). Review it. Reply to approve, or give changes. Execution waits for your go-ahead."

The user needs time to read the plan before subagents start writing code. Only proceed to Step 6 after the user explicitly approves. If they request changes, revise the affected file — plan.md (5.A) or the specific `plan-task-NN.md` plus the index row (5.B) — or re-dispatch that writer, then re-surface the gate. Do not interpret silence or an unrelated message as approval — wait for a clear go-ahead.

## Step 6 — Execute (only after plan approved)

**Precondition:** the Step 5 plan-review gate passed — the user explicitly approved plan.md. If resuming in a fresh session at this step (plan.md exists, tasks incomplete), confirm with the user that the plan was reviewed before dispatching. Do not auto-run.

Invoke **superpowers:subagent-driven-development** with the plan path AND the model-triage preset below:

```
Plan file: openspec/changes/<name>/.superpowers/plan.md

[5.B only — add verbatim when the plan is an index:]
plan.md is an INDEX, not the plan body. Each row maps Task N to a
sub-plan file `plan-task-NN.md` in the same directory — that file holds
Task N's full Files: block and Steps. Per task: read ONLY that task's
sub-plan (plus the index row for its Depends on), and tick its
checkboxes in that same sub-plan file. plan.md stays an index — do not
write Task content into it.

Run spec-compliance review after each task, but SKIP the code-quality
review stage AND the final whole-implementation reviewer — code quality
is handled ONCE by /simplify after all tasks (Step 7), never per task.

Apply the Model Triage rules from chaining-openspec-superpowers when
dispatching each subagent. Pass the chosen model explicitly via the
Task tool's `model:` parameter — do NOT inherit from the parent.
Never default to Opus for implementer or spec-reviewer roles.
```

The subagent-driven-development skill will then dispatch a fresh implementer per task followed by a **spec-compliance review only** — its per-task code-quality review and its final whole-implementation review are skipped (code quality is the single Step 7 `/simplify` pass). Each `Task` call MUST include an explicit `model:` per the triage rules below.

### Model Triage

Ladder: **Haiku → Sonnet → Opus → Fable.** Default to **Sonnet** for implementers. Use the signal table to move up to Opus or down to Haiku; Fable sits above Opus behind the narrow gate below. Score each signal, then apply the dominance rule.

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

**Fable — top tier, narrow gate.** Fable (`model: fable`) is the most capable model and the most expensive per task: roughly 2× Opus's per-token price, thinking always on, single turns that can run many minutes. Escalate Opus → Fable only when BOTH hold:

1. **Three or more signals lean Opus** — not one Opus trigger in an otherwise Sonnet-shaped task.
2. The task is **long-horizon or genuinely novel** — new architecture with no repo precedent, a new concurrency or protocol model, or a cross-cutting change whose blast radius the plan cannot enumerate.

Never Fable for: spec-compliance review, plan writing (5.A / 5.B / Step-C reconcile), or anything a Sonnet implementer already passes review on. In a parallel batch one Fable task stalls the batch behind it — prefer Opus when tasks run concurrently.

**Fable quota fallback.** Fable draws on a smaller, separate usage quota than Opus. If a `model: fable` dispatch fails on quota or availability (usage-limit error, model unavailable, rate limit naming the model), do NOT retry Fable and do NOT downgrade the task's scope — re-dispatch the SAME task on `model: opus` and announce it: _"Fable quota exhausted — Task 4 re-dispatched on Opus (next tier down)."_ Opus then becomes the standing top tier for the rest of the run; stop attempting Fable until the user says the quota reset.

**Hard overrides (these win regardless of signals):**
- **Spec compliance reviewer → always `model: sonnet`** (verification, not generation)
- **Implementer returns `BLOCKED` for reasoning reasons → upgrade one tier (haiku→sonnet→opus→fable) and re-dispatch.** A `BLOCKED` for missing context is NOT a tier upgrade — provide context and re-dispatch with the same model. **Fable is terminal:** a Fable implementer that returns `BLOCKED` for reasoning means the plan Task is underspecified — stop and take it back to the user, do not loop.

**When announcing a dispatch, state the chosen model and the dominant signal that drove it**, e.g. _"Dispatching implementer for Task 3 on Sonnet (default — multi-file integration, no Opus signals)."_ This makes triage decisions auditable.

## Step 7 — Simplify (one quality pass; only after all requirements implemented)

**Precondition:** every plan task is complete — all openspec requirements implemented, each having passed its per-task spec-compliance review. Do NOT run this mid-implementation.

Invoke the **/simplify** skill ONCE over the whole change:

```
/simplify
```

This is the single code-quality / cleanup gate — reuse, simplification, efficiency, altitude — replacing the old per-task code-quality review and the final whole-implementation review. It reviews the accumulated branch diff and applies the fixes.

`/simplify` is quality-only; it does NOT hunt bugs (spec compliance was already verified per task — run `/code-review` separately if you want a correctness sweep). Safe to re-run: a second pass just finds fewer cleanups, so on resume run it regardless. Once it settles, proceed to Step 8.

## Step 8 — Archive

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

## Output Discipline

- **Design.md** = thorough prose. User reviews this.
- **Plan.md** = terse, actionable lines only (the writers' terse write-style is the only pass — no post-hoc compression step).
- **End-of-orchestration summary** = SKIP. User reads ticked tasks in plan.md (5.A) or the sub-plans it indexes (5.B). Output at most one line: `Archived <name>. <N> tasks done. Plan: <path>.`
- Per-step status updates during run = one terse line each (e.g. `Step 4 done. Design at <path>.`).

## Delegation Reference

| Step | Delegate skill | Must be present |
|---|---|---|
| 2 | `openspec-new-change` | openspec plugin |
| 3 | `openspec-continue-change` | openspec plugin |
| 4 | `superpowers:brainstorming` | superpowers plugin |
| 5 | `superpowers:writing-plans` | superpowers plugin |
| 6 | `superpowers:subagent-driven-development` | superpowers plugin |
| 7 | `/simplify` | built-in (Claude Code) |

If any delegate skill is missing, jump back to Step 0 and surface the install commands. Do not try to recreate the step inline.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Invoking `superpowers:brainstorming` without the "specs already locked" preset — it re-asks requirements questions | Always include the preset in step 4; point brainstorming at `openspec/changes/<name>/specs/` |
| Skipping the `openspec validate` gate because "specs look fine" | Never skip. The whole value of openspec is that archive validates — if validate fails now, it fails at archive too |
| Archiving a `spec-driven` change without writing the stub pointers | Check schema first. If not `openspec-superpowers`, write the stubs |
| Reimplementing a step inline instead of delegating | If a delegate is missing, stop and tell the user. Never reinvent |
| Skipping state detection and restarting from step 1 | Always run `openspec status --json` first; resume at the right step |
| Dispatching implementer/spec-reviewer subagents without an explicit `model:` parameter — they silently inherit Opus from the parent | Apply the Model Triage table for every dispatch; Sonnet is the default, Haiku for trivial mechanical tasks, Opus reserved for complex/cross-cutting implementation and the Step-C reconcile |
| Reaching for Fable because a task "looks hard" — one Opus signal is not the Fable gate, and Fable burns ~2× Opus per token | Fable needs 3+ Opus signals AND long-horizon/novel work. Otherwise Opus. Never Fable for reviews or plan writing |
| Retrying Fable after a quota/availability failure, or silently dropping the task | Re-dispatch the same task on `model: opus` and announce the downgrade; Opus is the standing top tier for the rest of the run |
| Calling `openspec archive` without running `/simplify` first | Step 7 runs `/simplify` once (the sole quality/cleanup gate) before Step 8 archive |
| Letting `superpowers:brainstorming` auto-chain into `superpowers:writing-plans` — plan generation runs on Opus by inheritance even though it's mechanical | Tell brainstorming to STOP after design.md (Step 4), then dispatch writing-plans as its own Task on `model: sonnet` (Step 5) |
| Dispatching Step 5 right after design.md is written — user never got to review the design | Step 4 ends at a HARD GATE. Stop, ask the user to review design.md, wait for explicit approval before Step 5 |
| Dispatching Step 6 right after plan.md is written — user never got to review the plan | Step 5 ends at a HARD GATE. Stop, ask the user to review plan.md, wait for explicit approval before Step 6 |
| Letting writing-plans scope each Task to a single function / single test case — many tiny Tasks, each spinning a fresh subagent, execution drags | Step 5 dispatch prompt MUST include the TASK GRANULARITY OVERRIDE. One Task = one business requirement / vertical slice, may touch multiple files, ~15-30 min subagent runtime, ≤2 Tasks per spec `## Requirement` |
| Step 5 subagent writes the whole plan in one Write — Sonnet hits its output token limit, plan.md truncates mid-Task | Step 5 dispatch prompt MUST include the INCREMENTAL WRITE rule. First Write = header only, then one Edit-append per Task group. Never batch all Tasks into one call |
| Step 5 subagent echoes plan content back into its response — doubles output, recompounds the limit hit | Return ONLY path + Task count. Plan lives in the file, never in the message |
| Large scope (R>6) written by one sonnet subagent — truncates / drags serially | Run Step 5.0 first: count `## Requirement`. R>6 → fan out (5.B). R≤6 → single writer (5.A) |
| Fan-out (5.B) points >1 subagent at the same file — concurrent writes clobber | Each writer owns its own `plan-task-NN.md`. Only the coordinator writes `plan.md` (the index); the Step-C sync subagent touches only the conflicting sub-plans |
| Assembling the 5.B sub-plans — merging them into one file, copying their content into `plan.md`, or deleting them once indexed | One copy per Task. Sub-plans hold the content and stay put; `plan.md` holds index rows only: Task # → sub-plan path → requirement → files touched → depends on |
| Re-introducing a serial foundations pre-stage or a whole-plan stitch rewrite — fan-out cost ≈ a full single-writer pass on top of the writers, never beats 5.A | Foundations writer rides in the SAME parallel batch (peer, not prerequisite); coordinator assigns global Task numbers + extracts shared-file paths from design.md inline; assembly is an index over final-form sub-plans, not a rewrite |
| Fan-out writer dispatched on opus or fable — slow reasoning stalls the whole parallel batch behind it | Sonnet ceiling for writers (design is locked → writing is translation). haiku for trivial, never opus or fable. Opus only for the Step-C reconcile when concurrency flagged |
| Coordinator skips the overlapping-Modify check before declaring done — unsynced shared-file edits ship | While reading the `Files:` blocks for the index, check for two sub-plans Modifying the same file at overlapping ranges → dispatch the Step-C sync subagent scoped to those blocks only |
| Fanned out below threshold (R≤6) — coordination overhead, no gain | Use 5.A single writer. Fan-out only pays above R>6 (or when plan size alone would truncate) |

## Red Flags — Stop and Recheck

- About to call `openspec archive` without running `openspec validate` first.
- About to call step 4 without reading `openspec/changes/<name>/specs/` yourself.
- About to ask brainstorming requirements-gathering questions when specs already exist.
- About to write `.superpowers/design.md` outside the change directory.
- About to dispatch a subagent without an explicit `model:` parameter (silently inherits Opus).
- About to dispatch the implementer on Opus when no Opus signal from the triage table fired.
- About to dispatch on Fable without 3+ Opus signals AND long-horizon/novel work — or on Fable inside a parallel batch it would stall.
- About to retry Fable after a quota failure instead of re-dispatching the same task on Opus.
- About to let subagent-driven-development run its per-task code-quality review or its final whole-implementation reviewer — both removed; code quality is the single Step 7 `/simplify` pass.
- About to call `openspec archive` without running `/simplify` first (Step 7).
- About to let brainstorming auto-chain into writing-plans (plan generation will inherit Opus). Step 4 must end at design.md; Step 5 dispatches plan writing on Sonnet.
- About to dispatch Step 5 without an explicit user approval of design.md. Step 4 ends at a HARD GATE — the user must review the design first.
- About to dispatch Step 6 without an explicit user approval of plan.md. Step 5 ends at a HARD GATE — the user must review the plan first.
- About to dispatch Step 5 without the TASK GRANULARITY OVERRIDE in the prompt — writing-plans will produce one Task per 2-5 min atomic action and execution will crawl.
- About to dispatch Step 5 without the INCREMENTAL WRITE rule in the prompt — the subagent writes the whole plan in one Write, hits Sonnet's output limit, and plan.md truncates.
- About to dispatch Step 5 without first counting `## Requirement` (Step 5.0) — can't pick single-writer vs fan-out path.
- About to fan out (5.B) pointing more than one subagent at the same file — concurrent writes clobber. Each writer owns a `plan-task-NN.md`; only the coordinator writes the `plan.md` index.
- About to assemble the 5.B sub-plans — merge them into one file, copy their content into the index, or delete them once indexed. All three break one-copy-per-Task.
- About to dispatch a serial foundations pre-stage, or a whole-plan stitch rewrite — both reintroduce the barrier/duplicate-write tax that makes fan-out lose to 5.A. Foundations is a peer in the one parallel batch; assembly is an index over final-form sub-plans.
- About to dispatch a 5.B writer on opus or fable — sonnet ceiling; opus only for the Step-C reconcile.
- About to write the index and declare done without checking for overlapping shared-file Modifies — run the Step-C sync if any exist.
- About to fan out below the R>6 threshold, or single-write a plan large enough to truncate — wrong path for the scope.

All of these mean: stop, re-read this skill, and resume at the correct step.
