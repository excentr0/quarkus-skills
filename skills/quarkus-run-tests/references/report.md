# Result report format

The report the runner returns to the main agent after running the tests (Maven or Gradle). It is the
ONLY thing the runner returns: no build log, no console dump.

## Format

**Passed:**

```text
<scope>: PASSED (<total> tests)
```

**Failed:**

```text
<scope>: FAILED (<failed>/<total>)
- <test>
    <message>
    <key stacktrace line(s), verbatim>
```

**Not run** (the suite never started — a green/red verdict would be a lie here):

```text
<scope>: NOT RUN — <cause: no wrapper / task not found / container runtime unavailable / build failed before tests>
```

## Rules

- Report the failure `message` and the key `stacktrace` line(s) **verbatim** — enough for the main
  agent to act on the real error, never a vague "some tests failed".
- Give `file:line` from the stacktrace when the XML carries one: `expected: X but was: Y` alone says
  what broke but not where.
- Report the **scope that actually executed** (type + filter). `test: PASSED (3 tests)` after a filter
  is not "the tests pass" — do not let a narrowed run read as a full-suite verdict.
- Console noise is NOT a failure. Ignore Mockito self-attach warnings, JDK installation auto-detect
  notes, and Dev Services startup logs. Judge only by JUnit results.
- A run that timed out, or a task that never executed, is NOT passed.
- Missing results directory with a green exit code (e.g. `--rerun-tasks` absent, Gradle reported
  UP-TO-DATE) → report NOT RUN with that cause; do not report zero failures as a pass.

## Examples

Green:

```text
quarkus: PASSED (25 tests)
```

Red:

```text
quarkus: FAILED (1/14)
- org.acme.order.OrderServiceTest#createRejectsBlankName
    expected: <400> but was: <500>
    java.lang.AssertionError: expected: <400> but was: <500>
        at org.acme.order.OrderServiceTest.createRejectsBlankName(OrderServiceTest.java:88)
```

Not run:

```text
integration: NOT RUN — quarkusIntTest task not found in this build (no integration-test source set)
```
