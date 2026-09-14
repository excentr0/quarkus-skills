# Serializable (Java)

## Insert Point
Modifies the class declaration: adds `implements java.io.Serializable`.

## Code

```defaults
// Default: skip (only when the user asks for serializable DTOs)
```

**Serializable:**
```java
public class ${className} implements java.io.Serializable {
}
```

**Serializable with serialVersionUID:**
```java
public class ${className} implements java.io.Serializable {
    private static final long serialVersionUID = 1L;
}
```

A record implements Serializable the same way:

```java
public record ${className}(...) implements java.io.Serializable {
}
```

Note: `serialVersionUID` value — use `1L` as default.

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${className}` | DTO class name | -- |