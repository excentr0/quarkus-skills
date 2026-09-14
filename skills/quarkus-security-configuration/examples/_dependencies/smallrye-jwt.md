# MP-JWT Dependencies

## When to add
`MP_JWT` variant only.

## Dependencies

| Artifact ID | Group ID | Scope | Condition |
|-------------|----------|-------|-----------|
| quarkus-smallrye-jwt | io.quarkus | implementation | always (MP-JWT variant) |
| quarkus-security | io.quarkus | implementation | always — core security annotations and `SecurityIdentity` |

Versions are managed by the Quarkus BOM/platform — never add a version.

## Preferred command
```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-smallrye-jwt,quarkus-security"
```
```bash
./gradlew addExtension --extensions="quarkus-smallrye-jwt,quarkus-security"
```

## Gradle Kotlin DSL
```kotlin
implementation("io.quarkus:quarkus-smallrye-jwt")
implementation("io.quarkus:quarkus-security")
```

## Gradle Groovy
```groovy
implementation 'io.quarkus:quarkus-smallrye-jwt'
implementation 'io.quarkus:quarkus-security'
```

## Maven
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-jwt</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-security</artifactId>
</dependency>
```
