# Mutation testing report format

What the runner returns to the main agent. It is the ONLY thing it returns: no PIT log, no per-mutator
table, no timings.

## Format — a completed run

```text
Mutation score: <killed>/<total> (<pct>)
Test strength:  <killed>/<covered> (<pct>)
Mutated:        <targetClasses> minus exclusions, driven by <the fast test classes>
Threshold:      <n> — <PASSED | FAILED | not enforced (0)>

Survived (missing assertions), <n>:
- <Class>.<method>  <file>:<line>  <Mutator>
    <PIT's description of the mutant>

No coverage (not reached by the driving suite), <n>:
- <Class>.<method>  <file>:<line>  <Mutator>

HTML: <path to index.html>
```

List every survivor when there are ten or fewer; above that, list the ten in the classes with the most
survivors and give the remaining count.

Report **both** numbers, always: the mutation score alone conflates "not asserted on" with "not
reached", and those need different work.

## Format — nothing to mutate

Not a failure, and not a score of zero. Say what it means:

```text
Mutation score: NO MUTANTS — PIT found nothing to mutate in <targetClasses>.
```

Then give the reason, because the two possible causes need opposite responses: the code genuinely has
no mutable logic yet (fine, nothing to do), or `targetClasses`/`excludedClasses` no longer match the
codebase (a config bug that has been silently passing). Check which before reporting.

## Format — not measured

```text
Mutation score: NOT MEASURED — the run produced no report.
Cause: <n> failing test(s) in <suite>
- <test>
    <message>
    <key stacktrace line(s), verbatim>
```

Give the message AND the key stacktrace lines verbatim — the `file:line` is what makes it actionable.
Never fall back to an earlier number when this run produced none.

## Rules

- Numbers verbatim from `mutations.xml`, never a vague "mutation coverage looks reasonable".
- Every survivor carries `file:line` and a mutator name.
- A `NO_COVERAGE` block is only a coverage gap when the driving suite is supposed to reach it. When the
  class is covered by `@QuarkusTest`/IT suites outside the PIT scope, label it as outside the
  measurement instead of reporting it as untested code.
- A red build with a report present is the threshold firing — report it as such, not as a broken run.
- Console noise is not a failure: ignore JDK installation auto-detect notes, Mockito self-attach
  warnings and dependency-verification chatter. Judge only by the numbers and the threshold verdict.

## Example

```text
Mutation score: 34/41 (82.9%)
Test strength:  34/36 (94.4%)
Mutated:        org.acme.* minus *Config/*Properties/accessors, driven by the plain-JUnit test classes
Threshold:      75 — PASSED

Survived (missing assertions), 2:
- OrderService.applyDiscount  OrderService.java:48  ConditionalsBoundary
    changed conditional boundary
- Order.isExpired  Order.java:31  NegateConditionals
    negated conditional

No coverage (not reached by the driving suite), 5:
- OrderResource.update  OrderResource.java:77  NegateConditionals
  (+4 more in OrderResource — covered by the @QuarkusTest suite, which is not a PIT driver, so this is
   outside the measurement, not an untested class)

HTML: target/pitest-reports/index.html
```
