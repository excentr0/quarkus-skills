# Checkstyle with Gradle

## Commands

| Command | What it does | Fails the build? |
|---|---|---|
| `./gradlew checkstyleMain` | checks `src/main/java` | depends on `ignoreFailures` / `maxWarnings` |
| `./gradlew checkstyleTest` | checks `src/test/java` | same |
| `./gradlew check` | the full check lifecycle — runs the checkstyle tasks if the plugin is applied | same |

Reports land in `build/reports/checkstyle/main.html`, `main.xml`, `test.html`, `test.xml`.

Task names are conventional: if the project renamed them or uses custom source sets, discover the real
task names (`./gradlew tasks --all | grep -i checkstyle`) instead of assuming.

## Plugin configuration (Kotlin DSL)

```kotlin
plugins {
    id("checkstyle")
}

checkstyle {
    toolVersion = "${checkstyleToolVersion}"
    configFile = file("config/checkstyle/checkstyle.xml")
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}
```

Groovy DSL equivalent: `id 'checkstyle'`, `checkstyle { toolVersion = '...'; configFile = file('config/checkstyle/checkstyle.xml') }`.

## Config resolution

- Gradle looks for `config/checkstyle/checkstyle.xml` by default — a committed config at that exact path
  needs no extra wiring.
- Any other path or a bundled ruleset must be set explicitly via `configFile` (a file) or `config`
  (a `resources.text.fromFile(...)` / classpath resource).
- Do not rely on an implicit fallback ruleset: if no config file is present, set one explicitly so the
  ruleset in effect is visible in the build file.

## Gate vs report

| Setting | Effect |
|---|---|
| `ignoreFailures = false` | build fails on violations (default) |
| `maxWarnings = 0` | zero-tolerance for warnings-severity violations |
| `maxErrors = 0` | zero-tolerance for error-severity violations |
| `ignoreFailures = true` | report-only mode |

For a first run against a legacy codebase, report-only (`./gradlew checkstyleMain` with
`ignoreFailures = true`) is the honest default — a wall of violations should not block the build on day one.

## toolVersion

Gradle ships with its own default Checkstyle version, which can lag the ruleset the project expects. Set
`toolVersion` explicitly (from the project's catalog if it manages one — `libs.versions.toml`; otherwise
check the current Checkstyle release) rather than inheriting the Gradle default silently.