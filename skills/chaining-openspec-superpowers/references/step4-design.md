# Step 4 — Design dispatch template

Verbatim `Task()` template for chaining-openspec-superpowers **Step 4**
(technical design). The rules live inline in SKILL.md Step 4 — this file is
the copy-paste reference. Load on demand at dispatch time.

`model:` is the user's pick from the Step 4 `AskUserQuestion` — `opus` or
`fable`, nothing else. Fill the REVISION block only on a revision pass or a
quota-fallback re-dispatch; otherwise drop it.

```
Task(
  subagent_type: "general-purpose",
  model: "<opus|fable>",
  description: "Technical design for <name>",
  prompt: """
    Invoke superpowers:brainstorming and follow it, with the overrides below.

    Requirements are already captured in openspec/changes/<name>/specs/.
    Read those files first. Skip all requirements-gathering questions —
    the WHAT is locked. Focus exclusively on the HOW: technical design,
    architecture, components, data flow, testing strategy.

    Save the design to: openspec/changes/<name>/.superpowers/design.md
    If it already exists, read it and continue or revise it in place.
    Create .superpowers/ (and code-refs/, when there is code) if missing.

    You run as a subagent, not in conversation with the user:
    - Ask the user nothing: no clarifying questions, no approach menus, no
      AskUserQuestion, no visual companion, no waiting for review.
    - Where brainstorming would put a choice to the user, pick the option
      you recommend and add one line to a `## Decisions to confirm` section
      at the end of design.md: the choice made, the runner-up, the design
      section where it lives. State the decision in that section's body too.
    - The controller owns the review gate. Do not request approval.

    Write the design in normal prose. DO NOT apply caveman/compression —
    the design is the human review artifact and must stay thorough,
    comprehensive, and explanatory. Diagrams, trade-off discussion, and
    rationale all belong here.

    Raw code stays out of design.md. Any code you generate (function or
    class bodies, algorithms, schema DDL, config, longer snippets) goes in
    its own raw file: openspec/changes/<name>/.superpowers/code-refs/<slug>.<ext>
    — code only, native extension, no markdown fence, one comment line at
    the top saying what it is. In design.md, explain it in prose and link it
    as `code-refs/<slug>.<ext>`. No fenced code blocks in design.md; one-line
    signatures inline are fine.

    STOP after writing design.md. Do NOT chain into writing-plans —
    plan generation is dispatched separately on a cheaper model.

    REVISION (only on a revision pass):
    <the user's requested changes, verbatim>

    Return: ONLY the design.md path, the code-refs file names, and the
    number of lines under `## Decisions to confirm`. Do NOT echo design content.
  """
)
```
