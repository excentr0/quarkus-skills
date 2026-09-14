# REST client configuration reference

All keys below are verified Quarkus 3.x behavior (see `docs/quarkus-facts.md` §14).

## Property root

| Annotation | Property root |
|---|---|
| `@RegisterRestClient(configKey = "billing-api")` | `quarkus.rest-client."billing-api".url` |
| `@RegisterRestClient` (no configKey) | `quarkus.rest-client."org.acme.client.BillingClient".url` (interface FQN, quoted) |

- The quoted key must match the `configKey` (or the FQN) **character-for-character** — a mismatch
  leaves the client without a base URL.
- Keys containing dots (FQN) or dashes must be quoted. Unquoted keys with dashes are read as
  nested paths — always quote.

## Available keys

| Key | Required | Notes |
|---|---|---|
| `quarkus.rest-client."<key>".url` | yes (unless `baseUri` is set in `@RegisterRestClient`) | full base URL, e.g. `https://api.example.com` |
| `quarkus.rest-client."<key>".uri` | alternative to `url` | URI instead of URL |
| `quarkus.rest-client."<key>".scope` | no | CDI scope for the client bean, e.g. `jakarta.inject.Singleton` |
| `@RegisterRestClient(baseUri = "...")` | no | hardcodes the base URI in code — only when the URL is truly constant; config is preferable for deployability |

Per-invocation base-URL override: annotate a method parameter with
`@io.quarkus.rest.client.reactive.Url` and pass the URL at call time. Use it for redirect/follow-up
scenarios, not as a replacement for configuration.

## Environment profiles

```properties
quarkus.rest-client."billing-api".url=${BILLING_API_URL}
%dev.quarkus.rest-client."billing-api".url=http://localhost:8081
%prod.quarkus.rest-client."billing-api".url=${BILLING_API_URL}
```

- `${ENV_VAR}` is a real SmallRye Config expansion at runtime, not a template placeholder.
- Never commit literal tokens/API keys; keep the `${...}` reference and tell the user which
  environment variable to set.

## Testing implications

| Test type | Behavior | What to do |
|---|---|---|
| `@QuarkusTest` | client bean is replaced by `@InjectMock @RestClient` when mocked | mock it (see `examples/mock-test.md`); no URL is called |
| `@QuarkusIntegrationTest` | runs the packaged app out-of-process — **no** `@InjectMock` | point `%test.`/system config at a reachable instance (WireMock container, test service) |
| Dev Services | none for arbitrary HTTP APIs — Dev Services cover databases, Kafka, Keycloak | use WireMock Dev Services (`quarkus-wiremock`) when the project has it |

## Common pitfalls

- A missing `url` is not a build error: the failure appears at startup or on first client use
  (`Unable to determine the proper baseUrl/baseUri` style configuration error) — always grep for it.
- `.scope` on an existing client means the project controls the bean lifecycle explicitly; follow it.
- Switching `configKey` after the property is written silently orphans the old property — rename
  both sides together.
- The client interface lives in `src/main/java` (it is application code, not a test fixture) even
  when it is only used by tests through mocks.
