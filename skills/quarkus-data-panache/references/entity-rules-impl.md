# Entity Implementation Rules

Apply these rules when writing or modifying any Panache entity. All rules assume the conventions resolved
in `entity-conventions.md` (step 1.5) are already applied.

---

## Class — creating a new entity class

- Annotate with `@Entity`
- If naming strategy = explicit (step 1.5) — add `@Table(name = "...")` with the name derived from the table
  name template convention
- If naming strategy = implicit — add `@Table` without `name`
- Extend the base class resolved in step 1.5:
  - `PanacheEntity` (default) — provides `public Long id` and the Active Record API; do NOT redeclare `id`
  - `PanacheEntityBase` — use when a custom `@Id` type is required (see the Id section below)
  - no Panache base — plain JPA entity; Panache helpers are not available on it
- Field access per step 1.5: `public` fields for Panache entities (no accessors), or `private` fields with
  accessors written in the project's style
- Keep the import for the base class: `io.quarkus.hibernate.orm.panache.PanacheEntity` /
  `io.quarkus.hibernate.orm.panache.PanacheEntityBase`

---

## Active Record statics

When the resolved Panache style is Active Record, custom finders are `static` methods on the entity itself,
named after the repository naming convention:

```java
public static Person findByName(String name) {
    return find("name", name).firstResult();
}

public static List<Person> findAlive() {
    return list("status", Status.Alive);
}
```

Static methods on the entity may only be added to entities extending a Panache base class — for plain JPA
entities put the same methods on the repository instead.

---

## Id

Every entity must have an `id` — either inherited from `PanacheEntity` or declared directly. Before adding
`id` to an entity, check the base class: if it extends `PanacheEntity`, `id` is already there and must not be
redeclared.

If `id` must be declared directly (entity extends `PanacheEntityBase` or is a plain `@Entity`):

**Database-generated (SEQUENCE)** — declare `Long id` with the following annotations:

- Annotate with `@Id`
- Annotate with `@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "<name>")`
- If sequence scope = dedicated per table — also annotate with `@SequenceGenerator(name = "<name>")` using an
  entity-specific name (e.g. `loan_seq`)
- If sequence scope = shared — also annotate with `@SequenceGenerator(name = "<shared_name>")` using the shared
  name found in existing entities
- If sequence scope = Hibernate default — omit `@SequenceGenerator`
- If naming strategy = explicit — annotate with `@Column(name = "id", nullable = false)`

**Database-generated (IDENTITY)** — declare `Long id` with:

- `@Id` + `@GeneratedValue(strategy = GenerationType.IDENTITY)`
- `@Column(name = "id", nullable = false)` when naming is explicit

**Client-generated** — declare `UUID id` with:

- `@Id` + `@GeneratedValue(strategy = GenerationType.UUID)`
- `@Column(name = "id", nullable = false)` when naming is explicit

Note: Panache's Active Record finders (`findById`, `deleteById`, ...) always work against the declared `id`
field — a custom ID type therefore requires `PanacheRepositoryBase<Entity, ID>` for repository-style code.

---

## Field Annotation Rules

Every field must have `@Column` with an explicit `name` when the naming strategy is explicit:

```java
// CORRECT
@Column(name = "birth_date")
private LocalDate birthDate;

// WRONG — missing explicit column name
private LocalDate birthDate;
```

**Validation** — use Bean Validation (jakarta.validation) for field constraints, not ad-hoc checks in
service code. The `quarkus-hibernate-validator` extension must be present in the build.

---

## Field Type Rules

### BigDecimal

`BigDecimal` must always be declared with explicit `precision` and `scale` in `@Column` — without them
Hibernate uses database defaults which vary across vendors and cause precision loss:

```java
// CORRECT
@Column(name = "price", precision = 10, scale = 2)
private BigDecimal price;

// WRONG — missing precision and scale
@Column(name = "price")
private BigDecimal price;
```

---

## Relationship Rules

### OneToMany

Prefer **bidirectional** `@OneToMany` over unidirectional — unidirectional requires an extra join table or
produces inefficient SQL (extra DELETE + INSERT on collection changes). In a bidirectional relationship the
`@ManyToOne` side owns the FK column:

```java
// Parent side
@OneToMany(mappedBy = "owner", fetch = FetchType.LAZY)
@OrderBy("name")
private Set<Pet> pets = new LinkedHashSet<>();

// Child side owns the FK
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "owner_id")
private Owner owner;
```

