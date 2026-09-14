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

### repository + mapper + ObjectMapper (DTO mode, PATCH or PATCH_MANY selected)
<!-- ObjectMapper is a built-in CDI bean (quarkus-jackson, bundled by quarkus-rest-jackson).
     Inject it; customize serialization via ObjectMapperCustomizer beans, not by hand-building a mapper. -->
```java
private final ${RepoFqn} ${repoFieldName};
private final ${MapperFqn} ${mapperFieldName};
private final ${ObjectMapperFqn} objectMapper;

public ${ResourceName}(${RepoFqn} ${repoFieldName}, ${MapperFqn} ${mapperFieldName}, ${ObjectMapperFqn} objectMapper) {
    this.${repoFieldName} = ${repoFieldName};
    this.${mapperFieldName} = ${mapperFieldName};
    this.objectMapper = objectMapper;
}
```

### repository + ObjectMapper (no DTO, PATCH or PATCH_MANY selected)
(same ObjectMapper injectability note as the previous variant)
```java
private final ${RepoFqn} ${repoFieldName};
private final ${ObjectMapperFqn} objectMapper;

public ${ResourceName}(${RepoFqn} ${repoFieldName}, ${ObjectMapperFqn} objectMapper) {
    this.${repoFieldName} = ${repoFieldName};
    this.objectMapper = objectMapper;
}
```

### field injection (alternative)
```java
@jakarta.inject.Inject
${RepoFqn} ${repoFieldName};
```

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
