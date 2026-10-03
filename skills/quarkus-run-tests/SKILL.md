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

Use [`references/maven.md`](references/maven.md), [`references/gradle.md`](references/gradle.md), and
[`references/report.md`](references/report.md) for command resolution and compact result reporting.

## Test types

| Type | Meaning | Typical Maven command | Typical Gradle command |
|------|---------|----------------------|------------------------|
| `unit` | plain JUnit 5 — no CDI container, no app boot, no Dev Services | `./mvnw test -Dtest='${pattern}'` | `./gradlew test --tests '${pattern}'` |
| `quarkus` | `@QuarkusTest` — the application boots in the test JVM; Dev Services start (DB, Kafka, Keycloak) | `./mvnw test` | `./gradlew test` |
| `integration` | `@QuarkusIntegrationTest` — black-box tests against the packaged artifact (jar, native binary, or container) | `./mvnw verify -DskipITs=false` | `./gradlew quarkusIntTest` |
| `all` | test runners/source sets actually configured for unit, app, and integration tests | `./mvnw clean verify -DskipITs=false` only after confirming target-module Surefire/Failsafe bindings and naming | `./gradlew clean test quarkusIntTest` only after inspecting the task graph/source sets and confirming both tasks apply |

**Task names and bindings are project-specific** — discover them instead of assuming. Sequential phases in one Maven `verify` invocation are valid; Gradle test and integration tasks still use distinct source sets/tasks. Avoid duplicate executions by resolving the actual lifecycle/task graph before choosing one command.

`@QuarkusTest` and `@QuarkusIntegrationTest` use separate execution contexts: Maven Surefire and Failsafe are separate runners/phases, but one `mvn verify` invocation may run both. Gradle requires separate source sets/tasks. Report each phase/task that actually executed; do not mistake distinct runners for a prohibition on one Maven verify invocation.

## Preflight — project detection

Before rejecting the project or selecting a command, identify the target module. Inspect its build file plus root/parent build configuration for inherited Quarkus BOM/plugin, dependency management, and version properties/catalogs; use the target Maven module's effective POM when inheritance remains unclear. Prefer the project root wrapper with module selection (`-pl`/`-am` for Maven, `:module:task` for Gradle). If the wrapper is absent, check installed `mvn`/`gradle` and its version; if no usable tool is available, report a blocker/NOT RUN rather than calling the project invalid.


This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import;
   Gradle: `io.quarkus` plugin.
3. **Test extensions** — `quarkus-junit5` (required for `@QuarkusTest`), `quarkus-junit5-mockito`
   (`@InjectMock` on Quarkus 3.20.3; verify the target version), `rest-assured` (HTTP assertions), `quarkus-jacoco` (coverage).
4. **Persistence / messaging extensions** — `quarkus-hibernate-orm-panache`, `quarkus-flyway`,
   `quarkus-messaging-kafka`: with these present a `@QuarkusTest` run starts Dev Services
   (Docker required) and database state persists between tests.
5. **Test layout** — glob `src/test/java/**/*.java`: `*Test`/`*Tests` classes, `*IT` classes
   (integration), any JUnit 5 `@Tag` usage (used to split types), and the `%test.` profile in the detected application config file (`.properties` or YAML).

Before stopping for a missing build file, identify the requested target module and inspect root/parent build configuration and inherited Quarkus BOM/plugin. Use the target module's effective build model if inheritance is unclear. A missing wrapper is not proof the project is invalid: check installed Maven/Gradle and version; if no usable tool exists, report a blocker/NOT RUN.

---

## Step 0 — Read the request (no tools)


**Do NOT call any tools in this step.**

From the conversation, fix: **which type** (`unit` / `quarkus` / `integration` / `all`) and **what
scope** (whole project, a module, a package, a single class, a single method). "Run the tests" with no
qualifier usually means the fast suite — if the project has both types, prefer `quarkus` (the default
`./mvnw test` run) and say what you ran, rather than asking.

---

## Step 1 — Resolve the command


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


Delegate the run + result collection only when the caller/operator permits delegation and the environment supports it; otherwise run the detected command directly. Either way, the long build output must not flood the conversation — the
runner's only job is the report defined in `references/report.md`.

Give the runner: the resolved command, the expected results directory (`target/surefire-reports`,
`target/failsafe-reports`, or `build/test-results/<task>`), and the instruction to report
`references/report.md` and nothing else.

---

## Step 3 — Report and decide the next step


Present the report as it came. Then:

- **Green** — say what ran (type + scope + counts) and stop. No summary of skipped tests unless asked.
- **Red** — the report already carries each failure's message and key stacktrace line. Offer the
  concrete next move: reproduce the single failing test (narrowed command), then fix. Do not re-run
  the whole suite to "confirm".
- **Not run** — the suite never started (see `references/report.md`): report the cause
  (missing wrapper, unresolvable task, container runtime down for Dev Services) rather than silence.

---

## Portable resources and sibling handoffs

This skill's relative `references/` and `examples/` are bundled with its directory. Repository-level `docs/quarkus-facts.md` is optional when the skill is installed alone; if absent, verify version-sensitive claims against official versioned documentation/source or the actual project dependencies. Before a sibling-skill handoff, check whether that sibling is available. If missing, say so and apply equivalent local instructions only when the complete relevant example is available; never pretend to read a missing file. Skill activation/handoff alone does not authorize a child agent; delegate mechanically only when caller/operator permission and environment support are both present.

## Anti-hallucination checklist

- [ ] The command was built from the project's actual build file and discovered task names — not from
      this skill's "typical" column.
- [ ] Class/package/module names in the command were verified against the test sources.
- [ ] Surefire/Failsafe or Gradle source-set/task execution is reported accurately; a single Maven verify may run both phases.
- [ ] Failure messages and `file:line` stacktrace lines are verbatim from the JUnit XML.
- [ ] A green report names the type and scope that actually ran — never "all tests" when a filter was
      in effect.
- [ ] If the run needed Docker (Dev Services) and it was unavailable, that is stated — not hidden
      behind a partial pass.