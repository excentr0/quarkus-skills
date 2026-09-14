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

`Mappers.getMapper(...)` uses reflection to locate the generated implementation. In native
mode this only works when the mapper class is registered for reflection — in a Quarkus project
that is exactly what the `io.quarkiverse.mapstruct:quarkus-mapstruct` extension does. Prefer
the CDI component model anyway; the factory field exists for plain-MapStruct setups.