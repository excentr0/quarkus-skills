# Quarkus Facts — verified reference for skill writers

All facts below were verified against official Quarkus documentation (quarkus.io guides,
Quarkus 3.x LTS, 2025) before writing any skill. Skills MUST NOT contradict this file.
If a skill needs a fact that is missing here — verify it via context7 (`/websites/quarkus_io_guides`)
and add it here, or mark it in the skill with `<!-- VERIFY: ... -->`.

---

## 1. Build & tooling

| Action | Maven | Gradle |
|---|---|---|
| Dev mode | `./mvnw quarkus:dev` | `./gradlew quarkusDev` |
| Build | `./mvnw quarkus:build` | `./gradlew quarkusBuild` |
| Run tests | `./mvnw test` | `./gradlew test` |
| Add extension | `./mvnw quarkus:add-extension -Dextensions="quarkus-rest-jackson"` | `./gradlew addExtension --extensions="quarkus-rest-jackson"` |
| List extensions | `./mvnw quarkus:list-extensions` | `./gradlew listExtensions` |
| Create project | `mvn io.quarkus.platform:quarkus-maven-plugin:create -DprojectGroupId=org.acme -DprojectArtifactId=demo -Dextensions="rest-jackson,hibernate-orm-panache"` | same with `-DbuildTool=gradle` |

- Maven projects use `io.quarkus.platform:quarkus-bom` (import scope) + `io.quarkus.platform:quarkus-maven-plugin`
  (goals: `build`, `generate-code`, `dev`). Gradle projects use plugin `id("io.quarkus")`.
- Typical layout: `org.acme` root package; one module (microservice); `application.properties` in `src/main/resources`.
- Naming idioms: REST classes `XxxResource` (not `XxxController`), CDI services `XxxService`, repos `XxxRepository`,
  DTOs `XxxDto` / `Xxx` record in `.dto` or `.rest.dto` package, entities in `.domain` or `.entity`.
- `quarkus:dev` enables hot reload + Dev Services (auto-started DB/Kafka/Keycloak in dev and test modes).

## 2. Extensions (artifact ids under `io.quarkus:` unless noted)

| Extension | Purpose |
|---|---|
| `quarkus-arc` | CDI (ArC) — included by default |
| `quarkus-rest` | Jakarta REST on Quarkus REST (renamed from RESTEasy Reactive in Quarkus 3.9) |
| `quarkus-rest-jackson` | JSON serialization for REST |
| `quarkus-hibernate-orm-panache` | Hibernate ORM + Panache (sync) |
| `quarkus-hibernate-reactive-panache` | Hibernate Reactive + Panache (returns `Uni<...>`) |
| `quarkus-jdbc-postgresql` / `quarkus-jdbc-mysql` / `quarkus-jdbc-mariadb` / `quarkus-jdbc-h2` | JDBC drivers |
| `quarkus-reactive-pg-client` | reactive PostgreSQL driver (with hibernate-reactive) |
| `quarkus-flyway` / `quarkus-liquibase` | DB migrations |
| `quarkus-hibernate-validator` | Bean Validation (`@Valid`) |
| `quarkus-messaging-kafka` | Reactive Messaging with Kafka (SmallRye connector `smallrye-kafka`) |
| `quarkus-oidc` | OIDC: authorization code flow (`application-type=web-app`) and bearer tokens (`application-type=service`) |
| `quarkus-smallrye-jwt` | MP-JWT legacy alternative for bearer tokens (prefer `quarkus-oidc`) |
| `quarkus-security` | Core security annotations (`@RolesAllowed`, `SecurityIdentity`) |
| `quarkus-smallrye-openapi` | OpenAPI schema + Swagger UI in dev |
| `quarkus-jacoco` | JaCoCo coverage (test scope; replaces jacoco-maven-plugin) |
| `io.quarkiverse.mapstruct:quarkus-mapstruct` | MapStruct support (Quarkiverse): reads `@Mapper`/`@MapperConfig`, makes generated mappers native-safe and dev-mode-recompilable. It does NOT run the MapStruct annotation processor — the build still needs `org.mapstruct:mapstruct-processor` via maven-compiler-plugin `annotationProcessorPaths` (or Gradle `annotationProcessor`). |
| `quarkus-junit5` / `quarkus-junit-mockito` | `@QuarkusTest` / `@InjectMock` (`io.quarkus.test.InjectMock`) |
| `io.rest-assured:rest-assured` | HTTP tests (URL auto-configured in `@QuarkusTest`) |

