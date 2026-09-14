# Measuring coverage with Gradle

## 1. Setup — the extension replaces the plugin

```kotlin
testImplementation("io.quarkus:quarkus-jacoco")
```

That is the whole setup: the extension wires the JaCoCo agent and generates the report itself. Do NOT
also apply the `jacoco` Gradle plugin to the same classes — two agents on one classpath produce
"already instrumented" errors.

## 2. Commands

| Scope | Command |
|---|---|
| whole project | `./gradlew clean test` |
| one class/pattern | `./gradlew clean test --tests '${pattern}'` |
| one JUnit tag | `./gradlew clean test -Dgroups=${tag}` (only if the project tags tests) |
| integration tests too | `./gradlew clean test quarkusIntTest` (when the project declares that source set) |
| one module (multi-module) | prefix the task path: `./gradlew :${module}:clean :${module}:test` |

`clean` is the stale-report guard: without it a failed run leaves the previous report in place and the
measurement reads a number from code that no longer runs. If the user insists on skipping `clean`,
delete the report directory and the JaCoCo data file first.

## 3. Where the report lands

Do not assume a path — locate it:

```bash
find target build -type d -name '*jacoco*' 2>/dev/null
find target build -name index.html -path '*jacoco*' 2>/dev/null
```

The default report location is `target/jacoco-report`; on Gradle the build directory mirrors it, and
`quarkus.jacoco.report-location` / `quarkus.jacoco.data-file` in `application.properties` override both.
Read those properties first; fall back to the search.

## 4. Multi-module builds

Same verified settings as Maven — a shared data file plus aggregation:

```properties
quarkus.jacoco.data-file=/path/to/shared/data-file
quarkus.jacoco.reuse-data-file=true
quarkus.jacoco.aggregate-report-data=true
```

Without `reuse-data-file`, each module overwrites the shared file and the report describes only the
last module that ran.

## 5. Reading the number

In the report directory:

- `jacoco.csv`, if present — sum `INSTRUCTION_MISSED` and `INSTRUCTION_COVERED` over every row
  (the CSV has no total row; the sum is the total).
- otherwise `index.html` — take the Total row's instruction counters/percentage.

`coverage = covered / (covered + missed)`. Prefer the INSTRUCTION counter and report the percentage
with two decimals.

## 6. Failure shapes

| Symptom | Cause |
|---|---|
| no report directory after the run | a test failed before the report was written, or the report location was customized — check both |
| "already instrumented" | the Gradle `jacoco` plugin is applied alongside `quarkus-jacoco` — remove one |
| report exists but is from an earlier run | tests were UP-TO-DATE — re-run with `clean` or `--rerun-tasks` |
| zero/oddly low coverage | the `--tests` filter matched nothing, or Dev Services could not start (Docker down) |
