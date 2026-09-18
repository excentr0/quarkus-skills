---
name: quarkus-dto-creator
description: >
  Creates a DTO (Data Transfer Object) for a Quarkus entity: Java record or plain class,
  with selected attributes, inherited validation, and nested sub-DTOs.
  Use this skill when a DTO needs to be created, either standalone or as part of a larger
  task (REST resource, service layer, replacing entity usage with a DTO).
  Triggers on: "create DTO", "add DTO", "make a DTO for Order", "DTO for entity",
  "response object for", "request body type for", "record for entity".
  Russian phrases also trigger this: "создай DTO", "сделай DTO", "добавь DTO",
  "DTO для сущности", "сделай record для".
---

# DTO Creator

Creates a DTO (Java record or plain class) for an entity with selected attributes, constructors,
getters/setters, equals/hashCode, toString, and optional features.

---

> **CRITICAL: Code ONLY from examples/ files. If no matching example — STOP and ask the user.**
> **CRITICAL: For questions with a fixed set of choices, use your harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`) — its analogue if the exact name differs — and fall back to a numbered text list only when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 2–7 may already be answered by the user's prompt and prior turns. Re-asking what was already said is the #1 reason this skill feels slow.
> **Step 7 (mapper) is automatic when conversion is needed.** If it is clear from context that the DTO will be used in code that converts entities to/from DTOs (resource, service, replacing an entity in a response), the skill MUST delegate to `quarkus-mapper-creator` — never write manual mapping code inline. The `quarkus-mapper-creator` skill decides the implementation (MapStruct, custom converter, adding dependencies) — this skill just delegates.

---

## Preflight — Project detection (before Step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP server or IDE
integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`; Gradle: the
   `io.quarkus` plugin. If absent — stop and tell the user this skill targets Quarkus projects.
3. **Extensions** — dependencies starting with `io.quarkus:` (and Quarkiverse `io.quarkiverse.*`).

Derived flags (used all over this skill):

| Flag | True when the build contains |
|---|---|
| `hasJackson` | `quarkus-rest-jackson` (or `quarkus-resteasy-jackson`) |
| `hasValidation` | `quarkus-hibernate-validator` |
| `hasMapStruct` | `io.quarkiverse.mapstruct:quarkus-mapstruct` |
| `persistenceMode` | `quarkus-hibernate-orm-panache` → sync; `quarkus-hibernate-reactive-panache` → reactive; neither → none |

---

## Defaults

| Option | Default | Always ask? | Notes |
|--------|---------|-------------|-------|
| entity | — | YES | main branching: which entity to create the DTO for |
| attributes | all entity fields | YES | which fields to include |
| className | `${EntityName}Dto` | NO | suggest, confirm only |
| variant | `java-record` | YES | Java record / plain class (Lombok → see [`references/lombok-note.md`](references/lombok-note.md)) |
| mutable | false | NO | skip unless the user wants customization |
| allArgsConstructor | true | NO | plain class only |
| equalsHashCode | true | NO | plain class only |
| toString | true | NO | plain class only |
| fluentSetters | false | NO | only when mutable=true |
| jsonIgnoreUnknownProperties | false | NO | when `hasJackson` |
| serializableType | none | NO | rarely needed |
| packageName | detected DTO package, else `${rootPackage}.dto` | NO | auto-detected |
| subDtoType (per ToOne association) | FLAT with id-only sub | YES | Four options: New Class / New Nested Class / Existing Class / Flat. "Only ID" does NOT exist as a separate option — it is Flat with only the sub-entity `id` checked. See [`references/sub-dto.md`](references/sub-dto.md). |
| subDtoType (per ToMany / collection) | NEW_NESTED_CLASS | YES | same 4 options as ToOne. Flat IS supported for collections and produces composite plural fields like `List<Long> itemIds` — see [`references/sub-dto.md`](references/sub-dto.md). |
| fieldNameOverride (per field) | none | NO | per-field rename |
| extraValidations (per field) | none | NO | user-added constraints on top of inherited ones |
| removedValidations (per field) | none | NO | constraints inherited from the entity that the user wants dropped |
| indent | from `.editorconfig` (fallback 4-space) | NO | see § Indentation below |

