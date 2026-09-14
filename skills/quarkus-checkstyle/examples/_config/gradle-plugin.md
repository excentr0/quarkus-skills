# Gradle plugin block (Gradle)

## Insert Point

`build.gradle.kts` — `plugins { }` block at the top, `checkstyle { }` block beside other tool
configuration (after the Quarkus plugin).

## Code

```kotlin
plugins {
    id("checkstyle")
}

checkstyle {
    toolVersion = "${checkstyleToolVersion}"
    configFile = file("config/checkstyle/checkstyle.xml")
    // report-only first run:  ignoreFailures = true
    // gate:                   maxWarnings = 0
    reports {
        xml.required.set(true)
        html.required.set(true)
    }
}
```

Groovy DSL (`build.gradle`) equivalent:

```groovy
plugins {
    id 'checkstyle'
}

checkstyle {
    toolVersion = "${checkstyleToolVersion}"
    configFile = file('config/checkstyle/checkstyle.xml')
    reports {
        xml.required = true
        html.required = true
    }
}
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${checkstyleToolVersion}` | project's version catalog (`gradle/libs.versions.toml`) if present | current Checkstyle release (check it — Gradle's default may lag) |
| `config/checkstyle/checkstyle.xml` | project's ruleset path | created from `checkstyle-config.md` in this directory |

## Notes

- `config/checkstyle/checkstyle.xml` is Gradle's default lookup path — keep the file there and the
  `configFile` line is optional but explicit. Prefer explicit.
- `./gradlew checkstyleMain checkstyleTest` is report-only unless `ignoreFailures`/`max*` settings say
  otherwise; `./gradlew check` is the lifecycle entry point.
- In a Kotlin DSL multi-module build, the plugin must be applied in every module that should be checked
  (via `subprojects { }` or per-module).