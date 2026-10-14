# Step 6 — Report blocks

Replacement blocks for chaining-openspec-superpowers **Step 6**. SDD's
templates (`implementer-prompt.md`, `task-reviewer-prompt.md`,
`re-review-prompt.md`) shape their reports for a human reader. In this chain
no human reads them — every report is consumed by an agent: the controller
routes on it, the reviewer verifies it, a fix-round implementer resumes from
it. So each report carries what the next agent acts on, in fixed lines.

Dispatch from SDD's templates as usual and swap in the block named below.
Everything above the swap point stays as SDD wrote it.

---

## Implementer — replaces `## After Review Findings` through the end of the prompt

```
## Report

Your report is read only by agents: the controller, the task reviewer,
and any later fix-round implementer. Write it to [REPORT_FILE] as
exactly these lines:

Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
Commits: <sha7> <subject>                (one line per commit)
Files: <path> (created|modified)         (one line per file)
RED: `<test command>` → <decisive failing line>
GREEN: `<test command>` → <pass count>, output <clean|noisy>
Deviations: <where the code differs from the brief, and why> | none
Concerns: <doubt about correctness or scope> | none

DONE_WITH_CONCERNS = built it, doubt it is right. BLOCKED = cannot
finish. NEEDS_CONTEXT = missing information. Never silently ship work
you are unsure about.

Reply with the Status, Commits, and GREEN lines plus the report path.
BLOCKED or NEEDS_CONTEXT: the reply also states exactly what you need.

If resumed with review findings: fix them, re-run the tests covering
the amended code, and append to [REPORT_FILE]:

Fix <R>: <finding> → <change> (<file:line>)
Tests: `<test command>` → <result>

Then reply with the same lines as before plus the report path.
```

---

## Task reviewer — replaces `## Part 2: Code Quality` through the end of the prompt

Also retitle the dispatch `Review Task N (spec)`.

```
## Scope

Spec compliance only. Code quality is a separate pass over the whole
branch after all tasks finish; it is not part of this review.

## Severity

Critical / Important: the task cannot be trusted until fixed — a
missing, extra, or misbuilt requirement. Minor: everything else. A
defect the brief itself mandates is still a finding; label it
plan-mandated.

## Output Format

Your reply is read only by the controller. Reply with exactly these
lines, verdict first:

Spec: ✅ | ❌
<Critical|Important|Minor> <file:line> — <missing|extra|misunderstood>: <what> — fix: <how>
⚠️ <requirement> — controller check: <what to verify>

One line per finding. A ⚠️ line only for a requirement the diff cannot
show (it lives in unchanged code or spans tasks).
```

---

## Re-reviewer — replaces `## Output Format` through the end of the prompt

```
## Output Format

Your reply is read only by the controller. Reply with exactly these
lines:

<finding one-liner> — ADDRESSED | NOT ADDRESSED — <file:line>
New: <Critical|Important|Minor> <file:line> — <problem>
Out of scope: <file:line> — <issue>
Open: <finding one-liners> | none

One ADDRESSED/NOT ADDRESSED line per finding, in order. "Attempted" is
NOT ADDRESSED — the defect must be gone. One `New:` line per breakage
the fix introduced, or `New: none`. `Out of scope:` lines only when you
noticed something outside the fix diff.
```
