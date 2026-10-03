# Result report format

Return one concise report with command, actual scope, exit status, and fresh test-result counts. Do not use old XML as proof of a new run.

## Evidence collection

Before running, note the start time and expected result directories (`target/surefire-reports`, `target/failsafe-reports`, or `build/test-results/<task>`); retain a listing/mtime fingerprint of only those directories. Afterward, count only result files demonstrably produced or updated by this invocation. Do not delete arbitrary build/results directories to force freshness. A build's `clean` task is appropriate only when part of the resolved command and its scope is understood.

For Maven Surefire/Failsafe XML or Gradle JUnit XML, count suites and sum `tests`, `failures`, `errors`, and `skipped`. Executed count is `tests - skipped`; a file with zero executed tests cannot establish PASS. Errors and failures both count as failures. Report skipped counts alongside executed counts.

## Status rules

- **PASSED** only if the command exited successfully, relevant fresh results exist, at least one relevant test executed, and summed failures/errors are zero. State exact type/module/filter and whether other test phases also ran.
- **FAILED** if command/build exit status is nonzero, tests fail/error, or an execution timeout/interruption occurs. If tests never started, explicitly say `tests NOT RUN` within the failed build report; an earlier passing phase does not make the overall command pass.
- **NOT RUN** if command/task never executed, no fresh report exists, all selected tests were skipped, Gradle reported only `UP-TO-DATE` without fresh execution evidence, or results are stale/zero-execution. State the reason.
- Classify relevant toolchain warnings from the command's exit/result evidence; do not silently ignore them or call a warning failure without evidence.

## Format

```text
Command: <exact command>
Scope: <type + module/filter; name every phase actually run>
Status: PASSED | FAILED | NOT RUN
Results: <executed> executed, <skipped> skipped; <failures> failures, <errors> errors
Evidence: <fresh report paths and exit status; or concise blocker>
```

For failures include the test name, message, and decisive stacktrace line verbatim, with `file:line` when present. Avoid dumping full logs.

## Examples

```text
Command: ./mvnw clean verify -DskipITs=false
Scope: Maven module order-service; Surefire + Failsafe
Status: PASSED
Results: 37 executed, 2 skipped; 0 failures, 0 errors
Evidence: fresh target/surefire-reports and target/failsafe-reports; exit 0
```

```text
Command: ./gradlew :order-service:quarkusIntTest
Scope: Gradle integration task only
Status: FAILED
Results: 4 executed, 0 skipped; 1 failure, 0 errors
Evidence: fresh build/test-results/quarkusIntTest; exit 1
- OrderIT#createRejectsInvalidOrder: expected <400> but was <500>
  java.lang.AssertionError: expected <400> but was <500> (OrderIT.java:88)
```

```text
Command: ./gradlew quarkusIntTest
Scope: Gradle integration tests
Status: NOT RUN
Results: no fresh test results
Evidence: task was UP-TO-DATE and no XML was executed or refreshed
```
