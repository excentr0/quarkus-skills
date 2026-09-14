# Running mutation testing and reading the score

## Run it and collect the result — in ONE runner

If your harness supports subagents, delegate the run + result collection to ONE subagent; otherwise run
directly. Either way the long PIT output must not flood the conversation — the runner's only job is the
summary defined in `references/report.md`.

Command to pass (pick the build system):

```bash
# Maven
rm -f target/pitest-reports/mutations.xml && ./mvnw test-compile org.pitest:pitest-maven:mutationCoverage

# Gradle
rm -f build/reports/pitest/mutations.xml && ./gradlew pitest
```

If the build config sets `reportsDirectory` / a custom report dir, delete and read the XML there instead.

**The `rm -f` is the stale-report guard.** PIT writes `mutations.xml` only when a run completes, but a
previous file survives a failed run — without deleting it, a failed run hands back the previous score
for code that no longer exists.

## Reading the result

Parse `mutations.xml` (default `target/pitest-reports/mutations.xml`):

- every `<mutation>` element is one mutant with a `<status>`: `KILLED`, `SURVIVED`, `NO_COVERAGE`,
  `TIMED_OUT`, `NON_VIABLE`, `RUN_ERROR`, `MEMORY_ERROR`;
- `NON_VIABLE` mutants are not real mutants — exclude them from every count;
- **mutation score** = killed / total, where total is all remaining mutants (survived + killed +
  no_coverage + timed-out);
- **test strength** = killed / covered, where covered = total − no_coverage. Reporting both is
  mandatory: the score alone conflates "not asserted on" with "not reached".

Each mutant carries `<mutatedClass>`, `<mutatedMethod>`, `<lineNumber>`, `<mutator>` and a
`<description>` — that is the `file:line` + mutator + description the report needs. Survivors without
them are not actionable.

## Interpreting the exit status

- **Report exists, build green** — the score is below any configured `mutationThreshold`? No: green
  means the threshold passed or is 0. Report the score.
- **Report exists, build red** — the threshold fired. Add PIT's own line above the summary, e.g.
  `Mutation score of 33 is below threshold of 90`. A report plus a failed build is the gate working,
  not a broken run.
- **No report on disk** — the run produced nothing. Find the cause in the build output: a failing test
  (name it, with message and stacktrace verbatim), `No mutations found`, a plugin/version failure
  (check the Quarkus floor from `references/configuration.md` §2), or a compile error. Report it in the
  NOT MEASURED form from `references/report.md`. Never fall back to an earlier number.

## Reading the score for the user

- Report score, test strength, the mutated scope and the driving test suite together — a score without
  its scope is not interpretable.
- List survivors with `Class.method  file:line  Mutator` and PIT's description; group by class when
  there are many. A survivor is a missing assertion, so the follow-up is a test for that branch, not a
  configuration change.
- `NO_COVERAGE` mutants are a coverage gap **only** when the driving suite is supposed to reach the
  class. Where the class is covered by `@QuarkusTest`/IT suites outside the PIT scope, label it as
  outside the measurement (`references/quarkus-tests.md`).
- When the score improved past a non-zero threshold, the threshold was NOT raised — say so and leave
  that decision to the user.
