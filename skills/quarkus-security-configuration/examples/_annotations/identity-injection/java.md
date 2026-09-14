# SecurityIdentity injection fragment (Java)

## Insert Point
As an injected field or constructor parameter in a resource/service that already exists.

## Code

```java
// field injection
@jakarta.inject.Inject
io.quarkus.security.identity.SecurityIdentity identity;

// constructor injection (Quarkus generates the no-args constructor automatically)
public ${className}(io.quarkus.security.identity.SecurityIdentity identity) {
    this.identity = identity;
}

// usage
String username = identity.getPrincipal().getName();
boolean allowed = identity.hasRole("${role}");
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${role}` | user input or existing roles | skip the `hasRole` example when not needed |
| `${className}` | existing class name | — (never invent a class) |

## Notes
- `SecurityIdentity` is `io.quarkus.security.identity.SecurityIdentity` — extract into the import block.
- Use this fragment only when the code actually needs the caller's identity, not as decoration.
