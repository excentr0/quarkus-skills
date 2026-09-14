# Nested/inner class (Java)

## Insert Point

**Java class parent (non-record):** immediately before the closing `}` of the parent DTO class body,
after the last generated member (last getter/setter/equals/hashCode/toString). One blank line above
and below the nested declaration.

**Java record parent:** immediately before the closing `}` of the parent record. The parent record's
body is `{ }` (empty) when no nested classes are generated; for each `NEW_NESTED_CLASS` association,
insert the nested record **inside** that body. One blank line between the opening `{` and the first
nested record, and one blank line between adjacent nested records.

Use the Edit tool with the closing `}` of the parent as the anchor — never rewrite the whole file.

## Code

```defaults
// Default: skip (only when an attribute has subDtoType=NEW_NESTED_CLASS)
```

**Java class (non-record) — nested static class:**
```java
public static class ${subDtoName} {
	// fields, constructors, getters/setters generated recursively
}
```

The Javadoc above the `public static class …` line uses the **short name + import** form (see
`examples/_fragments/javadoc/java/javadoc.md`, "Nested class" variant). The body of the nested class
is generated recursively following the same Generation Order as the parent (fields, constructor,
getters, equals, toString, …) and inherits the parent's indent style.

**Java record — nested record (REQUIRED when the parent is a record):**
```java
public record ${subDtoName}(${Type1} ${field1}, ${Type2} ${field2}) {
}
```

When the parent DTO is a `public record`, the inner class for every `NEW_NESTED_CLASS` association
MUST also be a `public record` — never a `public static class`. The skill MUST NOT silently fall back
to `NEW_CLASS` (separate file) just because the record form looks shorter.

### How to fill the nested record's component list

For each scalar attribute of the sub-entity (auto-selected per `references/sub-dto.md`,
"Auto-selection of sub-entity attributes"), generate a record component using the same rules as the
top-level record body — i.e. `examples/_fragments/fields/java-record.md`:

- One component per scalar: `${Type} ${fieldName}`
- All inherited validators are **inlined onto the component parameter**
  (e.g. `@NotBlank String name`, `@Pattern(regexp="…") @NotBlank String telephone`)
- Multiple validators on the same component are space-separated
- Components are comma-separated, one per line when the line would be long, indented one level
  deeper than the `public record …(` line
- Back-reference associations of the sub-entity are filtered out (same rule as for the top level —
  see `references/sub-dto.md`, "Filtered fields")
- The sub-entity's own associations are NOT expanded recursively in the nested record (only scalars).
  If the user wants deeper nesting, they must ask for it explicitly

The nested record does NOT need its own skeleton, `@JsonIgnoreProperties`, or `Serializable` — those
apply only to the top-level DTO.

The Javadoc above the `public record ${subDtoName}(…)` line uses the **short name + import** form
(same "Nested class" variant of `examples/_fragments/javadoc/java/javadoc.md`).

### Example — `Order` with `List<OrderItem> items`

Parent record (after Step 6 of `references/java-record.md`):
```java
public record OrderDto(java.lang.Long id, java.lang.String number, java.util.List<OrderItemDto> items) {

	/**
	 * DTO for {@link OrderItem}
	 */
	public record OrderItemDto(java.lang.Long id, java.lang.String productName, int quantity) {
	}
}
```

Note: the parent record's `items` component already uses the nested `OrderItemDto` short name as the
element type — the field type substitution happens in `fields/java-record.md`, not here.

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${subDtoName}` | sub-DTO class name from the attribute | `${SubEntityName}Dto` (auto-suffixed on collision) |
| `${fieldN}` | sub-entity scalar attribute names | -- |
| `${TypeN}` | sub-entity scalar attribute types | -- |