# Sub-DTO Creation Rules

## SubDtoType options

When an entity has association attributes (`@ManyToOne`, `@OneToOne`, `@OneToMany`, `@ManyToMany` in
`jakarta.persistence`), each association can be handled differently.

**Four options are available, identical for ToOne and ToMany:**

| Option | SubDtoType | Notes |
|---|---|---|
| New Class | `NEW_CLASS` | separate file; sub-entity scalars auto-selected |
| New Nested Class | `NEW_NESTED_CLASS` | inner class/record in the parent DTO; sub-entity scalars auto-selected |
| Existing Class | `EXIST_CLASS` | reuse an existing DTO for the sub-entity |
| Flat | `FLAT` | inline sub-entity attributes into the parent (see below) |

**There is NO "Only ID" option** — not for ToOne, not for ToMany, not at any nesting level. Never
offer "Only ID" as a separate option. The "association id only" effect is achieved via
**Flat with only the `id` sub-attribute checked** (see "Flat — id-only" below).

The 4 options are the same for ToOne and ToMany; the **only** ToOne/ToMany difference lies in what
Flat produces (composite singular field for ToOne, composite plural collection for ToMany).

## Reading associations from the entity source

This skill is file-based: read the entity `.java` file and extract association attributes.

**How to find them:**
- grep the entity file for `@ManyToOne`, `@OneToOne`, `@OneToMany`, `@ManyToMany`.
- The attribute is the field (or getter) carrying the annotation.

**Panache entity specifics:**
- Active Record entities declare **public fields** (`public Customer customer;`) — read the field
  name and type directly.
- Collection associations are usually initialized in the declaration:
  `public List<OrderItem> items = new ArrayList<>();` — the element type is inside the generic.
- **`PanacheEntity` provides `public Long id` implicitly** — it is NOT declared in the source. Treat
  `id` (`java.lang.Long`) as the first scalar attribute of every entity extending `PanacheEntity`.
  Entities extending `PanacheEntityBase` (or plain `@Entity` classes) declare their own `@Id` field —
  read its name and type (may be `UUID`, `Integer`, composite, …).
- Plain `@Entity` classes may use private fields with getters/setters — in that case take the
  attribute name from the getter and the type from the field or getter return type.

## Auto-selection of sub-entity attributes when expanding

When the user picks **New Class**, **New Nested Class** or **Flat** on an association, **auto-select
every scalar attribute** of the sub-entity (id, name, …), leaving the sub-entity's own associations
unselected. The user is then free to drop individual sub-attributes; in particular, keeping only
`id` is the way to get the "association id only" effect (see Flat below).

## Bulk-selection shortcuts

Two bulk-selection modes are supported when including the entity's attributes:

1. **Basic attributes** — include all scalar (non-association) fields of the root entity.
   Associations are left out.
2. **Basic and association id attributes** — include all scalar fields **and** for every ToOne
   association, switch it to **Flat** with only the sub-entity's `id` selected. ToMany associations
   are left out.

Treat "include association IDs" as syntactic sugar for "Flat + only the id sub-attribute" — the
underlying mechanism is the same.

## NEW_CLASS (separate file)

Creates a new DTO file via recursive generation. The sub-DTO inherits ALL parent options:
equalsHashCode, toString, allArgsConstructor, isMutable, fluentSetters, isJavaRecord,
isJsonIgnoreUnknownProperties, serializableType.

The field in the parent DTO uses the sub-DTO short name as its type, and an `import` line for the
sub-DTO is added.

The new file's class-level Javadoc uses the **short name + import** form (see
`examples/_fragments/javadoc/java/javadoc.md`). This is the **same form as every other Javadoc**
generated — there is no asymmetry between top-level and sub-DTO Javadocs.

## NEW_NESTED_CLASS (inner class/record)

**Java non-record:**
```java
public static class ${SubDtoName} {
	// fields, constructors, getters/setters — same rules as the parent
}
```

**Java record:**
```java
public record ${SubDtoName}(${Type1} ${field1}, ${Type2} ${field2}) {
}
```

