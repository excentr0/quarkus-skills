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

Before rejecting the project or selecting a command, identify the target module. Inspect its build file plus root/parent build configuration for inherited Quarkus BOM/plugin, dependency management, and version properties/catalogs; use the target Maven module's effective POM when inheritance remains unclear. Prefer the project root wrapper with module selection (`-pl`/`-am` for Maven, `:module:task` for Gradle). If the wrapper is absent, check installed `mvn`/`gradle` and its version; if no usable tool is available, report a blocker/NOT RUN rather than calling the project invalid.


This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import; Gradle: `io.quarkus` plugin.
3. **Test dependencies** — use the Quarkus BOM-matched test extensions. For Quarkus 3.20.3, `quarkus-junit5` is required for `@QuarkusTest`, and `quarkus-junit5-mockito` provides `@InjectMock`; verify the extension name against the project's Quarkus version before adding. Also add the ordinary test library
   `io.rest-assured:rest-assured` for HTTP assertions. Use `add-extension` only for the Quarkus
   extensions; add Rest Assured as a test-scoped Maven/Gradle dependency when it is missing.
   For example (for Quarkus 3.20.3), `./mvnw quarkus:add-extension -Dextensions="quarkus-junit5-mockito"` /
   `./gradlew addExtension --extensions="quarkus-junit5-mockito"`.
4. **Test layout** — glob `src/test/java/**/*.java`: `*Test` classes (surefire / `test` task), `*IT`
   classes (failsafe / `quarkusIntTest` task), plain JUnit classes, `@Tag` usage.
5. **Test config** — `%test.` keys in the detected application config file (`.properties` or YAML), or a class implementing `QuarkusTestProfile` and activated via `@TestProfile(Profile.class)`. Note: `@QuarkusIntegrationTest` uses packaged production configuration, not `src/test/resources` application config.

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
| Test config | `%test.` properties or `QuarkusTestProfile` + `@TestProfile(Profile.class)` | — |

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


**Do NOT call any tools in this step.**

Extract from the request: **what** to test (class, endpoint, method), **which behaviour** matters
(contract, business rule, edge case), and any already-stated preferences (type, naming, data).

---

## Step 1 — Detect existing test conventions


Use [`references/conventions.md`](references/conventions.md) for project style and
[`references/mocking.md`](references/mocking.md) for CDI/unit-test mock boundaries.

Read 2–3 representative tests and follow the nearest consistent project convention. If examples are absent, use the stated default. Ask once only if conflicting evidence materially changes test behavior or isolation.

| Convention | Default |
|---|---|
| Test type in use (plain JUnit / `@QuarkusTest` / `*IT`) | `@QuarkusTest` for app code |
| Class naming (`XxxTest` / `XxxTests` / `XxxIT`) | `XxxTest` |
| Method naming (`method_scenario` / descriptive sentence) | `method_scenario_expectedOutcome` |
| Visibility (package-private vs public test classes) | package-private (JUnit 5 style) |
| HTTP testing style (rest-assured statics / `@TestHTTPEndpoint` class/method target or `@TestHTTPResource` URL field / client helper) | rest-assured statics |
| Assertions (JUnit / AssertJ / Hamcrest matchers) | JUnit 5 |
| Mocking (`@InjectMock` / plain Mockito / fakes) | `@InjectMock` in `@QuarkusTest`, plain Mockito in unit tests |
| Data setup (Panache calls / SQL / seed data) | Panache calls in the test |
| Cleanup (`@AfterEach` deleteAll / `@BeforeEach` truncate / `@Transactional` test methods) | explicit `@AfterEach` delete |
| Test config (`%test.` keys / `QuarkusTestProfile` + `@TestProfile` / `@TestResource`) | `%test.` keys |
| Parameterized tests used | no |

---

## Step 2 — Select the test type


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


Pick the example matching the type:

| Type | Example |
|---|---|
| REST endpoint via `@QuarkusTest` | [`examples/happy-path-rest-test.md`](examples/happy-path-rest-test.md) |
| Service with a mocked dependency | [`examples/inject-mock-test.md`](examples/inject-mock-test.md) |
| Pure logic, plain JUnit 5 | [`examples/unit-test.md`](examples/unit-test.md) |
| Packaged artifact (`@QuarkusIntegrationTest`) | [`examples/integration-test.md`](examples/integration-test.md) |

Insert point: new file `src/test/java/${testPackage}/${TargetClass}Test.java` (or `...IT.java` for the
integration type). Fill every `${variable}` from the real sources — read the DTO/entity/resource before
writing the test. Do not invent field names, paths, or status codes: wrong assertions are worse than no
test.

---

## Step 4 — Dependencies and test properties


- Missing Quarkus test extension → add via the detected build tool's extension command (never edit a
  version by hand). Missing ordinary libraries such as `io.rest-assured:rest-assured` → add as a
  test-scoped dependency in the existing Maven/Gradle build syntax (`<scope>test</scope>` for Maven,
  `testImplementation(...)` for Gradle); never pass them to `add-extension`.
- `@QuarkusIntegrationTest` present but no failsafe configured → the integration tests will not run under
  `./mvnw verify`; note it to the user (running is `quarkus-run-tests`' job).
- Test-only config → `%test.` keys in the detected application config file (e.g. datasource overrides); a whole variant
  profile → a class implementing `QuarkusTestProfile` (activated via `@TestProfile(Profile.class)`) with `getConfigOverrides()`.
- Never point `%test.` at production services: Dev Services should own infra in tests.

---

## Step 5 — Run the tests


Apply the **`quarkus-run-tests`** workflow — do not duplicate command knowledge here. Report its result verbatim; classify failures as production defects, test defects, contract mismatch, or infrastructure failure. A failing test may expose a production defect: compare behavior to the requested contract, fix production code when it violates that contract, and never weaken a valid assertion just to make the test green.

---

## Portable resources and sibling handoffs

This skill's relative `references/` and `examples/` are bundled with its directory. Repository-level `docs/quarkus-facts.md` is optional when the skill is installed alone; if absent, verify version-sensitive claims against official versioned documentation/source or the actual project dependencies. Before a sibling-skill handoff, check whether that sibling is available. If missing, say so and apply equivalent local instructions only when the complete relevant example is available; never pretend to read a missing file. Skill activation/handoff alone does not authorize a child agent; delegate mechanically only when caller/operator permission and environment support are both present.

## Step 6 — Anti-hallucination checklist


- [ ] The test type follows [`references/test-types.md`](references/test-types.md) — not habit.
- [ ] Every field name, path, and status code in assertions was read from the real source, not guessed.
- [ ] The test file is in the project's actual test package and naming convention.
- [ ] `@QuarkusIntegrationTest` test contains no `@Inject`/`@InjectMock` (they do not work there).
- [ ] `@QuarkusTest` tests that write data have explicit cleanup — Dev-Service state persists between tests.
- [ ] No dependency version was handwritten — extensions come from the build tool's add-extension command.
- [ ] The test was actually run (Step 5) before being reported as done.