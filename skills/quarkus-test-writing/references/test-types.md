# Test Types

Three levels, three different costs. Pick the cheapest one that can still fail for the right reason.

## Decision table

| What must be true for the test to have value | Type | Cost |
|---|---|---|
| A business rule / computation behaves correctly | plain JUnit 5 | milliseconds, no container |
| A CDI bean wires correctly and its logic works with real collaborators present | `@QuarkusTest` | app boot + Dev Services (Docker) |
| The HTTP contract is right: path, status code, JSON shape, validation errors | `@QuarkusTest` + rest-assured | app boot + Dev Services |
| A Panache query / transaction boundary behaves against a real database dialect | `@QuarkusTest` | app boot + Dev Services |
| The packaged artifact works (fast-jar, native binary, container) | `@QuarkusIntegrationTest` | packaging + process launch — slowest |

## plain JUnit 5

- No Quarkus annotations, no CDI. Construct the class under test directly (`new ${ClassName}()`).
- Collaborators: plain Mockito mocks or hand-written fakes — no `@InjectMock`, no container.
- Fastest tests in the project; most business logic belongs here.
- If a test "needs" CDI to run, that is a signal the logic is entangled with the framework — consider
  testing the extracted logic instead of booting the app for it.

## @QuarkusTest

- The application boots **inside the test JVM**. `@Inject` works, `@InjectMock` works, Dev Services
  (PostgreSQL, Kafka, Keycloak — whichever extensions are present) start automatically.
- rest-assured is preconfigured with the test base URL — no `baseURI` setup needed.
- `%test.` profile properties apply. Implement `QuarkusTestProfile` as an interface and activate it with `@TestProfile(MyProfile.class)`.
- **State persists**: all tests in a run share one app instance and one Dev-Service database. Tests that
  write data must clean up (`references/conventions.md`).
- Requires a container runtime for Dev Services when a datasource/messaging extension is present —
  without Docker these tests fail before any assertion runs.

## @QuarkusIntegrationTest

- Runs the packaged artifact using production configuration; the integration test process is separate from the app: no CDI injection, `@InjectMock`, or test-process config override for the packaged application. `src/test/resources` application configuration is not used by this packaged test process. Use black-box public interfaces.
- Write a separate integration test class by default. Do not assume an injectable `@QuarkusTest` parent; reuse a test parent only when source and build configuration prove it is compatible without CDI assumptions.

- Only worth it when packaging/startup itself is part of the risk (native image, container, CLI). For
  ordinary regression checks the `@QuarkusTest` variant covers the same endpoints.

## Naming decides the runner (Maven)

| Name pattern | Runner | Phase |
|---|---|---|
| `${...}Test` | surefire | `./mvnw test` |
| `${...}IT` | failsafe | `./mvnw verify -DskipITs=false` (after confirming target POM bindings; generated Quarkus 3.20.3 POM defaults Failsafe to skipped) |

- Maven failsafe's default includes are `**/IT*.java`, `**/*IT.java`, `**/*ITCase.java` — a class named
  `GreetingIT` runs under `verify`; `GreetingTest` runs under `test`.
- Gradle: the two types need different source sets and tasks (`test` vs `quarkusIntTest`) — do not mix.
- Maven Surefire and Failsafe are separate runners/phases, but a single `mvn verify` can execute both; this is valid. Gradle uses separate source sets/tasks. Report what each invocation actually ran.

## Anti-patterns

- Booting `@QuarkusTest` to test `new DiscountService().apply(10)` — pays the framework cost for nothing.
- A "unit" test that secretly needs a repository → NPE on the first real call; move it to `@QuarkusTest`.
- `@InjectMock` in an `*IT` class — compiles, does nothing, test fails at runtime.
- Asserting an HTTP status the resource never returns (e.g. `201` when the resource returns the entity
  with a default `200`) — read the resource first.