# Automatic instrumentation & instrumentation flags

What `quarkus-opentelemetry` traces **without any code**, and how to switch pieces off. Verified
against the Quarkus 3.33 LTS tracing guide.

## Instrumented core extensions (spans appear automatically)

| Extension | What it produces |
|---|---|
| `quarkus-rest` / `quarkus-resteasy` | server span per HTTP request (route-based names) |
| `quarkus-rest-client` / `quarkus-rest-client-jaxrs` / `quarkus-resteasy-client` | client span per outgoing call |
| `quarkus-vertx` | HTTP request spans on the Vert.x layer |
| `quarkus-agroal` | span per JDBC query — **only with `quarkus.datasource.jdbc.telemetry=true`** |
| `quarkus-messaging` | producer/consumer spans for Kafka, AMQP 1.0, RabbitMQ, Pulsar |
| `quarkus-grpc` | gRPC client/server spans |
| `quarkus-redis-client`, `quarkus-mongodb-client` | client spans |
| `quarkus-scheduler` | scheduled job spans |
| `quarkus-smallrye-graphql` | GraphQL operation spans |
| `websockets-next` | websocket spans |

Trace context propagation across HTTP and messaging is automatic (W3C `tracecontext` + `baggage`
by default) — a call chain across services arrives with the same `traceId` when every hop sends
the `traceparent` header (REST clients do this automatically).

## JDBC spans

```properties
quarkus.datasource.jdbc.telemetry=true
```

Off by default; one span per JDBC query once enabled. Enable only when the user asks (or a
one-line confirm when a datasource exists and the task is "trace database queries").

## Disabling individual instrumentations

`quarkus.otel.instrument.<name>` (default `true`; build-time):

`grpc`, `rest`, `resteasy`, `resteasy-client`, `messaging`, `vertx.http`, `vertx.event-bus`,
`vertx.sql-client`, `vertx.redis-client`, `jvm.metrics`, `http-server-metrics`

Example: keep server spans but stop tracing outgoing client calls:

```properties
quarkus.otel.instrument.resteasy-client=false
```

Note the metrics side: `quarkus.otel.instrument.jvm.metrics` and
`quarkus.otel.instrument.http-server-metrics` control OTel-generated JVM/HTTP **metrics**
(they are collected on Quarkus main; on 3.33 LTS the JVM/HTTP metrics story is Micrometer's —
see [`micrometer-interop.md`](micrometer-interop.md)).

## Suppression vs sampling vs disabling

| Goal | Tool |
|---|---|
| Hide `/q/*` or specific URIs from traces | `quarkus.otel.traces.suppress-application-uris` (non-app URIs already suppressed by default) |
| Reduce trace volume globally | `quarkus.otel.traces.sampler=parentbased_traceidratio` + `quarkus.otel.traces.sampler-arg=0.1` |
| Turn tracing off entirely | `quarkus.otel.traces.enabled=false` (build time) |
| Keep telemetry, stop network export | `quarkus.otel.exporter.otlp.enabled=false` |

## Manual context propagation (edge cases only)

For non-HTTP transports the W3C context can be injected/extracted manually with
`OpenTelemetry.getPropagators().getTextMapPropagator().inject(.../extract(...))` using
`TextMapSetter`/`TextMapGetter` carriers. `Baggage` travels alongside the trace context
(`Baggage.builder()...storeInContext(Context.current())`). Use only when the user explicitly needs
it (e.g. messaging payloads carrying `traceparent`); the full verified pattern lives in the
Quarkus OpenTelemetry Tracing guide ("Context propagation" section).