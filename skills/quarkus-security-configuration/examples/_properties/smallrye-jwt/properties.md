# MP-JWT Properties (quarkus-smallrye-jwt)

## application.properties

```properties
# --- Token verification (production values) ---
%prod.mp.jwt.verify.publickey.location=${publicKeyLocation}
%prod.mp.jwt.verify.issuer=${issuer}

# --- Dev/test with Dev Services for Keycloak ---
# keycloak.url is set automatically by Dev Services; use it only when the project relies on it:
# %dev.mp.jwt.verify.publickey.location=${keycloak.url}/realms/${realm}/protocol/openid-connect/certs
# %dev.mp.jwt.verify.issuer=${keycloak.url}/realms/${realm}

# --- Path permissions ---
quarkus.http.auth.permission.authenticated.paths=/*
quarkus.http.auth.permission.authenticated.policy=authenticated

# Public paths (optional; omit this block when there are none):
# quarkus.http.auth.permission.permit-public.paths=${publicPaths}
# quarkus.http.auth.permission.permit-public.policy=permit

# --- Role-restricted paths (optional) ---
# quarkus.http.auth.permission.roles1.paths=${rolePaths}
# quarkus.http.auth.permission.roles1.policy=${rolePolicyName}
# quarkus.http.auth.policy.${rolePolicyName}.roles-allowed=${roles}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${publicKeyLocation}` | user input | — (file path, classpath resource, or URL) |
| `${issuer}` | user input | — |
| `${realm}` | user input | `quarkus` (only for the Dev Services block) |
| `${publicPaths}` | user input | skip the block when empty |
| `${rolePaths}` | user input | skip the block when empty |
| `${rolePolicyName}` | derived from the path segment | e.g. `admin-roles` |
| `${roles}` | user input or existing roles | skip the block when empty |

## Notes
- `mp.jwt.verify.publickey.location` and `mp.jwt.verify.issuer` are both required for verification —
  ask for them; never invent values.
- No client secret exists in this variant — nothing to ask for and no env placeholder to report.
