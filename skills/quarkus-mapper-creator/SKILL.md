---
name: quarkus-mapper-creator
description: >
  Creates a mapper between a Panache entity and a DTO (MapStruct or custom converter).
  Use this skill when a mapper/converter between entity and DTO needs to be created,
  either standalone or as part of a larger task (e.g. after DTO creation, during CRUD setup).
  Russian phrases also trigger this: "создай маппер", "маппер для сущности", "конвертер между
  сущностью и DTO", "маппер entity DTO".
---

# Preflight — Project detection

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files before doing anything else:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
   Record it as `${buildFile}` / `${buildTool}` for Step 5.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`;
   Gradle: `io.quarkus` plugin + `quarkusPlatform` version. If the project is not a Quarkus
   application — stop and tell the user this skill targets Quarkus projects.
3. **MapStruct presence** — look for `io.quarkiverse.mapstruct:quarkus-mapstruct` and
   `org.mapstruct:mapstruct` in the dependency list, and for a `mapstruct-processor` entry in the
   `maven-compiler-plugin` `annotationProcessorPaths` (Maven) or an `annotationProcessor`
   configuration (Gradle). Record what is already present as `${presentDeps}`.
4. **Persistence mode** — `quarkus-hibernate-orm-panache` → sync Panache;
   `quarkus-hibernate-reactive-panache` → reactive Panache (`Uni`-returning). Both use the same
   entity style, so mapper code is identical; only the calling code differs.
5. **Entity accessor style** — Panache convention is `public` fields (direct field access:
   `entity.name`). If the project's entities instead declare `private` fields with getters/setters,
   the mapper bodies must use those accessors. Detect from the actual entity source in Step 2.

---

# Mapper Creator

Creates a mapper (MapStruct interface/abstract class or custom converter) for converting between
a Panache entity and a DTO.

---

> **CRITICAL: Code ONLY from examples/ files. If no matching example -- STOP and ask user.**
> **CRITICAL: For questions with a fixed set of choices, prefer your harness's structured-question tool (`AskUserQuestion` / `ask_user_question`) > its analogue > plain text list. Plain numbered text lists are the last resort when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 2–3 may already be answered by the user's prompt and prior turns. Re-asking what was already said is the #1 reason this skill feels slow.

---

## Defaults

| Option | Default | Always ask? | Notes |
|--------|---------|-------------|-------|
| entity | — | YES | which entity to map |
| dtoClass | — | YES | which DTO to map to |
| mapperType | MapStruct | YES | main choice: MapStruct or Custom |
| className | `${EntityName}Mapper` | NO | suggest, confirm |
| packageName | package next to DTO | NO | auto-determined |
| parentInterface | null | NO | extend a common mapper interface |
| componentModel | `cdi` | NO | MapStruct only; `cdi` is the Quarkus idiom — the generated mapper becomes an injectable bean |
| partialUpdate | no | NO | add partialUpdate method |
| partialUpdateNullStrategy | SET_TO_NULL | NO | if partialUpdate = yes: SET_TO_NULL / IGNORE / SET_TO_DEFAULT |
| updateWithNull | no | NO | add updateWithNull method |
| dtoIsRecord | auto-detected from DTO source | NO | `public record XDto(...)` → component accessors (`x()`), class → getters (`getX()`) |
| entityAccessors | auto-detected from entity source | NO | Panache public fields → direct field access; private fields → getters/setters |

**Smart defaults:** If the user says "use defaults", "all defaults", "default settings" -- skip all questions where "Always ask?" = NO. Ask only the required ones.

**Smart answer recognition:** When the user directly provides a value instead of choosing from a list -- accept it. Examples:
- Question "Which entity?" -> user answers "Order" -> that IS the entity
- Question "Mapper type?" -> user answers "mapstruct" -> that IS the choice
- If the user gave multiple answers in one message -> accept all, skip the answered questions
- NEVER re-ask what the user has already answered (even indirectly)

**Batch questions:** Group related questions into a single structured-question call (up to 4 questions):
- The main question (mapper type) is always asked SEPARATELY
- Do not group questions from DIFFERENT decision branches
- Prefer the structured-question tool; fall back to plain text only if it is unavailable

---

## Step 0 -- Conversation context first (REQUIRED, no tool calls)

Before any file read, before any question, **re-read the user's prompt and
the prior turns of this conversation** and extract whatever is already
stated. This step costs nothing and prevents the most common failure mode
of this skill — asking the user something they already said.

Build a mental checklist of inputs and tick off everything the user has
already provided, explicitly or implicitly:

| Input | Look for in the prompt / context |
|---|---|
| **entity** | a class name (`Order`, `Visit`, `ScheduleTemplate`); "for X"; "from X to Y"; a recently discussed entity |
| **DTO** | a class name ending in `Dto` / `Response` / `Request`; "to `OrderDto`"; "from X to Y"; a DTO that was just generated by `quarkus-dto-creator` in this same conversation |
| **mapperType** | "MapStruct", "mapstruct", "@Mapper", "custom", "manually", "static methods" → MapStruct vs Custom |
| **className** | "name it `OrderConverter`", "class `FooMapper`" |
| **package** | "in package `…`", "next to DTO", "next to resource" |
| **methods** | "only toDto", "with update", "partial update", "updateWithNull" |
| **smart defaults** | "use defaults", "all defaults", "default settings", "as usual" |
| **prior project facts** | build tool, Quarkus version, dependencies — already known if discussed earlier in this conversation; do not re-fetch |
| **delegated invocation** | if `quarkus-dto-creator` just delegated to this skill, the entity, DTO, package, and accessor style are ALL known — never re-ask |

For every input that is **explicitly or strongly implicitly answered**:
mark it as decided and skip the corresponding question in Steps 2–3. Do
NOT ask "which entity?" if the user wrote "create a mapper for Order
to OrderDto" — both entity and DTO are answered. Do NOT ask "MapStruct
or Custom?" if the user wrote "create a MapStruct mapper".

For every input that is **not** answered: defer to the Decision-making
principle below — try to derive it from project context first (Step 1),
and only then ask.

Step 0 is mental, not a tool call. Do not announce it to the user. Do not
write "Step 0 done". Just internalize what the user already said before
proceeding to Step 1.

---

## Decision-making principle — context first, then ask

Before asking the user **any** question, attempt to derive the answer from
the context already gathered: the build file, the entity and DTO sources,
existing mapper files in the package (grep for `@Mapper`), prior turns of
this conversation, and the user's original prompt. Only ask when the
context yields **no clear default** or when the choice is genuinely
user-specific (e.g. which entity, which DTO).

Hierarchy of decisions:

1. **Context is unambiguous → decide silently, do NOT ask.**
   Examples: MapStruct presence from `${presentDeps}`; mapper package from the
   DTO's package; className from `${EntityName}Mapper`; componentModel from
   Step 1 (`cdi` for Quarkus); accessor style from the entity source;
   mapperType when the user said "MapStruct" or "Custom" outright.

2. **Context gives a strong signal → state the decision + alternatives in one line, let the user override or stay silent.**
   Format:
   ```
   Will create `OrderMapper` (MapStruct, componentModel=cdi, in the same package as `OrderDto`).
   Alternatives: Custom mapper. OK?
   ```
   The user can answer "ok" / "yes" / silence → accept; or name an
   alternative → switch.

3. **Context yields no clear default → ask with the structured-question tool (preferred) or its analogue, with the recommended option first and `(Recommended)` appended.** Fall back to plain text if no interactive tool is available.

4. **Context is fully empty for a critical input → ask plainly.**
   This applies to: which entity, which DTO (when neither was mentioned),
   the user's intent itself.

### How to ask — prefer the structured-question tool

When a question must be asked, prefer the **structured-question tool** (or
its analogue) over writing a numbered list in the response body. Fall back
to plain text only if no interactive choice tool is available.

Rules for structured-question calls in this skill:

- Each call may contain up to **4 questions** that are independent of each
  other (the tool will render them together). Use this to batch related
  decisions in one round-trip.
- Each question has **2–4 options**. The tool auto-adds an "Other" choice
  for free-form input — never include it manually.
- Mark the recommended option by putting it **first** with `(Recommended)`
  appended to the label.
- `header` is a 12-char chip label (e.g. "Mapper", "Methods", "Package").
- Each option has a `description` explaining what the choice means.

When the structured-question tool is **not** the right tool:
- Free-form input where there is no enumerable set of options
  (e.g. arbitrary class name) — ask in plain text.
- The "single confirmation line" form from principle 2 — that is a plain
  yes/no, not an enumerated choice.

The screen-driven question lists in Steps 2–3 below are a **fallback** for
case 4. They are NOT a script to execute top-to-bottom. If a question's
answer is already determined by principles 1–3, **skip the question**.

---

## Step 1 -- Gather minimal project context (automatic, no questions)

Tell the user: `Step 1/5: Gathering project context...`

Read only the sources whose result is **actually consumed** by a later
step. Do not pre-fetch "in case we need it" — every variable here must
have a concrete downstream user.

| Source | What to extract | Variable | Used for |
|--------|----------------|----------|----------|
| `${buildFile}` (from preflight) | build tool, Quarkus version, dependency list | `${buildTool}`, `${presentDeps}` | Step 5 (is MapStruct already present? is the processor configured?), componentModel decision |

That is the entire Step 1. **Do NOT** fetch:
- Quarkus platform version beyond what the build file states — no branching depends on it
- `application.properties` — Step 5 writes nothing to properties
- `${mainPackage}` — Step 4 derives the mapper package from the DTO's package,
  not from the project root
- entity fields, entity accessor style, DTO members — these depend on knowing the entity
  and DTO, which happens in Step 2. Defer them to Step 2.
- existing sibling mappers — needed only at Step 13 of
  [`references/mapstruct-java.md`](references/mapstruct-java.md)
  (`uses = {...}` resolution) and only per **association entity**, which is
  unknown until the entity source is read. Defer to Step 13, do NOT
  pre-fetch in Step 1.

### componentModel — simplified

Determine `componentModel` from the project shape:
- Quarkus application (always, in this skill) → `cdi`. The generated mapper is a
  CDI bean, injectable via constructor injection or `@Inject`.
- Only when the user explicitly asks for plain MapStruct without CDI → `DEFAULT`
  (then the `MAPPER` factory field fragment is required).
- Never use the Spring component model in a Quarkus project.

---

## Step 2 -- Entity and DTO

Tell the user: `Step 2/5: Reading entity and DTO...`

By Step 0 you should already know entity and DTO if the user mentioned
them. Most common cases:

- **User wrote "create a mapper for Order to OrderDto"** → both known, skip
  the questions, go straight to the file reads below.
- **`quarkus-dto-creator` just delegated** → entity and DTO are passed in by
  the delegating skill. Never ask, never re-derive.
- **User wrote "create a mapper for Order"** → entity is `Order`. The DTO
  is the most recently created/discussed DTO for that entity in this
  conversation, OR — if there are multiple candidates — grep for
  `class` / `record` declarations ending in `Dto` for that entity and pick
  the unique one. Only ask if there are multiple and no other signal.

Ask only when context is genuinely empty. When asking, prefer plain text
(entity/DTO names are free-form input — the structured-question tool is the
wrong tool here):

```text
Which entity should I create a mapper for? And which DTO to map to?
```

After both entity file path and DTO file path are known, read both sources
(in parallel) and extract:

| Source | What to extract | Variable | Used for |
|--------|----------------|----------|----------|
| entity source file | fields (names, types, visibility), associations (`@ManyToOne`, `@OneToMany`, `mappedBy`), id field origin (`PanacheEntity` vs declared), active-record finders, **field visibility** (public Panache style vs private + accessors) | `${entityDetails}`, `${entityAccessors}` | Step 4 — building `@Mapping` annotations, detecting non-owner associations with `mappedBy` for `@AfterMapping`, selecting direct-field vs accessor bodies for Custom mappers |
| DTO source file | fields (name, type), declaration form (`public record XDto(...)` vs class), validation annotations | `${dtoFields}`, `${dtoIsRecord}` | Step 4 — comparing DTO fields against entity fields to decide which `@Mapping(source, target)` lines are needed |

Both reads are deferred to Step 2 because they require Step 2's inputs.
They are NOT part of Step 1.

---

## Step 3 -- Mapper type and variant settings

Tell the user: `Step 3/5: Mapper type and methods...`

### Mapper type — context first

Apply the **Decision-making principle**. Decide silently when context is
clear:

| Context signal | Decision |
|---|---|
| User said "MapStruct" / "@Mapper" | MapStruct, no question |
| User said "Custom" / "manually" / "static methods" | Custom, no question |
| MapStruct already in `${presentDeps}` AND user gave no signal | MapStruct (silent or one-line confirmation per principle 2) |
| MapStruct NOT in `${presentDeps}` AND project is small/simple | MapStruct is still a fine default — Step 5 will add the dependency. State this in the one-line confirmation: "Will create a MapStruct mapper. Will add the quarkus-mapstruct extension and the annotation processor to the build file. Alternative: Custom with no dependencies. OK?" |
| User says "use defaults" | MapStruct |

Only fall back to the structured-question tool when **none** of the rows
above matches. Use it with these options:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| What mapper type for `${Entity}` ↔ `${Dto}`? | Mapper | MapStruct (Recommended): interface with @Mapper/@Mapping / Custom: CDI bean with hand-written methods |

### Variant settings — defaults are usually correct

For both MapStruct and Custom variants the defaults are almost always
correct:
- `className` = `${EntityName}Mapper`
- `packageName` = same package as the DTO
- `partialUpdate` = no
- `updateWithNull` = no

Do NOT batch-ask these settings unless the user explicitly requested
configuration ("configure methods", "I want partial update") or said something
that contradicts a default.

When the user did ask for configuration, use a single structured-question
call (multiSelect: true) with the relevant subset:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Which methods to add to the mapper? | Methods | toDto + toEntity (Recommended): basic bidirectional conversion / + partialUpdate: update entity from DTO / + updateWithNull: partialUpdate with null overwrite |

Class name and package are free-form — ask in plain text only when the
user said "I want a different name" or "in a different package".

---

## Step 4 -- Generate code

Tell the user: `Step 4/5: Generating mapper...`

Determine the reference file based on mapper type:
- MapStruct + Java -> read [`references/mapstruct-java.md`](references/mapstruct-java.md)
- Custom + Java -> read [`references/custom-java.md`](references/custom-java.md)

Read the corresponding reference file and follow its Generation order exactly.

### Building @Mapping annotations

Read [`references/mapping-annotations.md`](references/mapping-annotations.md) for rules on how to
build `@Mapping` annotations.

Compare entity fields from `${entityDetails}` with DTO fields from `${dtoFields}`:
1. Match DTO fields to entity fields by name
2. For fields with different names, add `@Mapping(source, target)`
3. For association ID fields (e.g. `customerId` -> `customer.id`), add appropriate mapping
4. For flat fields (e.g. `customerName` -> `customer.name`), add expression or source.target mapping

### Reading skeleton and fragments

1. Read the skeleton file from `examples/_skeletons/{variant}-java.md`
2. Apply variable substitutions
3. Write the file to `src/main/java/${packagePath}/${className}.java`
4. For each fragment in the generation order:
   - Check if the fragment's condition is met
   - Read the fragment from `examples/_fragments/${fragment-name}/java.md`
   - Apply variable substitutions
   - Insert/edit into the created file

### Variable substitution rules
- `${packageName}` -> from Step 1 context or user answer
- `${className}` -> from user answer or default `${EntityName}Mapper`
- `${entityClassFqn}` -> entity FQN from context
- `${dtoClassFqn}` -> DTO FQN from context
- `${entityParamName}` -> decapitalized entity short name
- `${dtoParamName}` -> decapitalized DTO short name
- `${methodName}` -> from naming conventions (see [`references/method-naming.md`](references/method-naming.md))
- **NEVER substitute anything not listed in the Variables section of the example file**
- **NEVER add imports, methods, or code not in the example**
- **FQN handling (CRITICAL):** examples contain FQNs (e.g. `org.mapstruct.Mapper`,
  `org.mapstruct.Mapping`, `org.mapstruct.ReportingPolicy`,
  `org.mapstruct.MappingConstants.ComponentModel.CDI`, entity/DTO FQNs). When
  writing the final file, you MUST:
  1. Replace every FQN in the body with its **short name**
     (e.g. `@org.mapstruct.Mapper(...)` -> `@Mapper(...)`,
     `org.mapstruct.ReportingPolicy.IGNORE` -> `ReportingPolicy.IGNORE`,
     `${entityClassFqn}` -> entity short name, `${dtoClassFqn}` -> DTO short name).
  2. Collect every FQN you shortened and emit a corresponding `import` line
     right after the `package` statement, sorted, no duplicates.
  3. Classes from the same package as the mapper (entity, DTO if collocated)
     must NOT be imported — just use the short name.
  4. Types from `java.lang` must NOT be imported.
  5. The IDE will NOT optimize imports for you — the file is saved as-is.

### Entity accessors — Panache convention (CRITICAL)

Panache entities declare **public fields**; there are no getters/setters.
In custom mapper bodies and helper methods use **direct field access**:
- read: `pet.name`, `pet.type.id` (not `pet.getName()`, not `pet.getType().getId()`)
- write: `pet.name = ...` (not `pet.setName(...)`)
- flat collections: `.map(specialty -> specialty.id)` (there is no `getId()` to point a method reference at)

Exception: if the entity source declares `private` fields with getters/setters
(classic JPA style), use those accessors instead. Decide once from the entity
source in Step 2 (${entityAccessors}) and stay consistent.

DTO accessors depend on the DTO declaration form:
- `public record OrderDto(String name, ...)` → component accessors: `orderDto.name()`
- regular class → getters: `orderDto.getName()`

### Reactive projects

If the project uses `quarkus-hibernate-reactive-panache`, the entity style and
the mapper code are identical — mapping is synchronous. Call the mapper inside
the reactive chain (`.map(mapper::toDto)`); never block on it.

---

## Step 5 -- Add MapStruct dependencies (automatic, MapStruct variant only)

Tell the user: `Step 5/5: Updating build file...`

For Custom mapper: skip this step entirely. Custom mappers have no
external dependencies.

For MapStruct: check `${presentDeps}` and add missing pieces to the
project's build file.

### Required artifacts

| Artifact ID | Group ID | Role |
|-------------|----------|------|
| `quarkus-mapstruct` | `io.quarkiverse.mapstruct` | Quarkiverse extension: native-image reflection registration + dev-mode recompilation of mappers |
| `mapstruct` | `org.mapstruct` | MapStruct annotations API (implementation scope) |
| `mapstruct-processor` | `org.mapstruct` | annotation processor that generates the mapper implementation |

### Maven: the annotation processor MUST be configured explicitly

The `quarkus-mapstruct` extension only reads `@Mapper`/`@MapperConfig` annotations
(native registration, dev-mode recompilation) — it does **not** run the MapStruct
processor. Add it to `maven-compiler-plugin`:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <annotationProcessorPaths>
            <path>
                <groupId>org.mapstruct</groupId>
                <artifactId>mapstruct-processor</artifactId>
                <version>${mapstruct.version}</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

If the project already configures `annotationProcessorPaths`, insert the
`<path>` entry into the existing list — do not replace other processors
(Lombok, Quarkus `quarkus-extension-processor`, etc. must survive).

### Gradle

Inside the existing `dependencies { … }` block:

```groovy
implementation("org.mapstruct:mapstruct:${mapstructVersion}")
annotationProcessor("org.mapstruct:mapstruct-processor:${mapstructVersion}")
implementation("io.quarkiverse.mapstruct:quarkus-mapstruct:${quarkusMapstructVersion}")
```

(Groovy DSL: single quotes / `implementation 'org.mapstruct:mapstruct:…'`.)

### Versions

Do NOT hardcode blindly. In order:
1. Reuse versions already present in the project (build file, parent POM,
   `gradle/libs.versions.toml` version catalogue) — MapStruct and its processor
   must share one version.
2. If absent: `org.mapstruct:mapstruct` — a current stable line is `1.6.x`
   (e.g. `1.6.3`), keep `mapstruct` and `mapstruct-processor` in lockstep.
3. `io.quarkiverse.mapstruct:quarkus-mapstruct` is a Quarkiverse extension, NOT
   managed by the Quarkus platform BOM — its version must be declared. Check
   https://quarkus.io/extensions/io.quarkiverse.mapstruct/quarkus-mapstruct/
   for the current version (1.1.0 at the time of writing) and prefer whatever
   the project already uses.

Use the project's edit tool with `${buildFile}` as the target path. Make the
edit minimally — insert new entries into the existing blocks, do not rewrite
the file.

### No properties needed

Mapper creation does not write any `application.properties` entries.

Report: "Created mapper ${className} in package ${packageName}. Type: ${mapperType}. Methods: ${list of methods}."

---

## Anti-hallucination checklist

Before writing ANY code, verify:
- [ ] The code comes from an examples/ file (cite which one)
- [ ] Only declared variables were substituted
- [ ] No framework API calls were added "from knowledge"
- [ ] Import list matches the example exactly
- [ ] Method signatures match the example exactly
- [ ] No comments or convenience methods were added
- [ ] FQNs from examples are shortened in the body AND corresponding `import` lines were added after `package` (the IDE will NOT do this for you)
- [ ] `@Mapping` annotations match entity-DTO field comparison, not guessed
- [ ] Entity accessors follow the detected style — direct public-field access for Panache entities, getters/setters only for private-field entities
- [ ] DTO accessors follow the declaration form — `x()` for records, `getX()` for classes
- [ ] componentModel is `cdi` (or `DEFAULT` + factory field when the user asked for plain MapStruct) — never the Spring model
- [ ] `@AfterMapping` only added when the entity has non-owner associations with `mappedBy` + sub-DTO
- [ ] toDto uses individual `@Mapping(source, target)` pairs by default — `@InheritInverseConfiguration` only in the documented multi-flat-ToOne case or when the user explicitly asked for it
- [ ] Flat collection helper is generated only in `toDto` direction; `toEntity` does NOT try to load entities by id (no repository or EntityManager injection into the mapper)
- [ ] Flat collection helper name follows `${assocFieldName}To${capitalize(flatDtoFieldName)}` (e.g. `petsToPetIds`, not `petsToIds`)
- [ ] If MapStruct is new to the project, BOTH the `mapstruct` dependency AND the `mapstruct-processor` build configuration were added — the extension alone does not run the processor