## 3. Spring → Quarkus conversion (do not ship Spring code in Quarkus skills)

| Spring | Quarkus |
|---|---|
| `@Autowired` | `@Inject` (jakarta.inject) |
| `@Qualifier` | `@Named` |
| `@Value` | `@ConfigProperty` |
| `@Component` / `@Service` / `@Repository` | `@ApplicationScoped` (or `@Singleton`) CDI bean |
| `@Configuration` + `@Bean` | `@ApplicationScoped` class + `@Produces` method |
| `@RestController` + `@RequestMapping` | JAX-RS resource: `@Path("...")` + `@GET/@POST/...` |
| `@GetMapping` etc. | `@GET`, `@POST`, `@Path("...")` on the method |
| `JpaRepository` | `PanacheRepository<T>` / `PanacheRepositoryBase<T, ID>` |
| `Pageable`, `PageRequest`, `Page<T>` | `PanacheQuery.page(Page.of(index, size))` (page is 0-based) |
| `ResponseEntity<T>` | plain return + `@Produces`, `jakarta.ws.rs.core.Response`, or `org.jboss.resteasy.reactive.RestResponse` |
| `org.springframework.transaction.annotation.Transactional` | `jakarta.transaction.Transactional` |
| Spring Security `SecurityFilterChain` | `quarkus.http.auth.permission.*` config + `quarkus-oidc` |
| `@PreAuthorize` | `@RolesAllowed("role")` (jakarta.annotation.security) |
| `application.yml` | `application.properties` (or `application.yaml` if the YAML config extension is added) |

### Blocklist (must never appear in examples)
`org.springframework`, `@RestController`, `@RequestMapping`, `@GetMapping`, `@PostMapping`,
`@PutMapping`, `@DeleteMapping`, `@PatchMapping`, `@Service`, `@Repository`, `@Component`,
`@Autowired`, `@Configuration`, `@Bean`, `JpaRepository`, `CrudRepository`, `Pageable`,
`PageRequest`, `PageImpl`, `ResponseEntity`, `spring-boot-starter`, `Spring Boot`.

## 4. Panache (Hibernate ORM)

- Active Record: `@Entity public class Person extends PanacheEntity { public String name; }` —
  `Long id` provided; fields are `public` by convention; static finders:
  `find("name = ?1", name).firstResult()`, `list("status", Status.Alive)`, `listAll()`,
  `count()`, `delete("name", "Stef")`, `update("name = ?1 where status = ?2", ...)`,
  `persist()`, `persistAndFlush()`, `delete()`, `isPersistent()`.
- Repository: `@ApplicationScoped public class PersonRepository implements PanacheRepository<Person>`
  or `PanacheRepositoryBase<Person, Integer>` for a custom ID type. Same query API without statics.
- Custom ID: extend `PanacheEntityBase` and declare `@Id public Long id;` (or UUID with
  `@GeneratedValue(strategy = GenerationType.UUID)`).
- PanacheQL: string fragments like `"name = ?1"`, `"ORDER BY name"`; named parameters via
  `Map.of("name", value)`. Named queries: define with `@NamedQuery(name = "Person.getByName", ...)`
  and reference with the `#` prefix — `find("#Person.getByName", name)`. Pagination:
  `query.page(Page.of(index, size)).list()` (page index starts at 0), `.count()`, `.nextPage()`.
- Writes require `@Transactional` (`jakarta.transaction.Transactional`) on service/resource methods.
- Reactive (Hibernate Reactive + Panache): same API but returns `Uni<...>`:
  `person.persist()`, `Person.findById(23L)` → `Uni<Person>`, `Person.listAll()` → `Uni<List<Person>>`.
  Transactions: `@WithTransaction` (`io.quarkus.hibernate.reactive.panache.common.WithTransaction`)
  or `Panache.withTransaction(...)`. Plain `jakarta.transaction.Transactional` also works on
  `Uni`-returning methods.
- Jackson: `com.fasterxml.jackson.databind.ObjectMapper` is a built-in CDI bean (quarkus-jackson,
  bundled by `quarkus-rest-jackson`) — inject it; customize via `ObjectMapperCustomizer` beans.
