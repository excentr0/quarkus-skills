# MAPPER factory field (Java)

## Insert Point
Field inside the mapper interface body. Only when componentModel = DEFAULT.

## Code

```defaults
skip this fragment (componentModel is cdi by default)
```

### When componentModel = DEFAULT

```java
${className} MAPPER = org.mapstruct.factory.Mappers.getMapper(${className}.class);
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${className}` | user choice | `${EntityName}Mapper` |

## Note

`Mappers.getMapper(...)` uses reflection to locate the generated implementation. Native mode
requires verified reflection registration. A compatible Quarkiverse extension may provide it;
verify compatibility against the target Quarkus release before adding the extension. The
Quarkus 3.20.3 fixture verifies core CDI mapping only, not native reflection registration.
Prefer the CDI component model; the factory field exists for plain-MapStruct setups.