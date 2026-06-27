# Step 5 — Dispatch templates

Verbatim `Task()` templates and the granularity worked-example for
chaining-openspec-superpowers **Step 5** (implementation plan). The rules
these templates enforce live inline in SKILL.md Step 5 — this file is the
copy-paste reference. Load on demand at dispatch time.

- 5.A single-writer dispatch → use the **5.A template**.
- 5.B per-requirement fan-out → use the **Step-B writer template** (also the
  basis for the foundations writer in the same parallel batch).
- 5.B conflict reconcile → use the **Step-C reconcile template** (only when two
  parts Modify the same file at overlapping ranges; otherwise the coordinator
  just `cat`s the parts).

---

## 5.A — Single-writer dispatch template (R ≤ 6)

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Write implementation plan",
  prompt: """
    Invoke superpowers:writing-plans to produce the implementation plan.

    Inputs (read these first, do not ask the user):
    - openspec/changes/<name>/specs/        (locked requirements)
    - openspec/changes/<name>/.superpowers/design.md  (locked technical design)

    The WHAT and the HOW are both already decided. Your job is purely
    to translate the design into bite-sized TDD tasks with concrete
    code blocks per the writing-plans skill.

    Save plan to: openspec/changes/<name>/.superpowers/plan.md

    TASK GRANULARITY OVERRIDE — coarser than writing-plans default:
    writing-plans Task Structure already groups red/green/commit as
    STEPS inside one Task. Problem is Task scope itself runs too narrow
    (one function, one test case). OVERRIDE Task scope here.

    - One Task = one cohesive business requirement / capability /
      vertical slice — what a reviewer would PR-review as a unit.
    - A Task MAY touch multiple files when one requirement spans them.
      Use the writing-plans `Files:` block (Create / Modify / Test) to
      list every file in scope. Do not split a requirement across
      Tasks just because it touches >1 file.

      SCOPE EXAMPLE — right altitude per writing-plans Task Structure
      (Files: block uses Create/Modify/Test verbatim; signatures + test
      cases live inside Step code blocks, NOT in Files annotations):

      ### Task 3: User can reset password via email link

      **Files:**
        - Create: `src/services/PasswordResetService.ts`
        - Create: `src/routes/auth/reset-password.ts`
        - Create: `src/emails/password-reset.tsx`
        - Create: `db/migrations/0042_password_reset_tokens.sql`
        - Modify: `src/services/AuthService.ts:142-158`
        - Modify: `src/routes/index.ts:28`
        - Test: `tests/routes/auth/reset-password.test.ts`

      Steps follow writing-plans Task Structure (test-first, minimal
      impl, run, commit). All function signatures, SQL DDL, route
      payloads, and the 3 test cases (happy path, expired token → 410,
      invalid email → 404) live VERBATIM inside their Step code
      blocks. No placeholders.

      Right altitude: one requirement, every touched file enumerated,
      concrete code lands in Steps. Subagent has no room to improvise
      scope OR signatures.

      WRONG — too abstract (subagent deviates):
        ### Task 3: Implement password reset feature
        Files: src/auth/*, tests/*
        Steps: add password reset functionality

      WRONG — too granular (original problem returns):
        ### Task 3: Add generateToken() to PasswordResetService
        ### Task 4: Add verifyToken() to PasswordResetService
        ### Task 5: Add POST /auth/reset-password route
        ### Task 6: Add password reset email template
        (collapse into one Task)
    - A Task MAY contain multiple related test cases + their
      implementation together. Group tests by requirement, not 1:1
      with Tasks.
    - Target: 1 Task per spec capability (the `## Requirement` blocks
      in openspec/changes/<name>/specs/). If you emit >2 Tasks per
      requirement, you are over-decomposing — merge.
    - Implementer subagent should be able to finish a Task in ~15-30
      minutes wall clock.
    - Still NO placeholders, NO "TBD", full code blocks required for
      every file touched.

    WRITE STYLE — terse/compressed (independent of caveman plugin presence):
    - Drop articles (a/an/the), filler (just/really/basically), pleasantries.
    - Fragments OK. Pattern: "[file] [action] [reason]." per task line.
    - Keep all code blocks, file paths, function names, error strings VERBATIM.
    - Keep TDD discipline (test-first) and acceptance checkboxes per Task.
    - No prose summaries between Tasks. No restating the design.
    - Goal: every line is actionable. Zero filler.

    INCREMENTAL WRITE — MANDATORY (Sonnet output-limit guard):
    A full plan in one Write blows the Sonnet output token limit and
    truncates plan.md. Build the file incrementally instead:
    - First Write: create plan.md with header + any preamble ONLY.
    - Then ONE Edit-append per Task group (append Task N's full block,
      then Task N+1, …). One Task per Edit. Never batch all Tasks into
      one tool call.
    - Each tool call carries only the chunk it writes — never restate
      earlier Tasks or the design in a later call.
    - NEVER echo plan content into your response text. The plan lives in
      the file, not in your message.

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
fix its global number to `1`, write to `plan-part-01.md`, scope to the shared
shell only (see SKILL.md Step B). The coordinator assigns the global Task
number and shared-file list inline before dispatching — writers do NOT
renumber or reorder.

```
Task(
  subagent_type: "general-purpose",
  model: "<haiku|sonnet per triage — NEVER opus>",
  description: "Write plan Task N for <requirement>",
  prompt: """
    Invoke superpowers:writing-plans and apply its Task Structure to
    EXACTLY this one requirement — produce ONE Task block, no others, no
    whole-plan preamble/overview. If writing-plans emits more than this
    requirement's Task, keep only this requirement's block and discard the
    rest.

    Requirement: "<## Requirement title>" in
      openspec/changes/<name>/specs/<file>
    Your assigned GLOBAL Task number: <N>   (use it verbatim in the heading;
      do NOT renumber, the coordinator already fixed dependency order)

    Read first (do not ask the user):
    - openspec/changes/<name>/specs/                 (all locked requirements)
    - openspec/changes/<name>/.superpowers/design.md (locked design)
    Shared files already owned by Task 1 (reference, do NOT redefine):
    - <shared-file path list from design.md, or "none">

    Emit ONE `### Task <N>: <requirement title>` block per the writing-plans
    Task Structure: Files: block (Create/Modify/Test), test-first Steps
    with full code blocks. All signatures, DDL, payloads, test cases
    VERBATIM inside Step code blocks. No placeholders, no "TBD".
    If you must Modify a shared file owned by Task 1, say so in the Files:
    block — do NOT redefine its created contents.

    Write STYLE — terse: drop articles/filler, fragments OK, keep code
    + paths + names + error strings verbatim, keep TDD + checkboxes.

    Write the block to:
      openspec/changes/<name>/.superpowers/plan-part-NN.md
    (NN = your global Task number <N>, zero-padded). One Write; if the block
    is huge, header-Write then Edit-append the Steps. Touch ONLY this file.

    Return: ONLY the file path. Do NOT echo plan content.
  """
)
```

---

## 5.B Step C — Conflict reconcile template (only on overlapping shared Modifies)

Skip this entirely when no two parts Modify the same file at overlapping
ranges — the coordinator just `cat`s the part files into `plan.md` (they are
already final-form and globally numbered) and deletes the scratch files. Use
this ONLY to reconcile the specific conflicting blocks. It edits those blocks
in place; it NEVER re-emits the whole plan.

```
Task(
  subagent_type: "general-purpose",
  model: "<sonnet default | opus if design flagged concurrency/shared state>",
  description: "Reconcile overlapping shared-file Modifies in plan.md",
  prompt: """
    plan.md already exists (parts concatenated in global Task order). Two or
    more Tasks Modify the same file at overlapping ranges. Fix ONLY that.

    Conflicting Tasks: <Task numbers> over file(s): <paths>

    Read:
    - openspec/changes/<name>/.superpowers/plan.md   (the assembled plan)
    - openspec/changes/<name>/.superpowers/design.md (dependency intent)

    For each conflict: merge or sequence the overlapping Modify blocks, and
    note the dependency in the dependent Task ("depends on Task <k>'s edit to
    <file>"). Keep ALL code blocks, file paths, signatures, error strings
    VERBATIM. Edit ONLY the conflicting Task blocks — do NOT touch other
    Tasks, do NOT renumber, do NOT rewrite the whole file.

    Return: ONLY the Task numbers you edited.
  """
)
```
