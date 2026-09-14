# Measuring coverage with Maven

## 1. Setup — the extension replaces the plugin

```xml
<dependency>
  <groupId>io.quarkus</groupId>
  <artifactId>quarkus-jacoco</artifactId>
  <scope>test</scope>
</dependency>
```text

That is the whole setup: the extension wires the JaCoCo agent and generates the report itself. Do NOT
also add `jacoco-maven-plugin` — two agents on the same classes produce "classes already instrumented"
errors. Adding the extension does not require any plugin block.

Convenient: `./mvnw quarkus:add-extension -Dextensions="jacoco"` — then confirm the dependency landed
with `<scope>test</scope>`; if not, set the scope.

## 2. Defaults to know

| What | Default |
|---|---|
| data file | `target/jacoco-quarkus.exec` |
| report directory | `target/jacoco-report` (configurable: `quarkus.jacoco.report-location`) |
| data file override | `quarkus.jacoco.data-file` |
| report entry point | `target/jacoco-report/index.html` |

Read the report location from `application.properties` first (`quarkus.jacoco.report-location`,
`quarkus.jacoco.data-file`) and fall back to the defaults — a customized location is not an error, only
a thing to check before declaring the report missing.

## 3. Commands

| Scope | Command |
|---|---|
| whole project | `./mvnw clean verify -DskipITs=false` |
| one class/pattern | `./mvnw clean verify -Dtest='${pattern}'` |
| one JUnit tag | `./mvnw clean verify -Dgroups='${tag}'` (only if the project tags tests) |
| one module (multi-module) | `./mvnw clean verify -pl ${module} -am` |

`clean` is not decoration: it is the stale-report guard — without it a failed run can leave the previous
report in place and the measurement reads a number that belongs to code that no longer runs. When the
user insists on skipping `clean`, delete `target/jacoco-report` and `target/jacoco-quarkus.exec` first.

Integration tests (`*IT` classes, failsafe) count toward coverage only when they run — that is why the
command spells out `-DskipITs=false`.

## 4. Multi-module builds

One report across modules needs a shared data file and aggregation (verified settings):

```properties
quarkus.jacoco.data-file=/path/to/shared/data-file
quarkus.jacoco.reuse-data-file=true
quarkus.jacoco.aggregate-report-data=true
```

Without `reuse-data-file`, each module overwrites the shared file and the report describes the last
module that ran.

## 5. Reading the number

In the report directory:

- `jacoco.csv`, if present — sum `INSTRUCTION_MISSED` and `INSTRUCTION_COVERED` over every row
  (the CSV has no total row; the sum is the total).
- otherwise `index.html` — take the Total row's instruction counters/percentage.

`coverage = covered / (covered + missed)`. Prefer the INSTRUCTION counter (same rule the report format
uses) and report the percentage with two decimals.

## 6. Failure shapes

| Symptom | Cause |
|---|---|
| no report directory after the run | a test failed before the report task, or the report location was customized — check both |
| "classes already instrumented" | `jacoco-maven-plugin` is active alongside `quarkus-jacoco` — remove one |
| report exists but is from an earlier run | the build did not re-run the tests (`clean` skipped, tests UP-TO-DATE) — re-run with `clean` |
| zero/oddly low coverage | tests did not run (filter matched nothing) or Dev Services could not start (Docker down) |
