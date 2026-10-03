# Describe a JPA / Panache Entity

How to read an entity file and produce a source-backed summary.

## Locate and confirm entities

Entities may live in packages such as `.domain`, `.entity`, or `.model`. Search Java sources for both `@Entity` and `@jakarta.persistence.Entity`, then inspect imports and read matches to confirm the annotation. Also find classes extending `PanacheEntity` or `PanacheEntityBase` to identify inherited Panache APIs and IDs, but do not classify a subclass as a JPA entity from that inheritance alone: confirm its own `@Entity`/`@jakarta.persistence.Entity` annotation. Do not conclude that an entity is absent from an FQN-only grep.

## Extract from each source

1. **Class and persistence style** — `PanacheEntity`, `PanacheEntityBase`, or plain JPA entity; distinguish synchronous and reactive Panache from build dependencies.
2. **ID strategy** — actual `@Id` / `@GeneratedValue` mapping; `PanacheEntity` supplies an implicit `Long id`.
3. **Fields** — declared fields/accessors, types, and source-visible constraints (for example `@Column(nullable = false)`, `@NotNull`).
4. **Relations** — annotations and mapped sides, such as `@ManyToOne`, `@OneToMany(mappedBy = ...)`, and `@ManyToMany`.
5. **Active Record methods** — static finders declared on the entity.
6. **Query style** — distinguish PanacheQL fragments (for example `"name = ?1"` or `"ORDER BY name"`), named/named-native queries, and other query forms. The registered JPA named-query name is commonly `"Person.findByName"`; Panache invokes it as `find("#Person.findByName", name)`.
7. **equals/hashCode/toString** — report only relevant source-backed behavior; avoid traversing lazy relations in descriptions.

## Report

Keep the description compact and evidence-backed, for example:

```text
Order.java: Order (id: Long, status: OrderStatus, totalAmount: BigDecimal) → has many OrderItem (LAZY) → references Product
```

For reactive Panache, mention the reactive return shape only when visible in the actual source; do not infer APIs from the extension name alone. Plain `@Entity` without Panache is still a valid JPA entity to describe, but has no implied Panache repository/query behavior.

## Common traps

- `PanacheEntity` provides `public Long id`; do not claim it is declared in the entity source or add a second id.
- Plain JPA entities in a Panache project may intentionally use ordinary JPA; describe the actual class rather than reclassifying it.
- Check whether mapping annotations are on fields or accessors before describing the project convention.
