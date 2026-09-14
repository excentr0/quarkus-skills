---
name: quarkus-explore
description: >
  Explores a Quarkus application and builds primary context: tech stack,
  build system, Quarkus version, extensions, CDI beans, Panache entities and
  repositories, REST resources, configuration, and tests.
  Triggers on explicit requests: "explore project", "describe project", "project overview",
  "what is this project", "project structure", "tech stack", "give me context about the project",
  or whenever you need to understand the project before starting any task.
  Russian phrases also trigger this: "изучи проект", "опиши проект", "структура проекта",
  "контекст проекта", "что за проект".
---

# Explore Application

Collects primary project context in steps 0–6. Execute steps sequentially — each one
builds on the results of the previous.

**Important:** if context has already been collected in the current conversation, do not
repeat the exploration — use what is already known.

---

## Preflight — Project detection (before step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`,
   version property `quarkus.platform.version` / `quarkus.version`; Gradle: `io.quarkus` plugin + `quarkusPlatform` version.
3. **Extensions** — dependencies starting with `io.quarkus:` (and Quarkiverse `io.quarkiverse.*`).
   See [`references/extension-glossary.md`](references/extension-glossary.md).
4. **Persistence stack** — `quarkus-hibernate-orm-panache` → ORM Panache (sync);
   `quarkus-hibernate-reactive-panache` → reactive Panache (`Uni`-returning); neither → no Panache layer.
5. **Config files** — `src/main/resources/application.properties` (or `.yaml`), Flyway/Liquibase migrations under
   `src/main/resources/db/migration` / `db/changelog`.

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and tell
the user this skill targets Quarkus projects.

---

## Step 0 — Predict involvement from the user's request

Tell the user: `Step 0/6: Analyzing request...`

**Do NOT call any tools in this step.**

Read the user's request and reason about what the implementation likely involves.
Without calling any tools, make educated guesses based on naming conventions, domain
language, and typical Quarkus patterns:

- **Entities** — what domain objects are likely involved? (e.g. "create order" → `Order`, `OrderItem`)
- **Repositories** — which Panache repositories probably exist for those entities?
- **Services** — which `@ApplicationScoped` services are likely needed?
- **Resources** — which JAX-RS resources (`XxxResource`) probably handle this area?
- **Other beans** — mappers, validators, `@Incoming`/`@Outgoing` messaging beans, producers, configs, etc.
- **Files** — what non-Java files are likely relevant? (`application.properties`, Flyway/Liquibase
  migrations, `application.yaml`, HTML templates). Do not list Java classes here.

Build a preliminary gap list containing only what is genuinely required:

```
### Predicted involvement:
- Entities: Order, OrderItem, Customer
- Repositories: OrderRepository, CustomerRepository
- Services: OrderService
- Resources: OrderResource
- Other: OrderMapper
- Files: src/main/resources/db/migration/V1__create_orders.sql, application.properties
```

This prediction drives steps 1–5 — skip anything irrelevant to the task.

---

## Step 1 — Define exploration goal and select paths

Tell the user: `Step 1/6: Selecting exploration paths...`

**Do NOT call any tools in this step.**

Read the current conversation context — the user's request, any prior exploration results, remaining
gaps — and formulate the key exploration goal in one sentence. Show it to the user:

```
### Exploration goal:
Understand the Order aggregate structure and verify what repositories and mappers already exist.
```

Using this goal, go through each exploration path below and explicitly decide: **include** or **skip**,
with a one-line reason. Do this for every path — do not skip the evaluation itself.

**Project structure**
- **Build file analysis** — include if the stack, Quarkus version, extensions, or persistence mode are
  needed. This is almost always included on first exploration.
- **List REST resources** — include only if you need to check what already exists to avoid duplication
  or understand conventions. Skip if the request fully defines all endpoints from scratch.

**Domain model**
- **Entity descriptions** — include if entity fields or annotations are needed. Apply only to predicted
  entities, not all entities. See [`references/entity-description.md`](references/entity-description.md).