**Smart defaults:** if the user says "use defaults", "all defaults", "default settings" or similar —
skip ALL questions where "Always ask?" = NO. Only ask mandatory questions.

**Smart answer recognition:** when the user provides a value instead of choosing from a numbered list,
accept it directly:
- Question "Which entity?" → user answers "Order" → this IS the entity, don't re-ask
- Question "Variant?" → user answers "record" → this IS the Java record, don't show options
- If the user provides multiple answers in one message → accept all, skip answered questions
- NEVER ask a question the user already answered (even implicitly)

**Batch questions:** group closely related questions into a single structured-question call (up to 4
questions per call) when they:
- belong to the same logical section (e.g. both are plain-class method settings);
- do not depend on each other's answers;
- have obvious defaults the user can skip.

Rules:
- Maximum **3–4 questions** per call
- Mark the recommended option with `(Recommended)` and place it first
- Never batch questions from DIFFERENT decision branches
- The primary branching questions (entity selection, variant) are always asked ALONE
- Prefer the structured-question tool for choices; fall back to plain text lists only if unavailable

---

## Decision-making principle — context first, then ask

Before asking the user **any** question, attempt to derive the answer from the context already
gathered: build-file extensions, existing DTOs in the project, the entity source, prior turns of this
conversation, and the user's original prompt. Only ask when the context yields **no clear default** or
when the choice is genuinely user-specific (e.g. which entity, which fields).

Hierarchy of decisions:

1. **Context is unambiguous → decide silently, do NOT ask.**
   Examples: variant from the project's existing DTO style (records vs classes); `hasJackson` /
   `hasValidation` from the build file; package from the detected DTO package; className from
   `${Entity}Dto`; back-reference `@ManyToOne` filtering; auto-selection of sub-entity scalars;
   record vs plain class when the user asked for neither mutability nor setters.
   **Exception: subDtoType is NEVER decided silently** — it always requires at minimum principle 2
   (one-line confirmation), unless the USER explicitly stated the shape in their own message.

2. **Context gives a strong signal → state the decision + alternatives in one line, let the user override or stay silent.**
   Format:
   ```
   Will create `OrderDto` as a Java record with a nested `OrderItemDto` (record).
   Alternatives: plain class, separate file for OrderItemDto. OK?
   ```
   The user can answer "ok" / "yes" / silence → accept; or name an alternative → switch. This is
   **not** the same as the numbered question format — it is a single confirmation line.

3. **Context yields no clear default → ask with the structured-question tool, recommended option first.**
   Mark the recommended option with `(Recommended)` in its label and place it first. If the tool
   supports preview/code-shape options, show the concrete code shape for each option. If no interactive
   choice tool is available, fall back to a plain text list.
   **Never** ask iteratively ("which variant?" → user picks → "which fields?" → …) when one batched call
   would do.

4. **Context is fully empty for a critical input → ask plainly.**
   This applies to: which entity, which fields (when not "all"), the user's intent itself.

### How to ask — prefer the structured-question tool

When a question must be asked, prefer your harness's structured-question tool (e.g. `AskUserQuestion` /
`ask_user_question`) over writing a numbered list in the response body. Fall back to plain text only if
no interactive choice tool is available.

Rules for structured-question calls in this skill:

- Each call may contain up to **4 questions** that are independent of each other. Use this to batch
  related decisions in one round-trip.
- Each question has **2–4 options**. The tool auto-adds an "Other" choice for free-form input — never
  include it manually.
- Mark the recommended option by putting it **first** with `(Recommended)` appended to the label.
- Use `multiSelect: true` for "which fields to include" or "which validators to add" — anything where
  multiple answers are valid.
