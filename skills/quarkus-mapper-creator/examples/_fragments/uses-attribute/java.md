# @Mapper(uses = ...) attribute (Java)

## Insert Point
Modifies existing @Mapper annotation to add uses attribute.

## Code

```defaults
skip this fragment (no sub-mappers by default)
```

### When sub-mappers exist for association DTOs

```java
@org.mapstruct.Mapper(unmappedTargetPolicy = org.mapstruct.ReportingPolicy.IGNORE, componentModel = "cdi", uses = {SubMapper1.class, SubMapper2.class})
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| sub-mapper FQNs | existing mappers for association entities, explicitly requested by the user | — |

## Note

MapStruct resolves nested sub-DTO mappings **implicitly** within the same mapper interface —
`uses` is only for reusing a sibling mapper the user explicitly named (or resolving circular
mapper dependencies). Do not grep the project for sibling mappers and do not add `uses`
speculatively; the generated nested mapping is the default and requires no configuration.