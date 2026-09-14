---
name: quarkus-rest-client
description: >
  Creates a typed REST client for calling external HTTP services from a Quarkus application:
  the declarative MicroProfile REST Client interface, base-URL configuration, injection, and
  mocking in tests.
  Use this skill when a REST client needs to be created, extended, or fixed: calling a
  third-party or internal API, adding an operation to an existing client, configuring the
  base URL, or mocking a client in a test.
  Triggers on: "rest client", "call external API", "http client", "client for <service>",
  "integrate with <service> API", "microprofile rest client", "RegisterRestClient".
  Russian phrases also trigger this: "rest-клиент", "вызови внешний API", "клиент для сервиса",
  "интеграция по HTTP", "http-клиент", "добавь вызов сервиса".
---

# Preflight — Project detection (before step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`;
   Gradle: `id("io.quarkus")` plugin. Quarkus 3.x targets Jakarta EE (`jakarta.*`) — never `javax.*`.
3. **Extensions** — dependencies starting with `io.quarkus:`; feature gates for this skill:
   - `quarkus-rest-client` → declarative REST client (`hasRestClient`)
   - `quarkus-rest-client-jackson` → JSON (de)serialization for client DTOs (`hasRestClientJackson`)
   - `quarkus-junit5-mockito` → `@InjectMock` available in tests (`hasInjectMock`)
   - legacy `quarkus-resteasy-client` → the project uses the RESTEasy Classic client; the
     MicroProfile annotations below are identical, so add new clients to the existing stack
     instead of introducing a second client library (`hasLegacyClient`)
4. **Existing clients** — grep `@RegisterRestClient` in `src/main/java`: note the package,
   interface naming, and whether clients configure via `configKey` or the interface FQN.
5. **Existing client config** — grep `quarkus.rest-client` in `src/main/resources/application.properties`
   (or `.yaml`): note URL conventions, whether `.scope` is set, and `%prod.`/`%dev.` overrides.
6. **Language** — this skill generates **Java** only. If the client must be Kotlin — STOP and
   tell the user (no Kotlin examples exist in this skill).

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and
tell the user this skill targets Quarkus projects.

---

# REST Client

Creates (or extends) a typed REST client for an external service: the interface with
`@RegisterRestClient`, the mandatory base-URL property, injection into a resource or service,
and a mock-based test.

---

