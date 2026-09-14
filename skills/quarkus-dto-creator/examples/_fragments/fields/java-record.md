# Java record components

## Insert Point
Replace the empty record header `()` in the record declaration.

## Code

```defaults
// Default: record components for all selected attributes, validators inlined.
// Quarkus validates these via quarkus-hibernate-validator when the resource
// parameter is annotated with @Valid.
```

Generate record components joined by `, `:

```java
public record ${className}(${validationAnnotations}${Type1} ${field1}, ${validationAnnotations}${Type2} ${field2}) {
}
```

**With validation annotations** (inline before the type, space-separated when there are several):
```java
public record ${className}(@jakarta.validation.constraints.NotNull java.lang.String name, java.lang.Long id) {
}
```

If the component list makes the line exceed the project's line length convention, put one component per line, indented one extra level:

```java
public record ${className}(
		@jakarta.validation.constraints.NotBlank java.lang.String name,
		@jakarta.validation.constraints.NotNull java.lang.Long id) {
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${className}` | user choice | `${EntityName}Dto` |
| `${fieldN}` | entity attribute name | -- |
| `${TypeN}` | entity attribute type FQN (or sub-DTO type) | -- |
| `${validationAnnotations}` | constraints inherited from the entity field (+ user overrides), inline before the type | empty |