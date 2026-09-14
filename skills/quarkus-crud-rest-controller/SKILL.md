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
   persistence mode this resource should use.
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

Read only the files whose content is **actually consumed** by a later step. Do not pre-read
"in case we need it" — every variable here must have a concrete downstream user.

| File operation | Variable | Used for |
|----------------|----------|----------|
| read `pom.xml` / `build.gradle(.kts)` | `presentDeps`, `buildFile`, `hasRestJackson`, `hasValidation`, `hasMapStruct` | feature gates, Step 6 dependency edits |
| glob `src/main/java/**/*.java`, then grep `@jakarta.ws.rs.Path` | `resources` (class name, class-level `@Path`, package) | Step 4 path-conflict detection, naming/basePath/package conventions |
| grep `@jakarta.ws.rs.Path` values in `resources` | `existingBasePaths` | basePath + resourcePath defaults |
| read `src/main/resources/application.properties` | `securityRules` | optional: if `/api` paths are protected or open (informational for the report) |

From the resource scan, derive `mainPackage` (package of existing resources, or the root package
of `src/main/java` sources).

For the full convention-scoring procedure (ID strategy, DTO style, mapper naming, transactional
placement), follow [`references/detect-conventions.md`](references/detect-conventions.md).

Determine the build-related flags:
- `hasRestJackson` — `io.quarkus:quarkus-rest-jackson` (or `quarkus-rest` + a JSON provider) in the build file.
- `hasValidation` — `io.quarkus:quarkus-hibernate-validator` in the build file.
- `hasMapStruct` — `io.quarkiverse.mapstruct:quarkus-mapstruct` and `org.mapstruct:mapstruct` in the build file.
- **Jackson package resolution:** check the build file for Jackson dependencies. `com.fasterxml.jackson.*` →
  `JsonNodeFqn = com.fasterxml.jackson.databind.JsonNode`, `ObjectMapperFqn = com.fasterxml.jackson.databind.ObjectMapper`,
  `JsonProcessingExceptionFqn = com.fasterxml.jackson.core.JsonProcessingException`.
  If the project carries a different Jackson major (`tools.jackson.*`), resolve the three FQNs to that package instead.
  **Never hardcode blindly — always resolve from the project's dependencies.**

That is the entire Step 1. **Do NOT** fetch:
- the entity list — needed only if the user did not name an entity in their prompt. Defer to Step 2 as a lazy fallback.
- repositories — depends on knowing the entity, which happens in Step 2. Defer to Step 3 as a lazy fallback.
- entity details — depends on knowing the entity. Defer to Step 2.
- DTOs / mappers — depend on knowing the entity AND the DTO decision. Defer to Step 4.

If the project is multi-module (more than one module with `pom.xml` / `build.gradle` and Quarkus
extensions): ask which module to use, then repeat this step scoped to that module.

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

