---
name: quarkus-mutation-testing
description: >-
  Set up and run PIT (pitest) mutation testing on a Quarkus project (Maven or
  Gradle), tune what gets mutated, and read the mutation score.
  Use this skill whenever the user wants mutation testing added to a build,
  configured, run or re-run, wants a mutation score or a mutation report
  interpreted, asks why a particular mutant survived, asks what should be
  excluded, or wants something added to those exclusions — whether or not the
  tool is named. Also use it when the task calls for checking test quality
  rather than coverage: a high coverage number can hide tests that assert
  nothing.
  Russian phrases also trigger this: "мутационное тестирование", "запусти pitest",
  "мутационный скор", "оцени качество тестов", "какие мутанты выжили".
---

# Mutation testing

Use [`references/configuration.md`](references/configuration.md) for build setup,
[`references/quarkus-tests.md`](references/quarkus-tests.md) for test scope,
[`references/exclusions.md`](references/exclusions.md) for mutation boundaries,
[`references/usage.md`](references/usage.md) for commands, and
[`references/report.md`](references/report.md) for result extraction.

## Preflight — project detection

This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
   All commands below have both variants; use the one matching the build.
2. **Quarkus version** — from the build file (see `quarkus-explore` preflight if needed). It decides the
   `pitest-junit5-plugin` floor: Quarkus 3.22+ needs plugin ≥ 1.19.4.
3. **Existing PIT config** — `grep -n "pitest" pom.xml build.gradle build.gradle.kts`.
4. **Test layout — this decides whether PIT is even practical.** Glob the test sources and count:
   - plain JUnit 5 tests (no `@QuarkusTest` annotation) — fast, good PIT drivers;
   - `@QuarkusTest` classes — boot the whole application (and Dev Services) per run;
   - `*IT` classes — packaged-artifact tests, never PIT drivers.

   Read [`references/quarkus-tests.md`](references/quarkus-tests.md) before step 1: on this stack the test layout decides
   `targetClasses`/`targetTests`, and getting it wrong turns a useful run into a multi-hour one.

---

## Steps

Start by checking your project memory for this skill's own `pitest` entry for THIS project — the checks
below build on it. A missing entry is not an error; it means nothing has been recorded yet.

Then work through the steps in order. Each carries a check: when the check fires, the step is already
done — skip it and move on. Load a step's reference only when you actually run that step, so there is
context left for the PIT output.

### 1. Configure PIT in the build

**Skip if** PIT is already configured — the memory entry describes a configuration for this project, or
(preflight) the build file already has a PIT plugin. Do not spend a command confirming what the entry
just said.

Otherwise follow `references/configuration.md`, which applies the test-scope decision from
`references/quarkus-tests.md` and the exclusions from `references/exclusions.md` as part of the setup.

Tell the user: `Step 1/4: Configuring PIT...`

If step 3 then fails with a task/plugin-not-found error, the entry was stale: say so, run this step
after all, and continue.

### 2. Adjust what gets mutated

**Skip if** the request has nothing to do with exclusions or the mutated scope (`targetClasses` /
`targetTests`).

Otherwise follow [`references/exclusions.md`](references/exclusions.md). It answers a question as well as it applies a change —
when the request is only a question, stop after judging the candidate and leave the build alone.

Tell the user: `Step 2/4: Reviewing what gets mutated...`

### 3. Run PIT and report the score

**Skip if** the user asked only to wire PIT into the build, or only for advice on exclusions — then say
a run is available and stop there.

Otherwise follow [`references/usage.md`](references/usage.md). The report itself follows
[`references/report.md`](references/report.md).

Tell the user: `Step 3/4: Running PIT...`

### 4. Record what was resolved

**Skip if** the memory entry already describes what the run actually used.

Otherwise write or update the `pitest` entry in the shape [`references/configuration.md`](references/configuration.md) §5 defines.
This is what lets step 1 be skipped next time — dropping it makes the next run pay for the version
probing and test-scope analysis all over again.

Tell the user: `Step 4/4: Recording what was resolved...`

---

## Anti-hallucination checklist

- [ ] The PIT plugin and `pitest-junit5-plugin` versions come from preflight facts (and the ≥ 1.19.4
      floor for Quarkus 3.22+), not from memory of another project.
- [ ] `targetClasses` (mutated) / `targetTests` (drivers) name classes that actually exist and that PIT can drive —
      re-checked after any exclusion change.
- [ ] Reported score, threshold and mutant counts are verbatim from `mutations.xml` — never estimated
      from a percentage in an ad-hoc log line.
- [ ] Every listed survivor carries `file:line` and a mutator name.
- [ ] A `NO_COVERAGE` block is called out as "not reached by the driving suite", not silently counted as
      "untested code" when a slow suite outside the PIT scope covers it.
- [ ] A red build after a run whose report exists is reported as the threshold firing — not as a
      broken run.