- `header` is a short chip label (e.g. "Variant", "Sub-DTO", "Fields").
- Each option has a `description` explaining what the choice means or its consequence (one short
  sentence).

When the structured-question tool is **not** the right instrument:
- free-form input where there is no enumerable set of options (e.g. an arbitrary class name, an
  arbitrary field rename) — ask in plain text;
- the "single confirmation line" form from principle 2 — a plain question with an obvious
  accept/override answer, not an enumerated choice.

The question lists in Steps 2–5 below are a **fallback** for case 4. They are NOT a script to execute
top-to-bottom. If a question's answer is already determined by principles 1–3, **skip the question**.
Generation correctness is the goal — not UI fidelity.

---

## Step 0 — Conversation context first (REQUIRED, no tool calls)

Tell the user: `Step 0/7: Reading conversation context...`

Before any file read, before any question, **re-read the user's prompt and the prior turns of this
conversation** and extract whatever is already stated. This step costs nothing and prevents the most
common failure mode of this skill — asking the user something they already said.

Build a mental checklist of inputs and tick off everything the user has already provided, explicitly
or implicitly:

| Input | Look for in the prompt / context |
|---|---|
| **entity** | a class name (`Order`, `Customer`, `ScheduleTemplate`); "for X"; an open file; a file path; a recently discussed entity in this conversation |
| **purpose** | "for REST", "for API", "for mapping", "projection", "for service" — drives field selection and the mapper question |
| **fields** | "all fields", "only id and name", "without password", "with associations", "flat" |
| **variant** | "record", "plain class", "immutable", "with setters" |
| **mapper** | "and mapper", "with mapper", "only DTO", "no mapper" |
| **className** | "name it `OrderSummaryDto`", "class `Foo`" |
| **package** | "in package `…`", "next to the resource" |
| **smart defaults** | "use defaults", "all defaults", "default settings", "as usual" |
| **sub-DTO shape** | "nested", "separate class", "only id", "flat" |
| **prior project facts** | extensions, persistence mode, DTO style — already known if discussed earlier in this conversation; do not re-fetch |

For every input that is **explicitly or strongly implicitly answered**: mark it as decided and skip the
corresponding question in Steps 2–7. Do NOT ask "what entity?" if the user wrote "create DTO for
Order" — `Order` is the answer. Do NOT ask "record or class?" if the user wrote "make a record for
Order" — record is the answer.

**Only the user's own messages count as user intent.** Assumptions written by the calling agent (task
descriptions, plans, argument blocks) are not user statements — do not treat them as answers the user
gave. In particular, do NOT skip asking about sub-DTO shape just because a plan describes one.

Step 0 is mental, not a tool call. Do not announce its details to the user beyond the progress line.

---

## Step 1 — Gather minimal project context (automatic, no questions)

Tell the user: `Step 1/7: Detecting project context...`

Read only the files whose result is **actually consumed** by a later step. Do not pre-fetch "in case we
need it" — every variable here must have a concrete downstream user.

| Source | Variable | Used for |
|--------|----------|----------|
| `pom.xml` / `build.gradle(.kts)` | `presentExtensions` | derived flags: `hasJackson`, `hasValidation`, `hasMapStruct`, `persistenceMode` |
| glob + grep in `src/main/java` for `*Dto.java`, `*Request.java`, `*Response.java`, `record *Dto`, `class *Dto` | `dtoPackage`, `existingDtoStyle`, existing names | package convention, default variant (records vs classes), name-collision list |

That is the entire Step 1. **Do NOT** fetch:
- Quarkus version — no branching depends on it; Quarkus 3.x requires Java 17+, so records are available
- `application.properties` — DTO generation writes nothing to configuration
- Flyway/Liquibase migrations — DTOs do not touch the schema
- Entity details — deferred to Step 2 (depends on knowing the entity)
- Test sources — irrelevant for DTO creation

**Derived defaults:**
- `dtoPackage` = the package where existing DTOs live. If no DTO exists yet →
  `${rootPackage}.dto`, where `${rootPackage}` is the root package of the project (e.g. `org.acme`).
  State the chosen package in the one-line confirmation from principle 2.
