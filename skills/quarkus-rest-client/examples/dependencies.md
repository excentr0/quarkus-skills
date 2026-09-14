# Dependencies

| Artifact ID | Group ID | Scope | Condition |
|-------------|----------|-------|-----------|
| quarkus-rest-client | io.quarkus | implementation | always (declarative REST client) |
| quarkus-rest-client-jackson | io.quarkus | implementation | always (JSON bodies for client DTOs) |
| quarkus-junit-mockito | io.quarkus | test | when the client is mocked in tests (`hasInjectMock`) |
| rest-assured | io.rest-assured | test | when the test asserts over HTTP |

Preferred way to add a Quarkus extension (updates the build file and resolves the version):
```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-rest-client,quarkus-rest-client-jackson"
./gradlew addExtension --extensions="quarkus-rest-client,quarkus-rest-client-jackson"
```

## Gradle Kotlin DSL
```kotlin
implementation("io.quarkus:quarkus-rest-client")
implementation("io.quarkus:quarkus-rest-client-jackson")
// test-only:
testImplementation("io.quarkus:quarkus-junit-mockito")
testImplementation("io.rest-assured:rest-assured")
```

## Gradle Groovy
```groovy
implementation 'io.quarkus:quarkus-rest-client'
implementation 'io.quarkus:quarkus-rest-client-jackson'
// test-only:
testImplementation 'io.quarkus:quarkus-junit-mockito'
testImplementation 'io.rest-assured:rest-assured'
```

## Maven
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-rest-client</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-rest-client-jackson</artifactId>
</dependency>
<!-- test-only: -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-junit-mockito</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <scope>test</scope>
</dependency>
```

## Notes
- Quarkus artifacts are version-managed by the Quarkus BOM (`io.quarkus.platform:quarkus-bom`) —
  omit `<version>` / the version string unless the build file pins versions explicitly.
- If the project already contains a client stack (`quarkus-rest-client` or the legacy
  `quarkus-resteasy-client`), add only the missing artifacts — never introduce a second client
  library into the same project.
- No `application.properties` entry belongs in this file — the base URL configuration is written
  separately from `examples/config.md`.
