# Common Rules — permissions, annotations, identity, roles

Shared by all authentication variants. Read before generating any configuration.

---

## Path permissions (application.properties)

Quarkus guards request paths through permission sets, not through a filter chain:

```properties
# public paths — permit all (methods optional, comma-separated)
quarkus.http.auth.permission.permit1.paths=/public/*
quarkus.http.auth.permission.permit1.policy=permit
quarkus.http.auth.permission.permit1.methods=GET,HEAD

# everything else — authentication required
quarkus.http.auth.permission.authenticated.paths=/*
quarkus.http.auth.permission.authenticated.policy=authenticated

# role-restricted paths — a named policy with allowed roles
quarkus.http.auth.permission.roles1.paths=/api/admin/*
quarkus.http.auth.permission.roles1.policy=role-policy1
quarkus.http.auth.policy.role-policy1.roles-allowed=admin,user
```

### Rules

- **Built-in policies** — exactly three: `permit`, `deny`, `authenticated`. Any other value must be a
  named policy defined via `quarkus.http.auth.policy.<name>.*`.
- **Role policies** — `quarkus.http.auth.policy.<policy-name>.roles-allowed=role1,role2`. Referenced
  from a permission set via `quarkus.http.auth.permission.<set>.policy=<policy-name>`.
- **Path syntax** — a path ending in `/*` is a prefix match; anything else is an exact match.
  Multiple paths in one set are comma-separated.
- **Precedence — longest matching path wins.** File order does NOT matter. Never claim that moving a
  block up or down changes which rule applies.
- **Ties** — when several permission sets match with equal specificity: sets that explicitly list the
  request method win over sets without methods; otherwise the most restrictive permissions apply.
- **No rule = no configuration guard.** A path that matches no permission set is not protected by
  configuration (only method annotations apply). To protect everything, always generate the
  `/*` → `authenticated` rule alongside any `permit` rules for public paths.
- **Optional** — a permission set can pin the authentication mechanism for its paths:
  `quarkus.http.auth.permission.<set>.auth-mechanism=bearer` (or `basic`, or a comma-separated list).

### Questions (skip if "all defaults" or already answered)

```text
Path permissions:
1. Paths that must stay public (no authentication)? [none]
2. Paths restricted to specific roles? [none]
```

Ask question 1 and 2 in plain text (free-form patterns). If no public paths — omit the `permit` set
entirely. If no role-restricted paths — omit the named policy entirely.

---

## Method-level annotations

| Annotation | Package | Meaning |
|---|---|---|
| `@RolesAllowed("role")` | `jakarta.annotation.security` | caller must have the role (or any of several) |
| `@PermitAll` | `jakarta.annotation.security` | explicitly open — no authentication |
| `@DenyAll` | `jakarta.annotation.security` | always denied |
| `@Authenticated` | `io.quarkus.security` | any authenticated caller |
| `@PermissionsAllowed("read:orders")` | `io.quarkus.security` | caller must have the permission; token `scope` values are mapped to permissions automatically |

Annotations can sit on a resource class (applies to all methods) or on individual methods.

---

## Identity and token injection

| What | Fragment |
|---|---|
| Current user (name, roles) — `SecurityIdentity` | `examples/_annotations/identity-injection/java.md` |
| Token claims — `JsonWebToken` | `examples/_annotations/jwt-injection/java.md` |
| Any-authenticated / explicitly-public markers | `examples/_annotations/authenticated-and-permit/java.md` |
| Role restrictions | `examples/_annotations/roles-allowed/java.md` |

---

## How token claims become roles

- By default, the token **`groups` array claim** contains the roles. If the token was issued by
  Keycloak, the `realm_access/roles` and `realm_access/<client-id>/roles` claims are also checked
  automatically.
- Custom claim: `quarkus.oidc.roles.role-claim-path=<claim or nested/path>` — supports a top-level
  array claim or a nested path with `/` as separator; quote namespace-qualified claim names
  (`quarkus.oidc.roles.role-claim-path="https://example.com/roles"`).
- Custom claim with multiple values in one string: `quarkus.oidc.roles.role-claim-separator=,`
  (default separator is a space).
- Roles in the UserInfo response: `quarkus.oidc.roles.source=userinfo` (for bearer tokens also set
  `quarkus.oidc.authentication.user-info-required=true`).
- Code flow uses the **ID token** as the primary role source; bearer flow uses the **access token**.
- Token roles can be mapped to deployment-specific roles with a role policy
  (`quarkus.http.auth.policy.<name>.roles-allowed=...`) instead of using the raw claim values in
  `@RolesAllowed`.

Do not invent role-claim properties beyond this list — if the provider uses something unusual,
check the Quarkus OIDC guide rather than guessing.

---

## Dev Services for Keycloak (dev/test)

- When `quarkus-oidc` (or another Keycloak-aware extension) is present, Quarkus can start a Keycloak
  container automatically in dev and test mode — no manual setup.
- Import a realm definition: `quarkus.keycloak.devservices.realm-path=quarkus-realm.json`
  (effective in dev mode).
- Dev Services sets the `keycloak.url` property automatically — use it in dev-mode configuration
  (for example for the MP-JWT public key location).
- Keep the real provider URL under the `%prod.` prefix so dev/test keep using Dev Services:
  `%prod.quarkus.oidc.auth-server-url=https://id.example.com/realms/my-realm`.

---

## Not covered by this skill

LDAP directories, applications acting as their own authorization server, custom
`HttpAuthenticationMechanism` implementations, and `SecurityIdentityAugmentor` customization.
If the user asks for these — say they are out of scope and ask how to proceed instead of improvising.