- `defaultVariant` = `java-record`, unless the project's existing DTOs are plain classes (then the
  project convention wins) or the user requested mutability.

---

## Step 2 — Entity selection

Tell the user: `Step 2/7: Selecting entity...`

By Step 0 you should already know the entity if the user mentioned it. Most common case: the user wrote
"create DTO for `Order`" → entity is `Order`, skip the question.

**Lazy fallback — only when the entity is unknown:** grep `@Entity` (or `PanacheEntity`) across
`src/main/java`, list the candidates, and ask via the structured-question tool (options = entity names,
max 4; if more than 4 entities, use the 4 most likely candidates based on context and note that the
user can type a different name via "Other"). If the user named the entity in their prompt, do NOT
search for candidates.

After the entity FQN is known, resolve its source file (glob/grep the class name under `src/main/java`)
and read it. Extract:

| What | Where it comes from |
|---|---|
| attribute names & types | fields (Panache style: `public` fields) — or getters when the entity uses private fields |
| `id` | **`PanacheEntity` provides `public Long id` implicitly — it is not declared in the source.** Read `@Id` explicitly for `PanacheEntityBase` / plain `@Entity` classes (type may be `Long`, `UUID`, …) |
| associations | `@ManyToOne` / `@OneToOne` / `@OneToMany` / `@ManyToMany` (jakarta.persistence) on fields or getters |
| inherited validation | `jakarta.validation.constraints.*` (and `org.hibernate.validator.constraints.*`) on the entity fields |
| collection element types | generic parameter of `List<X>` / `Set<X>`; Panache collections are often initialized `= new ArrayList<>()` |

Do not invent attributes: every field in the DTO must trace to an attribute you actually read in the
entity source. Back-reference filtering happens in Step 3 / [`references/sub-dto.md`](references/sub-dto.md).

---

## Step 3 — Attribute selection

Tell the user: `Step 3/7: Selecting attributes...`

**Default: include every scalar attribute and every association** (with the sub-DTO defaults from
[`references/sub-dto.md`](references/sub-dto.md)). Ask only when context signals that the user wants something narrower.

### Decide from context (preferred over asking)

Use the **purpose** captured in Step 0 to pick a sensible default set:

| Purpose signal | Default field set |
|---|---|
| "for REST", "for API", "for response" | all scalars + all associations expanded (NEW_NESTED_CLASS for ToMany, FLAT id for ToOne) — the response shape, including related data |
| "projection", "summary", "list view", "for list" | scalars only, ToOne associations as Flat id, ToMany excluded |
| "for mapping", "for service", "for storage" | all scalars + all associations expanded |
| "only id and name" / explicit field list | exactly what the user named, nothing else |
| no purpose signal | all scalars + all associations expanded (richest reasonable default) |

If the chosen default matches the user's apparent intent, **do not ask**. Just generate. State the
choice in the one-line confirmation form (principle 2) at most.

### When to ask

Ask only if:
- the user explicitly said "choose fields" / "ask about fields" / "fine-tune settings", OR
- the entity has many fields, the purpose signal is ambiguous, AND the user did not say "use defaults".

When asking, use the structured-question tool with `multiSelect: true`:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Which fields to include in DTO `${Entity}Dto`? | Fields | All fields + associations (Recommended) / Scalars only / Only id and name / Specify manually |

For each **association** included, apply the sub-DTO defaults from [`references/sub-dto.md`](references/sub-dto.md). Do NOT ask
per-association unless the user explicitly requested fine-grained control. Per-field overrides
(rename, extra/removed validations) live in § Per-field options below and [`references/validation.md`](references/validation.md).

---

## Step 4 — Variant selection

Tell the user: `Step 4/7: Selecting variant...`

Apply the **Decision-making principle** above. The variant is almost always derivable from context —
explicit asking should be the exception, not the default.

