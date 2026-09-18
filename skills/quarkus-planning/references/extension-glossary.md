> Local copy of `quarkus-explore/references/extension-glossary.md` — keep the two in sync when editing.

# Extension Glossary

What each Quarkus extension in a build file tells you about the project. Read the build file
(`pom.xml` / `build.gradle`) and classify every `io.quarkus:*` and `io.quarkiverse:*` dependency.

| Artifact (`io.quarkus:`) | What it means for the project |
|---|---|
| `quarkus-arc` | CDI — always present; beans via `@ApplicationScoped` |
| `quarkus-rest` / `quarkus-resteasy` | Jakarta REST layer (Quarkus REST is the default since 3.9) |
| `quarkus-rest-jackson` / `quarkus-resteasy-jackson` | JSON serialization — REST methods can return POJOs/records |
| `quarkus-hibernate-orm-panache` | Sync persistence: `PanacheEntity` / `PanacheRepository`, `@Transactional` |
| `quarkus-hibernate-reactive-panache` | Reactive persistence: same API returning `Uni<...>` |
| `quarkus-jdbc-postgresql` / `mysql` / `mariadb` / `h2` | Database kind for JDBC datasources |
| `quarkus-reactive-pg-client` | Reactive PostgreSQL (pairs with hibernate-reactive) |
| `quarkus-flyway` / `quarkus-liquibase` | Schema migrations — look for `db/migration` / `db/changelog` resources |
| `quarkus-hibernate-validator` | Bean Validation — expect `@Valid` on resource parameters |
| `quarkus-messaging-kafka` | Kafka via Reactive Messaging: `@Incoming`/`@Outgoing`/`@Channel` |
| `quarkus-oidc` | OIDC auth (`application-type=service` → bearer, `web-app` → code flow) |
| `quarkus-smallrye-jwt` | MP-JWT bearer tokens (legacy; prefer quarkus-oidc) |
| `quarkus-security` | `@RolesAllowed`, `SecurityIdentity` |
| `quarkus-smallrye-openapi` | `/q/openapi` schema + Swagger UI in dev |
| `quarkus-jacoco` | Coverage via `./mvnw clean verify`, report `target/jacoco-report/` |
| `quarkus-junit5` / `quarkus-junit-mockito` | `@QuarkusTest` / `@InjectMock` test toolkit |
| `io.quarkiverse.mapstruct:quarkus-mapstruct` | MapStruct mappers compile in native mode too |
| `quarkus-config-yaml` | `application.yaml` supported |
| `quarkus-scheduler` / `quarkus-quartz` | Scheduled jobs (`@Scheduled`) |
| `quarkus-cache` / `quarkus-caffeine` | `@CacheResult` method caching |
| `quarkus-micrometer` / `quarkus-micrometer-registry-prometheus` | Metrics, `/q/metrics` |
| `quarkus-container-image-docker` etc. | Container builds via `quarkus.container-image.build=true` |

Unknown extension? Do not guess its semantics from the name — check
https://quarkus.io/extensions/ or verify via context7 before claiming what it does.