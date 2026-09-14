# OIDC Bearer Tokens (API) Variant

Authentication type: `OIDC_BEARER` — stateless JWT access tokens verified against an OIDC provider.
The classic choice for a REST API with no browser login.

## Property blocks used

- `examples/_properties/oidc-service/properties.md` (all blocks)

## Annotation fragments used

- `examples/_annotations/authenticated-and-permit/java.md` — when the user wants explicit
  `@Authenticated` / `@PermitAll` markers on resources
- `examples/_annotations/roles-allowed/java.md` — when role restrictions were requested
- `examples/_annotations/identity-injection/java.md` — when the user needs the caller's name/roles in code
- `examples/_annotations/jwt-injection/java.md` — when the user needs token claims in code

## Dependencies

- `examples/_dependencies/oidc.md`

## Questions

Ask only what Step 0/1 did not already answer.

### Provider connection (plain text)

```text
OIDC provider URL (auth-server-url, issuer URL)? [http://localhost:8180/realms/quarkus]
Client ID? []
```

- If the user names a provider (Keycloak, Auth0, Okta, Entra ID, Google), ask for its issuer URL —
  never invent one.
- For Keycloak and Dev Services, the local default is
  `http://localhost:8180/realms/quarkus` with realm name `quarkus`. Confirm it; the port may differ
  when Dev Services picks a free port — with Dev Services you normally do not set the URL in dev/test
  at all (see `%prod.` rule below).

**Do NOT ask the user for the client secret.** It is written as the `${OIDC_CLIENT_SECRET}`
environment-variable expansion, and in bearer mode it is usually not needed at all (see
`examples/_properties/oidc-service/properties.md` → "Client secret handling").

### Role claim (only when the provider does not use the default `groups` claim)

```text
Roles claim path? [default: groups array claim — plus Keycloak realm_access/roles]
```

If the user names a custom claim (e.g. `roles`, `resource_access/my-client/roles`,
`https://example.com/roles`), write `quarkus.oidc.roles.role-claim-path=<value>`.
If unsure, keep the default and say so — the default covers Keycloak and most providers.

### Path permissions

Ask the two questions from `references/common-rules.md` → Path permissions (public paths,
role-restricted paths). Defaults: `/*` → `authenticated`, no public paths, no role policy.

### Roles (only when role-restricted paths or `@RolesAllowed` were requested)

```text
Which roles are allowed to access the restricted paths? []
```

Suggest values from `existingRoles` (found in Step 1) if any. Never invent role names.

## Generation

1. Read `examples/_properties/oidc-service/properties.md`.
2. Write the provider block:
   - `%prod.quarkus.oidc.auth-server-url=<issuer URL>` — the `%prod.` prefix keeps Dev Services
     available in dev/test
   - `quarkus.oidc.client-id=<client id>`
   - `quarkus.oidc.application-type=service`
3. Write the roles block — only when a custom claim was confirmed.
4. Write the permission blocks:
   - `permit` set for each public path (omit when none)
   - `/*` → `authenticated` (always)
   - role policy + permission set when role-restricted paths were requested
5. Apply annotation fragments to the targeted resources — only the fragments the user's rules need.
6. Add dependencies from `examples/_dependencies/oidc.md` for artifacts not already present
   (prefer `./mvnw quarkus:add-extension -Dextensions="quarkus-oidc,quarkus-security"` /
   `./gradlew addExtension --extensions="quarkus-oidc,quarkus-security"`).
7. Report: property keys written, permission rules created, annotations applied, and — if the
   optional `credentials.secret` line was included — the `${OIDC_CLIENT_SECRET}` env var to set.

## Notes

- Token verification uses the provider's discovery document (`auth-server-url`); Quarkus validates
  the token signature and issuer. Do not add issuer/audience properties that were not requested.
- `quarkus.oidc.credentials.secret` and `quarkus.oidc.token-path` are needed **only** when the
  application itself calls the token endpoint (client credentials / password grant) — a pure
  resource server validates tokens without them.
- No session, no login page, no logout config in bearer mode. Do not generate logout properties here.
- 401 means the token is missing/invalid; 403 means the token is valid but roles are insufficient —
  useful when the user reports problems.