| Context | Action | Variant |
|---|---|---|
| Project's existing DTOs are records, user gave no mutability signal | decide silently | [`references/java-record.md`](references/java-record.md) |
| Project's existing DTOs are plain classes | decide silently (project convention wins) | [`references/java-plain.md`](references/java-plain.md) |
| User explicitly said "record" | decide silently | [`references/java-record.md`](references/java-record.md) |
| User explicitly said "plain class" / "mutable" / "with setters" | decide silently | [`references/java-plain.md`](references/java-plain.md) |
| User explicitly said "Lombok" | see [`references/lombok-note.md`](references/lombok-note.md) — follow the project's existing Lombok style if any; do not invent an annotation set | project style |
| No signal at all, no existing DTOs in the project | decide silently (record is the Quarkus default) and mention it in the one-line confirmation from principle 2 | [`references/java-record.md`](references/java-record.md) |

Only fall back to the full numbered question when **none** of the rows above matches AND the user has
not said "use defaults". Even then, prefer the "all variants with the default marked" format from
principle 3 over an iterative question.

Map the answer to a variant:
- record → [`references/java-record.md`](references/java-record.md)
- plain class → [`references/java-plain.md`](references/java-plain.md)
- Lombok → [`references/lombok-note.md`](references/lombok-note.md)

---

## Step 5 — Variant-specific questions

Tell the user: `Step 5/7: Confirming variant settings...`

Follow the variant-specific questions from the selected reference file. Only ask if the user did NOT say
"all defaults". Records need essentially no questions (immutability is built in); plain-class questions
are batched per [`references/java-plain.md`](references/java-plain.md).

---

## Step 6 — Generate code

Tell the user: `Step 6/7: Generating DTO...`

1. Determine the target path: `src/main/java/${packagePath}/${className}.java`.

2. Follow the **Generation Order** from the selected reference file.

3. Before writing, check for a **name collision**: glob/grep the target package for
   `${className}.java` / `record ${className}` / `class ${className}`. If the name is taken — for the
   parent DTO ask the user for another name; for a sub-DTO auto-suffix with a number
   (`${SubDtoName}1`, `${SubDtoName}2`, …) until the name is free.

4. For each generation step:

   **If skeleton (new file):**
   - read the skeleton `.md` from `examples/_skeletons/`
   - apply variable substitutions
   - use the available file-writing tool to create the file

   **If fragment:**
   - read the fragment `.md` from `examples/_fragments/`
   - read the Insert Point to know WHERE to insert
   - use the available file-editing tool to insert code at the specified point
   - apply variable substitutions

5. Variable substitution rules:
   - `${packageName}` → detected DTO package or user choice
   - `${className}` → from the user or the default `${EntityName}Dto`
   - field-level variables → from the entity source (Step 2)
   - **NEVER substitute anything not listed in Variables**
   - **NEVER add imports, methods, or code not in the example**
   - **FQN handling (CRITICAL):** examples contain FQNs (e.g. `java.util.List`,
     `jakarta.validation.constraints.NotNull`). When writing the final file, you MUST:
     1. Replace every FQN in the body with its **short name**
        (`java.util.List<Integer>` → `List<Integer>`, `@jakarta.validation.constraints.NotNull` → `@NotNull`).
     2. Collect every FQN you shortened and emit a corresponding `import` line right after the
        `package` statement, sorted, no duplicates.
     3. Types from `java.lang` (`String`, `Long`, …) must NOT be imported and must appear as short names.
     4. Classes from the same package as the DTO must NOT be imported.
     5. **Javadoc `{@link …}` references — UNIFORM:** generate **short name + import** for **every**
        shape: top-level class, top-level record, nested static class, nested record, and separate-file
        sub-DTO (`NEW_CLASS`). There is no asymmetry. Always shorten the entity reference and always add
        the corresponding `import` line (unless the entity is in the same package).
     6. **Group imports** in two blocks separated by ONE blank line:
        - **Block 1** — all third-party / project imports together: `jakarta.*`, `com.fasterxml.*`,
          `org.hibernate.*`, project packages, etc. (alphabetical inside the block).
        - **(blank line)**
        - **Block 2** — `java.*` and `javax.*` (alphabetical).
        Do NOT split block 1 into per-package sub-blocks.
     The final file must contain short names in the body (including every Javadoc `{@link …}`) and a
     clean, grouped import block at the top.

