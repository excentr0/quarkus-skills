# OIDC Authorization Code Flow (Web App) Variant

Authentication type: `OIDC_WEB_APP` — browser-based login through the provider, session cookie,
logout. The choice when the application has a UI served by Quarkus (or a server-rendered frontend)
and needs SSO.

## Property blocks used

- `examples/_properties/oidc-web-app/properties.md` (all blocks)

## Annotation fragments used

- `examples/_annotations/authenticated-and-permit/java.md` — public / denied paths
- `examples/_annotations/roles-allowed/java.md` — when role restrictions were requested
- `examples/_annotations/identity-injection/java.md` — when the user needs the caller's name/roles in code
- `examples/_annotations/jwt-injection/java.md` — when the user needs ID-token claims in code (`@IdToken`)

## Dependencies

- `examples/_dependencies/oidc.md`

## Questions

Ask only what Step 0/1 did not already answer.

### Provider connection (plain text)

```text
OIDC provider URL (auth-server-url)? [http://localhost:8180/realms/quarkus]
Client ID? []
```

- The redirect URI must be registered in the provider for this application — mention it as a
  deployment note; do not invent a URI in the config.
- **Do NOT ask for the client secret** — it is written as `${OIDC_CLIENT_SECRET}` and reported as an
  env-var requirement afterwards.

### Protected paths

```text
Protect all paths? [yes — /* requires authentication]
Public paths (no login required)? [none]
```

Default: `/*` → `authenticated`; public paths get a `permit` set. This default matches the upstream
"all endpoints secured" behaviour and should be kept unless the user says otherwise.

### Logout (default is fine)

```text
Logout path? [/logout]
```

Write `quarkus.oidc.logout.path=<path>` with the default unless the user chooses another path.

### Roles claim (only when the provider does not use the default `groups` claim)

Same as the bearer variant — see `references/oidc-service.md` → Role claim. In the code flow the
**ID token** is the primary role source; if roles arrive in UserInfo instead, write
`quarkus.oidc.roles.source=userinfo`.

## Generation

1. Read `examples/_properties/oidc-web-app/properties.md`.
2. Write the provider block:
   - `%prod.quarkus.oidc.auth-server-url=<issuer URL>`
   - `quarkus.oidc.client-id=<client id>`
   - `quarkus.oidc.credentials.secret=${OIDC_CLIENT_SECRET}` (code flow needs client credentials —
     keep this line verbatim, it is a real env-var expansion)
   - `quarkus.oidc.application-type=web-app`
3. Write the logout block (`quarkus.oidc.logout.path=/logout` by default).
4. Write the permission blocks: `/*` → `authenticated` (default), plus a `permit` set for public
   paths if any.
5. Apply annotation fragments — for web-apps, `@PermitAll` on public pages and `@RolesAllowed` where
   roles apply. Use the `@IdToken` fragment only if the user needs ID-token claims.
6. Add dependencies from `examples/_dependencies/oidc.md` (see the bearer variant for the command).
7. Report: property keys written, permissions, annotations, and the `${OIDC_CLIENT_SECRET}` env var
   the user must set.

## Notes

- Roles come from the **ID token** by default in the code flow (bearer flow uses the access token).
- `@IdToken` injection returns the ID token specifically; plain `JsonWebToken` injection returns the
  primary token for the flow.
- Do not add bearer-token-only properties (`quarkus.oidc.token-path`, `token.audience`) in this variant.
- The `%prod.` prefix on `auth-server-url` keeps Dev Services available in dev/test.
