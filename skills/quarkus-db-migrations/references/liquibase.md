# Liquibase in Quarkus

Liquibase is the alternative migration tool: changes live in **changesets** (usually XML) inside a
**changelog**, instead of versioned SQL files.

---

## 1. Structure

- A changelog is a file that lists changesets, or includes other changelog files.
- Every changeset carries a unique `id` + `author` pair; the pair is the identity in the history
  table — never reuse it, never edit an applied changeset.
- Changesets use DB-agnostic XML/YAML/JSON or raw `sql` bodies.

```text
src/main/resources/db/changelog/
├── master.xml                 # root changelog (path is project-specific — see §2)
└── changes/
    ├── 001-create-customers.xml
    └── 002-create-orders.xml
```

---

## 2. Changelog location — verify, do not assume

The changelog path and file name are **project-specific**. The Quarkus Liquibase guide's examples use
`db/changelog/master.xml` pointed at by `quarkus.liquibase.change-log`. Before writing anything:

1. glob `src/main/resources/db/**` for the actual changelog file(s);
2. read the existing `quarkus.liquibase.change-log` value (if present) — it is authoritative;
3. only when neither exists, create a changelog and set `change-log` explicitly to the path you
   created.

Do not claim a "default filename" — there is a documented example path, not a guaranteed default.

---

## 3. Configuration keys

| Key | Meaning |
|-----|---------|
| `quarkus.liquibase.migrate-at-start` | run changesets on application start |
| `quarkus.liquibase.change-log` | path to the root changelog (verify against the project) |

Migrations run during application startup (dev, test, prod) — same lifecycle as Flyway: Dev Services
provides the dev/test database, `%prod.` config points at the real one.

---

## 4. Adding the next change

Follow the project's existing granularity — one new changeset file per logical change when the
changelog includes a `changes/` directory, or a new changeset appended to the existing changelog
file. Use [`../examples/migration-file.md`](../examples/migration-file.md) for the changeset shape
and remember:

- new unique `id` + `author` — never edit an applied changeset;
- same naming convention as the neighbouring changesets;
- an FK gets its index in the same changeset;
- no destructive change (`dropTable`, `dropColumn`, ...) without an explicit user request.

---

## 5. Changelog inclusion

A root changelog that includes change files:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                            http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

    <include file="db/changelog/changes/001-create-customers.xml"/>
    <include file="db/changelog/changes/002-create-orders.xml"/>
</databaseChangeLog>
```

Add the new file's `include` in the right position (Liquibase orders by inclusion for the `include`
style, by changeset id otherwise) — appending at the end is the safe default.
