---
name: quarkus-planning
description: >
  Creates a structured implementation plan in docs/plans/ for a Quarkus application:
  intent parsing, focused questions, approach selection, and task decomposition.
  Triggers on: "create a plan", "write an implementation plan", "plan this feature",
  "plan the implementation", "break this down into tasks", "how should we implement this".
  Russian phrases also trigger this: "составь план", "создай план", "план реализации",
  "распиши план", "разбей на задачи".
---

# Implementation Plan Creation

Create an implementation plan in `docs/plans/yyyymmdd-<task-name>.md` with interactive context gathering.

---

## Preflight — Project detection (before step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`,
   version property `quarkus.platform.version` / `quarkus.version`; Gradle: `io.quarkus` plugin + `quarkusPlatform` version.
3. **Extensions** — dependencies starting with `io.quarkus:` (and Quarkiverse `io.quarkiverse.*`).
   See [`../quarkus-explore/references/extension-glossary.md`](../quarkus-explore/references/extension-glossary.md).
4. **Persistence stack** — `quarkus-hibernate-orm-panache` → ORM Panache (sync);
   `quarkus-hibernate-reactive-panache` → reactive Panache (`Uni`-returning); neither → no Panache layer.
5. **Config files** — `src/main/resources/application.properties` (or `.yaml`), Flyway/Liquibase migrations under
   `src/main/resources/db/migration` / `db/changelog`.

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and tell
the user this skill targets Quarkus projects.

Remember the build tool for later: every test command written into the plan must match it
(`./mvnw ...` vs `./gradlew ...`).

---

## Step 0 — Parse intent and gather context

Tell the user: `Step 0: Parsing request and scanning the project...`

Before asking questions, understand what the user is working on:

1. **Parse the user's request** to identify intent:
    - "add feature Z" / "implement W" → feature development
    - "fix bug" / "debug issue" → bug fix plan
    - "refactor X" / "improve Y" → refactoring plan
    - "migrate to Z" / "upgrade W" → migration plan
    - generic request → explore the current work

2. **Gather relevant context quickly** — targeted reads only (build file, the 2–3 files the request
   names, package globs). Keep discovery under 30 seconds. If you need conventions for reading entities
   or endpoints, load only the relevant reference:
   [`../quarkus-explore/references/entity-description.md`](../quarkus-explore/references/entity-description.md),
   [`../quarkus-explore/references/rest-endpoints.md`](../quarkus-explore/references/rest-endpoints.md).

**CRITICAL: do NOT launch a subagent for exploration and do NOT run the full quarkus-explore
step 0–6 cycle. The goal is a quick scan, not exhaustive analysis. If more context is needed,
ask the user in step 1.**

---

## Step 1 — Present context and ask focused questions

Tell the user: `Step 1: Asking focused questions...`

Show the discovered context, then ask questions **one at a time** using your harness's
structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`); if none is available,
present a short numbered list and wait for the answer.

```text
based on your request, i found: [context summary]
```

**Ask questions one at a time (do not overwhelm with multiple questions):**

1. **Plan purpose** — "what is the main goal?"
    - provide multiple choice with a suggested answer based on discovered intent
    - wait for the response before the next question

2. **Scope** — "which components/files are involved?"
    - provide multiple choice with the discovered files/areas
    - wait for the response before the next question

3. **Constraints** — "any specific requirements or limitations?"
    - can be open-ended if constraints vary widely
    - wait for the response before the next question

4. **Testing approach** — "do you prefer TDD, regular approach or no tests?"
    - options: "TDD (tests first)", "Regular (code first, then tests)", "None (no tests)"
    - store the preference for reference during implementation
    - wait for the response before the next question

5. **Plan title** — "short descriptive title?"
    - provide a suggested name based on intent

After all questions are answered, synthesize the responses into the plan context.

---

## Step 1.5 — Explore approaches

Tell the user: `Step 1.5: Comparing implementation approaches...`

Once the problem is understood, propose implementation approaches:

1. **Propose 2–3 different approaches** with trade-offs for each.
2. **Lead with the recommended option** and explain the reasoning.
3. **Present conversationally** — not as a formal document yet.

Example format:

```text
i see three approaches:

