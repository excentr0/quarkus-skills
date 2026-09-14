# Getters (Java)

## Insert Point
As methods in the class body, after constructors. **When `isMutable=true`, getters are NOT emitted
as a single block — they are interleaved with setters (`getX, setX, getY, setY, …`). See
`setters.md` for the interleaved layout.**

## Code

```defaults
// Default: always generated for Java plain-class DTOs.
// Format: multi-line, body indented.
```

For each field (always uses the `get` prefix, even for `boolean`):
```java
public ${Type} get${Name}() {
	return ${fieldName};
}
```

## Formatting rules
- **Multi-line**: signature on its own line, `return ...;` indented one level, closing `}` on its own line.
  Never collapse to one line.
- **One blank line** between consecutive getters (and between a getter and the next setter when
  interleaved in mutable mode).
- Indentation: use the project's detected indent unit (see SKILL.md § Indentation).

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${Name}` | capitalized field name | -- |
| `${fieldName}` | field name | -- |
| `${Type}` | field type | -- |