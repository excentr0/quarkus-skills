# Running tests with Maven

## 1. Surefire and Failsafe are separate runners/phases

| Type | Plugin | Phase | Command |
|---|---|---|---|
| `unit` + `quarkus` (`@QuarkusTest`) | surefire | `test` | `./mvnw test` |
| `integration` (`@QuarkusIntegrationTest`, `*IT.java`) | failsafe | `verify` (`integration-test` + `verify`; check whether Surefire also runs) | `./mvnw verify -DskipITs=false` |
| `all` | Surefire + Failsafe in separate lifecycle phases | `./mvnw clean verify -DskipITs=false` only after confirming target-module bindings and test naming |

`@QuarkusIntegrationTest` tests are black-box: they launch the packaged artifact (production profile/config)
and test public interfaces. CDI injection, `@InjectMock`, and test-process config overrides do not configure
the packaged application. Surefire and Failsafe are distinct runners/phases, but one `mvn verify` invocation
can run both; that is not an invalid mixed test process. Generated Quarkus 3.20.3 Maven configuration
defaults `skipITs` to true; `-DskipITs=false` enables Failsafe.

## 2. Narrow the run

| Scope | Flag |
|---|---|
| class or pattern | `-Dtest='Order*Test'` (surefire) / `-Dit.test='Order*IT'` (failsafe) |
| single method | `-Dtest='OrderServiceTest#createRejectsBlankName'` |
| package | `-Dtest='org.acme.order.**'` — prefer an explicit pattern over `**` when possible |
| JUnit 5 tag | `-Dgroups=unit` / `-DexcludedGroups=quarkus` (only if the project actually tags tests — confirm with a grep for `@Tag`) |
| module (multi-module build) | `-pl order-service` (add `-am` when the module needs its siblings built) |

`-Dtest` is Surefire's, `-Dit.test` is Failsafe's — mixing them silently runs the wrong scope. An IT-only request may still execute Surefire tests during `verify`; report them if they ran rather than silently claiming integration-only.

Useful switches: `-DskipTests` skips test execution and is not a universal way to isolate ITs;
`-DskipITs=false` enables generated Failsafe config where confirmed. `-Dnative` requires the project's
native profile; otherwise use a verified `quarkus.native.enabled` configuration and confirm build setup.

Plain unit tests and `@QuarkusTest` tests both live in `src/test/java` and run under Surefire; separate by
class pattern or `@Tag` only when actual test tags/config support it. Failsafe integration tests run in
their own phase. `verify` may run Surefire as well as Failsafe; report every phase and count that ran.

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
- all            -> ./mvnw clean verify -DskipITs=false (after confirming module Surefire/Failsafe config)
- order module / quarkus -> ./mvnw test -pl order-service
```

Write only what is new; do not rewrite an unchanged mapping.

## 6. Console noise that is not a failure

Ignore Mockito self-attach warnings and JDK "invalid/auto-detected installation" notes: they appear in
red but change nothing. Judge only by test results. Dev Services startup logs (container pull, datasource
ready) are normal on a `@QuarkusTest` run, not a problem.
