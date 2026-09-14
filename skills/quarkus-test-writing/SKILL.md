---
name: quarkus-test-writing
description: >-
  Writes tests for a Quarkus application: picks the right test type (plain unit test,
  @QuarkusTest, @QuarkusIntegrationTest), detects the project's own test conventions, and
  generates test code with the right dependencies and test-profile config.
  Use this skill when tests need to be written or extended — "write tests", "add a test for this",
  "cover this endpoint with tests", "test this service".
  To RUN tests use the `quarkus-run-tests` skill instead; for coverage use `quarkus-coverage`.
  Russian phrases also trigger this: "напиши тесты", "добавь тесты", "покрой тестами",
  "тесты для этого метода", "напиши тест на эндпоинт".
---

# Write Tests

> **CRITICAL: Code ONLY from examples/ files. If no matching example -- STOP and ask user.**
> **CRITICAL: For questions with a fixed set of choices, prefer your harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`) > plain text list. Plain numbered text lists are the last resort when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** The request and prior turns may already answer half the questions. Re-asking what was already said is the #1 reason this skill feels slow.

Sibling skills — use the right one:

| Skill | Responsibility |
|---|---|
| **`quarkus-test-writing`** (this skill) | Write test code, pick the test type, add test deps/properties |
| `quarkus-run-tests` | Run tests, report pass/fail |
| `quarkus-coverage` | Measure coverage (`quarkus-jacoco`) |
| `quarkus-mutation-testing` | Check test strength (PIT) |

---

## Preflight — project detection

This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import; Gradle: `io.quarkus` plugin.
3. **Test dependencies** — `quarkus-junit5` (required for `@QuarkusTest`), `quarkus-junit-mockito`
   (`@InjectMock`), `io.rest-assured:rest-assured` (HTTP assertions). Missing ones are added in Step 4:
   `./mvnw quarkus:add-extension -Dextensions="quarkus-junit-mockito"` /
   `./gradlew addExtension --extensions="quarkus-junit-mockito"`.
4. **Test layout** — glob `src/test/java/**/*.java`: `*Test` classes (surefire / `test` task), `*IT`
   classes (failsafe / `quarkusIntTest` task), plain JUnit classes, `@Tag` usage.
5. **Test config** — `%test.` keys in `src/main/resources/application.properties`, `@QuarkusTestProfile`
   classes under `src/test/java`.

If there is no Quarkus build file, stop: this skill targets Quarkus projects.

---

## Defaults

| Decision | Default | When to deviate |
|---|---|---|
| Test type | `@QuarkusTest` for anything behind REST/CDI/Panache; plain JUnit for pure logic | see [`references/test-types.md`](references/test-types.md) |
| Naming | `${TargetClass}Test` | follow the project's existing suffix (`Test`/`Tests`/`IT`) |
| Package | mirror the main package under `src/test/java` | project uses a separate `test` root — follow it |
| Assertions | JUnit 5 `Assertions` | project uses AssertJ/Hamcrest — follow the project |
| HTTP style | rest-assured `given/when/then` | project has its own client helper — follow it |
| Data cleanup | explicit `@BeforeEach`/`@AfterEach` against the Dev-Service DB | project already has a cleanup base class |
| Test config | `%test.` properties or a `@QuarkusTestProfile` | — |

---

## Decision-making principle — context first, then ask

Steps 1–2 answer most questions from the project code and the conversation. Ask only about genuine
forks, in **one batch** (single structured-question call):

- **test type** — only when the target is genuinely ambiguous (e.g. a service that is also reachable over HTTP)
- **scope** — happy path only, or edge cases/validation too
- **test data** — create fixtures in the test vs rely on existing seed data
- **cleanup strategy** — only when the project has no visible convention and the test writes data

Never ask about naming, package, or assertion style when the project's existing tests show them.

---

## Step 0 — Conversation context first (REQUIRED, no tool calls)

Tell the user: `Step 0/6: Reading the request...`

**Do NOT call any tools in this step.**

Extract from the request: **what** to test (class, endpoint, method), **which behaviour** matters
(contract, business rule, edge case), and any already-stated preferences (type, naming, data).

---

## Step 1 — Detect existing test conventions

Tell the user: `Step 1/6: Detecting test conventions...`

Read the project's existing tests (`src/test/java`, pick 2–3 representative classes) and score each
convention (1–100). For anything below 80 — ask in Step 2's batch; for anything absent from the code
(e.g. no `@InjectMock` usage anywhere yet) — use the default without asking.

| Convention | Default |
|---|---|
| Test type in use (plain JUnit / `@QuarkusTest` / `*IT`) | `@QuarkusTest` for app code |
| Class naming (`XxxTest` / `XxxTests` / `XxxIT`) | `XxxTest` |
| Method naming (`method_scenario` / descriptive sentence) | `method_scenario_expectedOutcome` |
| Visibility (package-private vs public test classes) | package-private (JUnit 5 style) |
| HTTP testing style (rest-assured statics / injected `@TestHTTPEndpoint` / client helper) | rest-assured statics |
| Assertions (JUnit / AssertJ / Hamcrest matchers) | JUnit 5 |
| Mocking (`@InjectMock` / plain Mockito / fakes) | `@InjectMock` in `@QuarkusTest`, plain Mockito in unit tests |
| Data setup (Panache calls / SQL / seed data) | Panache calls in the test |
| Cleanup (`@AfterEach` deleteAll / `@BeforeEach` truncate / `@Transactional` test methods) | explicit `@AfterEach` delete |
| Test config (`%test.` keys / `@QuarkusTestProfile` / `@TestResource`) | `%test.` keys |
| Parameterized tests used | no |

---

## Step 2 — Select the test type

Tell the user: `Step 2/6: Selecting the test type...`

Apply the decision table in [`references/test-types.md`](references/test-types.md). The short version:

| What is being tested | Type |
|---|---|
| REST endpoint contract (HTTP status, JSON shape) | `@QuarkusTest` + rest-assured |
| CDI service / repository / Panache query | `@QuarkusTest` (mock slow collaborators) |
| Pure business logic without CDI | plain JUnit 5 |
| The packaged artifact (jar / native / container) | `@QuarkusIntegrationTest` |

If Step 1 left open questions — ask them now in one batch. Otherwise state the chosen type and why.

---

## Step 3 — Generate test code

Tell the user: `Step 3/6: Generating test code...`

Pick the example matching the type:

| Type | Example |
|---|---|
| REST endpoint via `@QuarkusTest` | [`examples/happy-path-rest-test.md`](examples/happy-path-rest-test.md) |
| Service with a mocked dependency | [`examples/inject-mock-test.md`](examples/inject-mock-test.md) |
| Pure logic, plain JUnit 5 | [`examples/unit-test.md`](examples/unit-test.md) |

Insert point: new file `src/test/java/${testPackage}/${TargetClass}Test.java` (or `...IT.java` for the
integration type). Fill every `${variable}` from the real sources — read the DTO/entity/resource before
writing the test. Do not invent field names, paths, or status codes: wrong assertions are worse than no
test.

---

## Step 4 — Dependencies and test properties

Tell the user: `Step 4/6: Checking dependencies and test config...`

- Missing test dependency → add via the extension command from the preflight (never edit a version by hand).
- `@QuarkusIntegrationTest` present but no failsafe configured → the integration tests will not run under
  `./mvnw verify`; note it to the user (running is `quarkus-run-tests`' job).
- Test-only config → `%test.` keys in `application.properties` (e.g. datasource overrides); a whole variant
  profile → a `@QuarkusTestProfile` class with `getConfigOverrides()`.
- Never point `%test.` at production services: Dev Services should own infra in tests.

---

## Step 5 — Run the tests

Tell the user: `Step 5/6: Running the new tests...`

Hand over to the **`quarkus-run-tests`** skill — do not duplicate command knowledge here. Report its
result verbatim; a red test means the test or the expectation is wrong — say which one you believe it is,
do not weaken the assertion to make it green.

---

## Step 6 — Anti-hallucination checklist

Tell the user: `Step 6/6: Final check...`

- [ ] The test type follows [`references/test-types.md`](references/test-types.md) — not habit.
- [ ] Every field name, path, and status code in assertions was read from the real source, not guessed.
- [ ] The test file is in the project's actual test package and naming convention.
- [ ] `@QuarkusIntegrationTest` test contains no `@Inject`/`@InjectMock` (they do not work there).
- [ ] `@QuarkusTest` tests that write data have explicit cleanup — Dev-Service state persists between tests.
- [ ] No dependency version was handwritten — extensions come from the build tool's add-extension command.
- [ ] The test was actually run (Step 5) before being reported as done.