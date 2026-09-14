# Java record skeleton

## Code

```defaults
// Default: plain Java record, no Javadoc
// Quarkus 3.x requires Java 17+, so records are always available.
```

```java
package ${packageName};

public record ${className}() {
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${packageName}` | existing DTO package in the project, or `${rootPackage}.dto` | -- |
| `${className}` | user choice | `${EntityName}Dto` |