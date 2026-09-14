# PATCH method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
No DTO:
```java
@jakarta.ws.rs.PATCH
@jakarta.ws.rs.Path("/{id}")
@jakarta.transaction.Transactional
public ${EntityFqn} patch(@jakarta.ws.rs.PathParam("id") ${IdType} id, ${JsonNodeFqn} patchNode) {
    ${EntityFqn} ${entityVar} = ${repoFieldName}.findByIdOptional(id)
            .orElseThrow(() -> new jakarta.ws.rs.NotFoundException("Entity with id `%s` not found".formatted(id)));
    try {
        objectMapper.readerForUpdating(${entityVar}).readValue(patchNode);
    } catch (${JsonProcessingExceptionFqn} e) {
        throw new jakarta.ws.rs.BadRequestException("Invalid patch payload: " + e.getMessage());
    }
    return ${entityVar};
}
```

### with DTO + mapper
```java
@jakarta.ws.rs.PATCH
@jakarta.ws.rs.Path("/{id}")
@jakarta.transaction.Transactional
public ${DtoFqn} patch(@jakarta.ws.rs.PathParam("id") ${IdType} id, ${JsonNodeFqn} patchNode) {
    ${EntityFqn} ${entityVar} = ${repoFieldName}.findByIdOptional(id)
            .orElseThrow(() -> new jakarta.ws.rs.NotFoundException("Entity with id `%s` not found".formatted(id)));
    ${DtoFqn} ${dtoVar} = ${mapperFieldName}.${toDtoMethodName}(${entityVar});
    try {
        objectMapper.readerForUpdating(${dtoVar}).readValue(patchNode);
    } catch (${JsonProcessingExceptionFqn} e) {
        throw new jakarta.ws.rs.BadRequestException("Invalid patch payload: " + e.getMessage());
    }
    ${mapperFieldName}.${updateEntityMethodName}(${dtoVar}, ${entityVar});
    return ${mapperFieldName}.${toDtoMethodName}(${entityVar});
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${EntityFqn}` | entity FQN | -- |
| `${DtoFqn}` | DTO FQN | -- |
| `${dtoVar}` | decapitalized DTO name | -- |
| `${IdType}` | entity ID type | -- |
| `${repoFieldName}` | repository field name | -- |
| `${entityVar}` | decapitalized entity name | -- |
| `${mapperFieldName}` | mapper field name | -- |
| `${toDtoMethodName}` | mapper entity->DTO method | `toDto` |
| `${updateEntityMethodName}` | mapper method copying DTO into an existing entity | `updateEntity` |
| `${JsonNodeFqn}` | Jackson JsonNode FQN, resolved in Step 1 | `com.fasterxml.jackson.databind.JsonNode` |
| `${JsonProcessingExceptionFqn}` | Jackson exception FQN, resolved in Step 1 | `com.fasterxml.jackson.core.JsonProcessingException` |

## Notes
- The patched entity is managed inside the transaction — no explicit save call; changes are
  flushed on commit.
- The `objectMapper` field is injected by WA2 (`examples/_beans/injection/java.md`) — see the
  VERIFY note there about ObjectMapper injectability.
- A malformed patch payload returns 400, not 500.
