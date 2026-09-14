# Maven plugin block (Maven)

## Insert Point

Inside `<project><build><plugins>` in `pom.xml`, after existing plugin entries.

## Code

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-checkstyle-plugin</artifactId>
    <version>${checkstylePluginVersion}</version>
    <!-- 3.6.0 is the current stable maven-checkstyle-plugin release (verified on Maven Central);
         omit <version> entirely when the parent POM/BOM manages this plugin; otherwise
         check the current 3.x line on Maven Central before pinning a number here. -->
    <configuration>
        <configLocation>config/checkstyle/checkstyle.xml</configLocation>
        <includeTestSourceDirectory>true</includeTestSourceDirectory>
        <consoleOutput>true</consoleOutput>
    </configuration>
</plugin>
```

Report-only setup (the default recommendation for a first run): keep the block exactly as above and run
`./mvnw checkstyle:checkstyle`.

Gate setup: add the execution below so `./mvnw verify` fails on violations.

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

Bundled ruleset instead of a committed config file:

```xml
        <configLocation>google_checks.xml</configLocation>
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${checkstylePluginVersion}` | parent POM/BOM if managed — then drop the line | latest verified 3.x |
| `config/checkstyle/checkstyle.xml` | project's ruleset path | created from `checkstyle-config.md` in this directory |
| `google_checks.xml` | bundled classpath resource (ships with the plugin's Checkstyle) | alternative to a committed config |

## Notes

- `checkstyle:checkstyle` never fails the build; `checkstyle:check` does.
- Do not add `com.puppycrawl.tools:checkstyle` as a plugin dependency unless a specific engine version is
  required — the plugin bundles its own.