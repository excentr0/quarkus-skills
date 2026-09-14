# @RolesAllowed fragment (Java)

## Insert Point
On a resource class (applies to all methods) or on individual resource methods, in a file that
already exists. Do not create a new class for this.

## Code

```java
// class level -- every method requires one of the roles
@jakarta.annotation.security.RolesAllowed("${role}")
public class AdminResource {
}

// method level -- single role
@jakarta.annotation.security.RolesAllowed("${role}")
public ${returnType} ${methodName}(...) {
}

// method level -- any of several roles
@jakarta.annotation.security.RolesAllowed({"${role1}", "${role2}"})
public ${returnType} ${methodName}(...) {
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${role}` | user input or existing roles | — |
| `${role1}`, `${role2}` | user input | single role when only one was named |
| `${returnType}`, `${methodName}` | existing method signature | — (never invent a method) |

## Notes
- Role names must match what the token carries (after claim mapping) — use the roles the user named
  or the ones already used in the project (`existingRoles`).
- The import is `jakarta.annotation.security.RolesAllowed`; extract it into the import block and use
  the short annotation name in the code body.
