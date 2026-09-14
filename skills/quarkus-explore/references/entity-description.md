# Describe a Panache Entity

How to read an entity file and produce a summary line for the exploration report.

## Step 1 — Locate entities

Entities live in packages like `.domain`, `.entity`, `.model`. Find them:

- grep for `jakarta.persistence.Entity` across `src/main/java`.
- An entity either extends `io.quarkus.hibernate.orm.panache.PanacheEntity` (implicit `Long id`),
  `PanacheEntityBase` (declare your own `@Id`), or is a plain JPA entity.

## Step 2 — Extract from each file

1. **Class & base** — `extends PanacheEntity` / `PanacheEntityBase` / plain `@Entity`.
2. **ID strategy** — `@GeneratedValue` strategy (IDENTITY / SEQUENCE / UUID / none).
3. **Fields** — Panache convention is `public` fields; note type and constraints
   (`@Column(nullable = false)`, `@NotNull`).
4. **Relations** — `@ManyToOne(fetch = LAZY/EAGER)`, `@OneToMany(mappedBy = ...)`, `@ManyToMany`.
5. **Active Record methods** — static finders on the entity (`findByName`, `findAlive`) mean the
   Active Record pattern is used, not only repositories.
6. **Query style** — PanacheQL fragments (`"name = ?1"`, `"ORDER BY name"`) vs named queries
   (`find("Person.findByName", name)`) vs native.
7. **equals/hashCode/toString** — proxy-safe or id-based? `toString` must not touch lazy relations.

## Step 3 — Emit the summary line

```text
Order (id: Long SEQUENCE, status: OrderStatus, totalAmount: BigDecimal) → has many OrderItem (LAZY) → references Product
```

## Reactive variant

If the project uses `quarkus-hibernate-reactive-panache`, the same classes return `Uni<...>` —
note it in the report: `Person.findById(23L)` → `Uni<Person>`. Persistence is driven by
`Uni` chains, and resource methods return `Uni<Response>` instead of blocking types.

## Common traps

- `PanacheEntity` gives `public Long id` — no need to re-declare it; check for accidental duplicate `id` fields.
- Plain `@Entity` classes in a Panache project are usually intentional (no Panache features needed) — describe as-is.
- Field annotations on fields (not getters) are the Panache/JPA convention — report deviations.