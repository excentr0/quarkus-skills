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
| `io.quarkiverse.mapstruct:quarkus-mapstruct` | MapStruct support for native builds (Quarkiverse) |
| `quarkus-junit5` / `quarkus-junit5-mockito` | `@QuarkusTest` / `@InjectMock` |
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
- PanacheQL: string fragments like `"name = ?1"`, `"ORDER BY name"`; `find("Person.findByName", name)`
  for named queries. Pagination: `query.page(Page.of(index, size)).list()` (page index starts at 0),
  `.count()`, `.nextPage()`.
- Writes require `@Transactional` (`jakarta.transaction.Transactional`) on service/resource methods.
- Reactive (Hibernate Reactive + Panache): same API but returns `Uni<...>`:
  `person.persist()`, `Person.findById(23L)` → `Uni<Person>`, `Person.listAll()` → `Uni<List<Person>>`.
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
  `quarkus.http.auth.permission.<name>.policy=authenticated|permit-all|deny`.
- Method-level: `@RolesAllowed("admin")`, `@PermitAll`, `@DenyAll` (jakarta.annotation.security);
  user: inject `SecurityIdentity` (io.quarkus.security.identity) or `JsonWebToken`
  (org.eclipse.microprofile.jwt) — `jwt.getSubject()`, `jwt.getClaim("name")`, `idToken` via `@IdToken` (web-app).
- Dev Services can auto-start a Keycloak realm in dev/test.

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
- Mocking: `@InjectMock` field + `Mockito.when(...)` in `@BeforeEach` (quarkus-junit5-mockito).
- `@TestHTTPEndpoint(FruitResource.class)` on a `RestAssured` field targets the resource path.
- Surefire (Maven) needs a modern version + system props:
  `java.util.logging.manager=org.jboss.logmanager.LogManager`, `maven.home=${maven.home}`.
- Test config: `%test.` profile in `application.properties`, or `@QuarkusTestProfile` implementations.
- Data cleanup between tests: `@Transactional` on test methods (rollback semantics vary) — prefer explicit
  cleanup in `@BeforeEach`/`@AfterEach` against the real Dev-Service database.

## 10. Coverage & mutation testing

- Coverage: add `io.quarkus:quarkus-jacoco` (test scope). The extension wires the agent and generates the
  report itself — `./mvnw clean verify`, report at `target/jacoco-report/index.html` (data file
  `target/jacoco.exec`). Do NOT combine with `jacoco-maven-plugin` without special configuration (double
  instrumentation errors).
- Mutation testing: `org.pitest:pitest-maven` + `pitest-junit5-plugin` (≥ 1.19.4 required for Quarkus 3.22+;
  pitest ≥ 1.19.4). Run: `mvn org.pitest:pitest-maven:mutationCoverage` (or `pitest` task on Gradle).
  Target plain business classes; exclude `@QuarkusTest` test classes from `targetTests` (they are slow and
  framework-coupled); keep `targetClasses` scoped to `org.acme.*` business packages.

## 11. Native / container (background)

- Native build: `./mvnw package -Dnative` (requires GraalVM); container image: `quarkus-container-image-*`
  extensions, `./mvnw package -Dquarkus.container-image.build=true`. Skills should mention `quarkus:build`
  produces a fast-jar in `target/quarkus-app/` runnable via `java -jar target/quarkus-app/quarkus-run.jar`.