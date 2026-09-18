---
name: quarkus-crud-rest-controller
description: >
  Creates a Quarkus JAX-RS resource (XxxResource) with CRUD endpoints backed by a Panache
  repository, with optional DTO mapping, pagination, filtering, and patch support.
  Use this skill when a CRUD REST resource needs to be created, either standalone or as
  part of a larger task.
  Russian phrases also trigger this: "создай CRUD", "CRUD REST-ресурс для сущности",
  "создай REST-ресурс", "сделай CRUD-эндпоинты", "добавь REST для сущности".
---

# Preflight — Project detection (before step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`;
   Gradle: `id("io.quarkus")` plugin. Quarkus 3.x targets Jakarta EE (`jakarta.*`) — never `javax.*`.
3. **Extensions** — dependencies starting with `io.quarkus:` and `io.quarkiverse.*`. Feature gates for this skill:
   - `quarkus-rest-jackson` → JSON serialization (`hasRestJackson`)
   - `quarkus-hibernate-orm-panache` → synchronous Panache (`hasSyncPanache`)
   - `quarkus-hibernate-reactive-panache` → reactive Panache (`hasReactivePanache`)
   - `quarkus-hibernate-validator` → Bean Validation (`hasValidation`)
   - `io.quarkiverse.mapstruct:quarkus-mapstruct` + `org.mapstruct:mapstruct` → MapStruct mappers (`hasMapStruct`)
4. **Persistence mode** — if `hasSyncPanache` → proceed. If only `hasReactivePanache` →
   **STOP and ask the user**: this skill's examples are synchronous, and no `Uni`-returning CRUD
   examples exist here — do not improvise reactive code. If both are present, ask which
   persistence mode this resource should use. If `quarkus-hibernate-orm` is present without
   `quarkus-hibernate-orm-panache`, or neither Panache extension is present, **STOP** and explain
   that this skill requires synchronous Panache; do not add Panache silently.
5. **Language** — this skill generates **Java** only. If the resource must be Kotlin — STOP and
   tell the user (no Kotlin examples exist in this skill).

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and
tell the user this skill targets Quarkus projects.

---

# CRUD REST Resource

Generates a JAX-RS resource class (`XxxResource`) with standard CRUD endpoints for an entity,
using a Panache repository, optional DTO mapping, pagination, filtering, and patch support.

---

