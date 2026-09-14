# Repository creation (Java)

## Insert Point
New file `src/main/java/{packagePath}/{RepoName}.java`.

## Code

### defaults
Standard ID type (`Long` from `PanacheEntity` or an explicit `@Id`):
```java
package {packageName};

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class {RepoName} implements io.quarkus.hibernate.orm.panache.PanacheRepository<{EntityFqn}> {
}
```

### custom ID type
Use when the entity's ID type is not the one inferred from `PanacheRepository<Entity>`:
```java
package {packageName};

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class {RepoName} implements io.quarkus.hibernate.orm.panache.PanacheRepositoryBase<{EntityFqn}, {IdType}> {
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `{packageName}` | project context | entity package, or the package where existing repositories live |
| `{RepoName}` | user choice | `{EntityName}Repository` |
| `{EntityFqn}` | entity FQN | -- |
| `{IdType}` | entity ID type | -- |

## When to apply
Only when Step 3 found no repository for the entity AND the user agreed to create one.
A repository created here is later injected by WA2.
