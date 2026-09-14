# PanacheQL query patterns (Java)

Ready-to-adapt query fragments. Replace `${...}` variables and keep the parameter binding style resolved in
`references/entity-conventions.md` (step 1.5).

## Find one — positional parameter

```java
Entity result = find("${columnName} = ?1", ${value}).firstResult();
Optional<Entity> optional = find("${columnName} = ?1", ${value}).firstResultOptional();
```

## Find one — named parameters (several values)

```java
import java.util.Map;

Optional<Entity> result = find("${columnName} = :name and ${otherColumn} = :status",
        Map.of("name", ${value}, "status", ${otherValue}))
        .firstResultOptional();
```

## Named query (`#` prefix)

```java
Optional<Entity> result = find("#${EntityName}.${queryName}", ${value}).firstResultOptional();
```

A named query is declared with `@NamedQuery` / `@NamedQueries` on the entity class (or its super class) and
referenced by name with the `#` prefix — the same form works for `count`, `update`, and `delete`.

## List with ordering

```java
import io.quarkus.panache.common.Sort;

List<Entity> result = list("${columnName}", Sort.by("${orderColumn}").descending(), ${value});
```

## Count

```java
long total = count("${columnName}", ${value});
```

## Paged query (0-based index)

```java
import io.quarkus.panache.common.Page;

PanacheQuery<Entity> query = find("${columnName}", ${value});
long total = query.count();
List<Entity> pageItems = query.page(Page.of(${pageIndex}, ${pageSize})).list();
```

## Update (returns affected rows)

```java
long updated = update("${columnName} = ?1 where ${idColumn} = ?2", ${newValue}, ${id});
```

## Delete (returns affected rows)

```java
long deleted = delete("${columnName}", ${value});
```

## Active Record equivalents

For entities extending `PanacheEntity` the same calls are static methods on the entity class:

```java
Optional<Person> person = Person.find("name = ?1", name).firstResultOptional();
List<Person> alive = Person.list("status", Sort.by("name"), Status.Alive);
long removed = Person.delete("status", Status.Alive);
```

## Rules that always apply

- Bind every value — never concatenate strings into the query
- Positional (`?1`, `?2`, 1-based) for one or two parameters; named `Map.of(...)` for more
- Ordering through the `Sort` argument, not by appending `ORDER BY` (match the project's convention)
- `Page.of(index, size)` indices start at 0
- Every write (`update`, `delete`, `persist`, `flush`) needs an active transaction —
  see [`../../references/transaction-conventions.md`](../../references/transaction-conventions.md)
