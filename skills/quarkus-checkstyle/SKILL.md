---
name: quarkus-checkstyle
description: >-
  Sets up and runs Checkstyle on a Quarkus project via Maven or Gradle — no IDE required: detects an
  existing config, adds the plugin and a ruleset when missing, runs the check, and reports violations
  grouped by rule with a compact summary.
  Use this skill when the user asks to check code style, add Checkstyle, run style checks, or fix
  style violations ("run checkstyle", "add checkstyle", "style violations", "why does the build fail
  on style", "lint the code").
  Russian phrases also trigger this: "checkstyle", "проверь стиль", "подключи checkstyle",
  "нарушения стиля", "ошибки стиля", "почему падает билд из-за стиля".
---

# Checkstyle

Checkstyle is a **static style check**: it reports violations and never rewrites code. Fixing is a
separate, explicit step (Step 5) with the user's agreement. There is no CLI formatter in this skill
set — if the user wants code reformatted rather than checked, say that plainly instead of silently
rewriting their files.

---

## Preflight — project detection

This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Existing Checkstyle** — Maven: `maven-checkstyle-plugin` under `<build><plugins>`; Gradle:
   `checkstyle` plugin (`id("checkstyle")` / `id 'checkstyle'`). Config evidence:
   `config/checkstyle/checkstyle.xml`, `checkstyle.xml` at the root, `<configLocation>` / `configFile`,
   references to `google_checks.xml` or `sun_checks.xml`, a suppression file.
3. **Alternative style tools already present** — Spotless (`spotless` plugin), PMD (`maven-pmd-plugin`).
   If the project enforces style with one of them, say so and ask before adding Checkstyle: two checkers
   over the same files produce churn, not quality.
4. **Previous runs** — `target/checkstyle-result.xml`, `target/site/checkstyle.html`,
   `build/reports/checkstyle/*.xml` indicate the setup has already run.

If there is no Quarkus build file, stop: this skill targets Quarkus projects.

---

## Paths

| Situation | Path |
|---|---|
| Checkstyle already configured (preflight 2) | **A** — Step 3 (run) → Step 4 (report) → Step 5 (fix, on request) |
| No Checkstyle | **B** — Step 2 (add plugin + ruleset from `examples/`) → Step 3 → Step 4 → Step 5 |

---

## Defaults

| Decision | Default | When to deviate |
|---|---|---|
| Ruleset | the project's committed `config/checkstyle/checkstyle.xml` when present; otherwise `google_checks.xml` (bundled with the plugin) | user has a corporate ruleset — use it |
| Scope | main + test sources | user asked for main only |
| Mode | report-only first (`checkstyle:checkstyle` / `checkstyleMain checkstyleTest`), gate later | user explicitly wants the build to fail — configure `failOnViolation` / `maxWarnings`, then `checkstyle:check` |
| Fixing | only after the report was shown and agreed | never "fix everything" silently |

---

## Decision-making — context first, then ask

The request plus the build file answer most questions. Ask only genuine forks, in **one batch**
(single structured-question call, e.g. `AskUserQuestion` / `ask_user_question`; numbered list as the
last resort):

- **ruleset** — bundled `google_checks.xml` vs a committed project config vs a corporate config (ask only
  when none exists — never silently pick a strict ruleset for someone else's codebase)
- **mode** — report-only vs fail-the-build gate
- **fixing** — report only, or fix violations now (and which rule classes)

Drop any question the conversation already answers.

---

## Step 0 — Conversation context first (REQUIRED, no tool calls)

Tell the user: `Step 0/5: Reading the request...`

**Do NOT call any tools in this step.**

Fix from the request: **goal** (set up / run / report / fix), **mode** (report vs gate), and **scope**
(main only, main + tests, selected files). If the user said "check the style and fix it", that is two
jobs — the report comes first.

---

## Step 1 — Gather context

Tell the user: `Step 1/5: Gathering context...`

Read: the build file (plugins section), any existing checkstyle config and suppression files, and the
last result file if present. Then state the findings in three lines:

```text
### Context:
- Checkstyle: configured (maven-checkstyle-plugin, config/checkstyle/checkstyle.xml)
- Mode: report-only (no failOnViolation anywhere)
- Last run: target/checkstyle-result.xml, 17 violations
```

---

## Step 2 — Add plugin and ruleset (Path B only)

Tell the user: `Step 2/5: Adding Checkstyle...`

Take the build-file block from examples (never write it from memory):

| Build tool | Example |
|---|---|
| Maven | [`examples/_config/maven-plugin.md`](examples/_config/maven-plugin.md) |
| Gradle | [`examples/_config/gradle-plugin.md`](examples/_config/gradle-plugin.md) |

Ruleset file: if the project has none, create `config/checkstyle/checkstyle.xml` from
[`examples/_config/checkstyle-config.md`](examples/_config/checkstyle-config.md) — a small starter set,
not a maximal one. Prefer the bundled `google_checks.xml` when the user wants a known standard instead
of a project-owned file (it ships on the plugin's classpath, no file to commit).

Never pin a plugin or Checkstyle version blindly — see the note in the Maven example.

---

## Step 3 — Run the check

Tell the user: `Step 3/5: Running Checkstyle...`

Follow the reference for the project's build tool: [`references/maven.md`](references/maven.md) or
[`references/gradle.md`](references/gradle.md). Report-only and gate commands differ — run the one the
user chose in Step 0, and remember the exact command for this project so the next run skips discovery.

If the build tool downloads the Checkstyle engine on first run, that is expected — wait for it.

---

## Step 4 — Report violations

Tell the user: `Step 4/5: Reporting violations...`

Parse the result XML as described in [`references/report.md`](references/report.md) and present the
compact summary: total count, count per rule, one example `file:line` per rule, and the result file path
for details. Numbers come from the XML — never estimate.

Zero violations is a valid, good outcome — say "0 violations" plainly rather than implying work was done.

---

## Step 5 — Fix violations (only when asked)

Tell the user: `Step 5/5: Fixing violations...`

Work rule class by rule class, smallest diff first:

1. Group violations by rule id; fix the largest group first (usually `UnusedImports`, `LineLength`).
2. Apply the minimal change per violation class — remove the unused import, wrap the long line. Never
   reformat untouched code around a violation.
3. Re-run Step 3 after each group; the count must strictly decrease.
4. A rule that misfires on legitimate code (generated sources, long URLs, test fixtures) gets a
   suppression fragment from [`examples/_config/suppressions.md`](examples/_config/suppressions.md) —
   suppress the specific files/rule, never the whole project, and never without telling the user.
5. Finish with the final count and what was suppressed.

---

## Anti-hallucination checklist

- [ ] The run command matches the project's actual build tool and existing plugin configuration.
- [ ] Every violation in the report traces to a real entry in the result XML (`file`, `line`, `rule`).
- [ ] Rule names come from the XML `source` attribute — not guessed from memory.
- [ ] No plugin/Checkstyle version was pinned without checking how the project manages versions.
- [ ] Suppressions are narrow (file glob + rule) and were shown to the user before being committed.
- [ ] "0 violations" was only claimed when the result XML actually contains no `error` elements.
- [ ] Fixes changed only the lines the rules require.