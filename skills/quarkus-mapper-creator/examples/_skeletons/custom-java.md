# Custom mapper class (Java)

## Code

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class ${className} {
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${packageName}` | project context | — |
| `${className}` | user choice | `${EntityName}Mapper` |

## Note

`@ApplicationScoped` makes the converter an injectable CDI bean — Quarkus idiom. Consumers get
it via constructor injection or `@Inject`. The methods themselves are plain instance methods
with no framework dependencies, so the class stays unit-testable without booting Quarkus.