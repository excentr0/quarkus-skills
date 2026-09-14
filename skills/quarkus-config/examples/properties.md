# Properties block (application.properties)

Used by Step 3 and Step 4 of [`../SKILL.md`](../SKILL.md).

## Variables

| Variable | Source | Default |
|---|---|---|
| `${prefix}` | Step 2 | kebab-case feature name, or the project's existing custom prefix |
| `${fieldName}` | Step 0 | kebab-case key suffix (`retry-count`, `base-url`) |
| `${fieldValue}` | Step 0 | value from the request |
| `${devValue}` / `${testValue}` / `${prodValue}` | Step 4 | value that differs in that profile (omit the line when it does not) |
| `${ENV_VAR}` | Step 4 | environment variable name for a secret (e.g. `BILLING_CLIENT_SECRET`) |
| `${envVarFieldName}` | Step 4 | kebab-case key of the secret setting |

## Code — shared values, profile overrides, secret reference

```properties
# --- ${Feature} settings (shared by all profiles) ---
${prefix}.${fieldName}=${fieldValue}

# --- Profile-specific overrides (only where the value actually differs) ---
%dev.${prefix}.${fieldName}=${devValue}
%test.${prefix}.${fieldName}=${testValue}
%prod.${prefix}.${fieldName}=${prodValue}

# --- Secret: environment variable reference, never a literal value ---
${prefix}.${envVarFieldName}=${${ENV_VAR}}
```

## Notes

- An unprefixed key applies to all profiles — do not duplicate it under every `%`-prefix.
- Production-only settings (real datasource, external URLs) go under `%prod.` so Dev Services keep
  working in dev/test — see [`../references/profiles.md`](../references/profiles.md).
- The secret line must keep the `${ENV_VAR}` indirection in every profile, including `%prod.`.
- Append the block to the existing `application.properties` — never rewrite unrelated keys.
