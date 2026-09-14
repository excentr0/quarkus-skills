# GET_LIST method (Java)

## Insert Point
As new method in the resource class body, after the last method.

## Code

### defaults
Pagination, no filter, no sort, no DTO:
```java
@jakarta.ws.rs.GET
public java.util.List<${EntityFqn}> getAll(@jakarta.ws.rs.QueryParam("page") @jakarta.ws.rs.DefaultValue("0") int page,
                                           @jakarta.ws.rs.QueryParam("size") @jakarta.ws.rs.DefaultValue("20") int size) {
    return ${repoFieldName}.findAll()
            .page(io.quarkus.panache.common.Page.of(page, size))
            .list();
}
```

### pagination, no filter, with DTO
```java
@jakarta.ws.rs.GET
public java.util.List<${DtoFqn}> getAll(@jakarta.ws.rs.QueryParam("page") @jakarta.ws.rs.DefaultValue("0") int page,
                                        @jakarta.ws.rs.QueryParam("size") @jakarta.ws.rs.DefaultValue("20") int size) {
    java.util.List<${EntityFqn}> ${entityVarPlural} = ${repoFieldName}.findAll()
            .page(io.quarkus.panache.common.Page.of(page, size))
            .list();
    return ${entityVarPlural}.stream()
            .map(${mapperFieldName}::${toDtoMethodName})
            .toList();
}
```

### pagination, with filter, no DTO
```java
@jakarta.ws.rs.GET
public java.util.List<${EntityFqn}> getAll(@jakarta.ws.rs.QueryParam("${filterParamName}") String ${filterParamName},
                                           @jakarta.ws.rs.QueryParam("page") @jakarta.ws.rs.DefaultValue("0") int page,
                                           @jakarta.ws.rs.QueryParam("size") @jakarta.ws.rs.DefaultValue("20") int size) {
    io.quarkus.hibernate.orm.panache.PanacheQuery<${EntityFqn}> query = (${filterParamName} == null || ${filterParamName}.isBlank())
            ? ${repoFieldName}.findAll()
            : ${repoFieldName}.find("${filterFieldName} like ?1", "%" + ${filterParamName} + "%");
    return query.page(io.quarkus.panache.common.Page.of(page, size)).list();
}
```

### pagination, with filter, with DTO
```java
@jakarta.ws.rs.GET
public java.util.List<${DtoFqn}> getAll(@jakarta.ws.rs.QueryParam("${filterParamName}") String ${filterParamName},
                                        @jakarta.ws.rs.QueryParam("page") @jakarta.ws.rs.DefaultValue("0") int page,
                                        @jakarta.ws.rs.QueryParam("size") @jakarta.ws.rs.DefaultValue("20") int size) {
    io.quarkus.hibernate.orm.panache.PanacheQuery<${EntityFqn}> query = (${filterParamName} == null || ${filterParamName}.isBlank())
            ? ${repoFieldName}.findAll()
            : ${repoFieldName}.find("${filterFieldName} like ?1", "%" + ${filterParamName} + "%");
    java.util.List<${EntityFqn}> ${entityVarPlural} = query.page(io.quarkus.panache.common.Page.of(page, size)).list();
    return ${entityVarPlural}.stream()
            .map(${mapperFieldName}::${toDtoMethodName})
            .toList();
}
```

### pagination, with fixed sort, no DTO
```java
@jakarta.ws.rs.GET
public java.util.List<${EntityFqn}> getAll(@jakarta.ws.rs.QueryParam("page") @jakarta.ws.rs.DefaultValue("0") int page,
                                           @jakarta.ws.rs.QueryParam("size") @jakarta.ws.rs.DefaultValue("20") int size) {
    return ${repoFieldName}.findAll()
            .page(io.quarkus.panache.common.Page.of(page, size), io.quarkus.panache.common.Sort.by("${sortFieldName}"))
            .list();
}
```

### no pagination, no DTO
```java
@jakarta.ws.rs.GET
public java.util.List<${EntityFqn}> getAll() {
    return ${repoFieldName}.listAll();
}
```

### no pagination, with DTO
```java
@jakarta.ws.rs.GET
public java.util.List<${DtoFqn}> getAll() {
    java.util.List<${EntityFqn}> ${entityVarPlural} = ${repoFieldName}.listAll();
    return ${entityVarPlural}.stream()
            .map(${mapperFieldName}::${toDtoMethodName})
            .toList();
}
```

### pagination + total count, no DTO
```java
@jakarta.ws.rs.GET
public jakarta.ws.rs.core.Response getAll(@jakarta.ws.rs.QueryParam("page") @jakarta.ws.rs.DefaultValue("0") int page,
                                          @jakarta.ws.rs.QueryParam("size") @jakarta.ws.rs.DefaultValue("20") int size) {
    io.quarkus.hibernate.orm.panache.PanacheQuery<${EntityFqn}> query = ${repoFieldName}.findAll()
            .page(io.quarkus.panache.common.Page.of(page, size));
    return jakarta.ws.rs.core.Response.ok(query.list())
            .header("X-Total-Count", query.count())
            .build();
}
```

### pagination + total count, with DTO
```java
@jakarta.ws.rs.GET
public jakarta.ws.rs.core.Response getAll(@jakarta.ws.rs.QueryParam("page") @jakarta.ws.rs.DefaultValue("0") int page,
                                          @jakarta.ws.rs.QueryParam("size") @jakarta.ws.rs.DefaultValue("20") int size) {
    io.quarkus.hibernate.orm.panache.PanacheQuery<${EntityFqn}> query = ${repoFieldName}.findAll()
            .page(io.quarkus.panache.common.Page.of(page, size));
    java.util.List<${DtoFqn}> ${dtoVarPlural} = query.list().stream()
            .map(${mapperFieldName}::${toDtoMethodName})
            .toList();
    return jakarta.ws.rs.core.Response.ok(${dtoVarPlural})
            .header("X-Total-Count", query.count())
            .build();
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${EntityFqn}` | entity FQN | -- |
| `${DtoFqn}` | DTO FQN | -- |
| `${repoFieldName}` | repository field name | -- |
| `${mapperFieldName}` | mapper field name | -- |
| `${toDtoMethodName}` | mapper entity->DTO method | `toDto` |
| `${entityVarPlural}` | pluralized entity var | -- |
| `${dtoVarPlural}` | pluralized decapitalized DTO name | -- |
| `${filterFieldName}` | entity field used by the filter | -- |
| `${filterParamName}` | query parameter name for the filter | `${filterFieldName}` |
| `${sortFieldName}` | entity field used for sorting | -- |

## Notes
- Page index is 0-based: `?page=0` is the first page.
- The total-count variants return `Response` and add a `COUNT` query per request — use them only
  when the user asked for a total count.
- Combining more than one filter or a `sort` query param: see
  [`../../../references/panache-queries.md`](../../../references/panache-queries.md).
