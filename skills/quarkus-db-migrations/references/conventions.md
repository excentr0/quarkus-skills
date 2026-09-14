# Migration Conventions

Discipline rules that keep a migration history readable and recoverable. They apply to Flyway and
Liquibase alike.

---

## 1. Append-only history

- A migration that has been applied anywhere is immutable. A typo is fixed by the **next** migration,
  not by editing the old file.
- Version = max existing + 1, read from the directory listing. Never renumber, never reuse a number.
- One logical change per migration (a table, an alter group, a backfill). Mixed concerns make a
  failed migration hard to unwind.

## 2. Naming

Match the project; when the project has no precedent:

| Object | Convention | Example |
|--------|------------|---------|
| migration file | project's existing pattern | `V3__create_orders.sql` |
| table | `snake_case`, plural | `orders`, `order_items` |
| column | `snake_case` | `total_amount`, `created_at` |
| index | `idx_<table>_<column(s)>` | `idx_orders_customer_id` |
| foreign key | `fk_<table>_<referenced>` | `fk_orders_customers` |
| unique constraint | `uq_<table>_<column(s)>` | `uq_customers_email` |

The entity mapping wins over the table above: if `@Column(name = "TOTAL_AMOUNT")` exists, the DDL
uses that exact name.

## 3. Schema ownership

- When a migration tool manages the schema, Hibernate must not: set
  `quarkus.hibernate-orm.database.generation=none`.
- Dev Services databases start empty every time a container is created — migrations rebuild the
  schema at startup; that is the expected flow, not a bug.

## 4. Data migrations

- Backfills and data fixes go in their own migration, separate from the DDL that made them possible.
- Batch large updates or state explicitly that the table is small — an unbounded `UPDATE` on a
  production table can lock it.
- Derive-and-copy patterns: add the new column nullable, backfill, then add the constraint in a
  later migration when the project's cadence allows it.

## 5. Irreversibility

- Flyway Community has no automatic rollback; Liquibase rollback needs a hand-written rollback block.
  Assume **forward-only**: a mistake is repaired by a compensating migration.
- Destructive operations (`DROP TABLE`, `DROP COLUMN`, `TRUNCATE`; Liquibase `dropTable`,
  `dropColumn`) only on explicit request, and preferably in a separate migration that can be
  reviewed on its own.

## 6. Multiple datasources

- Keep one version sequence per datasource, in its own directory, with its own config prefix
  (`quarkus.flyway.<name>.*`).
- A migration belongs to exactly one datasource; cross-datasource changes are several migrations.