Use `Set<>` initialized as `LinkedHashSet` (preserves insertion order) as the default collection type — the
child entity then needs correct `equals`/`hashCode` (see below). If `List` is used instead, `equals`/`hashCode`
on the child side are not required.

### ManyToOne

```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "owner_id")
private Owner owner;
```

- No cascade on `@ManyToOne` (reference to existing data)
- Always specify `@JoinColumn(name = "...")` explicitly
- `FetchType.LAZY` by default — override to `EAGER` only when explicitly needed

### ManyToMany

```java
@ManyToMany
@JoinTable(
    name = "vet_specialties",
    joinColumns = @JoinColumn(name = "vet_id"),
    inverseJoinColumns = @JoinColumn(name = "specialty_id")
)
private Set<Specialty> specialties;
```

- Always use `Set` for many-to-many collections — `List` makes Hibernate delete and reinsert all rows on
  every change; use `List` only as a last resort
- Always define `@JoinTable` with an explicit table name and both join columns
- The inverse-side entity must have `equals`/`hashCode` — `Set` requires them for correct behavior

---

## PanacheQL Rules

- Bind every value — never concatenate input into the query string:
  - single parameter: positional form (1-based) — `find("name = ?1", name)`
  - multiple parameters: named form with a `Map` — `find("name = :name and status = :status", Map.of("name", name, "status", status))`
    (`java.util.Map`)
- Ordering: pass `Sort` as an extra argument instead of appending `ORDER BY` when the project uses `Sort`:
  `list("status", Sort.by("name"), Status.Alive)` (`io.quarkus.panache.common.Sort`)
- Pagination: `Page.of(index, size)` is **0-based**; apply it to a `PanacheQuery`:
  `find("status", status).page(Page.of(0, 20)).list()` (`io.quarkus.panache.common.Page`)
- Entity queries (`find`, `list`, `count`, `delete`, `update`, `stream`) target the entity named by the
  calling class — no `FROM Entity` prefix is needed unless the query joins another entity
- Updates and deletes return the number of affected rows; keep the returned value when the caller needs it
- Named queries: declare them with `@NamedQuery`/`@NamedQueries` on the entity (or its super class) and
  reference the name with the `#` prefix — `find("#Person.getByName", name)`, or
  `count("#Person.countByStatus", Map.of("status", status))` for a counted query
- Write operations (`persist`, `update`, `delete`, `flush`) require an active transaction — see
  [`transaction-conventions.md`](transaction-conventions.md)
- Prefer `persistAndFlush()` over `persist()` when the generated identifier is needed immediately after the
  call (e.g. for the response body)

---

## equals & hashCode

Never include relation fields (`@ManyToOne`, `@OneToMany`, `@ManyToMany`, `@OneToOne`) in `equals`/`hashCode` —
accessing them triggers lazy loading and causes `LazyInitializationException` outside a transaction. Only
include relation fields if the user explicitly requests it.

If no equals/hashCode convention exists in the project (step 1.5: style = none) — do not generate them.

**Manual proxy-safe pattern** — correctly handles uninitialized Hibernate proxies:

```java
@Override
public final boolean equals(Object o) {
    if (this == o) return true;
    if (o == null) return false;
    Class<?> objectEffectiveClass = o instanceof HibernateProxy proxy
        ? proxy.getHibernateLazyInitializer().getPersistentClass() : o.getClass();
    Class<?> thisEffectiveClass = this instanceof HibernateProxy proxy
        ? proxy.getHibernateLazyInitializer().getPersistentClass() : this.getClass();
    if (thisEffectiveClass != objectEffectiveClass) return false;
    Pet other = (Pet) o;
    return getId() != null && Objects.equals(getId(), other.getId());
}

@Override
public final int hashCode() {
    return this instanceof HibernateProxy proxy
        ? proxy.getHibernateLazyInitializer().getPersistentClass().hashCode()
        : getClass().hashCode();
}
```

Imports: `org.hibernate.proxy.HibernateProxy`, `java.util.Objects`.

---

## toString

Never include relation fields in `toString()` — accessing them triggers lazy loading and causes
`LazyInitializationException`. Include only local (non-relation) fields:

```java
@Override
public String toString() {
    return "Pet{id=" + id + ", name='" + name + "'}";
}
```

If the project's convention is "none" (step 1.5) — do not generate `toString()`.