> **CRITICAL: Code ONLY from examples/ files. If no matching example -- STOP and ask user.**
> **CRITICAL: The base URL property is mandatory — never finish without `quarkus.rest-client."<key>".url` (or an explicit `baseUri` in `@RegisterRestClient`).**
> **CRITICAL: For questions with a fixed set of choices, prefer your harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`) > its analogue > plain text list. Plain numbered text lists are the last resort when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 2–7 may already be answered by the user's prompt and prior turns. Re-asking what was already said is the #1 reason this skill feels slow.

---

## Defaults

| Option | Default | Notes |
|--------|---------|-------|
| clientName | `{ServiceName}Client` | e.g. service `Billing` → `BillingClient` |
| clientPackage | package of existing clients, else `{mainPackage}.client` | auto-detected in Step 1 |
| configKey | kebab-case service name, e.g. `billing-api` | must equal the property root exactly |
| remoteBasePath | from the API docs; omit `@Path` when the API has no common base path | — |
| operations | only what the task needs | never generate a hypothetical full API surface |
| returnTypes | DTO records when the project uses them; `Response` for status-only operations | missing DTOs → delegate to `quarkus-dto-creator` |
| baseUrl | per environment | `${ENV_VAR}` expansion for env-specific URLs; literal secrets are never committed |
| scope | project convention (often absent) | add `.scope` only when existing clients set it |
| tests | mock with `@InjectMock @RestClient` when the task expects tests | requires `quarkus-junit5-mockito` |

### Auto-detected (no questions)

| Option | Source |
|--------|--------|
| hasRestClient / hasRestClientJackson / hasInjectMock / hasLegacyClient | build file dependencies (preflight) |
| client naming, package, config-root style | existing `@RegisterRestClient` interfaces |
| DTO types | project DTO records |
| `.scope` usage, URL profile prefixes | existing `quarkus.rest-client` properties |

**Smart defaults:** If the user says "use defaults", "all defaults", "default settings", or
similar — skip ALL questions where a default is marked as recommended. Only ask mandatory
questions (target service when unknown, and any STOP conditions).

**Smart answer recognition:** When the user provides a value instead of choosing from a numbered
option — accept it, substitute it into the example, and continue. Do not re-ask.

### Decision-making principle — context first, then ask

1. Derive every option from the conversation context and the detected conventions first.
2. Score confidence (1–100). Confidence ≥ 80 → proceed with the detected/default value.
3. Confidence < 80 → ask, with the default option marked "Recommended" and first.
4. Never invent API contracts: unknown endpoints, request bodies, or response shapes must come
   from the user, from API docs, or from an OpenAPI document — otherwise stop and ask.

---

## Step 0 -- Conversation context first (REQUIRED, no tool calls)

Tell the user: `Step 0/8: Analyzing the request...`

**Do NOT call any tools in this step.**

Reason about what the request already tells you: which service is called, which operations are
needed, whether the client is new or extended, what the callers are, and whether tests are
expected. Predict the involvement:

```text
### Predicted involvement:
- Client: BillingClient (new)
- Operations: createInvoice (POST /invoices), getInvoice (GET /invoices/{id})
- Called from: InvoiceService
- Config: quarkus.rest-client."billing-api".url
- Tests: mock in InvoiceServiceTest
```

## Step 1 -- Preflight & conventions detection (automatic, no questions)

Tell the user: `Step 1/8: Detecting project conventions...`

Run the preflight above with file tools. Then score each convention below (1–100) from the code
and configuration you found (detection commands, placement rules, and the "what not to do" list:
[`references/conventions.md`](references/conventions.md)):

| Convention | How to detect | Default when absent |
|---|---|---|
| client package | existing `@RegisterRestClient` interfaces: `.client`, `.rest.client`, `.rest` | `{mainPackage}.client` |
| interface naming | existing client names: `XxxClient`, `XxxService`, `XxxApiClient` | `XxxClient` |
| config root | existing property keys: quoted `configKey` string vs quoted interface FQN | `configKey` |
| configKey style | existing keys: kebab-case (`billing-api`), snake, camelCase | kebab-case service name |
| `.scope` usage | `quarkus.rest-client."...".scope` present? | absent |
| URL environment handling | `%prod.` prefix vs single `url` vs `${ENV_VAR}` expansion | `${ENV_VAR}` expansion for env-specific URLs |
| DTO conventions | response types of existing clients: records in `.dto` vs entities | records via `quarkus-dto-creator` |

Report the result, e.g.: `Conventions detected: package .client, naming XxxClient, configKey kebab-case, no .scope, %prod. URL override.`

Conventions with confidence < 80 are collected and asked in Step 2 — not separately.

## Step 2 -- Target service, operations & types (context first, then ask)

Tell the user: `Step 2/8: Confirming client details...`

Derive from context first; ask only genuine unknowns, all in ONE batch (structured-question tool,
recommended option first):

- Which service/API is called, and where its base URL comes from (config property, secret store, env var).
- Which operations are needed — HTTP method + path per operation. If the user names operations,
  do not ask for the rest of the API.
- Response types: DTO records vs `Response`/raw types when only the status matters.
- Config key name, when it cannot be derived from conventions (default: kebab-case service name).
- Where the client is used from (service class vs resource) and whether tests are expected.

**Never invent endpoints, request/response fields, or auth schemes.** If the API contract is
unknown and the user cannot provide documentation, ask for the OpenAPI document URL or stop.

## Step 3 -- Dependencies (automatic)

Tell the user: `Step 3/8: Adding dependencies...`

1. Read [`examples/dependencies.md`](examples/dependencies.md)
2. Add only artifacts that are missing (`hasRestClient` / `hasRestClientJackson` / `hasInjectMock`)
3. Use the Quarkus extension-add command when a shell is available; otherwise edit the build file —
   omit versions (they are BOM-managed)
4. If `hasLegacyClient`, add to the existing client stack — never introduce a second client library

## Step 4 -- Client interface (code from examples only)

Tell the user: `Step 4/8: Creating the client interface...`

1. Read [`examples/client-interface.md`](examples/client-interface.md)
2. Substitute only the declared variables; place the interface per the detected conventions
3. One method per operation from Step 2, with JAX-RS annotations matching the remote API paths
4. Reuse existing DTO records for bodies; if response DTOs are missing, delegate to
   [`quarkus-dto-creator`](../quarkus-dto-creator/SKILL.md)
5. The import list must cover every shortened name used in the body

## Step 5 -- Base URL & configuration (code from examples only)

Tell the user: `Step 5/8: Writing client configuration...`

1. Read [`examples/config.md`](examples/config.md)
2. Write `quarkus.rest-client."<configKey>".url=...` — the quoted root must equal the `configKey`
   exactly (or the interface FQN when the client does not use `configKey`)
3. Environment-specific URLs → `%prod.`/`%dev.` prefixes or `${ENV_VAR}` expansion; API keys and
   tokens are never literal values in the file
4. Add `.scope` only when the project's existing clients set it

Details and pitfalls: [`references/client-config.md`](references/client-config.md).

## Step 6 -- Injection & usage (code from examples only)

Tell the user: `Step 6/8: Wiring the client in...`

1. Read [`examples/injection.md`](examples/injection.md)
2. Constructor injection with the `@RestClient` qualifier — the qualifier is mandatory; without
   it CDI cannot resolve which client to inject
3. Call the client from a service or resource — never from another REST client interface
4. Error handling: by default the MicroProfile client surfaces a response with status ≥ 400 as
   `jakarta.ws.rs.WebApplicationException`; wrap or map it only the way the project already does
   (see the callers of existing clients). Do not add retries, fallbacks, or circuit breakers
   unless the task asks for them.

## Step 7 -- Test the client (when tests are expected)

Tell the user: `Step 7/8: Writing the test mock...`

1. Read [`examples/mock-test.md`](examples/mock-test.md)
2. `@InjectMock @RestClient` replaces the client bean application-wide for the test class and
   requires `quarkus-junit5-mockito`; each test method gets a fresh mock
3. Stub only the operations the test exercises; assert over HTTP with rest-assured as the project
   does (see [`quarkus-test-writing`](../quarkus-test-writing/SKILL.md))
4. `@QuarkusIntegrationTest` runs out-of-process: mocking is impossible there — point the config
   at a real test instance instead ([`references/client-config.md`](references/client-config.md))
5. Running the tests: see [`quarkus-run-tests`](../quarkus-run-tests/SKILL.md)

## Step 8 -- Verify & report

Tell the user: `Step 8/8: Verifying...`

1. Compile: Maven `./mvnw -q -DskipTests compile`, Gradle `./gradlew -q compileJava`.
   Fix generated code before reporting.
2. Grep checks (a missing URL is **not** a compile error — it fails at startup or first use):
   - every `@RegisterRestClient` interface has a matching `quarkus.rest-client."<key>".url`
     (or `baseUri` in the annotation)
   - the quoted property root equals the annotation's `configKey` character-for-character
   - no hardcoded base URLs, API keys, or tokens in Java code
3. Report: client FQN, operations, config key and property file, consumer class, dependencies
   added, test file (if any).

---

## Anti-hallucination checklist

Before writing ANY code, verify:
- [ ] The code comes from an examples/ file (cite which one)
- [ ] Only declared variables were substituted
- [ ] No endpoints were invented — every method maps to an operation confirmed in Step 2
- [ ] `@RegisterRestClient` uses the detected config convention (`configKey` vs FQN) and the
      property root matches it exactly
- [ ] `quarkus.rest-client."<key>".url` exists; no client is left without a base URL
- [ ] No hardcoded base URLs, tokens, or API keys in Java code
- [ ] `@RestClient` qualifier present at every injection point
- [ ] DTO types exist in the project (or were created via `quarkus-dto-creator`)
- [ ] Import list covers all shortened names (no missing imports, no extras)
- [ ] Tests use `@InjectMock @RestClient`; no mocking attempted in `@QuarkusIntegrationTest`
- [ ] `.scope` added only when the project's clients use it
- [ ] The project's existing client stack was preserved (no second client library introduced)
- [ ] `jakarta.*` imports — never `javax.*`; no Spring annotations or imports
