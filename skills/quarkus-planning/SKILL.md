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

Before rejecting the project or selecting a command, identify the target module. Inspect its build file plus root/parent build configuration for inherited Quarkus BOM/plugin, dependency management, and version properties/catalogs; use the target Maven module's effective POM when inheritance remains unclear. Prefer the project root wrapper with module selection (`-pl`/`-am` for Maven, `:module:task` for Gradle). If the wrapper is absent, check installed `mvn`/`gradle` and its version; if no usable tool is available, report a blocker/NOT RUN rather than calling the project invalid.


This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`,
   version property `quarkus.platform.version` / `quarkus.version`; Gradle: `io.quarkus` plugin + `quarkusPlatform` version.
3. **Extensions** — dependencies starting with `io.quarkus:` (and Quarkiverse `io.quarkiverse.*`).
   See [`references/extension-glossary.md`](references/extension-glossary.md).
4. **Persistence stack** — `quarkus-hibernate-orm-panache` → ORM Panache (sync);
   `quarkus-hibernate-reactive-panache` → reactive Panache (`Uni`-returning); neither → no Panache layer.
5. **Config files** — the detected `src/main/resources/application.properties` or `.yaml`/`.yml` file, with
   Flyway/Liquibase migrations under
   `src/main/resources/db/migration` / `db/changelog`.

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and tell
the user this skill targets Quarkus projects.

Remember the build tool for later: every test command written into the plan must match it
(`./mvnw ...` vs `./gradlew ...`).

---

## Step 0 — Parse intent and gather context
Treat the requested work as the plan goal and derive a concise title from its action and subject. Do not ask the user to restate either. Before asking questions, understand what the user is working on:

1. **Parse the user's request** to identify intent:
    - "add feature Z" / "implement W" → feature development
    - "fix bug" / "debug issue" → bug fix plan
    - "refactor X" / "improve Y" → refactoring plan
    - "migrate to Z" / "upgrade W" → migration plan
    - generic request → explore the current work

2. **Gather relevant context quickly** — targeted reads only (build file, the 2–3 files the request
   names, package globs). Keep discovery under 30 seconds. If you need conventions for reading entities
   or endpoints, load only the relevant reference:
   [`references/entity-description.md`](references/entity-description.md),
   [`references/rest-endpoints.md`](references/rest-endpoints.md).

Use a focused quick scan, not the full quarkus-explore cycle. Read directly by default; a mechanical exploration handoff is allowed only when the caller/operator permits delegation and the environment supports it. If more context is needed, ask about material unknowns in Step 1.**

---

## Step 1 — Resolve only material unknowns
Use the request and discovered project context as authoritative input. Derive the goal and a concise title from the request; take scope, constraints, and test preferences already stated by the caller as decided. Ask only about unresolved choices that materially affect plan correctness or acceptance, in one batched round. Prefer the harness's structured-question tool when available; otherwise use a short numbered list. Do not ask the caller to repeat information already provided or infer permission to change the requested scope.

---

## Step 1.5 — Explore approaches
Once the problem is understood, compare approaches only when more than one materially different option is viable. Recommend one with concise trade-offs; don't manufacture alternatives for a clear solution.

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

Ask the user to select only if the choice remains unresolved and materially changes the plan. Use the structured-question tool when available; otherwise use a concise numbered question.

**Skip this step** if:
- the implementation approach is obvious (single clear path)
- the user explicitly specified how they want it done
- it's a bug fix with a clear solution

---

## Step 2 — Create plan file
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
- **testing approach**: [follow the user's stated preference; otherwise plan tests and validation by default, with None only when explicitly disabled or inapplicable]
- complete each task fully before moving to the next
- make small, focused changes
- **When tests apply, each task MUST include new/updated tests** for code changes in that task
    - write tests for new or modified functions and code paths
    - update existing test cases if behavior changes
    - cover both success and error scenarios where the chosen test type supports them
- **When tests apply, all relevant tests must pass before starting the next task**
- When tests are explicitly disabled or not applicable (for example, docs-only work), record the
  alternative validation instead of inventing a test requirement.
- **CRITICAL: update this plan file when scope changes during implementation**
- run the applicable tests or alternative validation after each change
- maintain backward compatibility

## Testing Strategy
- **unit tests**: plain JUnit 5 for business logic that needs no Quarkus runtime - fast, no container
- **@QuarkusTest**: for code that needs CDI wiring, REST endpoints, or a database - the app boots in
  the test JVM and Dev Services start the required infrastructure (database, Kafka, Keycloak)
  automatically; use rest-assured for HTTP assertions
- **@QuarkusIntegrationTest**: black-box tests against the packaged artifact; no CDI injection,
  no `@InjectMock`; in standard Quarkus projects these run at the `verify` phase
  (`./mvnw verify` / `./gradlew quarkusIntTest` where configured)
- **test config**: `%test.` profile keys in the detected application config file (`.properties` or YAML), or a
  `QuarkusTestProfile` implementation for per-test overrides
- **data cleanup**: clean up explicitly in `@BeforeEach`/`@AfterEach` - rollback semantics of
  `@Transactional` tests are not something to rely on
- **e2e tests**: if the project has UI-based e2e tests (Playwright, Cypress, etc.):
    - UI changes → add/update e2e tests in the same task as UI code
    - backend changes supporting UI → add/update e2e tests in the same task
    - when tests apply, treat e2e tests with the same rigor as unit tests (must pass before the next task);
      when tests are disabled or not applicable, record the alternative validation instead
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
- **When tests apply, each task MUST end with writing/updating tests before moving to the next**
  - write tests for all NEW code added in this task
  - write tests for all MODIFIED code in this task
  - include both success and error scenarios when applicable
  - list tests as SEPARATE checklist items, not bundled with implementation
  - when tests are explicitly disabled or not applicable, list the alternative validation instead

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
- Modify: the detected application config file (`.properties` or YAML)
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
- [ ] when tests apply, run the full test suite: `<project test command>`
- [ ] when integration tests apply, run them: `<project verify command>`
- [ ] when coverage is part of the request, verify it meets the project standard

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
After writing the plan file, scan it for tasks that involve domain entities. If there are none —
skip this step entirely.

If there are entity-related tasks, detect the persistence stack from the build file dependencies:

| Dependency detected | Stack | Skill to activate |
|---|---|---|
| `quarkus-hibernate-orm-panache` | Panache ORM (sync) | `quarkus-data-panache` |
| `quarkus-hibernate-reactive-panache` | Panache ORM (reactive, `Uni`-returning) | `quarkus-data-panache` |
| neither | none | skip this step |

Once the stack is resolved, apply the `quarkus-data-panache` skill instructions to relevant plan tasks. A skill handoff does not itself authorize launching a subagent: mechanically delegate only when the caller/operator permits it and the environment supports it; otherwise read and apply the skill directly. Ask one batched round only for unresolved, material stack decisions (for example repository vs Active Record or custom ID strategy); use a structured-question tool when available and a numbered text list otherwise. Preserve caller-resolved choices. Then revise the plan:
    - add stack-specific notes to the relevant tasks
    - add a reminder in each entity task: "> **quarkus-data-panache skill required.** Before writing any entity code: activate the skill and verify the implementation follows its rules. For any deviation — ask the developer before continuing."
    - add the corresponding DB migration task (Flyway/Liquibase) if not already present
    - if the project is reactive, add a reminder that persistence calls return `Uni` and the resource
      layer must return `Uni<...>` as well

**If the plan does NOT touch domain entities, or the project uses neither Panache extension:** skip
this step entirely.

---

## Step 3 — Next steps
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
    - if the testing approach is TDD or Regular and tests apply: add/update tests for all new functionality
      and run them
    - if the testing approach is None or tests are not applicable: use the detected build tool's manual or
      static validation (Maven `./mvnw quarkus:dev`, Gradle `./gradlew quarkusDev`, or a focused check)
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

- Ask only unresolved, material questions; batch independent decisions into one round and use a structured-question tool when available, with a numbered text fallback.
- Multiple choice is useful when options are genuinely bounded; use plain text for free-form answers.
- **DRY, YAGNI ruthlessly** — avoid unnecessary duplication and features, keep scope minimal (but prefer
  duplication over premature abstraction when it reduces coupling).
- **Lead with a recommendation** — have an opinion and explain why, but let the user decide.
- **Explore alternatives** — always propose 2–3 approaches before settling (unless obvious).
- **Duplication vs abstraction** — when code repeats, ask the user: prefer duplication (simpler, no
  coupling) or abstraction (DRY but adds complexity)? Explain the trade-offs before deciding.

---

## Portable resources and sibling handoffs

This skill's relative `references/` and `examples/` are bundled with its directory. Repository-level `docs/quarkus-facts.md` is optional when the skill is installed alone; if absent, verify version-sensitive claims against official versioned documentation/source or the actual project dependencies. Before a sibling-skill handoff, check whether that sibling is available. If missing, say so and apply equivalent local instructions only when the complete relevant example is available; never pretend to read a missing file. Skill activation/handoff alone does not authorize a child agent; delegate mechanically only when caller/operator permission and environment support are both present.

## Anti-hallucination checklist

- [ ] Every file path, class name, and extension named in the plan came from an actual read of the
      project — not from assumptions.
- [ ] The persistence stack in step 2.1 was detected from the build file dependencies.
- [ ] Test commands in the plan match the project's build tool (Maven vs Gradle).
- [ ] No idioms from other Java frameworks leaked into the plan (see the blocklist in
      [`../quarkus-explore/SKILL.md`](../quarkus-explore/SKILL.md) and
      [`../../docs/quarkus-facts.md`](../../docs/quarkus-facts.md)).
- [ ] Every task includes test work and a test run when tests apply; otherwise it records alternative validation.
- [ ] The plan file path and naming follow `docs/plans/yyyymmdd-<task-name>.md`.
- [ ] Any claim about existing behavior traces to a file you actually read.
