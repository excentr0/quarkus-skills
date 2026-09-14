# CREATE method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
No DTO, no validation:
```java
@jakarta.ws.rs.POST
@jakarta.transaction.Transactional
public ${EntityFqn} create(${EntityFqn} ${entityVar}) {
    ${repoFieldName}.persistAndFlush(${entityVar});
    return ${entityVar};
}
```

### no DTO, with @Valid
```java
@jakarta.ws.rs.POST
@jakarta.transaction.Transactional
public ${EntityFqn} create(@jakarta.validation.Valid ${EntityFqn} ${entityVar}) {
    ${repoFieldName}.persistAndFlush(${entityVar});
    return ${entityVar};
}
```

### with DTO
```java
@jakarta.ws.rs.POST
@jakarta.transaction.Transactional
public ${DtoFqn} create(${DtoFqn} ${dtoVar}) {
    ${EntityFqn} ${entityVar} = ${mapperFieldName}.${toEntityMethodName}(${dtoVar});
    ${repoFieldName}.persistAndFlush(${entityVar});
    return ${mapperFieldName}.${toDtoMethodName}(${entityVar});
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${EntityFqn}` | entity FQN | -- |
| `${EntityName}` | entity simple name | -- |
| `${DtoFqn}` | DTO FQN | -- |
| `${dtoVar}` | decapitalized DTO name | -- |
| `${entityVar}` | decapitalized entity name | -- |
| `${repoFieldName}` | repository field name | -- |
| `${mapperFieldName}` | mapper field name | -- |
| `${toEntityMethodName}` | mapper DTO->entity method | `toEntity` |
| `${toDtoMethodName}` | mapper entity->DTO method | `toDto` |

## Notes
- `persistAndFlush` (not `persist`) so a database-generated ID is assigned before the entity is
  serialized into the response.
- The request body is the unannotated parameter — JAX-RS/Quarkus deserializes it from JSON.
- `@Valid` only when `hasValidation = true` and the parameter type carries constraints.