6. For **sub-DTOs** (`subDtoType=NEW_CLASS`): create a separate file by repeating Steps 6.1–6.5
   recursively for the sub-entity.

7. For **nested classes/records** (`subDtoType=NEW_NESTED_CLASS`): add the inner declaration to the
   parent DTO file, then fill it following the same fragment rules.

8. **Nested record inside a record parent — MANDATORY:** when the parent DTO is a Java record, every
   `NEW_NESTED_CLASS` association MUST be emitted as a nested `public record` inside the parent record's
   body. The skill MUST NOT silently fall back to `NEW_CLASS` (separate file) just because the
   record-form fragment looks shorter. The full procedure is in [`references/java-record.md`](references/java-record.md) Step 6 and
   [`examples/_fragments/nested-class/java/nested-class.md`](examples/_fragments/nested-class/java/nested-class.md) ("Java record" variant). If those
   instructions seem ambiguous to you, that is a bug in this skill — fix the docs, do NOT work around it
   by changing the `subDtoType`.

---

## Step 7 — Mapper (automatic when conversion is needed)

Tell the user: `Step 7/7: Checking whether a mapper is needed...`

Decide whether a mapper is needed based on context, then act:

| Signal | Action |
|---|---|
| User said "only DTO" / "no mapper" / "without mapper" | Skip Step 7 entirely. Do NOT mention the mapper. |
| User explicitly asked for a mapper ("and mapper", "with mapper", "create mapper too") | Delegate to `quarkus-mapper-creator` immediately. |
| From context it is clear that entity↔DTO conversion will happen (replacing an entity with a DTO in a resource/service, "convert/map/transform", the DTO is a REST response type) | Delegate to `quarkus-mapper-creator` immediately. The conversion is inevitable — creating the DTO without a mapper would force manual inline mapping code, which is never acceptable. |
| Context is silent — no signal about how the DTO will be used | Skip Step 7. Do not mention the mapper. |

**CRITICAL:** never write manual mapping code (inline `toDto` / `fromDto` methods in resources, services,
or anywhere else). If conversion is needed, always delegate to `quarkus-mapper-creator`. That skill
decides the implementation strategy (MapStruct with `componentModel = "cdi"`, custom converter, adding
dependencies) — this skill just delegates.

Never ask a structured question for the mapper. If delegating, invoke the `quarkus-mapper-creator` skill
with the DTO and entity information directly — do not ask the user to confirm the delegation.

---

## Reactive projects

If `persistenceMode = reactive` (`quarkus-hibernate-reactive-panache` in the build):

- The **DTO shape does not change** — the same records/classes, the same generation order.
- Entity loading APIs return `Uni<...>` (`Order.findById(id)` → `Uni<Order>`), so the conversion happens
  inside the reactive chain (`map(...)` / `flatMap(...)`) and resource methods return `Uni<OrderDto>`.
- Mention this in one line when the mapper delegation happens, so the mapper is used in the reactive
  pipeline rather than on a blocking path.

---

## Indentation

The skill MUST detect the project's indentation style — never hardcode tabs or spaces. Detection order:

