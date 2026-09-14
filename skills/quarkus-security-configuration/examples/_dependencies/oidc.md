# OIDC Dependencies

## When to add
OIDC variants (`OIDC_BEARER`, `OIDC_WEB_APP`).

## Dependencies

| Artifact ID | Group ID | Scope | Condition |
|-------------|----------|-------|-----------|
| quarkus-oidc | io.quarkus | implementation | always (OIDC variants) |
| quarkus-security | io.quarkus | implementation | always — core security annotations and `SecurityIdentity` |

Versions are managed by the Quarkus BOM/platform — never add a version.

## Preferred command
```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-oidc,quarkus-security"
```
```bash
./gradlew addExtension --extensions="quarkus-oidc,quarkus-security"
```

## Gradle Kotlin DSL
```kotlin
implementation("io.quarkus:quarkus-oidc")
implementation("io.quarkus:quarkus-security")
```

## Gradle Groovy
```groovy
implementation 'io.quarkus:quarkus-oidc'
implementation 'io.quarkus:quarkus-security'
```

## Maven
```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-oidc</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-security</artifactId>
</dependency>
```