- `equals`/`hashCode` for entities: proxy-safe pattern or id-based; lazy relations must not be touched
  in `toString()`.

## 5. REST (quarkus-rest)

- `jakarta.ws.rs.*`: `@Path`, `@GET/@POST/@PUT/@DELETE/@PATCH`, `@Produces/@Consumes(MediaType.APPLICATION_JSON)`,
  `@PathParam/@QueryParam/@HeaderParam`, `@RequestBody` does NOT exist — the body is the annotated/unannotated
  method parameter.
- Injection: `@Inject` or constructor injection (Quarkus generates the required no-args constructor automatically;
  with a single constructor `@Inject` is optional).
- Errors: throw `jakarta.ws.rs.WebApplicationException` subclasses (`BadRequestException` → 400,
  `NotFoundException` → 404) or map custom exceptions with
  `@ServerExceptionMapper` (`org.jboss.resteasy.reactive.server.ServerExceptionMapper`), returning
  `org.jboss.resteasy.reactive.RestResponse` (or `Uni<RestResponse<?>>`). `@ServerExceptionMapper` inside a
  resource class = scoped; in a separate `@ApplicationScoped` bean = global. Standard JAX-RS
  `ExceptionMapper<T>` + `@Provider` also works.
- Validation: add `quarkus-hibernate-validator`, annotate request DTOs with constraints
  (jakarta.validation.constraints.*) and `@Valid` on resource method parameters.
- OpenAPI: `quarkus-smallrye-openapi` serves `/q/openapi` + Swagger UI at `/q/swagger-ui` in dev mode.

## 6. Configuration

- `application.properties` in `src/main/resources`. Profile prefixes: `%dev.`, `%test.`, `%prod.`
  (unprefixed values apply to all profiles).
- Recommended grouping: `@ConfigMapping(prefix = "server")` interface; per-property: `@ConfigProperty(name = "...", defaultValue = "...")`;
  optional injection via `Optional<T>` / `Optional<List<T>>`.
- Missing required property = startup failure (`io.quarkus.runtime.configuration.ConfigurationException`).
- Common keys: `quarkus.http.port`, `quarkus.datasource.db-kind`, `quarkus.datasource.username`,
  `quarkus.datasource.jdbc.url`, `quarkus.hibernate-orm.database.generation` (`none|update|drop-and-create|create`).
- Production config goes under `%prod.` so Dev Services keep working in dev/test.

## 7. Security

- `quarkus.oidc.application-type=service` → bearer token (API); `web-app` → authorization code flow (UI).
- Properties (service): `quarkus.oidc.auth-server-url`, `quarkus.oidc.client-id`,
  `quarkus.oidc.credentials.secret`, `quarkus.oidc.token-path` (e.g. `/realms/quarkus/protocol/openid-connect/token`).
- Path policies: `quarkus.http.auth.permission.<name>.paths=/api/*` and
  `quarkus.http.auth.permission.<name>.policy=authenticated|permit|deny` (three built-in policies;
  role-based policies via `quarkus.http.auth.policy.<role-policy>.roles-allowed=user,admin` and
  `.policy=<role-policy>`).
- Method-level: `@RolesAllowed("admin")`, `@PermitAll`, `@DenyAll` (jakarta.annotation.security);
  user: inject `SecurityIdentity` (io.quarkus.security.identity) or `JsonWebToken`
  (org.eclipse.microprofile.jwt) — `jwt.getSubject()`, `jwt.getClaim("name")`, `idToken` via `@IdToken` (web-app).
- Dev Services auto-starts Keycloak in dev/test; import a realm with
  `quarkus.keycloak.devservices.realm-path=<realm.json>`; the started instance URL is exposed as the
  `keycloak.url` config property (usable in other properties via `${keycloak.url}`).

## 8. Kafka (quarkus-messaging-kafka)

- Vocabulary: **channel** = logical name mapped to a Kafka topic via connector `smallrye-kafka`.
- Consumer bean: `@ApplicationScoped` + `@Incoming("fruit-in") void consume(String payload)` (returning
  `Uni<Void>`/`CompletionStage<Void>` also supported).
- Producer bean: `@Outgoing("fruit-out") Multi<String> produce()` — or imperative:
  `@Inject @Channel("fruit-out") Emitter<String> emitter;` then `emitter.send(payload)`.
