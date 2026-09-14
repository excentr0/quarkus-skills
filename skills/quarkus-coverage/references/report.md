# Coverage report format

The report the runner returns to the main agent after measuring coverage (Maven or Gradle). It is the
ONLY thing the runner returns: no build log, no console dump.

## Format — whole project

```text
Coverage: <coveragePct> (<covered>/<total> instructions)
Baseline: <baselinePct> | none found
Verdict:  <ABOVE | EQUAL | BELOW | n/a — no baseline>
HTML: <path to the report index.html>
```

The verdict is computed from the numbers, NOT applied: nothing was rewritten and nothing failed. Phrase
it conditionally — "the project's own gate would pass/fail" — and name the file the baseline came from
if one was found.

## Format — a narrowed run (one group or one module)

No baseline, no verdict: a baseline describes what ALL the tests cover together, so a subset has
nothing to be judged against. Name exactly what was measured:

```text
Coverage by ${scope}: <coveragePct> (<covered>/<total> instructions)
HTML: <path>
```

## Format — not measured

The run never produced a report. Most often a failing test stopped the build before the report task;
sometimes the run simply did not execute tests (filter matched nothing, or a container runtime was
unavailable for Dev Services). NEVER fall back to a previous number.

```text
Coverage: NOT MEASURED — the run produced no report.
Cause: <n> failing test(s) in <scope>
- <test>
    <message>
    <key stacktrace line(s), verbatim>
HTML: —
```

## Rules

- Report the coverage % and baseline % **verbatim** from the numbers read — never a vague "coverage
  looks fine".
- On BELOW, state the gap (current vs. baseline) so the main agent knows how far coverage fell.
- Never attach a verdict to a narrowed run, and never present its number as the project's coverage —
  it is a subset and is expected to differ.
- A partial or unit-only number is not whole-project coverage: if integration tests could not run
  (Docker unavailable), say so explicitly.
- Console noise is not a failure. Ignore Mockito self-attach warnings, JDK installation auto-detect
  notes, and Dev Services startup logs; judge only by the coverage number and the report's presence.

## Examples

Measured, no baseline in the project:

```text
Coverage: 84.12% (1215/1444 instructions)
Baseline: none found
Verdict:  n/a — no baseline
HTML: target/jacoco-report/index.html
```

Measured, compared to a project baseline:

```text
Coverage: 81.90% (1183/1444 instructions)
Baseline: 84.12% (from config/coverage-baseline.properties: coverage.instruction.minimum)
Verdict:  BELOW
Coverage dropped 2.22% below the baseline — the project's coverage gate would FAIL. Add tests for the
changed code, or confirm with the team before touching the baseline file.
HTML: target/jacoco-report/index.html
```

Narrowed run:

```text
Coverage by unit tests, of org.acme.order.*: 61.03% (214/350 instructions)
HTML: target/jacoco-report/index.html
```

Not measured:

```text
Coverage: NOT MEASURED — the run produced no report.
Cause: 1 failing test in test
- org.acme.order.OrderServiceTest#createRejectsBlankName
    expected: <400> but was: <500>
    at org.acme.order.OrderServiceTest.createRejectsBlankName(OrderServiceTest.java:88)
HTML: —
```
