# Authentication marker annotations fragment (Java)

## Insert Point
On resource classes or methods in a file that already exists.

## Code

```java
// any authenticated caller
@io.quarkus.security.Authenticated
public class ProfileResource {
}

// explicitly public -- no authentication required
@jakarta.annotation.security.PermitAll
public ${returnType} ${methodName}(...) {
}

// always denied
@jakarta.annotation.security.DenyAll
public ${returnType} ${methodName}(...) {
}

// permission-based: the caller must have the permission
// (OIDC token scope values are mapped to permissions automatically)
@io.quarkus.security.PermissionsAllowed("${permission}")
public ${returnType} ${methodName}(...) {
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${permission}` | user input (e.g. an OIDC scope value) | skip the fragment when not requested |
| `${returnType}`, `${methodName}` | existing method signature | — (never invent a method) |

## Notes
- `@Authenticated` is `io.quarkus.security.Authenticated`; `@PermitAll` and `@DenyAll` are
  `jakarta.annotation.security` — extract both into imports.
- Include only the fragments the user's rules require — a default setup does not need any of them.
