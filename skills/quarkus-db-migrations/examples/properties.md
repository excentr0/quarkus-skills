# Properties

## Flyway — minimal

```properties
# run migrations on application start
quarkus.flyway.migrate-at-start=true
```

## Flyway — non-default locations

```properties
# only when the project keeps migrations outside db/migration
quarkus.flyway.locations=db/migration,db/migration-extra
```

## Flyway — existing non-empty database

```properties
# only for a database whose schema already reflects migrations up to baseline-version;
# migrations with version <= baseline-version are skipped
quarkus.flyway.baseline-on-migrate=true
quarkus.flyway.baseline-version=${baselineVersion}
```

Do not enable these without verifying the database state (`references/flyway.md` §5).

## Flyway — multiple datasources

```properties
quarkus.flyway.migrate-at-start=true
quarkus.flyway.users.migrate-at-start=true
quarkus.flyway.users.locations=db/users/migration
```

## Liquibase

```properties
quarkus.liquibase.migrate-at-start=true
# path must match the project's actual changelog — verify it (references/liquibase.md §2)
quarkus.liquibase.change-log=db/changelog/master.xml
```

## Real datasource in production (context)

Migrations run against whatever datasource is active. Keep real datasource settings under the
`%prod.` prefix so Dev Services stay in charge of dev/test:

```properties
%prod.quarkus.datasource.db-kind=postgresql
%prod.quarkus.datasource.username=${DB_USER}
%prod.quarkus.datasource.password=${DB_PASSWORD}
%prod.quarkus.datasource.jdbc.url=jdbc:postgresql://${DB_HOST}:5432/${DB_NAME}
```

## Schema ownership

```properties
# when the migration tool owns the schema, Hibernate must not manage DDL
quarkus.hibernate-orm.database.generation=none
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${baselineVersion}` | version of the first migration on an existing schema | `1` |
| `${DB_USER}` / `${DB_PASSWORD}` | production datasource credentials (env references, never literals) | -- |
| `${DB_HOST}` / `${DB_NAME}` | production database host/name | -- |
