# Parent interface extends clause (Java)

## Insert Point
Modifies the interface declaration to add extends clause.

## Code

```defaults
skip this fragment (no parent interface by default)
```

### When parent interface selected

```java
public interface ${className} extends ${parentFqn}<${dtoClassFqn}, ${entityClassFqn}> {
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${className}` | user choice | `${EntityName}Mapper` |
| `${parentFqn}` | user choice | — |
| `${dtoClassFqn}` | DTO class FQN | — |
| `${entityClassFqn}` | entity class FQN | — |

## Note

The parent interface must be a CDI-visible type in the same project. With
`componentModel = "cdi"` the generated implementation still implements the full
type hierarchy, so injecting the parent interface type works.