- Properties: `mp.messaging.incoming.<channel>.connector=smallrye-kafka`, `.topic=...`,
  `.value.deserializer=...`; `mp.messaging.outgoing.<channel>.connector=smallrye-kafka`, `.topic=...`,
  `.value.serializer=...`. Built-in serializers: `io.quarkus.kafka.client.serialization.JsonbSerializer`,
  ObjectMapper-based; Quarkus autodetects serializers/deserializers from `@Incoming`/`@Outgoing`/`@Channel`
  declarations in many cases (built-in types, JsonObject, etc.).
- Kafka transactions with Hibernate: `KafkaTransactions<T>` from `@Channel` +
  `emitter.withTransaction(e -> { entity.persist(); e.send(entity); return Uni.createFrom().voidItem(); })`.
- Dev Services starts Kafka automatically in dev/test when `quarkus-messaging-kafka` is present.

## 9. Testing

- `@QuarkusTest` (quarkus-junit5): boots the app in the test JVM; CDI injection works; Dev Services start
  automatically; rest-assured base URL auto-configured.
- `@QuarkusIntegrationTest`: runs the packaged artifact (`quarkus:build` output / native binary); NO CDI injection,
  no `@InjectMock`, no config overrides — black-box HTTP tests only.
- Mocking: `@InjectMock` (`io.quarkus.test.InjectMock`, requires `quarkus-junit-mockito`) field +
  `Mockito.when(...)` in `@BeforeEach`; legacy package `io.quarkus.test.junit.mockito.InjectMock` is pre-3.x.
- `@TestHTTPEndpoint(FruitResource.class)` on a `RestAssured` field targets the resource path.
- Surefire (Maven) needs a modern version + system props:
  `java.util.logging.manager=org.jboss.logmanager.LogManager`, `maven.home=${maven.home}`.
- Test config: `%test.` profile in `application.properties`, or `@QuarkusTestProfile` implementations.
- Data cleanup between tests: `@Transactional` on test methods (rollback semantics vary) — prefer explicit
  cleanup in `@BeforeEach`/`@AfterEach` against the real Dev-Service database.

## 10. Coverage & mutation testing

- Coverage: add `io.quarkus:quarkus-jacoco` (test scope). The extension wires the agent and generates the
  report itself — `./mvnw clean verify`, report at `target/jacoco-report/index.html` (data file
  `target/jacoco-quarkus.exec`). Do NOT combine with `jacoco-maven-plugin` without special configuration (double
  instrumentation errors).
- Mutation testing: `org.pitest:pitest-maven` + `pitest-junit5-plugin` (≥ 1.19.4 required for Quarkus 3.22+;
  pitest ≥ 1.19.4). Run: `mvn org.pitest:pitest-maven:mutationCoverage` (or `pitest` task on Gradle).
  Target plain business classes; exclude `@QuarkusTest` test classes from `targetTests` (they are slow and
  framework-coupled); keep `targetClasses` scoped to `org.acme.*` business packages.



## 12. Native / container build (verified details)

- JVM fast-jar: `./mvnw quarkus:build` → runnable app in `target/quarkus-app/` —
  `java -jar target/quarkus-app/quarkus-run.jar`. Also `-Dquarkus.package.type=uber-jar` for a fat jar.
- Native: `./mvnw package -Dnative` (or `-Dquarkus.native.enabled=true`) — requires GraalVM/Mandrel locally
  OR a container build: `-Dquarkus.native.container-build=true` (builder image via
  `-Dquarkus.native.builder-image=quay.io/quarkus/ubi9-quarkus-mandrel-builder-image:jdk-21`).
  Gradle: `./gradlew build -Dquarkus.native.enabled=true`.
  Output: `target/*-runner` (native executable). `quarkus build --native` via Quarkus CLI works too.
- Container images: add `quarkus-container-image-docker` / `-jib` / `-podman`; build with
  `./mvnw package -Dquarkus.container-image.build=true`; name/group/tag via `quarkus.container-image.*`
  (`quarkus.container-image.group=<registry/project>`, `.name=`, `.tag=`). Native + container can be
  combined: `-Dquarkus.container-image.build=true -Dnative -Dquarkus.native.container-build=true`.

## 13. Flyway / Liquibase migrations

