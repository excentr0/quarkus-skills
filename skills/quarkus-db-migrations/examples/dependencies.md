# Dependencies

| Artifact ID | Group ID | Scope | Condition |
|-------------|----------|-------|-----------|
| quarkus-flyway | io.quarkus | implementation | when Flyway is the project's migration tool |
| quarkus-liquibase | io.quarkus | implementation | when Liquibase is the project's migration tool |
| quarkus-jdbc-postgresql / quarkus-jdbc-mysql / quarkus-jdbc-mariadb / quarkus-jdbc-h2 | io.quarkus | implementation | must already be present — the migration extension brings no driver |

Add exactly one migration extension — never both.

## Preferred way: extension command

```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-flyway"
./gradlew addExtension --extensions="quarkus-liquibase"
```

## Maven

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-flyway</artifactId>
</dependency>
```

## Gradle Kotlin DSL

```kotlin
implementation("io.quarkus:quarkus-flyway")
```

## Gradle Groovy

```groovy
implementation 'io.quarkus:quarkus-flyway'
```

## Notes

- Quarkus artifacts are version-managed by the Quarkus BOM (`io.quarkus.platform:quarkus-bom`) —
  omit the version unless the build file pins versions explicitly.
- The extension itself needs no additional properties to be usable; the behaviour keys are in
  `examples/properties.md`.
- Migration files are resources: `src/main/resources/db/**` — no build-file change is needed for them.
