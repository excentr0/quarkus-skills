# Panache repository skeleton (Java)

## Insert Point

New file: `src/main/java/${packagePath}/${EntityName}Repository.java`

## Code

```java
package ${packageName};

import java.util.List;
import java.util.Optional;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class ${EntityName}Repository implements PanacheRepository<${EntityName}> {

    public Optional<${EntityName}> findBy${FinderSuffix}(${fieldType} ${fieldName}) {
        return find("${columnName}", ${fieldName}).firstResultOptional();
    }

    public List<${EntityName}> listBy${FinderSuffix}(${fieldType} ${fieldName}) {
        return list("${columnName}", ${fieldName});
    }
}
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${packageName}` | project context | main package + `.repository` |
| `${packagePath}` | `${packageName}` with dots replaced by `/` | -- |
| `${EntityName}` | entity simple name | -- |
| `${fieldName}` | entity field to query | -- |
| `${fieldType}` | type of `${fieldName}` | -- |
| `${columnName}` | column mapped by `${fieldName}` | lower snake case of `${fieldName}` |
| `${FinderSuffix}` | method naming convention | PascalCase of `${fieldName}` |

## Variants

- **Non-`Long` identifier** — implement `PanacheRepositoryBase<${EntityName}, ${IdType}>` instead of
  `PanacheRepository<${EntityName}>`; the query API is identical.
- **Nullable single result** — use `firstResult()` instead of `firstResultOptional()` only when the project's
  return-style convention says so.
- **Pagination** — return `PanacheQuery<${EntityName}>` and let the resource apply `Page.of(index, size)`;
  see the query patterns in [`../_fragments/queries.md`](../_fragments/queries.md).
