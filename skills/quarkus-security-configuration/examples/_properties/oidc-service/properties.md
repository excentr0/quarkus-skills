# OIDC Bearer Token Properties (API)

## application.properties

```properties
# --- Provider connection ---
%prod.quarkus.oidc.auth-server-url=${authServerUrl}
quarkus.oidc.client-id=${clientId}
quarkus.oidc.application-type=service

# --- Optional: only when the application itself obtains tokens (client credentials / password grant) ---
# quarkus.oidc.credentials.secret=${OIDC_CLIENT_SECRET}
# quarkus.oidc.token-path=${tokenPath}

# --- Roles (only when roles come from a custom claim) ---
# quarkus.oidc.roles.role-claim-path=${roleClaimPath}

# --- Path permissions ---
# Public paths (omit this block when there are none):
quarkus.http.auth.permission.permit-public.paths=${publicPaths}
quarkus.http.auth.permission.permit-public.policy=permit

# Everything else requires authentication:
quarkus.http.auth.permission.authenticated.paths=/*
quarkus.http.auth.permission.authenticated.policy=authenticated

# --- Role-restricted paths (optional) ---
# quarkus.http.auth.permission.roles1.paths=${rolePaths}
# quarkus.http.auth.permission.roles1.policy=${rolePolicyName}
# quarkus.http.auth.policy.${rolePolicyName}.roles-allowed=${roles}

# --- Dev Services for Keycloak (dev mode; omit when the provider is external) ---
# quarkus.keycloak.devservices.realm-path=${realmFile}
```

## Client secret handling (security)

**Never substitute a literal client-secret value into the file.** Keep the
`${OIDC_CLIENT_SECRET}` line exactly as written — it is a real environment-variable expansion, not
a template placeholder — and tell the user afterwards which env var to set (shell `export`, IDE run
configuration, or a deployment secret store). Do NOT ask the user for the secret value; it must not
enter the conversation. When the application only validates tokens (pure resource server), the
optional secret line is not needed at all — omit it.

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${authServerUrl}` | user input or existing config | local Keycloak default in dev: `http://localhost:8180/realms/quarkus` |
| `${clientId}` | user input or existing config | — |
| `${tokenPath}` | user input | provider token endpoint path (only when the app obtains tokens) |
| `${roleClaimPath}` | user input | skip (default `groups` claim) |
| `${publicPaths}` | user input | skip the block when empty |
| `${rolePaths}` | user input | skip the block when empty |
| `${rolePolicyName}` | derived from the path segment | e.g. `admin-roles` |
| `${roles}` | user input or existing roles | skip the block when empty |
| `${realmFile}` | user input | e.g. `quarkus-realm.json`; skip when not using Dev Services |
