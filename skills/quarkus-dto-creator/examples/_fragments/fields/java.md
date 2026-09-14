# Java fields (plain class DTO)

## Insert Point
Inside the class body, as field declarations.

## Code

```defaults
// Default: immutable fields (private final).
// Indentation: use the project's detected indent unit (see SKILL.md § Indentation).
// Each field line is indented with one unit. Validation annotations sit on
// their own lines, also indented with one unit. No blank lines between fields.
```

For each selected attribute, generate a field:

**Immutable (isMutable=false, default):**
```java
${validationAnnotations}private final ${Type} ${fieldName};
```

**Mutable (isMutable=true):**
```java
${validationAnnotations}private ${Type} ${fieldName};
```

**Validation annotations** — each on a separate line before the field:
```java
@jakarta.validation.constraints.NotNull
@jakarta.validation.constraints.Size(min = 0, max = 255)
private final java.lang.String name;
```

For **collection** types, wrap the element type: `java.util.List<${InnerType}>`, `java.util.Set<${InnerType}>`.

For **sub-DTO** attributes (subDtoType != FLAT), use the sub-DTO type instead of the entity type.

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${fieldName}` | entity attribute name | -- |
| `${Type}` | entity attribute type FQN (or sub-DTO type for sub-DTOs), wrapped in the collection type if applicable | -- |
| `${validationAnnotations}` | constraints inherited from the entity field (+ user overrides), each as `@fqn` on its own line | empty |