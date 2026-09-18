---
name: quarkus-coverage
description: >-
  Measure a Quarkus project's code coverage with the quarkus-jacoco extension and
  report the coverage number: whole project, one test group, or one module.
  Use whenever coverage needs to be measured — a user asking to run the coverage
  report or check the current level, and also when the task calls for it:
  recording the starting coverage before development, confirming coverage did not
  drop after a change.
  Russian phrases also trigger this: "посчитай покрытие", "какое покрытие тестами",
  "покрытие кода", "проверь покрытие", "процент покрытия".
---

# Coverage

Use [`references/maven.md`](references/maven.md) or [`references/gradle.md`](references/gradle.md)
for command snippets and [`references/report.md`](references/report.md) for result extraction.

## What to cover

Coverage is measured from **the tests that actually ran** — the extension records what executed. So
the two dimensions are the ones the `quarkus-run-tests` skill uses: test **scope** (all tests, one
class/package, or one JUnit tag) and, in a multi-module build, a **module**.

| Coverage by | Meaning |
|---|---|
| whole project (default) | every test that runs in the build — the number a baseline refers to |
| one group | one class/package/tag's tests alone — a subset, not comparable to the whole-project number |
| one module | one module of a multi-module build |

**Warning that is worth stating up front:** merging coverage from `@QuarkusTest` runs with plain unit
tests is what the extension does by default (one data file, one report). Splitting them requires JUnit
tags — say so instead of pretending a filtered run is the project's coverage.

## Preflight — project detection

This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **The coverage extension** — grep the build file for `quarkus-jacoco`:
   - **present** — the agent is wired for you; nothing else to configure.
   - **absent** — nothing will measure anything until it is added (step 1 below).
3. **Never add/keep a `jacoco-maven-plugin` alongside it** — the two instrument the same classes and
   produce "already instrumented" errors. If the project has one, that is a decision to surface to the
   user, not to silently resolve.
4. **Existing baseline** — grep the project's config files (`.properties`, `.yaml`, `.yml`, CI configs,
   skipping `target/`, `build/`, `.git/`) for a key that looks like a coverage baseline: contains
   `coverage` plus `minimum` / `baseline` / `threshold` and a numeric value. Match on the key, not the
   file name — a baseline is a project invention with no conventional path.
5. **Multi-module build** — check whether the root build declares several modules; aggregation needs
   extra `quarkus.jacoco.*` properties (see `references/maven.md`).

---

## Step 0 — Read the request (no tools)

Tell the user: `Step 0/5: Reading the request...`

**Do NOT call any tools in this step.**

Fix what is being measured: whole project (usual default), one group (class/package/tag), or one
module. If the user asked for a number without qualifiers, whole project is the answer — only the
whole-project number can be compared to a baseline.

---

## Step 1 — Make sure something measures

Tell the user: `Step 1/5: Checking the coverage setup...`

If `quarkus-jacoco` is present — skip to step 2.

If it is absent, ask the user before touching the build (use your harness's structured-question tool,
e.g. `AskUserQuestion` / `ask_user_question`; a numbered list is the fallback) and offer:

- **Add `quarkus-jacoco` (test scope)** — the Quarkus way: the extension handles agent wiring and report
  generation; no plugin configuration. Exact snippets are in `references/maven.md` / `references/gradle.md`.
- **Add a standalone coverage plugin instead** — only when the project deliberately measures plain unit
  tests without Quarkus. Then never combine it with `quarkus-jacoco`.
- **Skip** — report that coverage cannot be measured and stop.

---

## Step 2 — Resolve the command

Tell the user: `Step 2/5: Resolving the coverage command...`

Follow [`references/maven.md`](references/maven.md) or [`references/gradle.md`](references/gradle.md)
to build one command:

- Whole project → a clean build+verify run (see the stale-report guard below).
- One group → the same build with the test scope narrowed (`-Dtest` / `--tests` / a tag filter).
- One module → the same command scoped to that module.

More than one plausible route → ask, do not guess. Do not run anything in this step.

---

## Step 3 — Run and collect the result

Tell the user: `Step 3/5: Measuring coverage...`

If your harness supports subagents, delegate the run + result collection to ONE subagent; otherwise
run directly. Coverage-build output is long and noisy — the runner's only job is the report defined in
[`references/report.md`](references/report.md).

**Stale-report guard (required).** Coverage is read from a report file that survives a failed run, so a
failing test would otherwise hand back the PREVIOUS run's number. Before running, either:

- prefer a clean build (`./mvnw clean verify`, `./gradlew clean test`) — `clean` removes the report
  directory and data file altogether; or
- if not cleaning, delete the report directory and the JaCoCo data file first
  (`target/jacoco-report`, `target/jacoco-quarkus.exec` on Maven) so an absent report can only mean
  "this run never got there".

Then run, and have the runner:

1. Find the report: `target/jacoco-report/index.html` by default on Maven — otherwise search the build
   directory for a `jacoco`-named `index.html`, since `quarkus.jacoco.report-location` may have moved it.
2. Read the number per `references/report.md`.
3. If the report is absent or older than the run → report NOT MEASURED with the cause (usually a failing
   test — name it with message and stacktrace), never a number.
4. If a baseline was found in preflight, compare and compute the verdict; for a narrowed run, give the
   number with NO verdict.

---

## Step 4 — Report and decide the next step

Tell the user: `Step 4/5: Reporting coverage...`

Present the report as it came. Then:

- **Number only (no baseline)** — state the number and that no project baseline was found, so no verdict
  is implied.
- **Verdict** — say what would happen if the project's own gate ran; do not run the gate (measurement
  must not mutate the repo or fail the build).
- **NOT MEASURED** — give the cause and the failing test; never fall back to an older number.
- Offer the obvious follow-ups: measure again after adding tests, or measure one package to find the
  uncovered area.

---

## Anti-hallucination checklist

- [ ] The report path was located (or the default verified) — not assumed.
- [ ] The number came from the report of THIS run; a stale report was ruled out before reporting.
- [ ] No number is reported when the run never reached the report task.
- [ ] A narrowed run's number is labelled as a subset and carries no baseline verdict.
- [ ] `quarkus-jacoco` and a standalone coverage plugin are never both active; if the project had one,
      the conflict was surfaced to the user.
- [ ] Multi-module aggregation settings, if used, come from `references/maven.md` — not invented.