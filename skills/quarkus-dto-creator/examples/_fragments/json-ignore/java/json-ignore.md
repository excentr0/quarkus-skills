# @JsonIgnoreProperties (Java)

## Insert Point
As an annotation on the class declaration.

## Code

```defaults
// Default: skip (isJsonIgnoreUnknownProperties=false by default)
// Jackson is available when quarkus-rest-jackson is in the build.
```

```java
@com.fasterxml.jackson.annotation.JsonIgnoreProperties(ignoreUnknown = true)
public class ${className} {
```

Works the same on a record declaration:

```java
@com.fasterxml.jackson.annotation.JsonIgnoreProperties(ignoreUnknown = true)
public record ${className}(...) {
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${className}` | DTO class name | -- |