By Step 0 you may already know the DTO mode if the user mentioned it (e.g. "with DTO", "without
DTO", "use entity directly", "map to ProductDto"). If so, skip the question and proceed.

If unknown, ask with the structured-question tool:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Use DTO for mapping? | DTO mode | Yes, use DTO (Recommended): select existing or create new via `quarkus-dto-creator` / No, use entity directly |

### If DTO selected:

Grep for DTO files (`record`/class names containing `{EntityName}Dto` or `{EntityName}RestDto`)
and mapper beans (`@org.mapstruct.Mapper` interfaces, or custom converter classes) related to the
entity.

**If existing DTO + mapper found:** ask the user to select them. Extract:
- `DtoFqn`, `dtoVar`, `dtoVarPlural`
- `MapperFqn` -- FQN of the mapper bean
- `mapperFieldName` -- decapitalized mapper class name
- `toDtoMethodName` -- mapper method entity-->DTO (default per quarkus-mapper-creator: `to${DtoShortName}`, e.g. `toOrderDto`)
- `toEntityMethodName` -- mapper method DTO-->entity (default: `toEntity`)
- `updateEntityMethodName` -- mapper method that copies a DTO into an existing entity (default per quarkus-mapper-creator: `partialUpdate`)

Warn: CREATE, PATCH and PATCH_MANY require the mapper to have `toEntity` and
`updateEntityMethodName` (the latter copying into an existing entity) methods in addition to `toDtoMethodName`.
quarkus-mapper-creator generates exactly this set with its defaults — keep the method names
consistent between the two skills.

**If no DTO exists for the entity:** delegate to the `quarkus-dto-creator` skill to create one.
That skill handles DTO generation and can hand off to `quarkus-mapper-creator` for the mapper
(conversion is inevitable for a REST resource). After both are created, return here and continue
with the path settings.

**If DTO exists but no mapper:** delegate to `quarkus-mapper-creator` to create one. After the
mapper is created, return here and continue.

### Path, pagination, filter & sort settings

Apply the **Decision-making principle**. These settings almost always have good defaults
derivable from context — use principle 2 (one-line confirmation) unless the user explicitly asked
for customization:

```text
Will create `{EntityName}Resource` in `{resourcePackage}` at `{basePath}/{entityVarPlural}`, page/size pagination, no filter, no total count. OK?
```

The user can answer "ok" / "yes" / silence → accept all defaults; or override specific values →
apply only those overrides.

Only fall back to individual questions when the user explicitly asked for fine-grained control
("custom paths", "configure pagination") or when context yields no clear defaults.

If the user selects a filter: ask for the filterable field(s). Extract `filterFieldName` and
`filterParamName` (default: the field name). Filters are **PanacheQL** fragments — there is no
Specification API in Quarkus; see [`references/panache-queries.md`](references/panache-queries.md).

If the user selects sorting: extract `sortFieldName` (default: the entity's first non-ID field,
confirmed by the user).

If the user selects total count: GET_LIST returns
`jakarta.ws.rs.core.Response` with an `X-Total-Count` header.

**Transaction placement:** if the project consistently routes writes through `@ApplicationScoped`
service beans, note that this skill generates writes directly on the resource with
`@jakarta.transaction.Transactional` (as in the examples). Ask the user whether to keep
resource-only writes; if they require a service layer, STOP — no service-layer examples exist here.

**Validation:** only generate `@jakarta.validation.Valid` when `hasValidation` is true AND the
annotated parameter's class (entity or DTO) actually carries constraints.

### Method selection

By Step 0 you may already know which methods the user wants (e.g. "read-only", "only GET and
CREATE", "full CRUD"). If so, skip the question.

If unknown, ask with the structured-question tool:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Which CRUD methods to generate? | Methods | Full CRUD (Recommended): GET_LIST, GET_ONE, GET_MANY, CREATE, PATCH, PATCH_MANY, DELETE, DELETE_MANY / Standard CRUD: GET_LIST, GET_ONE, CREATE, PATCH, DELETE / Read-only: GET_LIST, GET_ONE / Custom: select individual methods |

Store the selected method set as `selectedMethods`. Step 5.3 generates only these methods,
skipping the rest.

---

## Step 5 -- Generate code

Tell the user: `Step 5/6: Generating code...`

WA work units, in order. Load each example file right before writing its code.

| WA | Step | Output | Example file |
|----|------|--------|--------------|
| WA1 | 5.1 | resource class skeleton | [`examples/_skeletons/java.md`](examples/_skeletons/java.md) |
| WA2 | 5.2 | constructor injection | [`examples/_beans/injection/java.md`](examples/_beans/injection/java.md) |
| WA3 | 5.3 | GET_LIST | [`examples/_methods/get-list/java.md`](examples/_methods/get-list/java.md) |
| WA4 | 5.3 | GET_ONE | [`examples/_methods/get-one/java.md`](examples/_methods/get-one/java.md) |
| WA5 | 5.3 | GET_MANY | [`examples/_methods/get-many/java.md`](examples/_methods/get-many/java.md) |
| WA6 | 5.3 | CREATE | [`examples/_methods/create/java.md`](examples/_methods/create/java.md) |
| WA7 | 5.3 | PATCH | [`examples/_methods/patch/java.md`](examples/_methods/patch/java.md) |
| WA8 | 5.3 | PATCH_MANY | [`examples/_methods/patch-many/java.md`](examples/_methods/patch-many/java.md) |
| WA9 | 5.3 | DELETE | [`examples/_methods/delete/java.md`](examples/_methods/delete/java.md) |
| WA10 | 5.3 | DELETE_MANY | [`examples/_methods/delete-many/java.md`](examples/_methods/delete-many/java.md) |
| WA11 | 5.4 | repository creation (only when none exists and the user agrees) | [`examples/_beans/repository/java.md`](examples/_beans/repository/java.md) |

### 5.1 Create resource class (WA1)

Read `examples/_skeletons/java.md`.

Apply variable substitutions:
- `{packageName}` --> resourcePackage
- `{className}` --> resourceName
- `{requestPath}` --> basePath + resourcePath

Use the **Write** tool to create `src/main/java/{package-path}/{resourceName}.java`.

### 5.2 Add bean injection (WA2)

Read `examples/_beans/injection/java.md`.

Add a constructor parameter for the repository. If DTO with mapper: also inject the mapper bean.
If PATCH or PATCH_MANY is selected: also inject the Jackson `ObjectMapper` bean
(`${ObjectMapperFqn}` resolved in Step 1).

Use the **Edit** tool to modify the resource class.

### 5.3 Add CRUD methods (WA3–WA10)

For each method in `selectedMethods` (from Step 4 method selection):

1. Determine the example file path: `examples/_methods/{method-name}/java.md`

2. Read the example file

3. Select the correct code variant based on:
   - DTO mode (no DTO vs with DTO)
   - For GET_LIST: pagination (yes/no), filter (with/without), sort (with/without), total count (with/without)
   - For CREATE: with/without `@Valid`
   - For DELETE: default (returns the deleted entity/DTO) vs strict (204 No Content, 404 when missing)
   - For PATCH / PATCH_MANY: DTO vs no DTO (the patch strategy is Jackson `ObjectMapper` in both)

4. Apply variable substitutions (ONLY variables declared in the Variables section)

5. **FQN handling (CRITICAL):** examples contain FQNs (e.g. `jakarta.ws.rs.GET`,
   `io.quarkus.panache.common.Page`, entity/DTO/repository FQNs). When writing the final file, you MUST:
   1. Replace every FQN in the body with its **short name**
   2. Collect every FQN you shortened and emit a corresponding `import` line right after the
      `package` statement, sorted, no duplicates
   3. Classes from the same package as the resource must NOT be imported
   4. Types from `java.lang` must NOT be imported
   5. FQNs that cannot be shortened unambiguously (same simple name from different packages) keep the FQN form

6. Use the **Edit** tool to insert the method into the resource class body

### 5.4 Create repository if missing (WA11)

Only when Step 3 found no repository for the entity and the user agreed to create one:

Read `examples/_beans/repository/java.md`. Use the **Write** tool to create
`src/main/java/{package-path}/{RepoName}.java`.

---

## Step 6 -- Dependencies & properties (automatic)

Tell the user: `Step 6/6: Applying dependencies and properties...`

1. Read [`examples/_dependencies/dependencies.md`](examples/_dependencies/dependencies.md)
2. For each artifact NOT in `presentDeps`:
   - Use `buildFile` from Step 1 (Maven or Gradle)
   - Edit the build file to add the dependency (or use the Quarkus extension-add command listed in the example)
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
