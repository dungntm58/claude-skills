# Step 5 — Dispatch templates

Verbatim `Task()` templates for chaining-openspec-superpowers **Step 5**
(implementation plan). The rules these templates enforce live inline in
SKILL.md Step 5 — this file is the copy-paste reference. Load on demand at
dispatch time.

- 5.A single-writer dispatch → use the **5.A template**.
- 5.B per-requirement fan-out → use the **Step-B writer template** (also the
  basis for the foundations writer in the same parallel batch).
- 5.B sub-plan sync → use the **Step-C sync template** (only when two sub-plans
  Modify the same file at overlapping ranges; otherwise the coordinator just
  writes the `plan.md` index over them).

Both writer templates contain a `<<TASK SHAPE>>` slot. Paste the **TASK SHAPE**
block below into it verbatim — it is the one definition of what a plan Task
contains, so 5.A and 5.B plans come out the same shape.

---

## TASK SHAPE — shared by every writer

```
TASK SHAPE — signatures + pseudo code, not code. This replaces
writing-plans' Task Structure (its code-block Steps), the code
requirement in its No Placeholders list, and its Review Focus section.
The implementer writes the real code and tests from this block, so
write each step concrete enough that two implementers would build the
same behavior: exact names, values, error strings, branch outcomes.

A Task block is these parts, in order:
1. `### Task <N>: <requirement title>`
2. **Files:** one line each — `Create|Modify|Test: <exact path>`
   (Modify with line range when known), then ` — <role, few words>`.
3. **Interfaces:** `Consumes:` / `Produces:` — exact signatures (with
   types) that other Tasks call or provide. `none` if none.
4. **Data:** only when the Task adds or changes a schema, type, or
   payload — field list, `name: type, constraint`.
5. One entry per function / method / route / handler:
   **`<exact signature>`** — <what it does, one line>
   then numbered pseudo-code steps, one line each, when it has
   branches, ordering, or edge cases: plain words + exact identifiers,
   constants, error strings, status codes; outcomes inline
   (`null → NotFoundError("…")`).
   Trivial entries (getter, wiring, re-export): signature + purpose
   line only.
6. **Tests:** `<test file>` — one line per case, `<scenario> → <expected>`:
   each spec scenario and each design.md rule this Task implements,
   plus at most 3 failure modes neither states (bad input, empty,
   duplicate, expiry, …), most likely to bite first. Variants of one
   case share its line. writing-plans' Review Focus lands here.
7. `- [ ] Red → green → commit: <type>: <subject>`

Example — right shape, right altitude:

### Task 3: User can reset password via email link

**Files:**
- Create: `src/services/PasswordResetService.ts` — token issue + verify
- Create: `src/routes/auth/password-reset.ts` — two endpoints
- Create: `db/migrations/0042_password_reset_tokens.sql` — token table
- Modify: `src/routes/index.ts:28` — mount router
- Test: `tests/routes/auth/password-reset.test.ts`

**Interfaces:**
- Consumes: `UserRepo.findByEmail(email: string): Promise<User | null>` (Task 1)
- Produces: `PasswordResetService.requestReset(email: string): Promise<void>`,
  `PasswordResetService.confirmReset(token: string, password: string): Promise<void>`

**Data:** `password_reset_tokens` — `id: uuid pk`, `user_id: uuid fk users`,
`token_hash: text unique`, `expires_at: timestamptz`, `used_at: timestamptz null`

