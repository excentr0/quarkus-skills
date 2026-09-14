# @Mapper annotation (Java)

## Insert Point
Annotation on the mapper interface created from skeleton.

## Code

```defaults
CDI component model is the default for Quarkus.
```

### CDI component model (default)

```java
@org.mapstruct.Mapper(unmappedTargetPolicy = org.mapstruct.ReportingPolicy.IGNORE, componentModel = "cdi")
```

### CDI component model (MappingConstants form, MapStruct 1.5+)

```java
@org.mapstruct.Mapper(unmappedTargetPolicy = org.mapstruct.ReportingPolicy.IGNORE, componentModel = org.mapstruct.MappingConstants.ComponentModel.CDI)
```

### DEFAULT component model (only when the user explicitly asked for plain MapStruct without CDI)

```java
@org.mapstruct.Mapper(unmappedTargetPolicy = org.mapstruct.ReportingPolicy.IGNORE)
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| componentModel | `cdi` for a Quarkus project; `DEFAULT` only on explicit user request | `cdi` |

## Note — recommended default

Use the **CDI** variant: the generated mapper implementation becomes a CDI bean, injectable
via constructor injection or `@Inject`, and works in native mode. The DEFAULT variant is
listed for completeness — when it is used, the `MAPPER` factory field fragment becomes
mandatory (`examples/_fragments/factory-field/java.md`).

Never use the component model of another framework (e.g. the Spring or Jakarta EE models) in
a Quarkus project — `cdi` (or DEFAULT) only.