- Flyway: `quarkus-flyway` extension; versioned SQL in `src/main/resources/db/migration/`, naming
  `V<VERSION>__<Description>.sql` (e.g. `V1.1__My_description.sql`); repeatable migrations default prefix
  `R` (`quarkus.flyway.repeatable-sql-migration-prefix`). Enable at startup: `quarkus.flyway.migrate-at-start=true`.
  Other keys: `quarkus.flyway.locations` (default `db/migration`), `quarkus.flyway.table`,
  `quarkus.flyway.baseline-on-migrate`, `quarkus.flyway.schemas`.
- Multiple datasources: per-datasource prefix `quarkus.flyway.<datasource-name>.*`.
- Liquibase: `quarkus-liquibase` extension; `quarkus.liquibase.migrate-at-start=true`; changelog XML/YAML/SQL
  under `src/main/resources/db/` (verify exact default filename in the quarkus-liquibase guide before
  asserting it: the guide examples use `db/changelog/master.xml` with `quarkus.liquibase.change-log` to point at it).
- Flyway CLI goal inside Maven: the extension does the migration during dev/test/start — no separate
  maven goal needed. Dev Services: DB container starts in dev/test automatically; in `%prod` the real
  datasource config applies.

## 14. REST client (quarkus-rest-client)

- Dependencies: `quarkus-rest-client` + `quarkus-rest-client-jackson` (JSON).
- Declarative client: interface with JAX-RS annotations + `@RegisterRestClient(configKey = "bar")`
  (`org.eclipse.microprofile.rest.client.inject.RegisterRestClient`):
  `@Path("foo") @RegisterRestClient(configKey = "bar") public interface BarClient { @GET Response get(); }`
- Injection: `@Inject @RestClient BarClient client;` (qualifier `@RestClient` from the same package).
- Base URL is MANDATORY: `quarkus.rest-client."bar".url=https://api.example.com` (key = configKey,
  or the interface FQN without configKey). Optional `quarkus.rest-client."bar".scope=jakarta.inject.Singleton`.
  Per-invocation base-URL override: `@io.quarkus.rest.client.reactive.Url` on a method parameter.
- Testing: in `@QuarkusTest`, mock with `@InjectMock @RestClient BarClient client;` + `Mockito.when(...)`.
- A response with status ≥ 400 makes the client throw `jakarta.ws.rs.WebApplicationException` by
  default (MicroProfile REST Client behavior); map or catch it explicitly.

## 15. Config mapping details

- `@ConfigMapping(prefix = "server")` interface: methods map to properties (`server.host`, `server.port`).
- Nested groups: nested interfaces (`interface Log { boolean enabled(); }` → `server.log.enabled`).
- Defaults: `@WithDefault("8080")`; renames: `@WithName("optional.int")`.
- Optional types: `Optional<String>`, `OptionalInt` — absent property is fine; non-Optional missing
  property fails startup (`NoSuchElementException` → `ConfigurationException`).
- Lists: `List<String>` maps from comma-separated values. Environment variables override properties
  (`SERVER_HOST` → `server.host`).
- `@ConfigProperty(name = "...", defaultValue = "...")` for one-off injection; `Optional<T>` injection
  for may-be-missing properties.

## 16. RabbitMQ (quarkus-messaging-rabbitmq)
- Extension: `io.quarkus:quarkus-messaging-rabbitmq` (preview status); connector value is exactly
  `smallrye-rabbitmq`. Companion guides: quarkus.io/guides/rabbitmq and quarkus.io/guides/rabbitmq-reference.
- Programming model is standard Reactive Messaging: `@Incoming`/`@Outgoing`/`@Channel` + `Emitter` —
  same code as the Kafka connector, only connector config and JSON mapping differ.
- **Incoming channel → queue, outgoing channel → exchange.** Both names default to the channel name
  (`queue.name` / `exchange.name` written only when different; `""` = default exchange).
- Defaults: `queue.declare=true` (declares queue **and binding**), `queue.durable=true`,
  `exchange.declare=true`, `exchange.durable=true`, `exchange.auto-delete=false`, `exchange.type=topic`,
  `routing-keys=#` (binding), `failure-strategy=reject` (also `fail`, `accept`),
  `auto-acknowledgement=false`. Existing infra → name + `queue.declare=false` / `exchange.declare=false`.
- **No serializer/deserializer config keys exist** (unlike Kafka). Outgoing payload conversion is automatic:
  `String`/primitives/`UUID` → `text/plain`; `JsonObject`/`JsonArray`/any POJO → JSON (`application/json`,
  Json Mapper); `byte[]`/`Buffer` → binary. Unserializable payload → nacked.
