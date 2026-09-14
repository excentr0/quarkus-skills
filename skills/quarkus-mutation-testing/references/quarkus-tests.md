# Driving PIT on a Quarkus project's tests

Read this before configuring PIT. On this stack the test layout — not the PIT version — is what decides
whether a mutation run is useful or a multi-hour mistake.

## The problem

PIT forks a fresh minion JVM per mutant group and runs the tests against each mutant. A plain JUnit 5
test costs milliseconds to start. A `@QuarkusTest` class:

- boots the whole CDI container and the application;
- starts Dev Services (database, Kafka, Keycloak) — container startup per minion;
- keeps the JVM warm for the application's lifetime, not the mutant's.

Multiplied by hundreds of mutants and many minions, that is not "slow" — it is a run that never
finishes usefully. So `@QuarkusTest` classes are **not** PIT drivers; the fast plain-JUnit tests are.

## Classify the test sources before configuring

```bash
grep -rl "@QuarkusTest" src/test/java | head -50
grep -rl "@QuarkusIntegrationTest" src/test/java | head -50
grep -rL "@QuarkusTest\|@QuarkusIntegrationTest" src/test/java --include='*.java' | head -50
```

- **plain JUnit 5** (no Quarkus test annotation) → PIT drivers; put these in `targetTests`.
- **`@QuarkusTest`** → excluded from `targetTests`. Keep the exclusion explicit and recorded —
  "the framework tests don't drive PIT here" is a decision a later reader must be able to find.
- **`@QuarkusIntegrationTest` / `*IT`** → never PIT drivers (packaged artifact, HTTP black box).

## Consequences to state to the user

- Classes covered **only** by `@QuarkusTest` tests report `NO_COVERAGE` in PIT. That is not a coverage
  gap in the usual sense — it is outside the measurement. Say which layers that affects (usually JAX-RS
  resources and repository glue) instead of silently reporting them as untested.
- Maven keeps both kinds of tests in one source set, so the split is expressed in `targetTests`
  (a glob list), not by source set. Gradle can split by source set — prefer that when the project has
  separate source sets for framework tests.
- If the project has **only** `@QuarkusTest` tests and no plain unit tests, stop and say so. Options,
  in order of usefulness:
  1. add plain unit tests for the classes worth mutating (business logic extracted from resources);
  2. run PIT on a single small class anyway, accepting minutes per mutant group — only if the user
     explicitly wants it;
  3. skip mutation testing for now.
  Never quietly kick off a run that will not finish.

## After the split

Verify the split actually took: a first PIT run should discover tests and report a real covered count.
Zero tests discovered, or every class at `NO_COVERAGE`, means `targetTests` matched nothing —
fix the globs before drawing any conclusion about the score.
