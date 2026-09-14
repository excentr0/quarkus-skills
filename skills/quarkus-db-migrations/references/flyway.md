# Flyway in Quarkus

Flyway is the default migration tool for this skill: plain SQL files, version-ordered, minimal
configuration.

---

## 1. Migration file naming

Versioned migrations live in `src/main/resources/db/migration/` with the structure
`<prefix><VERSION><separator><DESCRIPTION><suffix>`:

```text
V1__create_orders.sql
V2__add_status_to_orders.sql
V1.1__My_description.sql          # version style is project-specific — copy the existing pattern
R__refresh_order_stats_view.sql   # repeatable (prefix R by default)
```

- Default prefix: `V` for versioned, `R` for repeatable (`quarkus.flyway.sql-migration-prefix`,
  `quarkus.flyway.repeatable-sql-migration-prefix`).
- The description is free text but must match the project's existing style (usually `snake_case`).
- Versions are ordered hierarchically: `1` < `1.1` < `2`. Pick the next value above the current max.

---

## 2. Configuration keys

| Key | Meaning | Default |
|-----|---------|---------|
| `quarkus.flyway.migrate-at-start` | run migrations on application start | `false` |
| `quarkus.flyway.locations` | migration directories (comma-separated) | `db/migration` |
| `quarkus.flyway.table` | history table name | `flyway_schema_history` |
| `quarkus.flyway.baseline-on-migrate` | baseline an existing non-empty schema instead of failing | `false` |
| `quarkus.flyway.baseline-version` | version the existing schema represents | `1` |
| `quarkus.flyway.baseline-description` | description recorded for the baseline | `<< Flyway Baseline >>` |
| `quarkus.flyway.schemas` | schemas to manage (comma-separated) | default schema |
| `quarkus.flyway.sql-migration-prefix` | versioned file prefix | `V` |
| `quarkus.flyway.repeatable-sql-migration-prefix` | repeatable file prefix | `R` |
| `quarkus.flyway.connect-retries` | connection retries at startup | `0` |

Example:

```properties
quarkus.flyway.migrate-at-start=true
# only when migrations live outside the default directory:
quarkus.flyway.locations=db/migration,db/migration-extra
```

---

## 3. How migrations run

The extension performs the migration **during application startup** — dev mode, tests, and
production. There is no separate Maven/Gradle goal to call; a build that only compiles does not
touch the database.

- **dev / test** — Dev Services starts a database container automatically; migrations apply to it
  at startup, so a fresh Dev Services database always ends up with the current schema.
- **prod** — the application runs the migration against the configured datasource on boot
  (with `migrate-at-start=true`); real datasource settings live under the `%prod.` prefix.

---

## 4. Multiple datasources

Each named datasource gets its own Flyway configuration under the datasource name:

```properties
quarkus.flyway.migrate-at-start=true
quarkus.flyway.users.migrate-at-start=true
quarkus.flyway.users.locations=db/users/migration
```

Migration files for a named datasource normally live in their own directory — keep the version
sequence per datasource, not global.

---

## 5. Existing non-empty database

If the target database already contains the schema (applied by hand or by another tool), Flyway
refuses to start on a non-empty schema without a history table. Two options:

- **Baseline** — `quarkus.flyway.baseline-on-migrate=true` records the existing schema at
  `baseline-version`; migrations with a version **≤** baseline are skipped. Set the baseline version
  to the migration the existing schema already reflects, then add the next migration above it.
- **Adopt** — start a fresh history table on a database whose schema genuinely matches the existing
  migrations (`baseline-version` = the last applied migration's version).

Never enable baseline against a database whose state you have not verified — a wrong baseline makes
Flyway skip migrations the database still needs.
