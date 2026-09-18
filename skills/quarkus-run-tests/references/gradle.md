# Running tests with Gradle

## 1. Discover the real tasks first

Never assume a task name — list them and read the descriptions:

```bash
./gradlew tasks --all
```

Conventional mapping for a Quarkus project:

| Type | Task |
|---|---|
| `unit` + `quarkus` (`@QuarkusTest`) | `test` |
| `integration` (`@QuarkusIntegrationTest`) | `quarkusIntTest` — exists only when the project declares an integration-test source set (`src/integrationTest/java`) |

If a requested type has no matching task, say so — do not guess one.

## 2. Narrow the run

| Scope | Flag |
|---|---|
| class or pattern | `--tests 'org.acme.order.OrderServiceTest'` / `--tests 'org.acme.order.*'` |
| single method | `--tests 'org.acme.order.OrderServiceTest.createRejectsBlankName'` |
| module (multi-module build) | prefix the task path: `:order-service:test` |
| force a fresh run | `--rerun-tasks` (without it Gradle may report UP-TO-DATE and run nothing) |

`--tests` is a task option: it must follow the task it applies to (`./gradlew test --tests '...'`), and
it is not a global option.

## 3. `@QuarkusTest` and `@QuarkusIntegrationTest` need separate source sets

Gradle runs everything in the `test` task's source set by default. An `@QuarkusIntegrationTest` class
placed in `src/test/java` breaks the run (the final artifact does not exist at `test` time) — it belongs
in a dedicated source set, run by its own task (`quarkusIntTest`), and must not be scheduled together
with `@QuarkusTest` classes.

Check the build file before claiming an integration task exists:

```bash
grep -n "integrationTest\|quarkusIntTest\|sourceSets" build.gradle build.gradle.kts
```

## 4. Where the results are

- `build/test-results/test/*.xml`
- `build/test-results/<task>/*.xml` for any other test task (e.g. `quarkusIntTest`)

Parse per `references/report.md`.

A full picture of everything that ran (all test tasks):

```bash
./gradlew test                    # first, when the project has both
./gradlew quarkusIntTest           # only after test passes
```

## 5. Remember the mapping

Record the resolved task per type/scope for this project — harness project memory if available,
otherwise a short note in the conversation. Example shape:

```text
Gradle test tasks (resolved <YYYY-MM-DD>):
- quarkus        -> ./gradlew test
- integration    -> ./gradlew quarkusIntTest
- all            -> ./gradlew clean test, then ./gradlew quarkusIntTest
- order module / quarkus -> ./gradlew :order-service:test
```

Write only what is new; do not rewrite an unchanged mapping.

## 6. Console noise that is not a failure

Ignore Mockito self-attach warnings and JDK "invalid/auto-detected installation" notes: they appear in
red but change nothing. Judge only by test results. Dev Services startup logs (container pull,
datasource ready) are normal on a `@QuarkusTest` run, not a problem.
