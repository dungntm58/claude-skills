# Step 4.5 — Condense dispatch template

Verbatim `Task()` template for chaining-openspec-superpowers **Step 4.5**
(condense the approved design). The rules live inline in SKILL.md Step 4.5 —
this file is the copy-paste reference. Load on demand at dispatch time.

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Condense design into design-brief.md",
  prompt: """
    Condense the approved design into an implementer-facing brief.

    Read (do not ask the user):
    - openspec/changes/<name>/.superpowers/design.md  (approved; human version)
    - openspec/changes/<name>/specs/                  (requirement + scenario names)

    Write: openspec/changes/<name>/.superpowers/design-brief.md
    NEVER edit, move, or delete design.md — it stays the human version.

    The brief replaces design.md as the input for plan writers and
    implementers. It must carry every decision they act on, and nothing else.

    KEEP — verbatim where exact:
    - Components / modules / files and each one's responsibility
    - Interfaces, signatures, types, schemas, payloads, config keys
    - Data flow and ordering, state transitions, concurrency rules
    - Exact names, paths, constants, limits, error strings, status codes
    - Constraints and invariants; dependency order between parts
    - Testing strategy: what to test where, fixtures, tools
    - Per requirement: which components implement it

    DROP:
    - Open questions, spec issues found, risks
    - "Understanding" / context narrative, motivational text
    - Revision history, the owner-ruling story
    - Rationale paragraphs, long "why this and not that" justifications
    - Rejected-alternatives tables
    - Duplicated explanations (state each fact once)
    - Big ASCII art diagrams — keep at most ONE small one, only if a
      slice truly needs it
    - Restated spec scenarios — refer to them as
      `<Requirement header> / <Scenario name>` instead

    One-clause reason ONLY where an implementer could otherwise "fix"
    something wrongly, e.g. "square collision body, not lit cells: do not
    change".

    Resolved decisions only: if design.md marks an open question as
    answered, keep the answer, drop the question. If one is still open,
    keep one line `OPEN: <question>` — never invent an answer.

    STYLE — caveman-compressed:
    - Drop articles, filler, hedging, pleasantries. Fragments OK.
    - Bullets and short field lists over paragraphs.
    - Keep signatures, paths, names, values, error strings VERBATIM.
    - Never drop not / never / no / only / except.
    - No invented abbreviations.

    Shape:
      # Design brief — <change-name>
      Source: design.md (approved). Brief wins for plan/implementation;
      design.md only to resolve a gap.
      ## Components
      ## Interfaces & data
      ## Flows & rules
      ## Requirement map   (requirement header -> components)
      ## Testing
      (omit an empty section)

    Return: ONLY the path, plus `design.md <W1> words -> brief <W2> words`.
    Do NOT echo brief content.
  """
)
```
