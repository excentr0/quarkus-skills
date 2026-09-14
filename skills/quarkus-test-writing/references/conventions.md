# Test Conventions

How to make a new test look like it was always part of the project.

## Layout

- `src/test/java` mirrors `src/main/java` — same package, same class name + `Test` suffix.
- Test-only helpers live in the same test package or a dedicated `${basePackage}.test` package when the
  project already has one.
- `src/test/resources` holds test fixtures; `application.properties` stays in `src/main/resources` with
  `%test.` keys.

## Naming

Default method naming: `${methodName}_${scenario}_${expectedOutcome}` (e.g. `apply_lowTier_returnsFullPrice`).
If Step 1 of the skill found a different convention in the project (descriptive sentences,
`should${...}When${...}`), follow the project — consistency beats this default.

## Assertions

- JUnit 5: `assertEquals(expected, actual)` — expected first, actual second.
- REST contract: rest-assured `.then().statusCode(200).body("field", is(value))` with Hamcrest `is`.
- A test asserting only `statusCode(200)` is often too weak — assert at least one body field that would
  break if the mapping regressed.

## Data setup and cleanup

`@QuarkusTest` runs share one application instance and one Dev-Service database for the whole run: data
written by one test is visible to the next.

- Prefer creating exactly the rows the test needs in `@BeforeEach` via Panache calls, and removing them
  in `@AfterEach`.
- `@Transactional` on a test method rolls back only the test-thread transaction. For REST tests the HTTP
  request runs in its own transaction, so the row written by the request **survives** the rollback — do
  not rely on `@Transactional` for cleanup of HTTP-triggered writes.
- Assertions on collection sizes must either own the full table state or filter by something unique the
  test created.
- Existing base classes (e.g. an abstract `AbstractResourceTest` with `@BeforeEach` truncation) — reuse,
  do not reinvent.

## Test configuration

- `%test.` keys in `application.properties`:

  ```properties
  %test.quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/test
  %test.quarkus.http.test-port=8081
  ```

  Unprefixed keys apply to all profiles; `%test.` overrides only in tests.
- Whole-profile variants: implement `io.quarkus.test.junit.QuarkusTestProfile` and annotate the test
  class with `@TestProfile(${ProfileClass}.class)`; `getConfigOverrides()` returns a `Map<String, String>`.
- `quarkus.http.test-port` defaults to `8081` in `@QuarkusTest` — port conflicts with a running dev mode
  are usually this, not a bug in the test.

## Surefire requirements (Maven)

The generated Quarkus project already wires these; when adding tests to a project that lacks them, the
surefire configuration must set:

```xml
<systemPropertyVariables>
  <java.util.logging.manager>org.jboss.logmanager.LogManager</java.util.logging.manager>
  <maven.home>${maven.home}</maven.home>
</systemPropertyVariables>
```

Without the log manager property the Quarkus test bootstrap fails with a logging-manager error — the
message is misleading enough that it is worth recognizing.

## What not to do

- No `Thread.sleep` to wait for async work — assert on a `Uni` (`await().indefinitely()` on Mutiny) or use
  the messaging test utilities the project already uses.
- No ordering between tests — JUnit 5 method order is deterministic but meaningless; each test must pass
  alone.
- No test that asserts on the Dev-Service implementation's internals (container names, ports) — those are
  environment details, not behaviour.