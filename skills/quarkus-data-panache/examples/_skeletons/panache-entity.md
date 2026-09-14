# Panache entity skeleton (Active Record, Java)

## Insert Point

New file: `src/main/java/${packagePath}/${EntityName}.java`

## Code

```java
package ${packageName};

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import io.quarkus.hibernate.orm.panache.PanacheEntity;

@Entity
@Table(name = "${tableName}")
public class ${EntityName} extends PanacheEntity {

    @Column(name = "${columnName}", nullable = false)
    public ${fieldType} ${fieldName};

    public static ${EntityName} findBy${FinderSuffix}(${fieldType} ${fieldName}) {
        return find("${columnName}", ${fieldName}).firstResult();
    }
}
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${packageName}` | project context | main package + `.domain` |
| `${packagePath}` | `${packageName}` with dots replaced by `/` | -- |
| `${EntityName}` | user choice | PascalCase singular noun |
| `${tableName}` | table name template convention | lower snake case of `${EntityName}` |
| `${fieldName}` | user choice | -- |
| `${fieldType}` | user choice | -- |
| `${columnName}` | column name template convention | lower snake case of `${fieldName}` |
| `${FinderSuffix}` | custom finder naming convention | PascalCase of `${fieldName}` |

## Variants

- **Custom `@Id` (e.g. `UUID`)** — extend `PanacheEntityBase` instead of `PanacheEntity` and declare the id
  field per the Id section of [`entity-rules-impl.md`](../../references/entity-rules-impl.md).
- **Private fields with accessors** — apply only when the project convention requires it; then write the
  accessors manually in the project's style.
- **Repository style instead of Active Record** — drop the static finder here and use
  [`panache-repository.md`](panache-repository.md) for query methods.