- **Repositories** — include if repositories for predicted entities are unknown or need to be verified.

**Services & mappers**
- **Services** — include if the task touches business logic and service beans are unknown.
- **Mappers** — include if the task involves DTOs and you need to know what mappers exist (MapStruct
  interfaces or custom converters).
- **DTOs** — include if you need to know what DTO records/classes already exist.

**REST layer**
- **REST endpoint summary** — include if you need verbs/paths/DTOs of relevant resources.
  See [`references/rest-endpoints.md`](references/rest-endpoints.md).

**Configuration**
- **application.properties scan** — include if the task touches configuration, datasources, security,
  or messaging; redact secrets when reporting.

Write out the evaluation explicitly, then produce the final plan from included paths only:

**Example** — for a request "Add a paginated endpoint returning all orders for a customer with order
items and product names":
```
### Path evaluation:
- Build file analysis: INCLUDE — need Quarkus version, extensions, persistence mode
- List REST resources: INCLUDE — need to check if an orders endpoint already exists
- Entity descriptions: INCLUDE — need Order, OrderItem, Product fields for response DTO design
- Repositories: INCLUDE — need to verify OrderRepository exists and supports pagination
- Services: SKIP — no service layer changes expected
- Mappers: INCLUDE — need to know if OrderMapper already exists before creating DTOs
- DTOs: INCLUDE — need to know if OrderDto already exists
- REST endpoint summary: SKIP — "List REST resources" is enough here
- application.properties scan: INCLUDE — need to confirm datasource/Flyway setup

### Exploration plan:
1. Read pom.xml (quarkus-bom version, extensions)
2. Glob src/main/java/**/*.java → index packages and class names
3. Read Order, OrderItem, Product entities
4. Read OrderRepository, CustomerRepository
5. Grep for MapStruct @Mapper / custom converters related to Order
6. Grep for OrderDto / OrderItemDto
7. Read src/main/resources/application.properties (redact secrets)
```

---

## Step 2 — Load references

Tell the user: `Step 2/6: Loading relevant references...`

**Do NOT call any tools in this step.**

Based on the exploration plan from step 1, load only the references needed for the selected paths
**that have not already been loaded in this conversation**:

| Selected path | Reference to load |
|---|---|
| Build file analysis | [`references/extension-glossary.md`](references/extension-glossary.md) |
| Entity descriptions | [`references/entity-description.md`](references/entity-description.md) |
| REST endpoint summary | [`references/rest-endpoints.md`](references/rest-endpoints.md) |

If none of the paths require references — skip this step and proceed to step 3.

---

## Step 3 — Build unified exploration plan

Tell the user: `Step 3/6: Building exploration plan...`

**Do NOT call any tools in this step.**

Using the selected paths from step 1 and the processes described in the loaded references, build a
single unified numbered plan of file-tool calls to execute in steps 4–5. Each item must be a concrete
tool call (read path / grep pattern / glob), not a category name.

```
### Unified exploration plan:
1. read pom.xml
2. glob src/main/java/**/domain/*.java
3. read Order.java, OrderItem.java, Product.java
4. read OrderRepository.java
5. grep "@Mapper" in src/main/java
6. read src/main/resources/application.properties
```

---

## Step 4 — Execute exploration plan

Tell the user: `Step 4/6: Executing exploration plan...`

If your harness offers subagents, you may delegate the mechanical reads to one subagent to keep your
context lean; otherwise execute the plan directly with your file tools. Either way:

- Collect and return ALL results in full — do not summarize or truncate.
- Secret redaction: if any returned value belongs to a key that looks like a credential
  (`password`, `secret`, `token`, `api-key`, `credentials`, `client-secret`, or similar), replace
  only the value with `[REDACTED]` and keep the key and surrounding structure intact. Never echo
  credential values verbatim.

Wait for all results before proceeding.

---

## Step 5 — Build exploration report

