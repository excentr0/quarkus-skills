# PATCH_MANY method (Java)

## Insert Point
Add the shared PATCH helpers from `patch/java.md` once if not already present; insert this endpoint for PATCH_MANY.

## Code

### no DTO
```java
@jakarta.ws.rs.PATCH
@jakarta.transaction.Transactional
public java.util.List<${IdType}> patchMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids, com.fasterxml.jackson.databind.JsonNode patchNode) {
    assertPatchAllowed(patchNode);
    java.util.List<${EntityFqn}> ${entityVarPlural} = ${repoFieldName}.list("id in ?1", ids);
    for (${EntityFqn} entity : ${entityVarPlural}) {
        applyPatch(entity, patchNode);
    }
    return ${entityVarPlural}.stream().map(entity -> ${idAccessExpression}).toList();
}
```

### with DTO + mapper
```java
@jakarta.ws.rs.PATCH
@jakarta.transaction.Transactional
public java.util.List<${IdType}> patchMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids, com.fasterxml.jackson.databind.JsonNode patchNode) {
    assertPatchAllowed(patchNode);
    java.util.List<${EntityFqn}> ${entityVarPlural} = ${repoFieldName}.list("id in ?1", ids);
    for (${EntityFqn} entity : ${entityVarPlural}) {
        ${DtoFqn} current = ${mapperFieldName}.${toDtoMethodName}(entity);
        ${DtoFqn} merged = mergePatchDto(current, patchNode);
        validatePatchState(merged);
        ${mapperFieldName}.${updateEntityMethodName}(merged, entity);
        validatePatchState(entity);
    }
    return ${entityVarPlural}.stream().map(entity -> ${idAccessExpression}).toList();
}
```

## Variables
| Variable | Source | Default |
|---|---|---|
| `${EntityFqn}` | entity FQN | — |
| `${DtoFqn}` | DTO FQN | — |
| `${IdType}` | boxed entity ID type | — |
| `${repoFieldName}` | repository field name | — |
| `${entityVarPlural}` | pluralized entity variable | — |
| `${idAccessExpression}` | ID access for lambda parameter `entity` | `entity.id` or `entity.getId()` |
| `${mapperFieldName}` | mapper field name | — |
| `${toDtoMethodName}` | entity-to-DTO mapper method | `to${DtoShortName}` |
| `${updateEntityMethodName}` | safe mapper method updating existing entity | `partialUpdate` |
| `${patchAssignments}` | no-DTO concrete field writes, as in `patch/java.md` | required no-DTO |
| `${patchTypeChecks}` | shared per-field type/range checks, as in `patch/java.md` | required |

## Notes
- Preserves the `ids` query parameter API and returns patched IDs.
- Reuse `assertPatchAllowed` and `validatePatchState` from `patch/java.md` once. No-DTO PATCH_MANY also inserts the no-DTO `applyPatch(Entity, JsonNode)` helper from `patch/java.md` once; it is absent in DTO mode. DTO methods use shared `${patchTypeChecks}` allowlist/type checks and safe mapper contract. `${patchTypeChecks}` executes before loading/mutation; inject a `Validator` for every variant.
- Validation failure or any later batch failure escapes as an unchecked exception from the transaction, rolling back all batch changes.
