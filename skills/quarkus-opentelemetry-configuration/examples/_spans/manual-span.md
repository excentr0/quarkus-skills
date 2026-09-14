# Manual spans (`Tracer`) — Java

Used by Step 5 of [`../SKILL.md`](../../SKILL.md) when the user needs explicit span control that the
`@WithSpan` annotation cannot express (custom start/stop points, async boundaries, child spans).

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 1 | package of the existing service, else root package |
| `${Service}` | user's task (instrumented service class) | simple name minus `Service`/`Controller` suffix (e.g. `OrderService` → `Order`) |
| `${className}` | derived | `${Service}Tracing` or appended into an existing bean |
| `${spanName}` | user's task | kebab-case operation name |

## Code

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

@ApplicationScoped
public class ${className} {

    @Inject
    Tracer tracer;

    public void doWork() {
        Span span = tracer.spanBuilder("${spanName}").startSpan();

        try (Scope ignored = span.makeCurrent()) {
            span.setAttribute("example.attribute", "value");
            span.addEvent("calculating");
            // business logic
        } catch (RuntimeException e) {
            span.recordException(e);
            throw e;
        } finally {
            span.end();
        }
    }
}
```

## Rules

- `OpenTelemetry`, `Tracer`, `Span`, and `Baggage` are CDI-injectable (`@Inject`) — provided by the
  extension per the MicroProfile Telemetry spec. Constructor injection also works.
- **Always call `span.end()`** — a span without `end()` is never exported. Prefer `@WithSpan`
  (which handles lifecycle) whenever explicit control is not required.
- A span not made current (no `makeCurrent()`) still exists and is exported, but it is not the
  *parent* of spans created inside the block — `makeCurrent()` establishes the parent relationship.
- `span.recordException(e)` + `Span.setStatus(StatusCode.ERROR)` is the convention for failures;
  auto-instrumented spans already do this for you.
- Do not create a span per loop iteration (span explosion) — one span per business operation.