# Custom metrics — OpenTelemetry API (`Meter`) — Java

Used by Step 5 of [`../SKILL.md`](../../SKILL.md) when the task needs application-generated metrics.
`Meter` is a CDI-injectable bean provided by `quarkus-opentelemetry` — no registry, no extra dependency.

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 1 | package of the existing service, else root package |
| `${Service}` | user's task (instrumented service class) | simple name minus `Service`/`Controller` suffix (e.g. `OrderService` → `Order`) |
| `${className}` | derived | `${Service}Metrics` or appended into an existing bean |
| `${metricBase}` | user's task | kebab-case, lowercase with dots, e.g. `orders.created` |
| `${attributeKey}` | derived | bounded category name, e.g. `feature` |

## Code — Counter (monotonic count: events, requests, created things)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.Meter;

@ApplicationScoped
public class ${className} {

    private final LongCounter counter;

    public ${className}(Meter meter) {
        this.counter = meter.counterBuilder("${metricBase}")
                .setDescription("Number of ${metricBase} events")
                .setUnit("{event}")
                .build();
    }

    public void record(String ${attributeKey}) {
        counter.add(1, Attributes.of(AttributeKey.stringKey("${attributeKey}"), ${attributeKey}));
    }
}
```

Other counter types: `LongUpDownCounter`, `DoubleCounter`, `DoubleUpDownCounter`.

## Code — Histogram (distribution: durations, sizes)

```java
package ${packageName};

import java.util.Arrays;
import java.util.List;

import jakarta.enterprise.context.ApplicationScoped;

import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.LongHistogram;
import io.opentelemetry.api.metrics.Meter;

@ApplicationScoped
public class ${className} {

    private final LongHistogram histogram;

    public ${className}(Meter meter) {
        this.histogram = meter.histogramBuilder("${metricBase}.duration")
                .ofLongs() // default histogram records Double; .ofLongs() for Long values
                .setDescription("Distribution of ${metricBase} durations")
                .setUnit("ms")
                .build();
    }

    public void record(long millis) {
        histogram.record(millis);
    }
}
```

- Histograms replace Micrometer Timers and Distribution Summaries — the OTel API has neither.
- Optional explicit buckets (values are **inclusive**): `meter.histogramBuilder("...")
  .setExplicitBucketBoundariesAdvice(Arrays.asList(10L, 50L, 100L, 500L))`.
- Bucket-boundary advice is ignored on some backends — boundaries are a *suggestion* the exporter
  may override.

## Code — Gauge (current value polled on export)

```java
@ApplicationScoped
public class ${className} {

    public ${className}(Meter meter) {
        meter.gaugeBuilder("${metricBase}.size")
                .setDescription("Current ${metricBase} size")
                .setUnit("{item}")
                .ofLongs() // default gauge records Double
                .buildWithCallback(result -> result.record(currentSize(), Attributes.empty()));
    }

    long currentSize() {
        return 0; // replace with the real observable
    }
}
```

## Rules

- **Cardinality:** each unique metric name + attribute-value combination creates its own time
  series, kept forever by the backend. Attribute values must be bounded enums/categories
  (`status=ok`, `feature=checkout`) — never IDs, user names, or free strings.
- Build instruments **once** (constructor / `@PostConstruct`) and reuse them; `add`/`record` are
  cheap, building is not.
- Metric naming: lowercase dot-separated (`orders.created`, `http.server.duration`); use the
  OpenTelemetry semantic conventions when a standard name exists
  (https://opentelemetry.io/docs/specs/semconv/).
- These metrics are exported via OTLP only; there is no `/q/metrics` endpoint for them (that is
  Micrometer/Prometheus territory — see [`../../references/micrometer-interop.md`](../../references/micrometer-interop.md)).
- `@Counted` / `@Timed` / `@Gauge` annotations are **Micrometer** annotations — do not use them with
  the plain OTel API.