# GET_ONE method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
No DTO:
```java
@jakarta.ws.rs.GET
@jakarta.ws.rs.Path("/{id}")
public ${EntityFqn} getOne(@jakarta.ws.rs.PathParam("id") ${IdType} id) {
    return ${repoFieldName}.findByIdOptional(id)
            .orElseThrow(() -> new jakarta.ws.rs.NotFoundException("Entity with id `%s` not found".formatted(id)));
}
```

### with DTO
```java
@jakarta.ws.rs.GET
@jakarta.ws.rs.Path("/{id}")
public ${DtoFqn} getOne(@jakarta.ws.rs.PathParam("id") ${IdType} id) {
    ${EntityFqn} ${entityVar} = ${repoFieldName}.findByIdOptional(id)
            .orElseThrow(() -> new jakarta.ws.rs.NotFoundException("Entity with id `%s` not found".formatted(id)));
    return ${mapperFieldName}.${toDtoMethodName}(${entityVar});
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
