---
name: quarkus-data-panache
description: >
  Rules and guidelines for working with Hibernate ORM Panache in a Quarkus project.
  ALWAYS use this skill when adding, removing, or modifying Panache entities or
  repositories, changing field annotations or database mappings, writing PanacheQL
  queries, or defining transaction boundaries. Trigger on any request that involves
  entity structure, new entities, field mapping changes, Panache repositories,
  custom finder/query methods, or transactional behavior in a Quarkus application.
  Russian phrases also trigger this: "добавь сущность", "измени поля сущности",
  "создай репозиторий Panache", "напиши запрос PanacheQL", "настрой транзакции",
  "описание модели данных".
---

# Preflight — Project detection (before any work)

This skill is harness-agnostic: it uses only file tools — no MCP server or IDE integration is required.

Detect the persistence setup from the build files before touching any code:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Persistence mode** —
   `quarkus-hibernate-orm-panache` → blocking Panache (this skill's default);
   `quarkus-hibernate-reactive-panache` → reactive Panache — read
   [`references/reactive.md`](references/reactive.md) before writing any persistence code;
   `quarkus-hibernate-orm` without a Panache extension → plain Hibernate ORM: the Panache-specific rules
   (Active Record statics, `PanacheQuery`, `PanacheRepository`) do not apply, the JPA mapping rules in
   [`references/entity-rules-impl.md`](references/entity-rules-impl.md) still do.
3. **Database driver** — `quarkus-jdbc-*` (blocking) or `quarkus-reactive-*-client` (reactive).
4. **Migrations** — `quarkus-flyway` or `quarkus-liquibase` present → schema changes require a migration file;
   never flip `quarkus.hibernate-orm.database.generation` as a shortcut for a schema change.
5. **Existing style** — Active Record statics, repositories, or both? Answer this with the convention
   detection below before writing code — do not assume.

If neither Panache extension is present, stop and tell the user this skill targets Panache projects;
offer to add the extension (`./mvnw quarkus:add-extension -Dextensions="hibernate-orm-panache,jdbc-postgresql"`).
  Required dependency blocks: [`examples/_dependencies/dependencies.md`](examples/_dependencies/dependencies.md).

---

# Working with Panache Entities

When the task involves creating or modifying a Panache entity:

1. If entity conventions have not been detected yet in this conversation — check your session memory for
   previously saved conventions first. If found, reuse them. Otherwise read
   [`references/entity-conventions.md`](references/entity-conventions.md) and follow all substeps there to
   detect the project conventions. Tell the user which substep you are on while running them
   (`Step 1.1/1.5: Finding existing entities...`).
2. Read [`references/entity-rules-impl.md`](references/entity-rules-impl.md) and follow the rules there when
   writing or modifying the entity.
3. Use the skeleton in [`examples/_skeletons/panache-entity.md`](examples/_skeletons/panache-entity.md)
   as the starting shape for a new entity — fill its `${variables}`, do not invent a different structure.
4. If the project uses Flyway or Liquibase, add the schema change as a new migration file in the same commit.

# Working with Panache Repositories

When the task involves creating or modifying a repository, or adding query methods:

1. If repository conventions have not been detected yet in this conversation — reuse them from memory, or read
   [`references/repository-conventions.md`](references/repository-conventions.md) and follow the detection
   substeps there.
2. Follow the implementation rules in the same reference when writing repository code.
3. Use the skeleton in
   [`examples/_skeletons/panache-repository.md`](examples/_skeletons/panache-repository.md) as the starting
   shape for a new repository.

# Working with Transactions

When the task involves adding or modifying transactional behavior:

1. If transaction conventions have not been detected yet in this conversation — reuse them from memory, or
   read [`references/transaction-conventions.md`](references/transaction-conventions.md) and follow the
   detection substeps there.
2. Follow the rules in the same reference when writing or modifying transactional code.
3. Remember: every Panache write (`persist`, `update`, `delete`, `flush`) needs an active transaction.

# Choosing Blocking or Reactive

If the project uses `quarkus-hibernate-reactive-panache`, read [`references/reactive.md`](references/reactive.md)
before writing any persistence code — the API mirrors blocking Panache but returns `Uni<...>`, and blocking
calls must not appear on the request path.

---

# Reviewing Panache Patterns

When the user asks to review Panache patterns, conventions, or code quality in the project:

1. Detect current conventions by following `references/entity-conventions.md` (substeps 1.1–1.5) and, for
   query code, `references/repository-conventions.md` (substeps 2.1–2.5).
2. Compare the detected conventions against the rules in `references/entity-rules-impl.md`,
   `references/repository-conventions.md`, and `references/transaction-conventions.md`. For each deviation,
   output a recommendation in the format:

```text
### Panache Review

**[Convention or pattern name]**
- Current: <what the project does>
- Recommended: <what the best practice says>
- Reason: <why this matters>
```

If no deviations are found — state that the project follows best practices.

---

## Anti-hallucination checklist

- [ ] Persistence mode (blocking Panache / reactive Panache / plain Hibernate ORM) confirmed from the build
      file before writing code.
- [ ] Panache style (Active Record vs repository) taken from the project's existing code, not invented.
- [ ] Entity conventions (base class, id strategy, field access, naming, equals/hashCode) resolved from real
      code with confidence scores — uncertainties asked, not guessed.
- [ ] PanacheQL strings use the documented parameter forms only; every value is bound, never concatenated
      into the query string.
- [ ] Every write path has an active transaction; the annotation import is `jakarta.transaction.Transactional`.
- [ ] Collection types, `@JoinColumn` names, and `@Column` precision/scale follow
      `references/entity-rules-impl.md`.
- [ ] Migrations added when Flyway/Liquibase is used — no silent schema-generation changes.
- [ ] No Spring Data / Spring DI idioms in generated code; use the conversion table in
      `docs/quarkus-facts.md` if an equivalent is unclear.
