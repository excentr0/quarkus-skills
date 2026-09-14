# DELETE method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
No DTO -- returns the deleted entity (or `null` when it did not exist):
```java
@jakarta.ws.rs.DELETE
@jakarta.ws.rs.Path("/{id}")
@jakarta.transaction.Transactional
public ${EntityFqn} delete(@jakarta.ws.rs.PathParam("id") ${IdType} id) {
    ${EntityFqn} ${entityVar} = ${repoFieldName}.findByIdOptional(id).orElse(null);
    if (${entityVar} != null) {
        ${repoFieldName}.delete(${entityVar});
    }
    return ${entityVar};
}
```

### with DTO
```java
@jakarta.ws.rs.DELETE
@jakarta.ws.rs.Path("/{id}")
@jakarta.transaction.Transactional
public ${DtoFqn} delete(@jakarta.ws.rs.PathParam("id") ${IdType} id) {
    ${EntityFqn} ${entityVar} = ${repoFieldName}.findByIdOptional(id).orElse(null);
    if (${entityVar} == null) {
        return null;
    }
    ${repoFieldName}.delete(${entityVar});
    return ${mapperFieldName}.${toDtoMethodName}(${entityVar});
}
```

### strict -- 204 No Content, 404 when missing
```java
@jakarta.ws.rs.DELETE
@jakarta.ws.rs.Path("/{id}")
@jakarta.transaction.Transactional
public void delete(@jakarta.ws.rs.PathParam("id") ${IdType} id) {
    if (!${repoFieldName}.deleteById(id)) {
        throw new jakarta.ws.rs.NotFoundException("Entity with id `%s` not found".formatted(id));
    }
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${EntityFqn}` | entity FQN | -- |
| `${DtoFqn}` | DTO FQN | -- |
| `${IdType}` | entity ID type | -- |
| `${repoFieldName}` | repository field name | -- |
| `${entityVar}` | decapitalized entity name | -- |
| `${mapperFieldName}` | mapper field name | -- |
| `${toDtoMethodName}` | mapper entity->DTO method | `toDto` |

## Notes
- The default variants are idempotent: deleting a missing entity is not an error.
- Pick the strict variant only when the user asked for 404 on a missing entity.
