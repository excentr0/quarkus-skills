# Dependencies

| Artifact ID | Group ID | Scope | Condition |
|-------------|----------|-------|-----------|
| quarkus-rest-jackson | io.quarkus | implementation | always (JSON serialization) |
| quarkus-hibernate-orm-panache | io.quarkus | implementation | always (synchronous Panache) |
| quarkus-hibernate-validator | io.quarkus | implementation | when `@Valid` is generated (`hasValidation`) |
| quarkus-mapstruct | io.quarkiverse.mapstruct | implementation | when DTO mode uses MapStruct |
| mapstruct | org.mapstruct | compile (annotation API) | when DTO mode uses MapStruct |
| mapstruct-processor | org.mapstruct | annotation processor (maven-compiler-plugin annotationProcessorPaths / Gradle annotationProcessor) | when DTO mode uses MapStruct |

Preferred way to add a Quarkus extension (updates the build file and resolves the version):
```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-rest-jackson"
./gradlew addExtension --extensions="quarkus-rest-jackson"
```

## Gradle Kotlin DSL
```kotlin
implementation("io.quarkus:quarkus-rest-jackson")
implementation("io.quarkus:quarkus-hibernate-orm-panache")
// conditional:
implementation("io.quarkus:quarkus-hibernate-validator")
implementation("io.quarkiverse.mapstruct:quarkus-mapstruct")
annotationProcessor("org.mapstruct:mapstruct-processor")
```

## Gradle Groovy
```groovy
implementation 'io.quarkus:quarkus-rest-jackson'
implementation 'io.quarkus:quarkus-hibernate-orm-panache'
// conditional:
implementation 'io.quarkus:quarkus-hibernate-validator'
implementation 'io.quarkiverse.mapstruct:quarkus-mapstruct'
annotationProcessor 'org.mapstruct:mapstruct-processor'
```

## Maven
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-rest-jackson</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-orm-panache</artifactId>
</dependency>
<!-- conditional: -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-validator</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkiverse.mapstruct</groupId>
    <artifactId>quarkus-mapstruct</artifactId>
</dependency>
<dependency>
    <groupId>org.mapstruct</groupId>
    <artifactId>mapstruct</artifactId>
</dependency>
```

<!-- MapStruct processor wiring (maven-compiler-plugin annotationProcessorPaths with
     org.mapstruct:mapstruct-processor) is owned by the quarkus-mapper-creator skill. -->

## Notes
- Quarkus artifacts are version-managed by the Quarkus BOM (`io.quarkus.platform:quarkus-bom`) —
  omit `<version>` / the version string unless the build file pins versions explicitly.
- `io.quarkiverse.mapstruct:quarkus-mapstruct` is not part of the Quarkus Platform BOM — if the
  build file has no Quarkiverse BOM, add the version already used by the project or the one
  compatible with its Quarkus version. Never invent a version number.
- The MapStruct dependency/annotation-processor wiring is owned by the `quarkus-mapper-creator`
  skill when it creates the mapper; only add what is still missing.
- No `application.properties` entries are needed by this skill.
