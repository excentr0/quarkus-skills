# Conventions — REST clients in this project

Detected in Step 1 from the existing code; every convention below is resolved to either the
project's own pattern or the stated default. Confidence < 80 → ask in Step 2.

## Detection commands (file tools)

| What | How |
|---|---|
| existing clients | grep `@RegisterRestClient` in `src/main/java` |
| client packages | package declarations of the files found above |
| client naming | interface names of the files found above |
| config roots | grep `quarkus.rest-client` in `src/main/resources/application.properties` (or `.yaml`) |
| `.scope` usage | same grep — look for `".scope"` keys |
| URL environment style | same grep — `%prod.`/`%dev.` prefixes or `${ENV_VAR}` expansions |
| DTO types | response types of existing clients + project DTO package (`.dto`, `.rest.dto`) |
| error handling | callers of existing clients: do they catch/wrap client exceptions? |

## Scoring

| Convention | Default when the project has no example | Ask when |
|---|---|---|
| package | `{mainPackage}.client` | two or more conflicting packages exist |
| naming | `{ServiceName}Client` | the project uses a different suffix consistently (e.g. `XxxApi`) — follow it |
| config root | `configKey` | existing clients use raw FQNs — follow them for consistency |
| configKey style | kebab-case service name (`payment-service`) | existing keys use another style |
| `.scope` | absent | existing clients set it — repeat the same value |
| URL env handling | `${ENV_VAR}` expansion (+ `%dev.` when a local instance exists) | URLs are hardcoded in the project's config (flag it, do not copy) |
| DTO usage | records; create missing ones via `quarkus-dto-creator` | the project reuses entities in its clients |

## Placement

- Interface in the same package as the project's other clients; a new subpackage only when the
  project already groups by integration (e.g. `.client.billing`).
- One interface per external service; extend the existing interface when only operations are added.
- Request/response DTOs: reuse project records; never expose Panache entities from a client
  interface (client types are wire types, not persistence types).
- Method names mirror the remote operation (`getInvoice`, `createInvoice`) or the project's verb
  convention when the existing clients follow one.

## What NOT to do

- Do not create a second client stack next to an existing one (legacy RESTEasy Classic vs the
  current client) — add to what the project already uses.
- Do not add client-side caching, retries, or fallbacks unless the task asks — Quarkus extensions
  (e.g. fault tolerance) own that concern.
- Do not put business logic in the client interface — it is a wire adapter; mapping belongs to the
  caller or a mapper (see [`quarkus-mapper-creator`](../../quarkus-mapper-creator/SKILL.md)).