Tell the user: `Step 5/6: Building exploration report...`

**Do NOT call any tools in this step — reason only from the collected results.**

Synthesize all findings collected across all exploration cycles into a single report. Include only what
is genuinely valuable for the task — omit noise and obvious defaults.

Structure:

```
### Exploration Report

**Stack:** Java 21 · Quarkus 3.20 · Maven
**Persistence:** Hibernate ORM Panache (sync)   <!-- Panache sync · Panache reactive · none — required when any entity-touching path ran -->

**Domain model:**
- Order (id, status, totalAmount) → has many OrderItem → references Product
- Customer (id, name, email)

**Repositories:**
- OrderRepository — PanacheRepository, custom finder findByCustomer

**Services:**
- OrderService — @ApplicationScoped, handles order creation and status transitions

**Mappers:**
- OrderMapper (MapStruct, componentModel="cdi") — maps Order ↔ OrderDto

**DTOs:**
- OrderDto, OrderItemDto — records, already exist

**REST API (relevant endpoints):**
- GET /orders — paginated list
- POST /orders — create order

**Configuration:**
- PostgreSQL datasource (%prod config), Flyway enabled

**Notable findings:**
- Security: quarkus-oidc bearer — /api/* requires authentication
- No mapper for Customer — will need to create one
```

---

## Step 5.5 — Formulate implicit assumptions

Tell the user: `Step 5.5/6: Formulating implicit assumptions...`

**Do NOT call any tools in this step — reason only from the collected results and the user's request.**

Based on the exploration report and the user's request, identify everything the user did **not**
explicitly say but likely expects from the implementation. These are implicit assumptions — unstated
requirements, conventions, and design decisions the user probably takes for granted.

Focus on:
- **Behavioral expectations** — e.g. "user probably expects soft delete, not hard delete", "pagination assumed to be page/size"
- **Security/access control** — e.g. "endpoint likely should require authentication like all others in this project"
- **Validation** — e.g. "fields like email and price are likely expected to be validated"
- **Error handling** — e.g. "returning 404 on missing entity is likely expected, not 500"
- **Conventions** — e.g. "response format likely expected to match existing endpoints (camelCase, plain JSON)"
- **Related side effects** — e.g. "creating an order probably expected to update inventory or emit a Kafka event"
- **DTO shape** — e.g. "response probably expected to include nested items, not just IDs"

Output all assumptions explicitly so they can be validated or corrected:

```
### Implicit assumptions:
1. The new endpoint should require authentication — all existing endpoints use quarkus-oidc bearer.
2. Response format should match existing endpoints — camelCase JSON, no wrapper object.
3. Pagination is expected to be page/size params — consistent with other list endpoints.
4. Missing entity should return 404 via NotFoundException, not 500.
5. Price field is expected to be validated as positive — consistent with other monetary fields.
6. OrderItem list in response should include product name and quantity — implied by "order details" framing.
```

If no implicit assumptions can be identified — state that explicitly:
```
### Implicit assumptions: none identified — the request is fully specified.
```

---

## Step 6 — Decide on next cycle

Tell the user: `Step 6/6: Evaluating next cycle...`

**Do NOT call any tools in this step — reason only from the collected results.**

Predict the value of an additional cycle (0–100): how critical are the remaining gaps, and are they
resolvable with file tools? Show score and reasoning:

```
### Additional cycle value: 87/100 → additional exploration cycle required.
```

**Score > 80** — go to **Step 1**. **Score ≤ 80** — stop.

---

## Anti-hallucination checklist

- [ ] Quarkus version and extension list came from the build file — not from assumptions.
- [ ] Persistence mode (sync vs reactive Panache) verified from dependencies before any entity work.
- [ ] Entity field lists come from actual source files.
- [ ] Endpoint verb/path list matches `@Path`/`@GET`/`@POST` annotations actually present.
- [ ] Secrets in application.properties were redacted in the report.
- [ ] Every claim in the report traces to a file you actually read.