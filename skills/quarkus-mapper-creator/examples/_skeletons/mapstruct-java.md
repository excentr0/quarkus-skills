# MapStruct mapper interface (Java)

## Code

```java
package ${packageName};

public interface ${className} {
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${packageName}` | project context | — |
| `${className}` | user choice | `${EntityName}Mapper` |

## Note

With `componentModel = "cdi"` MapStruct generates `${className}Impl` as a CDI bean — the
interface stays a plain interface, and consumers inject `${className}` directly (constructor
injection or `@Inject`). Nothing else is required in the interface body besides the abstract
mapping methods.