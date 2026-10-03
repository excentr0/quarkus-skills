# Bean injection into resource (Java)

## Insert Point
Fields and constructor in the resource class body.

## Code

### defaults
Constructor injection (single bean -- repository):
```java
private final ${RepoFqn} ${repoFieldName};

public ${ResourceName}(${RepoFqn} ${repoFieldName}) {
    this.${repoFieldName} = ${repoFieldName};
}
```

### repository + mapper (DTO mode)
```java
private final ${RepoFqn} ${repoFieldName};
private final ${MapperFqn} ${mapperFieldName};

public ${ResourceName}(${RepoFqn} ${repoFieldName}, ${MapperFqn} ${mapperFieldName}) {
    this.${repoFieldName} = ${repoFieldName};
    this.${mapperFieldName} = ${mapperFieldName};
}
```

### repository + mapper + ObjectMapper + Validator (DTO mode, PATCH or PATCH_MANY selected)
<!-- ObjectMapper is a built-in CDI bean (quarkus-jackson, bundled by quarkus-rest-jackson).
     Inject it; customize serialization via ObjectMapperCustomizer beans, not by hand-building a mapper. -->
```java
private final ${RepoFqn} ${repoFieldName};
private final ${MapperFqn} ${mapperFieldName};
private final ${ObjectMapperFqn} objectMapper;
private final jakarta.validation.Validator validator;

public ${ResourceName}(${RepoFqn} ${repoFieldName}, ${MapperFqn} ${mapperFieldName}, ${ObjectMapperFqn} objectMapper, jakarta.validation.Validator validator) {
    this.${repoFieldName} = ${repoFieldName};
    this.${mapperFieldName} = ${mapperFieldName};
    this.objectMapper = objectMapper;
    this.validator = validator;
}
```

### repository + Validator (no DTO, PATCH or PATCH_MANY selected)
```java
private final ${RepoFqn} ${repoFieldName};
private final jakarta.validation.Validator validator;

public ${ResourceName}(${RepoFqn} ${repoFieldName}, jakarta.validation.Validator validator) {
    this.${repoFieldName} = ${repoFieldName};
    this.validator = validator;
}
```

### field injection (alternative)
```java
@jakarta.inject.Inject
${RepoFqn} ${repoFieldName};
```

### Validator injection (any PATCH or PATCH_MANY)
The PATCH-specific constructor variants above include the final Validator field and constructor parameter. Do not add a second copy.

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${RepoFqn}` | FQN of the repository class | -- |
| `${repoFieldName}` | decapitalized repository class name | -- |
| `${MapperFqn}` | FQN of the mapper bean | -- |
| `${mapperFieldName}` | decapitalized mapper class name | -- |
| `${ObjectMapperFqn}` | resolved in Step 1 from project dependencies | `com.fasterxml.jackson.databind.ObjectMapper` |
| `${ResourceName}` | resource class name | `{EntityName}Resource` |

## Notes
- Quarkus allows constructor injection without `@Inject` when the bean has a single constructor.
- Inject only the beans the generated methods actually use.
