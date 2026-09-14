---
name: quarkus-run-tests
description: >-
  Run a Quarkus project's tests by test type or module — plain unit tests,
  @QuarkusTest tests, or @QuarkusIntegrationTest tests — via Maven or Gradle,
  and report a compact pass/fail result.
  Use this skill whenever the user wants to run, re-run, or check the
  project's tests (e.g. "run the unit tests", "run all tests", "run the
  integration tests for the order module", "did the tests pass?", "why do
  the tests fail?").
  Russian phrases also trigger this: "запусти тесты", "прогони тесты",
  "проверь тесты", "тесты падают", "почему падают тесты", "запусти интеграционные тесты".
---

# Run tests

## Test types

| Type | Meaning | Typical Maven command | Typical Gradle command |
|------|---------|----------------------|------------------------|
| `unit` | plain JUnit 5 — no CDI container, no app boot, no Dev Services | `./mvnw test -Dtest='${pattern}'` | `./gradlew test --tests '${pattern}'` |
| `quarkus` | `@QuarkusTest` — the application boots in the test JVM; Dev Services start (DB, Kafka, Keycloak) | `./mvnw test` | `./gradlew test` |
| `integration` | `@QuarkusIntegrationTest` — black-box tests against the packaged artifact (jar, native binary, or container) | `./mvnw verify -DskipITs=false` | `./gradlew quarkusIntTest` |
| `all` | everything above | `./mvnw clean verify -DskipITs=false` | `./gradlew clean test quarkusIntTest` |

**Task names are project-specific** — the Gradle column shows the conventional names; discover the
real ones instead of assuming (see `references/gradle.md`).

**Never mix `@QuarkusTest` and `@QuarkusIntegrationTest` in one test run.** Maven: surefire runs the
former (`test` phase), failsafe runs the latter (`verify` phase, `*IT.java` naming). Gradle: the two
must live in different source sets. A single run of both is documented not to work.

## Preflight — project detection

This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import;
   Gradle: `io.quarkus` plugin.
3. **Test extensions** — `quarkus-junit5` (required for `@QuarkusTest`), `quarkus-junit-mockito`
   (`@InjectMock`), `rest-assured` (HTTP assertions), `quarkus-jacoco` (coverage).
4. **Persistence / messaging extensions** — `quarkus-hibernate-orm-panache`, `quarkus-flyway`,
   `quarkus-messaging-kafka`: with these present a `@QuarkusTest` run starts Dev Services
   (Docker required) and database state persists between tests.
5. **Test layout** — glob `src/test/java/**/*.java`: `*Test`/`*Tests` classes, `*IT` classes
   (integration), any JUnit 5 `@Tag` usage (used to split types), and the `%test.` profile in
   `src/main/resources/application.properties`.

If there is no Quarkus build file, stop: this skill targets Quarkus projects.

---

## Step 0 — Read the request (no tools)

Tell the user: `Step 0/4: Reading the request...`

**Do NOT call any tools in this step.**

From the conversation, fix: **which type** (`unit` / `quarkus` / `integration` / `all`) and **what
scope** (whole project, a module, a package, a single class, a single method). "Run the tests" with no
qualifier usually means the fast suite — if the project has both types, prefer `quarkus` (the default
`./mvnw test` run) and say what you ran, rather than asking.

---

## Step 1 — Resolve the command

Tell the user: `Step 1/4: Resolving the test command...`

Follow `references/maven.md` or `references/gradle.md` (whichever matches the build system) to turn
the type + scope into one concrete command:

- Narrow by class/package/method or by JUnit tag — patterns, not guessed names.
- More than one plausible way to run the requested type → ask the user, using your harness's
  structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`); fall back to a numbered
  list. Do not guess — the wrong command runs the wrong tests.
- Once resolved, **remember the mapping for this project** (harness project memory if available,
  otherwise keep it in the conversation) so the next run skips the discovery.

Do not run the tests in this step.

---

## Step 2 — Run and collect the result

Tell the user: `Step 2/4: Running tests...`

If your harness supports subagents, delegate the run + result collection to ONE subagent; otherwise
run the command directly. Either way, the long build output must not flood the conversation — the
runner's only job is the report defined in `references/report.md`.

Give the runner: the resolved command, the expected results directory (`target/surefire-reports`,
`target/failsafe-reports`, or `build/test-results/<task>`), and the instruction to report
`references/report.md` and nothing else.

---

## Step 3 — Report and decide the next step

Tell the user: `Step 3/4: Reporting...`

Present the report as it came. Then:

- **Green** — say what ran (type + scope + counts) and stop. No summary of skipped tests unless asked.
- **Red** — the report already carries each failure's message and key stacktrace line. Offer the
  concrete next move: reproduce the single failing test (narrowed command), then fix. Do not re-run
  the whole suite to "confirm".
- **Not run** — the suite never started (see `references/report.md`): report the cause
  (missing wrapper, unresolvable task, container runtime down for Dev Services) rather than silence.

---

## Anti-hallucination checklist

- [ ] The command was built from the project's actual build file and discovered task names — not from
      this skill's "typical" column.
- [ ] Class/package/module names in the command were verified against the test sources.
- [ ] `@QuarkusTest` and `@QuarkusIntegrationTest` were never scheduled in the same run.
- [ ] Failure messages and `file:line` stacktrace lines are verbatim from the JUnit XML.
- [ ] A green report names the type and scope that actually ran — never "all tests" when a filter was
      in effect.
- [ ] If the run needed Docker (Dev Services) and it was unavailable, that is stated — not hidden
      behind a partial pass.