1. **`.editorconfig`** at the project root (or any parent of the target file's directory). For Java
   files, look up the `[*.java]` or `[*]` section and read `indent_style` (`tab` or `space`) and
   `indent_size` / `tab_width`.
2. **Sample existing Java files** in the target DTO package (or the nearest ancestor package that
   contains Java files). Detect whether the leading whitespace on indented lines uses `\t` or spaces, and
   how many.
3. **Default to 4-space** if neither source is conclusive.

Whatever style is chosen, apply it **uniformly** to every line of every generated fragment (fields,
constructors, getters/setters, equals/hashCode, toString, nested classes/records). Never mix tabs and
spaces inside the same file.

---

## Per-field options

The skill must support the following per-field controls:

- **Field rename** (`fieldNameOverride`): the DTO field name can differ from the entity attribute name.
  Mapper generation still maps it from the original attribute.
- **Add validations** (`extraValidations`): add `jakarta.validation` constraints on top of the ones
  inherited from the entity. The allowed constraints depend on the field type — see
  [`references/validation.md`](references/validation.md).
- **Remove inherited validations** (`removedValidations`): drop any constraint that came from the
  entity field.
- **Edit annotation parameters** (`message`, `min`, `max`, `regexp`, …): all parameters of every
  constraint are editable.

These options never appear unless the user explicitly asks for "fine-tune field settings",
"per-field validation" or similar. By default the skill just inherits everything from the entity.

---

## Anti-hallucination checklist

Before writing ANY code, verify:
- [ ] The code comes from an `examples/` file (cite which one)
- [ ] Only declared variables were substituted
- [ ] No framework API calls were added "from knowledge"
- [ ] Import list matches the example exactly
- [ ] Method signatures match the example exactly
- [ ] No comments or convenience methods were added
- [ ] FQNs from examples are shortened in the body AND corresponding `import` lines were added after `package`
- [ ] **Every** Javadoc shape — top-level class, top-level record, nested static class, nested record, separate-file sub-DTO — uses the short name `{@link Order}` AND adds a matching `import` (unless the entity is in the same package). Uniform rule, no asymmetry.
- [ ] Name-collision check was performed against the target package; sub-DTO names are auto-suffixed (`PetDto1`) when taken
- [ ] When generating a **Java record**, the inner declaration for any `NEW_NESTED_CLASS` association is also a **record** (not a static class, not a separate file). All component validators are inlined onto the record component parameters (`@NotBlank String firstName`), not on separate field declarations
- [ ] When variant=java-record, the output has NO `equals()`, `hashCode()`, `toString()`, setters, or fluent setters — records auto-generate these
- [ ] Class-level Javadoc is **multi-line** (`/**\n * DTO for {@link …}\n */`), never collapsed to one line
- [ ] Getters and setters are **multi-line** (signature line, indented body, closing brace), never one-liners
- [ ] In `mutable=true && fluentSetters=false` mode, getters and setters are **interleaved** (`getX, setX, getY, setY, …`), not grouped
- [ ] In `mutable=true` mode, **both** the no-args constructor and the all-args constructor are emitted
- [ ] The skill does NOT offer "Only ID" as a separate option — that option does not exist (neither for ToOne nor for ToMany). The "association id only" effect is produced by **Flat with only the sub-entity `id` checked**
- [ ] For collection associations (`List<X>`, `Set<X>`), Flat **is** offered and produces composite plural fields (`List<Long> itemIds`), and sub-entity scalars are auto-checked
- [ ] Back-reference `@ManyToOne` fields are filtered out of the attribute list (e.g. `OrderItem.order` is not offered when creating `OrderItemDto`)
- [ ] Imports are grouped with a blank line between the third-party/project block and the `java.*` block
- [ ] Indentation matches the project's detected style (`.editorconfig` first, then sampling existing files in the same package, then 4-space default). Never hardcode tabs or spaces; apply uniformly across every fragment
- [ ] Attributes (names, types, associations, constraints) trace to the entity source that was actually read — nothing invented. `PanacheEntity`'s implicit `public Long id` was treated as an attribute; `@Id` was read explicitly only for `PanacheEntityBase` / plain `@Entity`
- [ ] Validation annotations were emitted only when `hasValidation = true`
- [ ] No Hibernate-proxy equals/hashCode variant was generated for the DTO (DTOs are never proxies)
- [ ] For Lombok projects, the annotation set mirrors an existing Lombok DTO in the project — never invented