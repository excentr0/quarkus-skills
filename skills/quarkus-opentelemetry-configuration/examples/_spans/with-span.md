# Custom spans — Java

Used by Step 5 of [`../SKILL.md`](../../SKILL.md) when the task needs application-generated spans.
The annotations come with `quarkus-opentelemetry` transitively — no extra dependency.

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 1 (package of the existing service, else root package) | root package |
| `${Service}` | user's task (instrumented service class) | simple name minus `Service`/`Controller` suffix (e.g. `OrderService` → `Order`) |
| `${className}` | derived | `${Service}Tracing` or appended into an existing bean |
| `${operationName}` | user's task | kebab-case operation, e.g. `order-processing` |

## Code — annotation-driven spans (`@WithSpan`)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import io.opentelemetry.instrumentation.annotations.AddingSpanAttributes;
import io.opentelemetry.instrumentation.annotations.SpanAttribute;
import io.opentelemetry.instrumentation.annotations.WithSpan;

@ApplicationScoped
public class ${className} {

    @WithSpan("${operationName}")
    public void process() {
        // business logic
    }

    // Span name = method name when no value is given; kind defaults to INTERNAL.
    @WithSpan
    void span() {
    }

    @WithSpan("span-name")
    void spanName() {
    }

    @WithSpan(kind = io.opentelemetry.api.trace.SpanKind.SERVER)
    void spanKind() {
    }

    // Method arguments become span attributes via @SpanAttribute:
    @WithSpan
    void spanArgs(@SpanAttribute(value = "arg.name") String arg) {
    }

    // Adds attributes to the CURRENT span without creating a new one:
    @AddingSpanAttributes
    void addArgumentToExistingSpan(@SpanAttribute(value = "arg.name") String arg) {
    }
}
```

## Rules

- The annotation target is **any CDI bean method** (`@ApplicationScoped`, `@Singleton`, …).
  On non-CDI classes (plain `new`, static methods) the interceptor never runs — silently nothing happens.
- The class must be called through its CDI proxy from another bean; a self-invocation inside the
  same bean does not trigger `@WithSpan`.
- Methods returning reactive types (`Uni`, `Multi`, `CompletionStage`) are supported — the span
  ends when the returned async type completes. For manual spans *inside* Mutiny pipelines Quarkus
  provides `io.quarkus.opentelemetry.runtime.tracing.mutiny.MutinyTracingHelper.wrapWithSpan(...)`
  (documented in the official tracing guide) — use only when the user explicitly needs it.
- If both `@WithSpan` and `@AddingSpanAttributes` are applied, `@WithSpan` takes precedence.
- Attribute values must be bounded (never a raw request ID / user name) — attributes are stored per
  span; keep them small and low-cardinality.

## Code — adding attributes to the current span from within a method

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import io.opentelemetry.api.trace.Span;

@ApplicationScoped
public class ${className} {

    public void handle(String orderId) {
        Span.current().setAttribute("order.id", orderId);
        // business logic
    }
}
```

`Span.current()` returns the active span (typically the auto-instrumented HTTP span); when there is
no active span it returns a no-op span — the call is always safe.