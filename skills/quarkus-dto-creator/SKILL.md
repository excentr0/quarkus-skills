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

Before any file read or question, re-read the user's prompt and prior turns and mark every already
answered input. Read [`references/interaction-workflow.md`](references/interaction-workflow.md) for
the full context checklist and question matrices before Steps 2–5.

- **NEVER** ask a question the user already answered, even implicitly.
- **Exception: `subDtoType` is NEVER decided silently**; confirm it at minimum through the one-line
  decision protocol unless the user explicitly supplied the shape.

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

Before selecting fields, read [`references/interaction-workflow.md`](references/interaction-workflow.md).
Use the entity purpose and source-derived fields to choose the default set; ask only when the user
requests a narrower or fine-grained selection. Apply the sub-DTO rules in `references/sub-dto.md`.

---

## Step 4 — Variant selection

Tell the user: `Step 4/7: Selecting variant...`

Read [`references/interaction-workflow.md`](references/interaction-workflow.md) for the variant
matrix. Derive record/plain-class/Lombok from project conventions and explicit user intent; ask only
when no signal remains.

---

## Step 5 — Variant-specific questions

Tell the user: `Step 5/7: Confirming variant settings...`

Read [`references/interaction-workflow.md`](references/interaction-workflow.md) and the selected
variant reference before asking. Records need no settings questions; batch only unresolved plain-class
questions, and skip them when the user said "all defaults".

---

## Step 6 — Generate code

Tell the user: `Step 6/7: Generating DTO...`

Before writing, read [`references/generation-workflow.md`](references/generation-workflow.md). Follow
the selected variant's generation order, collision rules, fragment insert points, indentation and
per-field behavior from that reference.

- **NEVER** substitute anything not listed in Variables.
- **NEVER** add imports, methods, or code not in the example.
- **FQN handling (CRITICAL):** examples contain FQNs. When writing the final file, you **MUST** shorten
  them consistently and add the corresponding grouped imports.
- For `NEW_NESTED_CLASS` in a Java record, the nested declaration **MUST** be a nested `public record`;
  the skill **MUST NOT** silently fall back to `NEW_CLASS`.

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

Rules for reactive persistence are in
[`references/generation-workflow.md`](references/generation-workflow.md) § Reactive projects.

---

## Indentation

Detection order and the uniformity rule are in
[`references/generation-workflow.md`](references/generation-workflow.md) § Indentation.

---

## Per-field options

The rename/validation/annotation-parameter controls are in
[`references/generation-workflow.md`](references/generation-workflow.md) § Per-field options.

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
