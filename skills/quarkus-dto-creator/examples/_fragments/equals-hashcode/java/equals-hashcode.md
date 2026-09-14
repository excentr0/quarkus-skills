# equals() and hashCode() (Java)

## Insert Point
As methods in the class body, after getters/setters.

## Code

```defaults
// Default: generated (isEqualsHashCode=true by default).
// Indentation: use the project's detected indent unit (see SKILL.md § Indentation).
```

```java
@Override
public boolean equals(Object o) {
	if (this == o) return true;
	if (o == null || getClass() != o.getClass()) return false;
	${className} entity = (${className}) o;
	return java.util.Objects.equals(this.${field1}, entity.${field1}) &&
		java.util.Objects.equals(this.${field2}, entity.${field2});
}

@Override
public int hashCode() {
	return java.util.Objects.hash(${field1}, ${field2});
}
```

**When no fields:**
```java
@Override
public boolean equals(Object o) {
	if (this == o) return true;
	if (o == null || getClass() != o.getClass()) return false;
	return true;
}

@Override
public int hashCode() {
	return java.util.Objects.hash();
}
```

## Formatting rules
- Cast variable name is always `entity`.
- The `&&` chain hangs on the right side of the previous line; each continuation line is indented
  one extra unit beyond `return`.
- Methods are separated by a single blank line.

## Note
DTOs are never Hibernate proxies — a proxy-aware equals variant is deliberately NOT generated for
DTOs. (Panache entities get the proxy-safe pattern in the `quarkus-data-panache` skill; DTOs do not.)

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${className}` | DTO class name | -- |
| `${fieldN}` | field names from the selected entity attributes | -- |