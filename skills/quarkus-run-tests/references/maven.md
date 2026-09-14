# Running tests with Maven

## 1. The two plugins, two phases

| Type | Plugin | Phase | Command |
|---|---|---|---|
| `unit` + `quarkus` (`@QuarkusTest`) | surefire | `test` | `./mvnw test` |
| `integration` (`@QuarkusIntegrationTest`, `*IT.java`) | failsafe | `verify` (`integration-test` + `verify`) | `./mvnw verify -DskipITs=false` |
| `all` | both | `verify` | `./mvnw clean verify -DskipITs=false` |

`@QuarkusIntegrationTest` tests are black-box: they launch the artifact the build produced
(`target/quarkus-app/quarkus-run.jar`, a native binary with `-Dnative`, or a container image) and test
it over HTTP. CDI injection, `@InjectMock`, and config overrides do not exist there — if the user
expects to inject a bean inside an `*IT` test, that is a design error to point out, not something to
make work.

## 2. Narrow the run

| Scope | Flag |
|---|---|
| class or pattern | `-Dtest='Order*Test'` (surefire) / `-Dit.test='Order*IT'` (failsafe) |
| single method | `-Dtest='OrderServiceTest#createRejectsBlankName'` |
| package | `-Dtest='org.acme.order.**'` — prefer an explicit pattern over `**` when possible |
| JUnit 5 tag | `-Dgroups=unit` / `-DexcludedGroups=quarkus` (only if the project actually tags tests — confirm with a grep for `@Tag`) |
| module (multi-module build) | `-pl order-service` (add `-am` when the module needs its siblings built) |

`-Dtest` is surefire's, `-Dit.test` is failsafe's — mixing them silently runs the wrong scope.

Useful switches: `-DskipTests` (compile, run nothing), `-DskipITs` (skip only the integration phase),
`-Dnative` (build + test the native image — slow, GraalVM required).

Plain unit tests and `@QuarkusTest` tests both live in `src/test/java` and both run under surefire, so
Maven cannot separate them by flag alone — separate by class pattern or by `@Tag`.

## 3. Surefire's Quarkus settings

The Quarkus project template configures surefire with:

```xml
<systemPropertyVariables>
  <java.util.logging.manager>org.jboss.logmanager.LogManager</java.util.logging.manager>
  <maven.home>${maven.home}</maven.home>
</systemPropertyVariables>
```

and a modern surefire version (the old Maven default does not understand JUnit 5). If tests boot with
log-manager errors or zero tests are discovered, check these first — a missing
`java.util.logging.manager` shows up as a confusing logging failure, not as a config error.

## 4. Where the results are

- surefire: `target/surefire-reports/TEST-*.xml`
- failsafe: `target/failsafe-reports/TEST-*.xml`

Parse per `references/report.md`.

## 5. Remember the mapping

Record the resolved command per type/scope for this project — harness project memory if available,
otherwise a short note in the conversation. Example shape:

```text
Maven test commands (resolved <YYYY-MM-DD>):
- quarkus        -> ./mvnw test
- integration    -> ./mvnw verify -DskipITs=false
- all            -> ./mvnw clean verify -DskipITs=false
- order module / quarkus -> ./mvnw test -pl order-service
```

Write only what is new; do not rewrite an unchanged mapping.

## 6. Console noise that is not a failure

Ignore Mockito self-attach warnings and JDK "invalid/auto-detected installation" notes: they appear in
red but change nothing. Judge only by test results. Dev Services startup logs (container pull, datasource
ready) are normal on a `@QuarkusTest` run, not a problem.