- Incoming JSON body → consumer takes `io.vertx.core.json.JsonObject` and maps with `.mapTo(MyType.class)`
  (not the POJO as parameter); `content-type-override` forces `content_type` on incoming.
- Metadata: `io.smallrye.reactive.messaging.rabbitmq.IncomingRabbitMQMetadata` (getRoutingKey/getHeaders/
  getContentType/getHeader...) and `.OutgoingRabbitMQMetadata` (Builder: withRoutingKey/withHeader/
  withTimestamp) attached via `Message.of(payload, Metadata.of(metadata))`.
- Broker access: global `rabbitmq-host`/`rabbitmq-port` (5672)/`rabbitmq-username`/`rabbitmq-password`;
  per-channel `host`/`port`/`username`/`password` (aliases). Writing them unprefixed disables Dev
  Services for RabbitMQ — real broker goes under `%prod.` only.
- Dev Services: image `docker.io/library/rabbitmq:3.12-management` (http-port = management UI),
  `quarkus.rabbitmq.devservices.{enabled,port,http-port,shared,service-name,image-name}` plus
  pre-provisioning keys `exchanges.<n>.{type,durable,auto-delete,vhost}` (type default `direct`),
  `queues.<n>.{durable,auto-delete,vhost}`, `bindings.<n>.{source,routing-key,destination,
  destination-type,vhost}`.
- DLQ (incoming): `auto-bind-dlq=true` + `dead-letter-queue-name` (default `<queue>.dlq`),
  `dead-letter-exchange` (default `DLX`), `dead-letter-exchange-type` (default `direct`),
  `dead-letter-routing-key`, `dlx.declare`, `dead-letter-queue-type` [quorum, classic, stream].
- `@Blocking` (`io.smallrye.reactive.messaging.annotations.Blocking`) runs a blocking consumer method on
  a worker thread. Health: per-channel `health-enabled` with `quarkus-smallrye-health`.

## 17. OpenTelemetry (quarkus-opentelemetry) — verified 2026-09 against Quarkus 3.33 LTS + main
- Extension: `io.quarkus:quarkus-opentelemetry`. **Traces are on by default** once the extension is
  present (sampler `parentbased_always_on`, propagators `tracecontext,baggage`, OTLP export to
  `http://localhost:4317`).
- **Metrics are disabled by default** on 3.33 LTS ("tech preview") — enable explicitly with
  `quarkus.otel.metrics.enabled=true`. On newer main the default flipped to true — writing it
  explicitly is correct on both.
- Version drift (verified on both branches): `quarkus.otel.exporter.otlp.protocol` defaults to
  **`grpc`** (port 4317) on 3.33 LTS and to **`http/protobuf`** (port 4318) on newer main. Only
  `grpc` and `http/protobuf` are supported; when writing an endpoint, always write the protocol with
  the matching port. Per-signal endpoints: `quarkus.otel.exporter.otlp.{traces,metrics}.endpoint`.
- Exporter defaults: endpoint `http://localhost:4317`, timeout `10s`, headers
  `key1=value1,key2=value2`, compression unset (= none). Exporters are wired via CDI
  (`quarkus.otel.traces.exporter` / `...metrics.exporter` default `cdi`); values `otlp`, `none`,
  `logging` (needs `io.opentelemetry:opentelemetry-exporter-logging`).
- Disable layers: `quarkus.otel.enabled=false` (build time, everything),
  `quarkus.otel.exporter.otlp.enabled=false` (build time — telemetry still generated/propagated,
  nothing sent), `quarkus.otel.sdk.disabled=true` (runtime), per-signal `quarkus.otel.traces.enabled`
  / `quarkus.otel.metrics.enabled` (build time).
- Resource attributes (automatic): `service.name` = `quarkus.application.name` (fallback artifactId),
  `service.version` = artifact version, `host.name`, `telemetry.sdk.*`, `webengine.*`. Extra:
  `quarkus.otel.resource.attributes=key1=val1,...`; `quarkus.otel.service.name` takes precedence.
