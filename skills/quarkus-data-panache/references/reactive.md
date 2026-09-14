# Reactive Panache (Hibernate Reactive)

Read this before writing any persistence code when the project depends on
`quarkus-hibernate-reactive-panache`.

## How to confirm the mode

- Build file dependency: `quarkus-hibernate-reactive-panache` (plus a reactive driver such as
  `quarkus-reactive-pg-client`).
- Imports in existing code: `io.quarkus.hibernate.reactive.panache.*` — note this is a **different package**
  from the blocking variant (`io.quarkus.hibernate.orm.panache.*`). A classpath can contain both extensions;
  the import line, not the class name, tells you which API you are using.

## What changes for entities and repositories

- Entities extend `io.quarkus.hibernate.reactive.panache.PanacheEntity` (or `PanacheEntityBase` for a custom
  `@Id`); JPA mapping rules from [`entity-rules-impl.md`](entity-rules-impl.md) apply unchanged.
- Repositories implement `io.quarkus.hibernate.reactive.panache.PanacheRepository` /
  `PanacheRepositoryBase<Entity, ID>`; the detection flow in
  [`repository-conventions.md`](repository-conventions.md) is the same.
- Every operation mirrors the blocking API but returns a `Uni`:

```java
Uni<Void> persistOperation = person.persist();
Uni<Person> byId = Person.findById(23L);
Uni<List<Person>> alive = Person.list("status", Status.Alive);
Uni<Long> total = Person.count();
```

- PanacheQL, parameter binding, `Sort`, and pagination rules are identical to the blocking variant.

## Rules

- Never block: no `.await().indefinitely()` and no synchronous JDBC calls on the request path — compose with
  `Uni` combinators (`map`, `flatMap`, `chain`) and let resource methods return `Uni<T>`.
- Do not mix blocking and reactive Panache imports in the same repository/resource — pick the project's mode
  and stay consistent within a call chain.
- A repository method returns `Uni` rather than a materialized list; callers chain onto it instead of
  subscribing early.
- Lazy relations: use the reactive fetch/join patterns from the project's existing code rather than assuming
  blocking lazy loading.

## Transactions

Wrap methods that modify data (or run several queries) in a transaction. Two supported forms:

```java
import io.quarkus.hibernate.reactive.panache.common.WithTransaction;
import io.smallrye.mutiny.Uni;

@WithTransaction
public Uni<Void> rename(Long id, String name) {
    return Person.<Person>findById(id)
            .invoke(person -> person.name = name)
            .replaceWithVoid();
}
```

- `@WithTransaction` (`io.quarkus.hibernate.reactive.panache.common.WithTransaction`) intercepts a
  `Uni`-returning CDI method and runs the returned `Uni` inside a transaction boundary — the reactive
  counterpart of the blocking placement rules. `@jakarta.transaction.Transactional` also works on such methods
- Programmatic alternative: `Panache.withTransaction(() -> ...)` (`io.quarkus.hibernate.reactive.panache.Panache`)
  when an annotation does not fit the call site
- As in blocking code: one unit of work = one transaction; do not hold a transaction open across remote calls

## Tests

`@QuarkusTest` applies to reactive applications too, Dev Services still provision the database automatically,
and test methods may return `Uni` for asynchronous assertions. Follow the existing reactive test style in the
project.