**Option A: [name]** (recommended)
- how it works: ...
- pros: ...
- cons: ...

**Option B: [name]**
- how it works: ...
- pros: ...
- cons: ...

which direction appeals to you?
```

Use the structured-question tool to let the user select the preferred approach before creating the plan.

**Skip this step** if:
- the implementation approach is obvious (single clear path)
- the user explicitly specified how they want it done
- it's a bug fix with a clear solution

---

## Step 2 — Create plan file

Tell the user: `Step 2: Creating the plan file...`

Check `docs/plans/` for existing files, then create `docs/plans/yyyymmdd-<task-name>.md`
(use the current date).

### Plan structure

````markdown
# [Plan Title]

## Overview
- clear description of the feature/change being implemented
- problem it solves and key benefits
- how it integrates with the existing Quarkus application

## Context (from discovery)
- files/components involved: [list from step 0]
- related patterns found: [patterns discovered]
- dependencies identified: [extensions, config keys, datasources]

## Development Approach
- **testing approach**: [TDD / Regular - from the user's preference in planning]
- complete each task fully before moving to the next
- make small, focused changes
- **CRITICAL: every task MUST include new/updated tests** for code changes in that task
    - tests are not optional - they are a required part of the checklist
    - write unit tests for new functions/methods
    - write unit tests for modified functions/methods
    - add new test cases for new code paths
    - update existing test cases if behavior changes
    - tests cover both success and error scenarios
- **CRITICAL: all tests must pass before starting the next task** - no exceptions
- **CRITICAL: update this plan file when scope changes during implementation**
- run tests after each change
- maintain backward compatibility

## Testing Strategy
- **unit tests**: plain JUnit 5 for business logic that needs no Quarkus runtime - fast, no container
- **@QuarkusTest**: for code that needs CDI wiring, REST endpoints, or a database - the app boots in
  the test JVM and Dev Services start the required infrastructure (database, Kafka, Keycloak)
  automatically; use rest-assured for HTTP assertions
- **@QuarkusIntegrationTest**: black-box tests against the packaged artifact; no CDI injection,
  no `@InjectMock`; in standard Quarkus projects these run at the `verify` phase
  (`./mvnw verify` / `./gradlew quarkusIntTest` where configured)
- **test config**: `%test.` profile properties in `application.properties`, or a
  `@QuarkusTestProfile` implementation for per-test overrides
- **data cleanup**: clean up explicitly in `@BeforeEach`/`@AfterEach` - rollback semantics of
  `@Transactional` tests are not something to rely on
- **e2e tests**: if the project has UI-based e2e tests (Playwright, Cypress, etc.):
    - UI changes → add/update e2e tests in the same task as UI code
    - backend changes supporting UI → add/update e2e tests in the same task
    - treat e2e tests with the same rigor as unit tests (must pass before the next task)
    - store e2e tests alongside unit tests (or in the designated e2e directory)

## Progress Tracking
- mark completed items with `[x]` immediately when done
- add newly discovered tasks with `[+]` prefix
- document issues/blockers with `[!]` prefix
- update the plan if implementation deviates from the original scope
- keep the plan in sync with the actual work done

## Solution Overview
- high-level approach and architecture chosen
- key design decisions and rationale
- how it fits into the existing application (which layers, which packages)

## Technical Details
- data structures and changes
- parameters and formats
- processing flow

## What Goes Where
- **Implementation Steps** (`[ ]` checkboxes): tasks achievable within this codebase - code changes,
  tests, documentation updates
- **Post-Completion** (no checkboxes): items requiring external action - manual testing, changes in
  consuming projects, deployment configs, third-party verifications

## Implementation Steps

<!--
Task structure guidelines:
- Each task = ONE logical unit (one entity, one endpoint, one component)
- Use specific descriptive names, not generic "[Core Logic]" or "[Implementation]"
- Each task MUST have a **Files:** block listing files to Create/Modify (before checkboxes)
- Aim for ~5 checkboxes per task (more is OK if logically atomic)
- **CRITICAL: Each task MUST end with writing/updating tests before moving to the next**
  - tests are not optional - they are a required deliverable of every task
  - write tests for all NEW code added in this task
  - write tests for all MODIFIED code in this task
  - include both success and error scenarios in tests
  - list tests as SEPARATE checklist items, not bundled with implementation

Example (NOTICE: Files block + tests as separate checklist items):

### Task 1: Add the Discount entity and repository

**Files:**
- Create: `src/main/java/org/acme/discount/Discount.java`
- Create: `src/main/java/org/acme/discount/DiscountRepository.java`

- [ ] create `Discount` entity extending `PanacheEntity` with the fields from the Overview
- [ ] create `DiscountRepository` implementing `PanacheRepository<Discount>` with a `findActive()` finder
- [ ] add the Flyway migration for the new table under `src/main/resources/db/migration`
- [ ] write tests for `findActive()` covering active, inactive and empty result cases
- [ ] run tests - must pass before task 2

### Task 2: Add the POST /discounts endpoint

**Files:**
- Create: `src/main/java/org/acme/discount/DiscountResource.java`
- Create: `src/main/java/org/acme/discount/DiscountDto.java`
- Modify: `src/main/resources/application.properties`
- Create: `src/test/java/org/acme/discount/DiscountResourceTest.java`

- [ ] create `DiscountDto` as a record with bean validation constraints
- [ ] create `DiscountResource` with `@POST @Path("/discounts")`, `@Valid` body parameter
- [ ] annotate the write path with `@Transactional` and persist via the repository
- [ ] write `@QuarkusTest` tests for the success case and for validation failures (400)
- [ ] run tests - must pass before task 3
-->

### Task 1: [specific name - what this task accomplishes]

**Files:**
- Create: `src/main/java/org/acme/.../NewFile.java`
- Modify: `src/main/java/org/acme/.../ExistingFile.java`

- [ ] [specific action with file reference - code implementation]
- [ ] [specific action with file reference - code implementation]
- [ ] write tests for new/changed functionality (success cases)
- [ ] write tests for error/edge cases
- [ ] run tests - must pass before the next task

### Task N-1: Verify acceptance criteria
- [ ] verify all requirements from Overview are implemented
- [ ] verify edge cases are handled
- [ ] run the full test suite: `<project test command>`
- [ ] run integration tests if the project has them: `<project verify command>`
- [ ] verify test coverage meets the project standard

### Task N: [Final] Update documentation
- [ ] update README.md if needed
- [ ] update CLAUDE.md if new patterns were discovered
- [ ] move this plan to `docs/plans/completed/`

## Post-Completion
*Items requiring manual intervention or external systems - no checkboxes, informational only*

**Manual verification** (if applicable):
- manual UI/UX testing scenarios
- performance testing under load
- security review considerations

**External system updates** (if applicable):
- consuming projects that need updates after this change
- configuration changes in deployment systems
- third-party service integrations to verify
````

---

## Step 2.1 — Analyze plan for domain persistence work

Tell the user: `Step 2.1: Checking the plan for persistence work...`

After writing the plan file, scan it for tasks that involve domain entities. If there are none —
skip this step entirely.

If there are entity-related tasks, detect the persistence stack from the build file dependencies:

| Dependency detected | Stack | Skill to activate |
|---|---|---|
| `quarkus-hibernate-orm-panache` | Panache ORM (sync) | `quarkus-data-panache` |
| `quarkus-hibernate-reactive-panache` | Panache ORM (reactive, `Uni`-returning) | `quarkus-data-panache` |
| neither | none | skip this step |

Once the stack is resolved:

1. activate the `quarkus-data-panache` skill
2. follow the skill's environment setup steps
3. ask the user focused questions about the stack-specific decisions the plan implies — one at a time
   using the structured-question tool (e.g. Active Record on the entity vs a Panache repository;
   ID strategy — `PanacheEntity` long id vs a custom `UUID` id; for reactive: which layers return `Uni`)
4. after all answers are collected, revise the plan:
    - add stack-specific notes to the relevant tasks
    - add a reminder in each entity task: "> **quarkus-data-panache skill required.** Before writing any entity code: activate the skill and verify the implementation follows its rules. For any deviation — ask the developer before continuing."
    - add the corresponding DB migration task (Flyway/Liquibase) if not already present
    - if the project is reactive, add a reminder that persistence calls return `Uni` and the resource
      layer must return `Uni<...>` as well

**If the plan does NOT touch domain entities, or the project uses neither Panache extension:** skip
this step entirely.

---

## Step 3 — Next steps

Tell the user: `Step 3: Handing off the plan...`

After creating the file, tell the user: "created plan: `docs/plans/yyyymmdd-<task-name>.md`"

Then ask via the structured-question tool (or a numbered list as fallback):

```json
{
  "questions": [{
    "question": "Plan created. What's next?",
    "header": "Next step",
    "options": [
      {"label": "Review", "description": "Print the plan and collect review feedback"},
      {"label": "Implement", "description": "Commit the plan and start implementing"},
      {"label": "Done", "description": "Commit the plan, no further action"}
    ],
    "multiSelect": false
  }]
}
```

- **Review**: print the plan path and a compact summary of the tasks, then tell the user:
  "Plan is ready — review it and tell me what to change." Wait for feedback in the conversation,
  apply the requested changes, and ask again with the same options (minus "Review"). No IDE tooling is
  required; if your harness can open files in the editor, offer to open the plan file.
- **Implement**: commit the plan with a message like "docs: add <topic> implementation plan", then begin
  implementing task 1 interactively in this session. Use a todo tool if your harness has one, and mark
  items complete immediately (do not batch).
- **Done**: commit the plan with a message like "docs: add <topic> implementation plan", stop.

---

## Execution enforcement

**Rules during implementation:**

1. **Complete each task fully before moving to the next**:
    - STOP before moving to the next task
    - if the testing approach is TDD or Regular: add/update tests for all new functionality and run them
    - if the testing approach is None: verify manually via the running application (`./mvnw quarkus:dev`)
    - mark completed items with `[x]` in the plan file

2. **If tests are used and fail**:
    - fix the failures before proceeding
    - do NOT move to the next task with failing tests

3. **Plan tracking during implementation**:
    - update checkboxes immediately when tasks complete
    - add the `[+]` prefix for newly discovered tasks
    - add the `[!]` prefix for blockers
    - modify the plan if the scope changes significantly

4. **On completion**:
    - move the plan to `docs/plans/completed/`
    - create the directory if needed: `mkdir -p docs/plans/completed`

This ensures each task is solid before building on top of it.

---

## Key principles

- **One question at a time** — do not overwhelm the user with multiple questions in a single message.
- **Multiple choice preferred** — easier to answer than open-ended when possible.
- **DRY, YAGNI ruthlessly** — avoid unnecessary duplication and features, keep scope minimal (but prefer
  duplication over premature abstraction when it reduces coupling).
- **Lead with a recommendation** — have an opinion and explain why, but let the user decide.
- **Explore alternatives** — always propose 2–3 approaches before settling (unless obvious).
- **Duplication vs abstraction** — when code repeats, ask the user: prefer duplication (simpler, no
  coupling) or abstraction (DRY but adds complexity)? Explain the trade-offs before deciding.

---

## Anti-hallucination checklist

- [ ] Every file path, class name, and extension named in the plan came from an actual read of the
      project — not from assumptions.
- [ ] The persistence stack in step 2.1 was detected from the build file dependencies.
- [ ] Test commands in the plan match the project's build tool (Maven vs Gradle).
- [ ] No idioms from other Java frameworks leaked into the plan (see the blocklist in
      [`../quarkus-explore/SKILL.md`](../quarkus-explore/SKILL.md) and
      [`../../docs/quarkus-facts.md`](../../docs/quarkus-facts.md)).
- [ ] Every task ends with test work and a test run before the next task.
- [ ] The plan file path and naming follow `docs/plans/yyyymmdd-<task-name>.md`.
- [ ] Any claim about existing behavior traces to a file you actually read.
