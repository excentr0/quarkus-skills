# OIDC Authorization Code Flow Properties (Web App)

## application.properties

```properties
# --- Provider connection ---
%prod.quarkus.oidc.auth-server-url=${authServerUrl}
quarkus.oidc.client-id=${clientId}
quarkus.oidc.credentials.secret=${OIDC_CLIENT_SECRET}
quarkus.oidc.application-type=web-app

# --- Logout ---
quarkus.oidc.logout.path=${logoutPath}

# --- Path permissions ---
# Everything requires login by default:
quarkus.http.auth.permission.authenticated.paths=/*
quarkus.http.auth.permission.authenticated.policy=authenticated

# Public paths (optional; omit this block when there are none):
# quarkus.http.auth.permission.permit-public.paths=${publicPaths}
# quarkus.http.auth.permission.permit-public.policy=permit

# --- Roles (only when roles come from a custom claim, or from UserInfo) ---
# quarkus.oidc.roles.role-claim-path=${roleClaimPath}
# quarkus.oidc.roles.source=userinfo

# --- Dev Services for Keycloak (dev mode; omit when the provider is external) ---
# quarkus.keycloak.devservices.realm-path=${realmFile}
```

## Client secret handling (security)

**Never substitute a literal client-secret value into the file.** Keep the
`${OIDC_CLIENT_SECRET}` line exactly as written — it is a real environment-variable expansion, not
a template placeholder — and tell the user afterwards which env var to set. Do NOT ask the user for
the secret value; it must not enter the conversation. The authorization code flow requires client
credentials, so this line is always kept in this variant.

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${authServerUrl}` | user input or existing config | local Keycloak default in dev: `http://localhost:8180/realms/quarkus` |
| `${clientId}` | user input or existing config | — |
| `${logoutPath}` | user input | `/logout` |
| `${publicPaths}` | user input | skip the block when empty |
| `${roleClaimPath}` | user input | skip (default `groups` claim) |
| `${realmFile}` | user input | e.g. `quarkus-realm.json`; skip when not using Dev Services |
