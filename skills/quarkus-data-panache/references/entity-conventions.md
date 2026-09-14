# Detect Entity Conventions

Follow substeps 1.1 → 1.2 → 1.3 → 1.4 → 1.5 in order. Do not skip or reorder them.
Tell the user which substep you are on while running them: `Step 1.1/1.5: Finding existing entities...`.

---

## Step 1.1: Find existing entities

Locate the project's entities with a grep for `jakarta.persistence.Entity` across `src/main/java`.
Pick 2–3 representative ones and read their source files in full.

---

## Step 1.2: Score each convention

For each convention below, determine the answer from the code and assign a confidence score (1–100):

Panache style:

- **Panache style** — Active Record (entities extend `PanacheEntity` and expose static finder methods),
  repositories (`@ApplicationScoped` classes implementing `PanacheRepository` / `PanacheRepositoryBase`),
  or both? Default: match the dominant style found in the code; if the project has no Panache code yet — Active Record
- **Entity base class** — `PanacheEntity` (implicit `Long id`), `PanacheEntityBase` (the entity declares its own
  `@Id`), or a plain `@Entity` without a Panache base class? Default: `PanacheEntity`
- **Field access modifier** — are entity fields `public` (Panache idiom) or `private` with getters/setters?
  Default: `public` for entities extending a Panache base class; `private` + accessors for plain entities
- **Accessors** — if fields are private: manual getters/setters, Lombok annotations, or none?
  Default: none for public-field Panache entities; match the project when it uses accessors
- **Custom finder placement** — static methods on the entity (Active Record) or methods on a repository class?
  Default: follow the Panache style resolved above

General conventions:

- **ID strategy** — check existing `@Id` fields: `Long` with `@GeneratedValue(strategy = SEQUENCE)` (sequence),
  `Long` with `@GeneratedValue(strategy = IDENTITY)` (identity/autoincrement), or `UUID` with
  `@GeneratedValue(strategy = UUID)` (client-generated)? Default: database-generated (`Long` + `SEQUENCE`).
  Note: entities extending `PanacheEntity` inherit `id` — there is nothing to score for them
- **Sequence scope** — if SEQUENCE is used, check `@SequenceGenerator`: a dedicated sequence per table (each
  entity has its own generator name), a shared sequence across all tables, or no `@SequenceGenerator` at all
  (Hibernate default sequence)? Default: dedicated sequence per table
- **Annotation placement** — are `@Column`, `@Id`, etc. on fields or getter methods? Default: on fields
- **`serialVersionUID`** — does any entity declare `private static final long serialVersionUID`?
  Default: not generated
- **FetchType on @ManyToOne / @OneToOne** — check the `fetch` attribute. Default: `LAZY`
- **Naming strategy** — does the project rely on the JPA implicit naming strategy (names omitted from
  `@Table`/`@Column`), or are all names explicit? Default: explicit — always name JPA objects explicitly
- **Table name template** — check `@Table(name = ...)` values: case (lower/upper/as-is), prefix, postfix,
  underscores, pluralized? Default: lower case, underscore, no prefix/postfix, not pluralized
- **Column name template** — check `@Column(name = ...)` values: case, prefix, postfix, underscores?
  Default: lower case, underscore, no prefix/postfix
- **Entity class name convention** — is the Java class name transformed in any way (prefix/postfix)?
  Default: as-is, no transformation
- **Index/constraint name case** — check `@Index(name = ...)`, `@UniqueConstraint(name = ...)`. Default: `lower`
- **PanacheQL parameter style** — positional (`"name = ?1"`) or named (`"name = :name"` with a
  `Map<String, Object>` argument)? Default: positional for a single parameter; named `Map.of(...)` when a
  query takes several
- **Single-result return style** — `Optional<Entity>` via `firstResultOptional()` or a nullable result via
  `firstResult()`? Default: `Optional`

equals & hashCode conventions (score separately):

