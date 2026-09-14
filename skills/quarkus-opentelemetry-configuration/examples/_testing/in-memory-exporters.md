# InMemory exporters for tests — Java

Used by Step 6 of [`../SKILL.md`](../../SKILL.md) when the user wants tests that assert on
telemetry. Requires the `opentelemetry-sdk-testing` test dependency
(see [`../_dependencies/dependencies.md`](../_dependencies/dependencies.md)) and the `%test.`
properties from [`../_properties/testing.md`](../_properties/testing.md).

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | project's test source root package | test root package |
| `${Service}` | user's task (service under test) | simple name, e.g. `OrderService` → `Order` |
| `${expectedSpanName}` | user's task | the operation to assert on |

## Producer beans (test sources only)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import jakarta.inject.Singleton;

import io.opentelemetry.sdk.testing.exporter.InMemoryMetricExporter;
import io.opentelemetry.sdk.testing.exporter.InMemorySpanExporter;

@ApplicationScoped
public class InMemoryExportersProducer {

    @Produces
    @Singleton
    InMemorySpanExporter inMemorySpanExporter() {
        return InMemorySpanExporter.create();
    }

    // Only when metrics are tested:
    @Produces
    @Singleton
    InMemoryMetricExporter inMemoryMetricExporter() {
        return InMemoryMetricExporter.create();
    }
}
```

The extension detects these CDI exporter beans and wires them into the SDK
(`quarkus.otel.traces.exporter` / `quarkus.otel.metrics.exporter` default to `cdi`).

## Span assertion in a `@QuarkusTest`

```java
package ${packageName};

import java.util.List;

import jakarta.inject.Inject;

import io.opentelemetry.sdk.testing.exporter.InMemorySpanExporter;
import io.opentelemetry.sdk.trace.data.SpanData;

import io.quarkus.test.junit.QuarkusTest;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

@QuarkusTest
public class TracingTest {

    @Inject
    InMemorySpanExporter inMemorySpanExporter;

    @Inject
    ${Service}Client client; // whatever triggers the operation under test

    @org.junit.jupiter.api.Test
    public void spanIsRecorded() {
        client.call();

        List<SpanData> spans = inMemorySpanExporter.getFinishedSpanItems();
        assertTrue(spans.stream().anyMatch(span -> span.getName().equals("${expectedSpanName}")));
    }
}
```

## Metric assertion in a `@QuarkusTest`

```java
@Inject
InMemoryMetricExporter inMemoryMetricExporter;

// ...

List<MetricData> metrics = inMemoryMetricExporter.getFinishedMetricItems();
```

`MetricData` comes from `io.opentelemetry.sdk.metrics.data.MetricData`; filter by
`metricData.getName()` and inspect points via `metricData.getData().getPoints()`.

## `@QuarkusIntegrationTest` (separate process)

Test classes cannot inject beans into the running artifact. Expose the in-memory data through a
REST endpoint inside the application (this mirrors Quarkus's own `ExporterResource`), then assert
against the HTTP response:

```java
@GET
@Path("/export")
public List<SpanData> exportTraces() {
    return inMemorySpanExporter.getFinishedSpanItems()
            .stream()
            .filter(span -> !span.getName().contains("export")) // exclude calls to this endpoint
            .collect(java.util.stream.Collectors.toList());
}
```

## Rules

- Producers live in `src/test/java` for `@QuarkusTest`; only the integration-test variant moves
  them into `src/main/java` behind an endpoint.
- Clear state between tests when asserting counts: `inMemorySpanExporter.reset()` exists — use it
  in `@BeforeEach` when the test asserts exact numbers.
- Do not point tests at a real OTLP endpoint and do not start the LGTM Dev Service in tests
  implicitly — deterministic in-memory assertions are the point.