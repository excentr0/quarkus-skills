# Base URL configuration (application.properties)

## Code

### default (single environment)
```properties
quarkus.rest-client."${configKey}".url=${baseUrl}
```

### with explicit CDI scope (only when the project's clients set it)
```properties
quarkus.rest-client."${configKey}".url=${baseUrl}
quarkus.rest-client."${configKey}".scope=jakarta.inject.Singleton
```

### per environment
```properties
quarkus.rest-client."${configKey}".url=${baseUrl}
%dev.quarkus.rest-client."${configKey}".url=${devBaseUrl}
%prod.quarkus.rest-client."${configKey}".url=${prodBaseUrl}
```

### interface FQN as the config root (project does not use configKey)
```properties
quarkus.rest-client."${clientFqn}".url=${baseUrl}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${configKey}` | `@RegisterRestClient(configKey = ...)` | kebab-case service name, e.g. `billing-api` |
| `${clientFqn}` | client interface FQN | `org.acme.client.{ServiceName}Client` |
| `${baseUrl}` | user / deployment config | — (mandatory; never leave unset) |
| `${devBaseUrl}` | local instance | `http://localhost:8081` |
| `${prodBaseUrl}` | deployment config | `${SERVICE_API_URL}` (env-var expansion) |

## Notes
- The quoted property root must match the annotation exactly (configKey, or the interface FQN when
  no configKey is used). A mismatch leaves the client without a base URL.
- Keys with dots or dashes are always quoted.
- `${...}` values are real SmallRye Config expansions at runtime — keep `${API_TOKEN}`-style
  references instead of literal secrets, and tell the user which environment variable to set.
- The `%test.` profile can point the client at a stub service for `@QuarkusIntegrationTest`
  (mocking is impossible there).