- **equals/hashCode style** — manual proxy-safe implementation, id-based implementation, or none at all?
  Default: none — do not generate them unless the project has them or the user asks. If the project has
  implementations, match their style. If a manual implementation is needed, use the proxy-safe pattern from
  [`entity-rules-impl.md`](entity-rules-impl.md)
- **Fields included** — `id` only, or a business/natural key? Default: `id` only

toString conventions (score separately):

- **toString style** — manual override, Lombok-generated, or none? Default: none unless the project has them
- **toString fields** — if manual: all local (non-relation) fields, relations never included

---

## Step 1.3: Collect uncertain conventions

Score confidence only for conventions where the code contains relevant examples but the pattern is ambiguous
or inconsistent. If a convention is simply absent from the code (e.g. no `@ManyToOne` exists yet, no
equals/hashCode anywhere) — confidence is high, use the default without asking.

Collect all conventions where confidence < 80. For each, formulate a question with explicit answer options;
put the default value first (marked as "Recommended").

---

## Step 1.4: Ask developer

If there are any uncertain conventions from step 1.3, ask the developer in a single prompt — use your
harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`); if none is available,
fall back to a numbered list in plain text. Do not ask one question at a time.

Example shape — adapt the question list and options to what you actually found:

```json
{
  "questions": [
    {
      "header": "Panache style",
      "question": "How is persistence code structured in this project?",
      "multiSelect": false,
      "options": [
        { "label": "Active Record (Recommended)", "description": "Entities extend PanacheEntity and expose static finders" },
        { "label": "Repositories", "description": "@ApplicationScoped classes implementing PanacheRepository" },
        { "label": "Both", "description": "Repositories for cross-entity queries, statics on entities for simple lookups" }
      ]
    },
    {
      "header": "Field access",
      "question": "How are entity fields exposed?",
      "multiSelect": false,
      "options": [
        { "label": "public fields (Recommended)", "description": "Panache idiom — direct field access, no accessors" },
        { "label": "private + accessors", "description": "Encapsulated fields with generated getters/setters" }
      ]
    },
    {
      "header": "ID strategy",
      "question": "How are entity identifiers generated?",
      "multiSelect": false,
      "options": [
        { "label": "Long + SEQUENCE (Recommended)", "description": "Database-generated sequence per table" },
        { "label": "Long + IDENTITY", "description": "Database autoincrement column" },
        { "label": "UUID", "description": "Client-generated identifier" }
      ]
    }
  ]
}
```

Ask follow-up questions only when their prerequisite was confirmed: sequence scope only if SEQUENCE was
chosen; accessor style only if fields are private; equals/hashCode fields only if an implementation exists.

---

## Step 1.5: Summarize resolved conventions

Do NOT call any tools in this step — reason only from what you read and what the developer confirmed.

Before writing any code, output a single consolidated list of **all conventions from Step 1.2**, with each
value filled in from what you actually found in the code or what the developer confirmed in Step 1.4.
Do not copy the example below — construct your own list based on the real project.

Every convention from Step 1.2 must appear in the list. Each value must reflect the actual project state,
not the defaults.

**Example format** (values here are illustrative only — replace with what you discovered):

```text
- Panache style: Active Record
- Entity base class: PanacheEntity
- Field access modifier: public
- Accessors: none
- Custom finder placement: static methods on the entity
- ID strategy: inherited from PanacheEntity (Long, sequence)
- Sequence scope: dedicated per table
- Annotation placement: on fields
- serialVersionUID: not generated
- FetchType on @ManyToOne: LAZY
- Naming strategy: explicit
- Table name template: lower case, underscore, no prefix/postfix, not pluralized
- Column name template: lower case, underscore, no prefix/postfix
- Entity class name convention: as-is
- Index/constraint name case: lower
- PanacheQL parameter style: positional ?1 for single, Map.of(...) for multiple
- Single-result return style: Optional
- equals/hashCode style: none
- toString style: none
```

This list is your working contract for all entity code written in this session.