> **CRITICAL: Code ONLY from examples/ files. If no matching example -- STOP and ask user.**
> **CRITICAL: For questions with a fixed set of choices, prefer your harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`) > its analogue > plain text list. Plain numbered text lists are the last resort when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 2–4 may already be answered by the user's prompt and prior turns. Re-asking what was already said is the #1 reason this skill feels slow.

---

## Defaults

The options below are grouped by topic. `persistenceMode`, `language`, and the build-related
flags are auto-detected in the preflight; all other options are resolved via the
Decision-making principle (derive from context → confirm → ask).

### Block 1 — Entity & repository

| Option | Default | Notes |
|--------|---------|-------|
| entity | -- | which entity to create the resource for |
| repository | first existing for entity | which Panache repository to use |

### Block 2 — DTO mode

| Option | Default | Notes |
|--------|---------|-------|
| DTO mode | DTO (recommended) | if no existing DTO for the entity, delegate to `quarkus-dto-creator`; user can opt out to use the entity directly |

### Block 3 — Resource naming & paths

| Option | Default | Notes |
|--------|---------|-------|
| resourceName | `{EntityName}Resource` | suggest based on the project's naming convention |
| resourcePackage | same package as existing resources or `mainPackage` | auto-detected from the project |
| basePath | `/api` | persistent base path; detect from existing resources |
| resourcePath | `/{entityVarPlural}` | auto from entity name |

### Block 4 — Pagination, filtering & total count

| Option | Default | Notes |
|--------|---------|-------|
| pagination | true | `page`/`size` query params on GET_LIST |
| pageParams | `page=0`, `size=20` | page index is **0-based** (Panache `Page.of(index, size)`) |
| sort | none | optional fixed sort via `Sort.by("field")` |
| filter | None | PanacheQL filter params on entity fields (there is no Specification API in Quarkus) |
| totalCount | false | when true, return `X-Total-Count` header via `jakarta.ws.rs.core.Response` |

### Auto-detected (no questions)

| Option | Source |
|--------|--------|
| persistenceMode (sync / reactive) | build file dependencies (preflight) |
| patchStrategy | Jackson `ObjectMapper` (`com.fasterxml.jackson` on Quarkus 3.x; resolve from project dependencies, never hardcode) |
| idAccessor | entity file: public `id` field (Panache convention) or `getId()` |
| hasValidation / hasMapStruct / hasRestJackson | build file dependencies |
| resource naming & base path | existing `@Path` resources in the project |

**Smart defaults:** If the user says "use defaults", "all defaults", "default settings",
or similar -- skip ALL questions where a default is marked as recommended. Only ask mandatory
questions (entity when unknown, and any STOP conditions).

**Smart answer recognition:** When the user provides a value instead of choosing from a numbered
list, accept it directly. Examples:
- Question "Which entity?" --> user answers "Product" --> this IS the entity, don't re-ask
- Question "Repository?" --> user answers "ProductRepository" --> this IS the choice
- If the user provides multiple answers in one message --> accept all, skip answered questions
- NEVER ask a question that the user already answered (even implicitly)

**Batch questions:** When multiple questions must be asked (i.e. cannot be resolved by
principles 1–2 of the Decision-making principle), group them into a single structured-question
call (up to 4 questions per call) when they:
- Belong to the same logical section
- Don't depend on each other's answers

Rules:
- Maximum **3-4 questions** per structured-question call
- Mark the recommended option with `(Recommended)` and place it first
- Never batch questions from DIFFERENT decision branches
- The primary branching question (entity selection) is always asked ALONE
- Prefer the structured-question tool for choices; fall back to plain text lists only if unavailable

---

## Decision-making principle — context first, then ask

Before asking the user **any** question, attempt to derive the answer from the context already
gathered: the build file, existing resources, the entity and repository source files, the
conventions detected from existing code, prior turns of this conversation, and the user's
original prompt. Only ask when the context yields **no clear default** or when the choice is
genuinely user-specific (e.g. which entity, which repository).

Hierarchy of decisions:

1. **Context is unambiguous → decide silently, do NOT ask.**
   Examples: persistence mode from the build file; repository when there is exactly one for the
   entity; resource package from existing resources; basePath from existing endpoints; validation
   from `quarkus-hibernate-validator` presence; pagination params when the project already uses
   one style consistently; `idAccessor` from the entity file.

2. **Context gives a strong signal → state the decision + alternatives in one line, let the user override or stay silent.**
   Format:
   ```
   Will create `ProductResource` at `/api/products` with Page pagination, no DTO, no filter. OK?
   ```
   The user can answer "ok" / "yes" / silence → accept; or name an alternative → switch. This is
   **not** the same as the numbered question format — it is a single confirmation line.

3. **Context yields no clear default → ask with the structured-question tool (preferred), with the recommended option first.**
   When a structured-question tool is available, use it with the recommended option marked
   `(Recommended)` and placed first. If no interactive choice tool is available, fall back to a
   plain text list.
   **Never** ask iteratively ("which entity?" → user picks → "repository?" → …)
   when one batched call would do.

4. **Context is fully empty for a critical input → ask plainly.**
   This applies to: which entity (when not mentioned), the user's intent itself.

### How to ask

When a question must be asked, prefer the harness's **structured-question tool**
(`AskUserQuestion` / `ask_user_question` or its analogue) over writing a numbered list in the
response body. Fall back to plain text only if no interactive choice tool is available.

Rules for structured-question calls in this skill:

- Each call may contain up to **4 questions** that are independent of each other (the tool will
  render them together). Use this to batch related decisions in one round-trip.
- Each question has **2–4 options**. The tool auto-adds an "Other" choice for free-form input —
  never include it manually.
- Mark the recommended option by putting it **first** with `(Recommended)` appended to the label.
- `header` is a 12-char chip label (e.g. "Entity", "DTO mode", "Paths").
- Each option has a `description` explaining what the choice means.

When the structured-question tool is **not** the right tool:
- Free-form input where there is no enumerable set of options (e.g. arbitrary class name,
  arbitrary path) — ask in plain text.
- The "single confirmation line" form from principle 2 — that is a plain question with an obvious
  yes/no, not an enumerated choice.

The screen-driven question lists in Steps 2–4 below are a **fallback** for case 4. They are NOT a
script to execute top-to-bottom. If a question's answer is already determined by principles 1–3,
**skip the question**.

---

## Step 0 -- Conversation context first (REQUIRED, no tool calls)

Tell the user: `Step 0/6: Analyzing conversation context...`

Before any file read, before any question, **re-read the user's prompt and the prior turns of
this conversation** and extract whatever is already stated. This step costs nothing and prevents
the most common failure mode of this skill — asking the user something they already said.

Build a mental checklist of inputs and tick off everything the user has already provided,
explicitly or implicitly:

| Input | Look for in the prompt / context |
|---|---|
| **entity** | a class name (`Product`, `Order`, `Vet`); "for X"; an open file in the IDE; a file path; a recently discussed entity in this conversation |
| **repository** | "use `ProductRepository`", "with `OrderRepo`"; or implied — if only one repository exists for the entity |
| **DTO mode** | "with DTO", "without DTO", "use entity directly", "map to `ProductDto`" |
| **resource name** | "name it `ProductResource`", "class `FooResource`" |
| **paths** | "at `/api/products`", "base path `/api`", "resource path `/items`" |
| **pagination** | "with pagination", "no pagination", "page and size params" |
| **filter** | "with filter", "no filter", "filter by name" |
| **total count** | "with total count", "X-Total-Count", "without count" |
| **sort** | "sort by name", "no sorting" |
| **methods** | "all CRUD", "only read", "read-only", "without delete", "GET + CREATE", "full CRUD" |
| **smart defaults** | "use defaults", "all defaults", "default settings", "as usual" |
| **prior project facts** | persistence mode, dependencies, package layout — already known if discussed earlier in this conversation; do not re-detect |

For every input that is **explicitly or strongly implicitly answered**: mark it as decided and
skip the corresponding question in Steps 2–4. Do NOT ask "which entity?" if the user wrote
"create CRUD resource for Product" — `Product` is the answer. Do NOT ask "which repository?" if
there is exactly one repository for the entity.

For every input that is **not** answered: defer to the Decision-making principle above — try to
derive it from project context first (Step 1), and only then ask.

Step 0 is mental, not a tool call. Do not announce it to the user. Do not write "Step 0 done".
Just internalize what the user already said before proceeding to Step 1.

---

## Step 1 -- Gather minimal project context (automatic, no questions)

Tell the user: `Step 1/6: Gathering project context...`

Before this step, read [`references/context-gathering.md`](references/context-gathering.md). It
contains the lazy file-operation table and derived flags. Read only the files consumed by later
steps; defer entity, repository, DTO and mapper reads until their selection steps.

---

## Step 2 -- Select entity

Tell the user: `Step 2/6: Selecting entity...`

By Step 0 you should already know the entity if the user mentioned it.
Most common case: the user wrote "create CRUD resource for Product" → entity is `Product`, skip
the question, go straight to the read below.

**Lazy fallback — only when entity is unknown:** grep `@jakarta.persistence.Entity` across
`src/main/java` → list of entity classes, then ask with the structured-question tool (options =
entity names from the list, max 4; if more than 4 entities, use the 4 most likely candidates
based on context and add a note that the user can type a different name via "Other").

This is the only place the entity list should be fetched. If the user named the entity in their
prompt, do NOT scan for it.

After the entity FQN is known, read the entity source file and extract:
- `IdType` -- entity ID field type (e.g. `java.lang.Long`, `java.util.UUID`)
- `entityVar` -- decapitalized entity name (e.g. `product`)
- `entityVarPlural` -- pluralized decapitalized name (e.g. `products`)
- `EntityName` -- simple class name (e.g. `Product`)
- `EntityNamePlural` -- pluralized simple name (e.g. `Products`)
- `idAccessExpression` -- ID access inside a lambda whose parameter is named `entity`:
  `entity.id` when the entity extends `PanacheEntity`/`PanacheEntityBase` with a public `id` field
  (Panache convention, default), or `entity.getId()` when the ID is exposed through a getter
- Whether the entity has validation annotations (`jakarta.validation.constraints.*`) --> `entityHasValidation`
- Whether the entity extends `PanacheEntity`/`PanacheEntityBase` (Active Record available) or is a plain `@Entity`

---

## Step 3 -- Select repository

Tell the user: `Step 3/6: Selecting repository...`

By Step 0 you may already know the repository if the user mentioned it.

Grep `implements io.quarkus.hibernate.orm.panache.PanacheRepository` and
`PanacheRepositoryBase` across `src/main/java`, then read the `PanacheRepository<...>` /
`PanacheRepositoryBase<...>` type arguments to find repositories for this entity → `repos`.

Then apply the Decision-making principle:
- If exactly one repository exists → select it silently (principle 1).
- If the user named a specific repository → use it directly, skip the question.
- If multiple repositories exist → ask with the structured-question tool, options from `repos`.
- If no repository exists → ask whether to create one (WA11, `examples/_beans/repository/java.md`).
  Active Record CRUD (static finders on the entity, no repository) is a different pattern and is
  **not** generated by this skill — if the user wants that, STOP and tell them the skill covers the
  repository-based pattern only.

After selection:
- `repoFieldName` -- decapitalized repository class name (e.g. `productRepository`)
- `RepoFqn` -- FQN of the repository class
- `RepoName` -- simple repository class name (needed only when WA11 creates it)

---

## Step 4 -- DTO and customization questions

Tell the user: `Step 4/6: Resolving DTO and customization...`

Before this step, read [`references/customization-workflow.md`](references/customization-workflow.md).
Resolve DTO/mapper, path, pagination, filtering, sorting, total-count, and `selectedMethods` from
context first; ask only unresolved choices.

**Transaction placement:** if the project requires a service layer, STOP — no service-layer examples
exist here. **Validation:** add `@jakarta.validation.Valid` only when `hasValidation` is true and the
selected entity/DTO actually carries constraints.

---

## Step 5 -- Generate code

Tell the user: `Step 5/6: Generating code...`

Before generating, read [`references/generation-workflow.md`](references/generation-workflow.md) and
load each selected example immediately before writing it. The reference contains the WA work units,
method variants, substitutions, and edit order.

Guard rails for this step:
- Apply variable substitutions — **ONLY** variables declared in the Variables section.
- **FQN handling (CRITICAL):** examples contain FQNs. When writing the final file, you **MUST**
  replace shortened FQNs with short names, add sorted non-duplicate imports, skip same-package and
  `java.lang` imports, and retain ambiguous FQNs.

---

## Step 6 -- Dependencies & properties (automatic)

Tell the user: `Step 6/6: Applying dependencies and properties...`

1. Read [`examples/_dependencies/dependencies.md`](examples/_dependencies/dependencies.md)
2. For each artifact NOT in `presentDeps`:
   - Use `buildFile` from Step 1 (Maven or Gradle).
   - For `io.quarkus:*` or `io.quarkiverse.*` extensions, use the detected build tool's extension-add
     command when the example provides one, or edit the build file directly.
   - For ordinary dependencies such as `org.mapstruct:*` and annotation processors, edit the existing
     Maven/Gradle dependency or processor block; never pass them to a Quarkus extension command.
3. No properties are written for this skill (a CRUD resource has no `application.properties` entries)
4. If a shell is available, verify the project still compiles:
   Maven `./mvnw -q -DskipTests compile`, Gradle `./gradlew -q compileJava`.
   If compilation fails — fix the generated code before reporting.
5. Report: "Created resource {resourceName} with CRUD endpoints for {EntityName}. Added dependencies: [list]."

---

## Anti-hallucination checklist

Before writing ANY code, verify:
- [ ] The code comes from an examples/ file (cite which one)
- [ ] Only declared variables were substituted
- [ ] No framework API calls were added "from knowledge"
- [ ] Import list covers all FQNs shortened in the body (no missing imports, no extras)
- [ ] Method signatures match the example exactly
- [ ] No comments or convenience methods were added
- [ ] Panache API only: `findByIdOptional`, `list`/`listAll`/`find(...).page(Page.of(...)).list()`,
      `persistAndFlush`, `delete(entity)`/`deleteById(id)`/`delete("query", params)`, `count()` —
      no other repository method names
- [ ] Every write method (CREATE, PATCH, PATCH_MANY, DELETE, DELETE_MANY) carries
      `@jakarta.transaction.Transactional`
- [ ] Missing entities produce `jakarta.ws.rs.NotFoundException` (404), not 500
- [ ] `idAccessExpression` matches the entity's actual ID access (public `id` field vs getter)
- [ ] Jackson FQNs (`JsonNodeFqn`, `ObjectMapperFqn`, `JsonProcessingExceptionFqn`) were resolved from
      the project's dependencies — never hardcoded blindly
- [ ] The `ObjectMapper` bean is injectable in this project (see the marker in
      `examples/_beans/injection/java.md`); otherwise construct it in the resource instead
- [ ] `@jakarta.validation.Valid` is only added when `hasValidation = true` AND the parameter type has constraints
- [ ] The generated `@Path` does not conflict with an existing resource path (checked in Step 1)
- [ ] No reactive variant was generated (`Uni`) — the project uses synchronous Panache (or the user confirmed)
- [ ] No `javax.*` imports — Quarkus 3.x is `jakarta.*`
