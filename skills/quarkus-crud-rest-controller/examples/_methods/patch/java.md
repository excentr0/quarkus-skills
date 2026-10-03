# PATCH method (Java)

## Insert Point
Add the shared helpers once to the resource class when either PATCH or PATCH_MANY is selected; insert this endpoint for PATCH.

## Shared helpers (insert once)
```java
private void assertPatchAllowed(com.fasterxml.jackson.databind.JsonNode patchNode) {
    if (patchNode == null || !patchNode.isObject()) {
        throw new jakarta.ws.rs.BadRequestException("Patch body must be a JSON object");
    }
    java.util.Set<String> allowed = java.util.Set.of(${mutableFieldNames});
    java.util.Iterator<String> fields = patchNode.fieldNames();
    while (fields.hasNext()) {
        String field = fields.next();
        com.fasterxml.jackson.databind.JsonNode value = patchNode.get(field);
        if (!allowed.contains(field) || value.isObject() || value.isArray()) {
            throw new jakarta.ws.rs.BadRequestException("Patch contains an unsupported field or value");
        }
    }
    java.util.Set<String> primitiveFields = java.util.Set.of(${primitiveFieldNames});
    for (String field : primitiveFields) {
        if (patchNode.has(field) && patchNode.get(field).isNull()) {
            throw new jakarta.ws.rs.BadRequestException("Null is not allowed for this field");
        }
    }
${patchTypeChecks}
}

private <T> void validatePatchState(T value) {
    if (!${validatorFieldName}.validate(value).isEmpty()) {
        throw new jakarta.ws.rs.BadRequestException("Patch produces an invalid state");
    }
}
```

`patchAssignments` is assembled from one concrete per-field fragment per mutable scalar field; never deserialize a JSON object directly into a managed entity. For each field, generate a `has(field)` guard, reject null for primitives, assign null for nullable references, and perform a matching JSON-token check followed by typed conversion with conversion/range failures mapped to a sanitized `BadRequestException`. Only scalar types listed in the corresponding per-field fragment are supported; stop for other types. `${mutableFieldNames}` is a comma-separated Java string-literal list from actual mutable entity fields, excluding id, version, server-managed fields and associations. Unknown/protected keys and object/array values are rejected before any mutation.

## Shared DTO helper (DTO mode only)
```java
private ${DtoFqn} mergePatchDto(${DtoFqn} current, com.fasterxml.jackson.databind.JsonNode patchNode) {
    assertPatchAllowed(patchNode);
    com.fasterxml.jackson.databind.node.ObjectNode merged = objectMapper.valueToTree(current);
    java.util.Iterator<String> fields = patchNode.fieldNames();
    while (fields.hasNext()) {
        String field = fields.next();
        merged.set(field, patchNode.get(field));
    }
    try {
        return objectMapper.treeToValue(merged, ${DtoFqn}.class);
    } catch (com.fasterxml.jackson.core.JsonProcessingException | IllegalArgumentException e) {
        throw new jakarta.ws.rs.BadRequestException("Invalid patch payload");
    }
}
```

This merges only allowlisted scalar keys; absent DTO properties remain from the current snapshot. DTO constructors/accessors and JSON property names must be verified in source. Explicit null is preserved and must clear nullable values; null for primitive DTO properties is rejected. If the DTO representation cannot preserve these semantics, stop.

## Code

### no DTO
The no-DTO variant adds this `applyPatch` helper once (not in DTO mode):
```java
private void applyPatch(${EntityFqn} entity, com.fasterxml.jackson.databind.JsonNode patchNode) {
    assertPatchAllowed(patchNode);
${patchAssignments}
    validatePatchState(entity);
}
```

```java
@jakarta.ws.rs.PATCH
@jakarta.ws.rs.Path("/{id}")
@jakarta.transaction.Transactional
public ${EntityFqn} patch(@jakarta.ws.rs.PathParam("id") ${IdType} id, com.fasterxml.jackson.databind.JsonNode patchNode) {
    assertPatchAllowed(patchNode);
    ${EntityFqn} ${entityVar} = ${repoFieldName}.findByIdOptional(id)
            .orElseThrow(() -> new jakarta.ws.rs.NotFoundException("Entity not found"));
    applyPatch(${entityVar}, patchNode);
    return ${entityVar};
}
```

### with DTO + mapper
```java
@jakarta.ws.rs.PATCH
@jakarta.ws.rs.Path("/{id}")
@jakarta.transaction.Transactional
public ${DtoFqn} patch(@jakarta.ws.rs.PathParam("id") ${IdType} id, com.fasterxml.jackson.databind.JsonNode patchNode) {
    assertPatchAllowed(patchNode);
    ${EntityFqn} ${entityVar} = ${repoFieldName}.findByIdOptional(id)
            .orElseThrow(() -> new jakarta.ws.rs.NotFoundException("Entity not found"));
    ${DtoFqn} current = ${mapperFieldName}.${toDtoMethodName}(${entityVar});
    ${DtoFqn} merged = mergePatchDto(current, patchNode);
    validatePatchState(merged);
    ${mapperFieldName}.${updateEntityMethodName}(merged, ${entityVar});
    validatePatchState(${entityVar});
    return ${mapperFieldName}.${toDtoMethodName}(${entityVar});
}
```

The DTO merge helper must copy the current DTO snapshot, replace only validated present scalar fields, preserve absent fields, and reconstruct the DTO; it must not accept arbitrary input keys. Use project accessors / record constructor. Validate both merged DTO and resulting entity. Require the mapper safe variant in the mapper handoff.

## Variables
| Variable | Source | Default |
|---|---|---|
| `${EntityFqn}` | entity FQN | — |
| `${DtoFqn}` | DTO FQN | — |
| `${IdType}` | entity ID type | — |
| `${entityVar}` | decapitalized entity name | — |
| `${repoFieldName}` | repository field name | — |
| `${mapperFieldName}` | mapper field name | — |
| `${toDtoMethodName}` | entity-to-DTO mapper method | `to${DtoShortName}` |
| `${updateEntityMethodName}` | safe mapper method updating existing entity | `partialUpdate` |
| `${mutableFieldNames}` | explicit mutable scalar field names as Java string literals; excludes protected fields/associations | required |
| `${patchAssignments}` | concatenation of no-DTO per-field write statements using entity argument `entity`; only runs after shared checks pass | required in no-DTO variant |
| `${patchTypeChecks}` | concatenation of per-field JSON type/range checks, executed inside `assertPatchAllowed` before any mutation in both variants | required |
| `${primitiveFieldNames}` | names of primitive fields in the mutable API representation, as Java string literals | required (empty if none) |
| `${validatorFieldName}` | injected `jakarta.validation.Validator` field name | `validator` |

## Notes
- Inject `jakarta.validation.Validator` for all PATCH modes. Add `quarkus-hibernate-validator` when absent and report the dependency addition.
- An unchecked `BadRequestException` must escape the transactional method; do not catch/swallow failures. A failing batch mutation must roll back the transaction.
- Managed entity changes flush on commit; no explicit save is needed.