- Traces knobs: `quarkus.otel.traces.sampler` (`parentbased_always_on` default;
  `always_on`, `always_off`, `traceidratio`, `parentbased_*`) + `quarkus.otel.traces.sampler-arg`
  (default `1.0d`); `quarkus.otel.traces.suppress-non-application-uris=true` (default, hides `/q/*`),
  `quarkus.otel.traces.suppress-application-uris`, `quarkus.otel.traces.include-static-resources`
  (default `false`); BSP defaults: `schedule.delay=5s`, `max.queue.size=2048`,
  `max.export.batch.size=512`, `export.timeout=30s`.
- Metric interval: `quarkus.otel.metric.export.interval` default `60s`.
- Auto-instrumented extensions (spans, no code): quarkus-rest/resteasy (server),
  quarkus-rest-client(-jaxrs)/resteasy-client (client), quarkus-vertx (http), quarkus-grpc,
  quarkus-messaging (Kafka, AMQP 1.0, RabbitMQ, Pulsar), quarkus-redis-client,
  quarkus-mongodb-client, quarkus-scheduler, quarkus-smallrye-graphql, websockets-next.
  JDBC spans: `quarkus.datasource.jdbc.telemetry=true` (off by default) — one span per JDBC query.
- Instrumentation flags (default true, build time): `quarkus.otel.instrument.{grpc,rest,resteasy,
  resteasy-client,messaging,vertx.http,vertx.event-bus,vertx.sql-client,vertx.redis-client,
  jvm.metrics,http-server-metrics}`.
- CDI-injectable: `io.opentelemetry.api.OpenTelemetry`, `io.opentelemetry.api.trace.Tracer`,
  `io.opentelemetry.api.trace.Span`, `io.opentelemetry.api.baggage.Baggage`, and
  `io.opentelemetry.api.metrics.Meter` (metrics API).
- Custom spans: `io.opentelemetry.instrumentation.annotations.{WithSpan,SpanAttribute,
  AddingSpanAttributes}` on **any CDI bean** method; reactive return types supported; if both
  `@WithSpan` and `@AddingSpanAttributes` apply, `@WithSpan` wins. Manual spans:
  `tracer.spanBuilder("name").startSpan()` + `Scope` + `end()`.
- OTel metrics API: `Meter` (`counterBuilder` → `LongCounter`, `histogramBuilder(...).ofLongs()` →
  `LongHistogram`, `gaugeBuilder(...).ofLongs().buildWithCallback(...)`). Attributes via
  `io.opentelemetry.api.common.{Attributes,AttributeKey}`. No Timers/Distribution Summaries and no
  annotations in the OTel API — histograms replace them; `@Counted`/`@Timed`/`@Gauge` are
  **Micrometer-only**. Histogram bucket boundaries are inclusive and advisory only.
- Dev-mode observability: LGTM Dev Service via `io.quarkus:quarkus-observability-devservices-lgtm`
  (Maven scope `provided`) — starts Grafana + Tempo + Prometheus + Loki + OTel collector in dev mode
  only and auto-injects the OTLP endpoint (do NOT write an unprefixed OTLP endpoint alongside it).
  Disabled with `quarkus.observability.lgtm.enabled=false`; tests opt-in via
  `quarkus.observability.enabled-in-tests=true`. Jaeger v2 alternative (manual, no properties
  needed — default endpoint matches): `docker run -it -p 16686:16686 -p 4317:4317 -p 4318:4318
  jaegertracing/jaeger:latest`, UI on 16686.
- Testing: `io.opentelemetry:opentelemetry-sdk-testing` (test scope) + `@Produces @Singleton`
  producers of `io.opentelemetry.sdk.testing.exporter.InMemory{Span,Metric}Exporter`; assert via
  `getFinishedSpanItems()` / `getFinishedMetricItems()`. Speed-up keys from Quarkus's own
  integration tests: `quarkus.otel.bsp.schedule.delay=100`, `quarkus.otel.metric.export.interval=100ms`.
  For `@QuarkusIntegrationTest`, expose the exporters through a REST endpoint inside the app.
- Micrometer interop (3 paths, do not mix): classic Micrometer + registry → `/q/metrics` (Prometheus;
  unrelated to OTel); Quarkiverse `io.quarkiverse.micrometer.registry:quarkus-micrometer-registry-otlp`
  pushes Micrometer metrics via OTLP; bridge `io.quarkus:quarkus-micrometer-opentelemetry`
  (preview, since 3.19) routes Micrometer metrics through the OTel SDK (auto Micrometer binders off
  by default — enable with `quarkus.micrometer.binder.*`).
