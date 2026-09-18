# Security variant selection

## Step 0 -- Conversation context first (REQUIRED, no tool calls)

Before any file read, before any question, **re-read the user's prompt and the prior turns of
this conversation** and extract whatever is already stated. This step costs nothing and prevents
the most common failure mode of this skill — asking the user something they already said.

Build a mental checklist of inputs and tick off everything the user has already provided,
explicitly or implicitly:

| Input | Look for in the prompt / context |
|---|---|
| **authentication type** | "bearer", "JWT", "access token", "API" -> bearer; "login", "SSO", "web app", "frontend", "browser" -> code flow; "MP-JWT" -> legacy |
| **provider** | "Keycloak", "Auth0", "Okta", "Entra ID", "Azure AD", "Google" |
| **auth-server-url / realm** | explicit provider URLs or realm names — "realm quarkus" |
| **client-id** | explicit value — "client id backend-service" |
| **path rules** | "only /orders should be public", "everything under /api must be authenticated", "admin endpoints" |
| **roles** | "only ADMIN", "role user", "restrict to auditors" |
| **smart defaults** | "use defaults", "all defaults", "default settings", "minimal setup" |
| **prior project facts** | extensions, existing `quarkus.oidc.*` values, resource paths — already known if discussed earlier in this conversation; do not re-read files you already read |

For every input that is **explicitly or strongly implicitly answered**: mark it as decided and
skip the corresponding question in Steps 2–3. Do NOT ask "Authentication type?" if the user wrote
"configure bearer tokens" — bearer is the answer.

For every input that is **not** answered: defer to the Decision-making principle in [`SKILL.md`](../SKILL.md) — try to
derive it from project context first (Step 1), and only then ask.

Step 0 is mental, not a tool call. Do not announce it to the user. Do not write "Step 0 done".
Just internalize what the user already said before proceeding to Step 1.

---

## Step 2 -- Authentication type

Tell the user: `Step 2/5: Choosing authentication type...`

Ask (skip if answered in Step 0):

```text
Authentication type?
1. OIDC bearer tokens (API) (Recommended) -- verifies JWT access tokens from an OIDC provider; stateless, no login page
2. OIDC authorization code flow (web app) -- browser login via the provider, session cookie, logout
3. MP-JWT legacy (quarkus-smallrye-jwt) -- verifies tokens by public key/issuer without OIDC discovery
```

Map answer to reference file:
- 1 -> [`references/oidc-service.md`](../references/oidc-service.md)
- 2 -> [`references/oidc-web-app.md`](../references/oidc-web-app.md)
- 3 -> [`references/smallrye-jwt.md`](../references/smallrye-jwt.md)

**Not covered by this skill** (tell the user if they ask for them): LDAP directories,
applications acting as their own authorization server, custom authentication mechanisms
(a custom `HttpAuthenticationMechanism` is out of scope here).

---

## Step 3 -- Variant-specific questions (inline)

Tell the user: `Step 3/5: Collecting variant settings...`

Read the mapped reference file and follow its question flow.
Only asked if the user did NOT say "all defaults".

Each reference file specifies:
- Which property blocks to write
- Which annotation fragments apply
- Which dependencies to add
- Which permissions/policies to generate
- Variant-specific questions

---
