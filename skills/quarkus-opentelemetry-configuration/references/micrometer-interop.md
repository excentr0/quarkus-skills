# Micrometer ↔ OpenTelemetry interop

Read this when the project already has Micrometer, or when the user asks about
`/q/metrics`, `@Counted`, `@Timed`, or Prometheus. Three separate Micrometer paths exist; do not
mix them blindly.

## Which metrics path to pick

| Situation | Path |
|---|---|
| No Micrometer in the project, user wants OTel metrics | Plain `quarkus-opentelemetry` (this skill's default path) |
| Project uses Micrometer + Prometheus (`/q/metrics` must stay) | Keep Micrometer; add this skill only for traces. OTel metrics + Prometheus both running is allowed but two metric systems — confirm with the user |
| Micrometer annotations wanted, export via OTel | `quarkus-micrometer-opentelemetry` bridge (preview) |
| Micrometer metrics pushed to an OTLP backend without OTel SDK metrics | Quarkiverse `quarkus-micrometer-registry-otlp` |

## Path 1 — Classic Micrometer (status quo, unchanged by this skill)

- Dependencies: `io.quarkus:quarkus-micrometer` + a registry (`quarkus-micrometer-registry-prometheus`).
- Endpoint: `GET /q/metrics` (Prometheus text). **`/q/metrics` has nothing to do with
  `quarkus-opentelemetry`** — OTel metrics never appear there.
- Annotations: `io.micrometer.core.annotation.{Counted,Timed,Gauge}`; `MeterRegistry` injection.
- `@Counted`/`@Timed`/`@Gauge` are **Micrometer** annotations — never present them as
  "OpenTelemetry annotations", and do not mix them into the plain OTel API path.

## Path 2 — Micrometer → OTLP registry (Quarkiverse)

```properties
# io.quarkiverse.micrometer.registry:quarkus-micrometer-registry-otlp
quarkus.micrometer.export.otlp.url=http://collector:4318/v1/metrics
```

Pushes Micrometer metrics out via the OTLP protocol *without* the OTel SDK metrics being involved.
The LGTM Dev Service sets `quarkus.micrometer.export.otlp.url` automatically. Use when the user
wants Micrometer's automatic instrumentations (HTTP server, JVM binders) in an OTLP backend but
does not need OTel SDK metrics.

## Path 3 — Bridge: `io.quarkus:quarkus-micrometer-opentelemetry` (preview, since 3.19)

- Single dependency that pulls in `quarkus-micrometer` + `quarkus-opentelemetry` + a bridge; do not
  add those two separately when using it.
- With it present: OTel tracing/metrics/logs export via OTLP as usual, and Micrometer metrics
  (manual + `@Counted`/`@Timed`) flow through the OTel SDK. The OTel SDK's own HTTP-server/JVM
  auto-metrics are disabled by default (Micrometer covers them).
- Micrometer's automatic metrics are also disabled by default — enable binders explicitly:

```properties
quarkus.micrometer.binder.jvm=true
quarkus.micrometer.binder.http-server.enabled=true
```

- Mapping is **not 1:1**: Micrometer `Timer` → OTel Histogram + `<name>.max` gauge;
  `DistributionSummary` → Histogram (+ `.max`); `LongTaskTimer` → two observable counters;
  `Counter` → DoubleSum. Some empty metrics may be missing from the output.
- Status: **preview** — backward compatibility is not guaranteed. Do not choose this path silently;
  state the preview status and confirm with the user.
- Debugging: `quarkus.otel.metrics.exporter=logging` + `quarkus.otel.metric.export.interval=10000ms`
  prints metrics to the console (dev only, with `opentelemetry-exporter-logging`).

## Cardinality applies everywhere

Unbounded tag/attribute values (user IDs, request IDs, free strings) explode series counts in
Prometheus and in OTel backends alike — bind attribute values to bounded categories.