# PATCH_MANY method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
No DTO:
```java
@jakarta.ws.rs.PATCH
@jakarta.transaction.Transactional
public java.util.List<${IdType}> patchMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids, ${JsonNodeFqn} patchNode) {
    java.util.List<${EntityFqn}> ${entityVarPlural} = ${repoFieldName}.list("id in ?1", ids);
    for (${EntityFqn} ${entityVar} : ${entityVarPlural}) {
        try {
            objectMapper.readerForUpdating(${entityVar}).readValue(patchNode);
        } catch (${JsonProcessingExceptionFqn} e) {
            throw new jakarta.ws.rs.BadRequestException("Invalid patch payload: " + e.getMessage());
        }
    }
    return ${entityVarPlural}.stream()
            .map(entity -> ${idAccessExpression})
            .toList();
}
```

### with DTO + mapper
```java
@jakarta.ws.rs.PATCH
@jakarta.transaction.Transactional
public java.util.List<${IdType}> patchMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids, ${JsonNodeFqn} patchNode) {
    java.util.List<${EntityFqn}> ${entityVarPlural} = ${repoFieldName}.list("id in ?1", ids);
    for (${EntityFqn} ${entityVar} : ${entityVarPlural}) {
        ${DtoFqn} ${dtoVar} = ${mapperFieldName}.${toDtoMethodName}(${entityVar});
        try {
            objectMapper.readerForUpdating(${dtoVar}).readValue(patchNode);
        } catch (${JsonProcessingExceptionFqn} e) {
            throw new jakarta.ws.rs.BadRequestException("Invalid patch payload: " + e.getMessage());
        }
        ${mapperFieldName}.${updateEntityMethodName}(${dtoVar}, ${entityVar});
    }
    return ${entityVarPlural}.stream()
            .map(entity -> ${idAccessExpression})
            .toList();
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${EntityFqn}` | entity FQN | -- |
| `${DtoFqn}` | DTO FQN | -- |
| `${dtoVar}` | decapitalized DTO name | -- |
| `${IdType}` | entity ID type (boxed) | -- |
| `${repoFieldName}` | repository field name | -- |
| `${entityVar}` | decapitalized entity name | -- |
| `${entityVarPlural}` | pluralized entity var | -- |
| `${idAccessExpression}` | ID access inside a lambda whose parameter is `entity` (Step 2) | `entity.id` (or `entity.getId()`) |
| `${mapperFieldName}` | mapper field name | -- |
| `${toDtoMethodName}` | mapper entity->DTO method | `toDto` |
| `${updateEntityMethodName}` | mapper method copying DTO into an existing entity | `updateEntity` |
| `${JsonNodeFqn}` | Jackson JsonNode FQN, resolved in Step 1 | `com.fasterxml.jackson.databind.JsonNode` |
| `${JsonProcessingExceptionFqn}` | Jackson exception FQN, resolved in Step 1 | `com.fasterxml.jackson.core.JsonProcessingException` |

## Notes
- Returns the IDs of the patched rows.
- The same patch payload is applied to every selected entity.
- Entities are managed inside the transaction — changes are flushed on commit.
