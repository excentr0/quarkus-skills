---
name: quarkus-db-migrations
description: >
  Adds and evolves database schema migrations in a Quarkus application with Flyway or
  Liquibase: detecting the tool the project already uses, creating the next migration
  file, wiring it into application.properties, and verifying that it applies.
  Use this skill when the database schema must change (new table, column, index,
  constraint, data fix) or when a migration tool needs to be set up in the project.
  Russian phrases also trigger this: "добавь миграцию", "создай миграцию", "измени схему",
  "добавь таблицу в БД", "добавь колонку", "настрой flyway", "настрой liquibase".
---

# Preflight — Project detection (before step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`;
   Gradle: `id("io.quarkus")` plugin. Quarkus 3.x targets Jakarta EE.
3. **Migration extension** — `quarkus-flyway` → Flyway (`hasFlyway`); `quarkus-liquibase` →
   Liquibase (`hasLiquibase`); neither → the project has no migration tool yet.
4. **Migration files** — glob `src/main/resources/db/**`: `db/migration/*.sql` (Flyway) or
   `db/changelog/**` (Liquibase). Files found → the project's tool decision is already made:
   **never switch the tool**.
5. **Existing naming convention** — list the migration file names and derive the pattern:
   version style (`V1__` vs `V1.0.0__`), separator, description style (`snake_case` vs `camelCase`).
   The next file MUST match the existing convention exactly.
6. **Persistence & datasource** — `quarkus-hibernate-orm-panache` / `quarkus-hibernate-reactive-panache`;
   db kind from `quarkus.datasource.db-kind` or the `quarkus-jdbc-*` / `quarkus-reactive-*-client`
   dependency; whether `%prod.` datasource config exists; whether Hibernate schema generation is on
   (`quarkus.hibernate-orm.database.generation`).

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and
tell the user this skill targets Quarkus projects.

---

# DB Migrations

Creates and evolves schema migrations for a Quarkus application using the project's existing
migration tool — Flyway or Liquibase — following its naming and versioning conventions.

---