**`requestReset(email: string): Promise<void>`** — issue one-time token, email the link.
1. user = UserRepo.findByEmail(email); null → return (no email; caller can't tell)
2. token = 32 random bytes as hex; insert sha256(token), expires_at = now + 30 min
3. send email template `password-reset` with link `/reset?token=<token>`

**`confirmReset(token: string, password: string): Promise<void>`** — verify token, set password, burn token.
1. row = find by sha256(token); none → InvalidTokenError("invalid token")
2. expires_at < now or used_at set → ExpiredTokenError("token expired")
3. one transaction: set user password hash; set row used_at = now

**`POST /auth/forgot-password`** `{ email }` — requestReset → always 202
**`POST /auth/reset-password`** `{ token, password }` — confirmReset → 204;
InvalidTokenError → 400; ExpiredTokenError → 410

**Tests:** `tests/routes/auth/password-reset.test.ts`
- valid token + new password → 204; login with new password succeeds
- expired token → 410 `token expired`
- token used twice → second call 410 `token expired`
- unknown token → 400 `invalid token`
- unregistered email → 202, no email sent

- [ ] Red → green → commit: `feat: password reset via email link`
```

---

## 5.A — Single-writer dispatch template (R ≤ 6)

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Write implementation plan",
  prompt: """
    Invoke superpowers:writing-plans to produce the implementation plan.
    Where this prompt and writing-plans differ, this prompt wins.

    Inputs (read these first, do not ask the user):
    - openspec/changes/<name>/specs/        (locked requirements)
    - openspec/changes/<name>/.superpowers/design.md  (locked technical design)

    The WHAT and the HOW are both already decided. Your job is purely
    to translate the design into Tasks of the TASK SHAPE below.

    Save plan to: openspec/changes/<name>/.superpowers/plan.md

    PLAN HEADER — replaces writing-plans' header. Exactly:
      # Plan — <change-name>
      **Goal:** <one sentence>
      **Spec:** openspec/changes/<name>/specs/ + .superpowers/design.md
      ## Global Constraints
      - <rule binding more than one Task, exact value copied from
        spec/design> (one line each; "- none" if none)

    TASK GRANULARITY OVERRIDE — coarser than writing-plans default:
    - One Task = one cohesive business requirement / capability /
      vertical slice — what a reviewer would PR-review as a unit.
    - A Task MAY touch many files; list every one in its Files: block.
      Do not split a requirement across Tasks because it touches >1 file.
    - A Task MAY hold many related test cases + their implementation.
      Group tests by requirement, not 1:1 with Tasks.
    - Target: 1 Task per spec requirement (each `### Requirement:`
      block in openspec/changes/<name>/specs/). >2 Tasks per
      requirement = over-decomposed — merge.
    - Implementer subagent finishes a Task in ~15-30 min wall clock.
    - Right altitude = the TASK SHAPE example.
      WRONG — too abstract (implementer improvises scope + names):
        ### Task 3: Implement password reset feature
        Files: src/auth/*, tests/*
        Steps: add password reset functionality
      WRONG — too granular (one subagent per function, execution crawls):
        ### Task 3: Add generateToken() to PasswordResetService
        ### Task 4: Add verifyToken() to PasswordResetService
        ### Task 5: Add POST /auth/reset-password route
        (collapse into one Task)

    <<TASK SHAPE>>

    WRITE STYLE — terse (this is the ONLY compression pass; nothing
    post-processes the plan, so write it tight the first time):
    - Drop articles (a/an/the), filler (just/really/basically), pleasantries.
    - Fragments OK.
    - Keep signatures, file paths, names, values, error strings VERBATIM.
    - No prose between Tasks. No restating the design.

    INCREMENTAL WRITE — MANDATORY (Sonnet output-limit guard):
    - First Write: create plan.md with the PLAN HEADER only.
    - Then ONE Edit-append per Task (Task N's full block, then Task N+1,
      …). Never batch all Tasks into one tool call.
    - Each tool call carries only the chunk it writes — never restate
      earlier Tasks or the design in a later call.
    - NEVER echo plan content into your response text.

    Skip writing-plans' Execution Handoff — the orchestrator owns review
    and execution.

    Return: ONLY the path to the saved plan and Task count. No prose
    summary. Do NOT echo plan content.
  """
)
```

---

## 5.B Step B — Per-requirement writer template (R > 6)

All writers go out in ONE parallel message. Also the basis for the
**foundations writer** (a peer in the same batch, NOT a serial pre-stage):
replace "this requirement" with "the shared scaffolding named in design.md",
fix its global number to `1`, write to `plan-task-01.md`, scope to the shared
shell only (see SKILL.md Step B). The coordinator assigns the global Task
number and shared-file list inline before dispatching — writers do NOT
renumber or reorder.

```
Task(
  subagent_type: "general-purpose",
  model: "<haiku|sonnet per triage — NEVER opus or fable>",
  description: "Write plan Task N for <requirement>",
  prompt: """
    Invoke superpowers:writing-plans and apply it to EXACTLY this one
    requirement — ONE Task block, no plan header, no other Tasks. Where
    this prompt and writing-plans differ, this prompt wins.

    Requirement: "<requirement title>" in
      openspec/changes/<name>/specs/<file>
    Your assigned GLOBAL Task number: <N>   (use it verbatim in the heading;
      do NOT renumber, the coordinator already fixed dependency order)

    Read first (do not ask the user):
    - openspec/changes/<name>/specs/                 (all locked requirements)
    - openspec/changes/<name>/.superpowers/design.md (locked design)
    Shared files already owned by Task 1 (reference, do NOT redefine):
    - <shared-file path list from design.md, or "none">

    <<TASK SHAPE>>

    If you must Modify a shared file owned by Task 1, list it in Files:
    as Modify — never redefine its created contents.

    WRITE STYLE — terse: drop articles/filler, fragments OK; keep
    signatures, paths, names, values, error strings verbatim.

    Write the block to:
      openspec/changes/<name>/.superpowers/plan-task-NN.md
    (NN = your global Task number <N>, zero-padded). This file IS the durable
    sub-plan for your Task and its execution brief, so it must stand alone.
    One Write. Touch ONLY this file.

    Return: ONLY the file path. Do NOT echo plan content.
  """
)
```

---

## 5.B Step C — Sub-plan sync template (only on overlapping shared Modifies)

Skip this entirely when no two sub-plans Modify the same file at overlapping
ranges — the coordinator just writes the `plan.md` index over the sub-plans
(already final-form and globally numbered) and stops. Sub-plans are the
durable plan and are never deleted. Use this ONLY to
sync the specific conflicting blocks, in place, across the sub-plan files that
actually conflict.

```
Task(
  subagent_type: "general-purpose",
  model: "<sonnet default | opus if design flagged concurrency/shared state>",
  description: "Sync overlapping shared-file Modifies across sub-plans",
  prompt: """
    Each Task lives in its own sub-plan file, already final-form and globally
    numbered. Two or more Tasks Modify the same file at overlapping ranges.
    Fix ONLY that.

    Conflicting Tasks: <Task numbers> over file(s): <paths>

    Read (ONLY these sub-plans, one per conflicting Task):
    - openspec/changes/<name>/.superpowers/plan-task-NN.md   (one per Task above)
    - openspec/changes/<name>/.superpowers/design.md         (dependency intent)

    For each conflict: merge or sequence the overlapping Modify entries and
    their pseudo code, and note the dependency in the dependent Task
    ("depends on Task <k>'s edit to <file>"). Keep signatures, pseudo-code
    steps, file paths, error strings VERBATIM. Edit ONLY the conflicting
    entries, in the sub-plan file that owns each one. Do NOT touch
    non-conflicting sub-plans, do NOT touch the plan.md index, do NOT
    renumber, do NOT rewrite a whole file, do NOT merge sub-plans into one
    file.

    Return: ONLY the Task numbers you edited and, for each, the dependency you
    recorded (or "none"). The coordinator uses this to update the index's
    Depends on column.
  """
)
```
