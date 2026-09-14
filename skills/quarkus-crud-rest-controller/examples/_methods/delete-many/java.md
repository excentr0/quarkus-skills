# DELETE_MANY method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
```java
@jakarta.ws.rs.DELETE
@jakarta.transaction.Transactional
public void deleteMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids) {
    ${repoFieldName}.delete("id in ?1", ids);
}
```

### returns the number of deleted rows
```java
@jakarta.ws.rs.DELETE
@jakarta.transaction.Transactional
public long deleteMany(@jakarta.ws.rs.QueryParam("ids") java.util.List<${IdType}> ids) {
    return ${repoFieldName}.delete("id in ?1", ids);
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${IdType}` | entity ID type (boxed) | -- |
| `${repoFieldName}` | repository field name | -- |

## Notes
- Deletes by query without loading entities; the returned count is the number of deleted rows.
- Requested as a repeated query parameter: `?ids=1&ids=2&ids=3`.
