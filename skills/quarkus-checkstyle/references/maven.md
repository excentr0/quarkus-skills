# Checkstyle with Maven

## Commands

| Goal | What it does | Fails the build? |
|---|---|---|
| `./mvnw checkstyle:check` | analyzes and fails on violations (`failOnViolation`, `violationSeverity`) | yes, by default |
| `./mvnw checkstyle:checkstyle` | generates the report (XML + HTML site page) | no |
| `./mvnw checkstyle:checkstyle-aggregate` | multi-module aggregate report | no |

- Default result file: `target/checkstyle-result.xml` (override with `<outputFile>`).
- HTML report: `target/site/checkstyle.html`.
- `consoleOutput` defaults to `false` — set it to `true` when a console summary is wanted in CI logs.

## Plugin configuration

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-checkstyle-plugin</artifactId>
    <version>${checkstylePluginVersion}</version>
    <configuration>
        <configLocation>config/checkstyle/checkstyle.xml</configLocation>
        <includeTestSourceDirectory>true</includeTestSourceDirectory>
        <consoleOutput>true</consoleOutput>
    </configuration>
</plugin>
```

## configLocation semantics

| Value | Meaning |
|---|---|
| `config/checkstyle/checkstyle.xml` | file path, resolved against the project — the config is committed to the repo |
| `google_checks.xml` / `sun_checks.xml` | **classpath resource bundled with the Checkstyle dependency of the plugin** — nothing to commit, the ruleset is the well-known Google/Sun standard |

The plugin brings its own Checkstyle engine; adding `com.puppycrawl.tools:checkstyle` as a plugin
dependency is only needed to pin a specific engine version.

## Gate vs report

- Gate (build fails on violations): either use the `check` goal, or bind it to a lifecycle phase:

  ```xml
  <executions>
      <execution>
          <id>checkstyle-check</id>
          <phase>verify</phase>
          <goals>
              <goal>check</goal>
          </goals>
      </execution>
  </executions>
  ```

- Report-only: run `checkstyle:checkstyle` (or `checkstyle:check` with `<failOnViolation>false</failOnViolation>`
  when a console summary is wanted without failing).

## Tuning knobs worth knowing

| Parameter | Effect |
|---|---|
| `includeTestSourceDirectory` | also check `src/test/java` (default `false`) |
| `violationSeverity` | minimum severity that counts as a violation (`error` by default; set `warning` to be stricter) |
| `failOnViolation` | whether the `check` goal fails the build |
| `sourceDirectories` | check directories outside the default `src/main/java` |

## Version note

Do **not** invent the plugin version:

- if the project's parent POM or BOM manages `maven-checkstyle-plugin`, no `<version>` is needed at all;
- otherwise check the current 3.x on Maven Central and pin it — and say where the version came from.