> **CRITICAL: SQL and changesets ONLY from examples/ files. If no matching example -- STOP and ask user.**
> **CRITICAL: NEVER edit an already-applied migration. Always append the next version.**
> **CRITICAL: For questions with a fixed set of choices, prefer your harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`) > its analogue > plain text list. Plain numbered text lists are the last resort when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions may already be answered by the user's prompt and prior turns. Re-asking what was already said is the #1 reason this skill feels slow.

---

## Defaults

### Block 1 — Migration tool

| Option | Default | Notes |
|--------|---------|-------|
| tool | detected from the project (`hasFlyway` / `hasLiquibase` / `db/` dirs); if neither → **Flyway** | Flyway is SQL-first and the simplest path; do not ask when the project already uses one |

### Block 2 — File & versioning

| Option | Default | Notes |
|--------|---------|-------|
| migrationDir | detected (`db/migration` for Flyway; the project's changelog dir for Liquibase) | never move an existing directory |
| version | max existing version + 1 | read from the directory listing — never guess |
| description | `snake_case`, matching existing files | e.g. `create_orders`, `add_status_to_orders` |
| fileType | Flyway → `.sql`; Liquibase → XML changeset in the changelog | `repeatable R__` only if the project already uses it |

### Block 3 — Configuration

| Option | Default | Notes |
|--------|---------|-------|
| migrateAtStart | `true` | the Quarkus way: migrations run on application start (dev, test, prod) |
| locations | leave default | set only when the project keeps migrations in a non-default directory |
| baseline | off | turn on only for an existing non-empty database (see `references/flyway.md` §5) |
| hibernateSchemaGeneration | `none` when migrations own the schema | never let Hibernate and migrations both manage DDL |

### Auto-detected (no questions)

| Option | Source |
|--------|--------|
| build system, Quarkus version | build file (preflight) |
| tool, migration dir, naming pattern | build file + `db/**` listing |
| next version | max existing migration version |
| db kind, datasource names | dependency list + `quarkus.datasource.*` keys |
| entity ↔ table mapping style | entity files (`@Table`/`@Column` names) and existing migrations |

**Smart defaults:** if the user says "use defaults" or similar — skip every question that has a
default and proceed.

---

## Decision-making principle — context first, then ask

1. **Derive from the project first** — an existing tool, directory, or naming pattern answers the
   question; asking about it is a defect.
2. **Derive from the request second** — table/column names, types, and constraints usually follow
   from the entity or from the wording of the task.
3. **Ask only genuine forks**, in one structured-question call:
   - no migration tool anywhere in the project → Flyway vs Liquibase (recommend Flyway);
   - the database already has the schema applied by hand → manage with `baseline-on-migrate` or not;
   - a destructive change (drop column/table) that the user did not explicitly request.

---

## Step 0 — Read the request (no tools)

Tell the user: `Step 0/6: Reading the request...`

**Do NOT call any tools in this step.**

From the conversation, fix what the change is:
- **Tables** — new table? existing table being altered?
- **Columns** — names, types, nullability, defaults.
- **Constraints & indexes** — PK, unique, FK (and the index an FK needs), check constraints.
- **Data** — pure schema change, backfill, or both (backfills belong in their own migration).
- **Entity link** — if the table maps to a Panache entity, its `@Table`/`@Column`/field mapping
  defines the exact names and types.

Output:

```text
### Predicted change:
- New table: orders (id, customer_id FK, status, total_amount, created_at)
- New index: idx_orders_customer_id
- Entity: Order (exists) — DDL must match its mapping
```

---

## Step 1 — Detect the tool and its conventions

Tell the user: `Step 1/6: Detecting migration setup...`

Read-only discovery; do not write anything yet:

1. Build file → `hasFlyway` / `hasLiquibase` (preflight).
2. Glob `src/main/resources/db/**` → migration files with their exact names.
3. Derive the next version and the naming pattern from those names.
4. `application.properties` → existing `quarkus.flyway.*` / `quarkus.liquibase.*` keys,
   datasource keys, `%prod.` prefixes (redact secrets).
5. Entity files for the affected tables → mapped `@Table(name=...)` / `@Column(name=...)`,
   JDBC types, nullability.

Output:

```text
### Migration context:
- Tool: Flyway (hasFlyway) · dir: src/main/resources/db/migration
- Existing: V1__create_customers.sql, V2__create_orders.sql → next version: V3
- Naming: V<number>__<snake_case_description>.sql
- Datasources: default (PostgreSQL); %prod config present
- Conflict: quarkus.hibernate-orm.database.generation not set → set to none
```

If no migration setup exists at all — go to Step 2. Otherwise skip Step 2.

---

## Step 2 — Choose the tool (only when the project has none)

Tell the user: `Step 2/6: Choosing the migration tool...`

Default to **Flyway** and say why: plain SQL files, minimal configuration, the smallest moving part
for a Quarkus app. Choose **Liquibase** instead when the project already contains a changelog
directory, the user names Liquibase, or DB-vendor-independent changelogs are a stated requirement.

Ask the user only when the signals genuinely conflict (e.g. a `db/changelog` directory without the
extension). Never set up both tools.

---

## Step 3 — Add the extension (when missing)

Tell the user: `Step 3/6: Adding the migration extension...`

Use the snippets in [`examples/dependencies.md`](examples/dependencies.md). Prefer the extension
command so the build file stays consistent:

```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-flyway"
```

The JDBC driver for the project's db kind must already be present (`quarkus-jdbc-*`) — the migration
extension does not bring one.

---

## Step 4 — Create the migration file

Tell the user: `Step 4/6: Creating the migration...`

Rules:

- **Append-only** — never edit a migration that has been applied anywhere; write the next version.
- **Next version = max existing + 1**, taken from the Step 1 directory listing.
- **One logical change per migration** (one table, one alter group) — simpler to trace and revert.
- **DDL matches the entity mapping** — same table/column names, JDBC types, nullability; check the
  entity from Step 1 when one exists.
- **An FK gets its index** in the same migration.
- **No destructive statements** (`DROP TABLE`, `DROP COLUMN`, `TRUNCATE`, `DELETE` without `WHERE`)
  unless the user explicitly asked for them.
- Repeatable `R__` migrations only when the project already uses them (views, functions, triggers).

File content comes from [`examples/migration-file.md`](examples/migration-file.md) — pick the
variant matching the db kind and the change type, and fill the `${variables}`.

---

## Step 5 — Wire the configuration

Tell the user: `Step 5/6: Updating application.properties...`

Use [`examples/properties.md`](examples/properties.md):

- `quarkus.flyway.migrate-at-start=true` (or the Liquibase equivalent) — the Quarkus way to run
  migrations on startup.
- Set `locations` / `change-log` **only** when the project's directory differs from the default.
  For Liquibase, the changelog path must be verified against the project — never assume the default
  filename (see [`references/liquibase.md`](references/liquibase.md) §2).
- Leave `%prod.` datasource configuration untouched so Dev Services keep working in dev/test.
- Multiple datasources → per-datasource prefix `quarkus.flyway.<name>.*`.
- When migrations own the schema, set `quarkus.hibernate-orm.database.generation=none` — never let
  Hibernate and the migration tool both manage DDL.

---

## Step 6 — Verify and report

Tell the user: `Step 6/6: Verifying...`

Prove the migration applies — do not report success on "file written" alone:

1. Run the project's tests once (`./mvnw test`) or start dev mode briefly — Dev Services starts a
   database and the migration runs at startup. Running tests is covered by
   [`../quarkus-run-tests/SKILL.md`](../quarkus-run-tests/SKILL.md).
2. Check the run output for migration errors (bad SQL, missing table, wrong version order).
3. If the target database already contains the schema, apply the baseline decision from the Defaults
   (never run migrations blindly against a populated database).

Report: migration file path + version, tool, config keys added, verification result (applied / failed
with the error), and any baseline caveat.

---

## Anti-hallucination checklist

- [ ] Tool, directory, and file naming came from the project — not from this skill's defaults.
- [ ] The new version is max existing + 1, taken from a real directory listing.
- [ ] The file name matches the project's existing pattern character for character.
- [ ] Config keys used are only those present in `references/flyway.md` or `references/liquibase.md`.
- [ ] DDL column names/types match the entity mapping when an entity exists.
- [ ] No destructive statement was written without an explicit user request.
- [ ] The Liquibase changelog path was verified against the project, not assumed.
- [ ] Verification actually ran (tests or dev mode) — or the report states why it could not.