# GET_MANY method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
No DTO:
```java
@jakarta.ws.rs.GET
@jakarta.ws.rs.Path("/by-ids")
public java.util.List<${EntityFqn}> getMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids) {
    return ${repoFieldName}.list("id in ?1", ids);
}
```

### with DTO
```java
@jakarta.ws.rs.GET
@jakarta.ws.rs.Path("/by-ids")
public java.util.List<${DtoFqn}> getMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids) {
    java.util.List<${EntityFqn}> ${entityVarPlural} = ${repoFieldName}.list("id in ?1", ids);
    return ${entityVarPlural}.stream()
            .map(${mapperFieldName}::${toDtoMethodName})
            .toList();
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${EntityFqn}` | entity FQN | -- |
| `${DtoFqn}` | DTO FQN | -- |
| `${IdType}` | entity ID type (boxed) | -- |
| `${repoFieldName}` | repository field name | -- |
| `${entityVarPlural}` | pluralized entity var | -- |
| `${mapperFieldName}` | mapper field name | -- |
| `${toDtoMethodName}` | mapper entity->DTO method | `toDto` |

## Notes
- Requested as a repeated query parameter: `?ids=1&ids=2&ids=3`.
- An empty `ids` list matches nothing — the method returns an empty list.