For Java, also apply the Javadoc fragment (`examples/_fragments/javadoc/java/javadoc.md`, "Nested
class" variant) above the `public static class …` / `public record …` declaration. It uses the short
name `{@link Pet}` plus an `import` for the sub-entity FQN — same as the top-level form.

## EXIST_CLASS (reuse an existing DTO)

Use this option when the project already has a DTO for the sub-entity that should be reused instead of
generating a new one.

### How to detect candidates

For each association attribute that the skill is about to handle, search the DTO target package (and,
if nothing is found there, the whole source tree) for existing DTOs of the sub-entity:

- glob/grep for `${SubEntityName}Dto.java`, `${SubEntityName}Request.java`, `${SubEntityName}Response.java`;
- also grep for `record ${SubEntityName}Dto` / `class ${SubEntityName}Dto` declarations;
- collect the matches as the EXIST_CLASS candidates for that association.

The search is per-association and on-demand: do not pre-fetch it in Step 1 or Step 2 of `SKILL.md`.

### How to apply EXIST_CLASS

- Field type in the parent DTO = the chosen existing DTO **short name**.
- Add an `import ${existingDtoFqn};` line (unless the existing DTO is in the same package as the
  parent DTO).
- Do NOT generate a new file or a new nested class/record for this attribute.
- For collection associations (`List<Pet>`), the field type becomes `List<PetDto>` — the collection
  wrapper stays, only the element type is replaced.

### Sanity check

Before substituting, check that the candidate DTO actually targets the sub-entity — its class-level
Javadoc should contain `{@link ${SubEntityName}}` (this skill and `quarkus-dto-creator` output always
generate that Javadoc). If the found class does not match, fall back to NEW_NESTED_CLASS and warn the
user.

## FLAT (flatten) — works for BOTH ToOne and ToMany

Flat **inlines** the chosen sub-entity attributes into the parent DTO. The exact result depends on
cardinality and on which sub-attributes the user left checked.

### Flat on ToOne (`@ManyToOne`, `@OneToOne`)

For each checked scalar sub-attribute, a field is added to the parent with **composite singular
naming**:

```text
${associationName} + ${SubAttributeName capitalised}
```

Examples (Order → Customer):
- Sub-attributes checked: `id` only → parent gets `Long customerId`
- Sub-attributes checked: `id`, `name` → parent gets `Long customerId`, `String customerName`

If the user leaves only `id` checked under Flat, the result is the classic "association id only" form.
There is no separate option for this — Flat with id-only IS the mechanism, and the
"Basic + association id" bulk-selection shortcut produces exactly this configuration automatically.

### Flat on ToMany (`@OneToMany`, `@ManyToMany`, `List<X>`, `Set<X>`)

For each checked scalar sub-attribute, a **collection** field is added to the parent with **composite
plural naming**:

```text
singular(${associationName}) + ${SubAttributeName capitalised} + s   →   wrapped in the original collection type
```

Examples (Order → OrderItem, where the field is `items: List<OrderItem>`):
- Sub-attributes checked: `id` only → parent gets `List<Long> itemIds`
- Sub-attributes checked: `id`, `productName` → parent gets `List<Long> itemIds` AND
  `List<String> itemProductNames`

The collection wrapper (`List`/`Set`) is preserved; only the element type is replaced. The base name is
the **singular** form of the association name (`items → item`, `pets → pet`).

**Important:** Flat works correctly for collections, but only **after** the user explicitly checks at
least one sub-attribute. If the user picks Flat without checking anything, no fields are generated for
that association. Auto-check the sub-entity scalars when switching to Flat (same behaviour as for
NEW_NESTED_CLASS), so this corner case never occurs.

## Filtered fields — back-references

**Do NOT offer** back-reference `@ManyToOne` fields in the attribute list. Concretely: `Pet` has an
`Order order` field annotated `@ManyToOne`, but when creating the `Pet` DTO, `order` is excluded
because it points back to a parent entity that owns `Pet`.

Rule: when listing the entity's attributes, **drop any `@ManyToOne` field whose target entity also has
a `@OneToMany` / `@ManyToMany` collection of the current entity**. To check this, read the target
entity's source file (the association type) and grep it for a collection of the current entity type.
Do not offer such fields to the user.

## Reactive projects

The DTO shape does not change in reactive projects (`quarkus-hibernate-reactive-panache`). Only the
conversion point moves: mapping entity → DTO happens inside the `Uni` chain, and lazy associations must
be fetched before mapping (see `SKILL.md` § Reactive projects). The sub-DTO options above apply as-is.

## Asking the user

For each association attribute found in the entity source (after filtering back-references), use the
harness's structured-question tool. If the tool supports preview/code-shape options, show the concrete
code shape for each option.

### ToOne (`@ManyToOne`, `@OneToOne`)

| Option | Label | Description |
|--------|-------|-------------|
| Flat (Recommended) | `Flat — only ${type}Id` | Most compact form: a single `${type}Id` field |
| New Nested Class | `Nested record/class` | Nested class/record with sub-entity scalars |
| New Class | `Separate file` | Separate DTO file for the sub-entity |
| Existing Class | `Existing class` | Reuse an existing DTO (offer only when a candidate was found) |

Default: **Flat with only `id` checked** — the most compact and common combination.

### ToMany (`@OneToMany`, `@ManyToMany`, `List<X>`, `Set<X>`)

| Option | Label | Description |
|--------|-------|-------------|
| New Nested Class (Recommended) | `Nested record/class` | Nested class/record with sub-entity scalars |
| New Class | `Separate file` | Separate DTO file for the sub-entity |
| Existing Class | `Existing class` | Reuse an existing DTO (offer only when a candidate was found) |
| Flat | `Flat — scalar collection` | `${Collection}<${IdType}> ${singular}Ids` etc. |

Default: **New Nested Class**.

In both cases, **never** offer "Only ID" as a separate option — that option does not exist. It is
achieved via Flat-with-id-only.