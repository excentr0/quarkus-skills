# Profiles and secrets

## 1. How profile prefixes work

In `application.properties` a key can carry a profile prefix:

```properties
# applies to every profile
${prefix}.retry-count=3

# applies only in dev
%dev.${prefix}.retry-count=1

# applies only in test
%test.${prefix}.retry-count=2

# applies only in prod
%prod.${prefix}.retry-count=5
```

Rules:

- **An unprefixed key applies to all profiles.** Add a profile prefix only where the value actually
  differs — duplicating a shared value under all three prefixes is noise.
- Profile-prefixed keys override unprefixed ones for that profile.
- The profile prefix is `%<name>.` — the leading `%` is part of the key.

## 2. Which profile is active when

| Profile | Active when |
|---|---|
| `dev` | `./mvnw quarkus:dev` |
| `test` | a test run (`@QuarkusTest` / unit tests) |
| `prod` | a packaged application run (fast-jar, native, container) |

There is no "default" profile fallback to configure: what is not prefixed is shared by all three.

## 3. `%prod` and Dev Services

Production-only settings belong under `%prod.` — most importantly the real datasource and external
service URLs. In dev and test, Quarkus Dev Services start a throwaway database (and Kafka, Keycloak,
etc.) when no connection is configured; a datasource configured globally (unprefixed) disables that
and forces the real database in every profile.

```properties
# --- production datasource only ---
%prod.quarkus.datasource.db-kind=postgresql
%prod.quarkus.datasource.username=${DB_USERNAME}
%prod.quarkus.datasource.password=${DB_PASSWORD}
%prod.quarkus.datasource.jdbc.url=${DB_URL}
```

## 4. Secrets

- Secrets are **environment variable references**, never literal values: a key like
  `${prefix}.credentials.secret` takes its value from an environment variable —
  `billing.credentials.secret=${BILLING_CREDENTIALS_SECRET}`, not a pasted secret.
- This holds for every profile, including `%prod.`.
- Reading the value: it is resolved at startup from the environment; the same key can be overridden
  by the environment without editing the file.
- When reporting configuration to the user, redact resolved secret values.

## 5. Test-specific configuration

- `%test.` keys in `application.properties` override values for all tests.
- Per-test-class overrides use `@QuarkusTestProfile` (a test profile implementation), not new
  `%`-prefixes.

## 6. Common mistakes

- A literal password or token committed in `application.properties`.
- Configuring the production datasource unprefixed — breaks Dev Services in dev/test.
- Assuming a `default` profile exists and placing generic values under `%prod.` — they then do not
  apply in dev/test.
- Putting test-only overrides under `%dev.` (dev mode is not a test run).
