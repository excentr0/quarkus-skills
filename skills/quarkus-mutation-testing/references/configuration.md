# Configuring PIT in a Quarkus build

## 1. Read the build's facts first

Four facts decide versions and shape. Gather them before touching the build file.

**Quarkus version** — from the build file (`quarkus.platform.version` / the `io.quarkus` plugin version).
Quarkus 3.22+ requires `pitest-junit5-plugin` ≥ 1.19.4; older Quarkus releases work with older plugin
versions, so never copy a version pair from another project.

**Java version** — `maven.compiler.release` / `java.version` / the Gradle toolchain. PIT forked minions
must run the same JDK as the project.

**JUnit Platform version** (Maven):

```bash
./mvnw -q dependency:tree -DincludeArtifactIds=junit-platform-commons
```

If it resolves to 6.x, the `pitest-junit5-plugin` bridge works but the run needs its own launcher on the
PIT classpath (the plugin's dependency block below is where it goes) — otherwise discovery can silently
find nothing and every class reports `NO_COVERAGE`, which reads like success. In that case pin
`junit-platform-launcher` and the Jupiter engine to the platform version inside the plugin dependencies.

**Test layout** — see `references/quarkus-tests.md`. It decides `targetTests`: on this stack the
fast plain-JUnit tests are the drivers, and `@QuarkusTest` classes must stay out.

## 2. Resolve the versions

Take the newest releases (Maven Central for both):

```bash
curl -s "https://repo1.maven.org/maven2/org/pitest/pitest/maven-metadata.xml" | grep -E "<latest>|<release>"
curl -s "https://repo1.maven.org/maven2/org/pitest/pitest-maven/maven-metadata.xml" | grep -E "<latest>|<release>"
curl -s "https://repo1.maven.org/maven2/org/pitest/pitest-junit5-plugin/maven-metadata.xml" | grep -E "<latest>|<release>"
```

Then check the `pitest-junit5-plugin` release against the Quarkus floor: ≥ 1.19.4 for Quarkus 3.22+.

## 3. Write the Maven config

```xml
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <version>${pitestMavenVersion}</version>
  <dependencies>
    <dependency>
      <groupId>org.pitest</groupId>
      <artifactId>pitest-junit5-plugin</artifactId>
      <version>$${pitestJunit5PluginVersion}</version>
    </dependency>
  </dependencies>
  <configuration>
    <targetClasses>
      <param>$${targetClasses}</param>
    </targetClasses>
    <targetTests>
      <param>$${targetTests}</param>
    </targetTests>
    <excludedClasses>
      <param>${excludedClasses}</param>
    </excludedClasses>
    <excludedMethods>
      <param>${excludedMethods}</param>
    </excludedMethods>
    <outputFormats>
      <param>XML</param>
      <param>HTML</param>
    </outputFormats>
    <timestampedReports>false</timestampedReports>
    <threads>${threads}</threads>
    <failWhenNoMutations>false</failWhenNoMutations>
    <mutationThreshold>0</mutationThreshold>
  </configuration>
</plugin>
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${pitestMavenVersion}` | newest on Central | — (resolve in §2) |
| `${pitestJunit5PluginVersion}` | newest on Central, ≥ 1.19.4 for Quarkus 3.22+ | — |
| `${targetClasses}` | project business packages | `org.acme.*` |
| `${targetTests}` | the fast plain-JUnit test classes | the `*Test` classes that do not boot the app |
| `{excludedClasses}` | `references/exclusions.md` answers | noise globs only |
| `{excludedMethods}` | `references/exclusions.md` answers | `equals`, `hashCode`, `toString`, `get*`, `set*`, `is*` |
| `{threads}` | half the available cores | `4` |

(The placeholders are literal text: substitute the resolved value in the build file, do not ship them.)

Four of these are decisions, not defaults:

- **`targetTests`** — start with the fast suite. PIT forks a fresh minion per mutant group, so a
  suite that boots the application pays that cost again and again. Name the layers this leaves outside
  the measurement.
- **`failWhenNoMutations=false`** — keeps a build with little logic green, at the price of passing
  silently once `targetClasses` stops matching. Flip it to `true` once there is logic worth mutating,
  and say so rather than leaving it quiet.
- **`mutationThreshold=0`** — no gate until a real score exists; then set it just below the score
  achieved.
- **`outputFormats`** — keep `XML`: the report is read from `mutations.xml`.

Do not wire PIT into the default build lifecycle (`verify`); offer it as a choice instead — a mutation
run is minutes, not seconds.

Reports land in `target/pitest-reports/` (`mutations.xml`, `index.html`) unless the configuration sets
`reportsDirectory` — read that value if it is present.

## 4. Gradle variant

```groovy
plugins {
    id 'info.solidsoft.pitest' version '${gradlePitestPluginVersion}'
}

pitest {
    pitestVersion = '${pitestVersion}'
    junit5PluginVersion = '$${pitestJunit5PluginVersion}'
    targetClasses = ['$${targetClasses}']
    targetTests = ['$${targetTests}']
    excludedClasses = ['${excludedClasses}']
    excludedMethods = ['${excludedMethods}']
    threads = Runtime.runtime.availableProcessors().intdiv(2) ?: 1
    timestampedReports = false
    outputFormats = ['HTML', 'XML']
    failWhenNoMutations = false
    mutationThreshold = 0
}
```

Gradle reports land in `build/reports/pitest/`. The `info.solidsoft.pitest` plugin is on the Gradle
Plugin Portal — take the portal's `<release>` value, not Maven Central's index, which lags behind it.

## 5. What the memory entry holds

This skill's OWN `pitest` file (one per project) — not the `run-tests` or `coverage` skill's entries. It
records what a later run needs, and nothing a glance at the build file answers.

```text
PIT configuration (resolved <YYYY-MM-DD>):
- build tool        -> Maven | Gradle
- pitest-maven      -> <version>  (pitest core <version>)
- junit5 plugin     -> <version>  (Quarkus <version> floor: >= 1.19.4 for 3.22+)
- run               -> ./mvnw test-compile org.pitest:pitest-maven:mutationCoverage
- report            -> target/pitest-reports/mutations.xml, target/pitest-reports/index.html
- mutated           -> <targetClasses>, minus excludedClasses/excludedMethods in the build file
- driven by         -> <the fast plain-JUnit test classes>; @QuarkusTest classes are NOT PIT drivers
- gates             -> failWhenNoMutations=<bool>, mutationThreshold=<n>
```

Plus a **Why** line for whatever cost real time here (the plugin/Quarkus version floor usually does),
and a **How to apply** line naming the trap to avoid next time. One file per project: an existing entry
is updated, never joined by a second.
