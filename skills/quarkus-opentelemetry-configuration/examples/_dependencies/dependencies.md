# Dependencies

## When to add

| Artifact ID | Group ID | Scope | Condition |
|-------------|----------|-------|-----------|
| quarkus-opentelemetry | io.quarkus | implementation | always (traces and/or metrics) |
| quarkus-observability-devservices-lgtm | io.quarkus | implementation (`provided` in Maven) | only when the LGTM Dev Service is chosen |
| opentelemetry-exporter-logging | io.opentelemetry | implementation | only for the console/logging exporter (debug) |
| opentelemetry-sdk-testing | io.opentelemetry | test | only when the InMemory-exporter test setup is requested |

Versions of `io.quarkus:*` are managed by the Quarkus BOM/platform — never add a version.
Versions of `io.opentelemetry:*` are managed transitively by `quarkus-opentelemetry` — never add a
version there either.

## Preferred command

```bash
./mvnw quarkus:add-extension -Dextensions="opentelemetry"
```
```bash
./gradlew addExtension --extensions="opentelemetry"
```

LGTM Dev Service (choose only when the user picked it):

```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-observability-devservices-lgtm"
```
```bash
./gradlew addExtension --extensions="quarkus-observability-devservices-lgtm"
```

## Maven

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-opentelemetry</artifactId>
</dependency>
<!-- Only when the LGTM Dev Service is chosen (Maven: provided keeps it out of the packaged app) -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-observability-devservices-lgtm</artifactId>
    <scope>provided</scope>
</dependency>
<!-- Only for the console/logging exporter (debug) -->
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-logging</artifactId>
</dependency>
<!-- Only for the InMemory-exporter test setup -->
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-sdk-testing</artifactId>
    <scope>test</scope>
</dependency>
```

## Gradle Kotlin DSL

```kotlin
implementation("io.quarkus:quarkus-opentelemetry")
// Only when the LGTM Dev Service is chosen:
implementation("io.quarkus:quarkus-observability-devservices-lgtm")
// Only for the console/logging exporter (debug):
implementation("io.opentelemetry:opentelemetry-exporter-logging")
// Only for the InMemory-exporter test setup:
testImplementation("io.opentelemetry:opentelemetry-sdk-testing")
```

## Gradle Groovy

```groovy
implementation 'io.quarkus:quarkus-opentelemetry'
// Only when the LGTM Dev Service is chosen:
implementation 'io.quarkus:quarkus-observability-devservices-lgtm'
// Only for the console/logging exporter (debug):
implementation 'io.opentelemetry:opentelemetry-exporter-logging'
// Only for the InMemory-exporter test setup:
testImplementation 'io.opentelemetry:opentelemetry-sdk-testing'
```

## Notes

- `quarkus-opentelemetry` alone already produces traces (and OTLP export) with zero configuration.
- The LGTM Dev Service is dev-mode-only by default (enable in tests explicitly if ever needed —
  see [`../_properties/dev-observability.md`](../_properties/dev-observability.md)).
- Do NOT add `quarkus-micrometer-opentelemetry` or Micrometer registries here — see
  [`../../references/micrometer-interop.md`](../../references/micrometer-interop.md) when the project
  already uses Micrometer.