# `quarkus.otel.*` configuration reference (verified)

Verified against the Quarkus 3.33 LTS guide/config reference (2026-03) and the Quarkus main branch.
Facts live in `docs/quarkus-facts.md` §17. **Never write a `quarkus.otel.*` key that is not in this
file.**

## On/off switches

| Key | Default | When | Effect |
|---|---|---|---|
| `quarkus.otel.enabled` | `true` | build time | `false` disables the whole OpenTelemetry usage at build time |
| `quarkus.otel.sdk.disabled` | `false` | runtime | disables the OTel SDK at runtime (legacy autoconfig key) |
| `quarkus.otel.exporter.otlp.enabled` | `true` | build time | `false` disables the built-in OTLP senders — telemetry still generated, contexts still propagated, nothing sent out |
| `quarkus.otel.traces.enabled` | `true` | build time | `false` disables tracing |
| `quarkus.otel.metrics.enabled` | **`false`** (3.33 LTS) / `true` (newer main) | build time | `true` enables metrics — **always write it explicitly** |
| `quarkus.otel.traces.exporter` / `quarkus.otel.metrics.exporter` | `cdi` | build time | `otlp` / `cdi` / `none` / `logging` (with the logging-exporter dep); `none` disables the signal's output |

## Exporter (OTLP)

| Key | Default | Notes |
|---|---|---|
| `quarkus.otel.exporter.otlp.endpoint` | `http://localhost:4317` | signal-agnostic base; per-signal overrides below |
| `quarkus.otel.exporter.otlp.traces.endpoint` | (signal-agnostic value) | traces to a separate collector |
| `quarkus.otel.exporter.otlp.metrics.endpoint` | (signal-agnostic value) | metrics to a separate collector |
| `quarkus.otel.exporter.otlp.protocol` | `grpc` (3.33 LTS) / `http/protobuf` (newer main) | only `grpc` and `http/protobuf` are supported |
| `quarkus.otel.exporter.otlp.headers` | — | `key1=value1,key2=value2` |
| `quarkus.otel.exporter.otlp.timeout` | `10s` | per signal too (`...traces.timeout`, `...metrics.timeout`) |
| `quarkus.otel.exporter.otlp.compression` | unset (= none) | `gzip` |
| `quarkus.otel.exporter.otlp.memory-mode` | `immutable-data` | `reusable-data` = object pooling |

**Port rule:** `grpc` ↔ 4317, `http/protobuf` ↔ 4318. When writing an endpoint, always write the
protocol with it. Signal-specific keys also support `headers` / `compression` / `timeout`.

## Traces

| Key | Default | Notes |
|---|---|---|
| `quarkus.otel.traces.sampler` | `parentbased_always_on` | `always_on`, `always_off`, `traceidratio`, `parentbased_always_on`, `parentbased_always_off`, `parentbased_traceidratio` |
| `quarkus.otel.traces.sampler-arg` | `1.0d` | 0.0–1.0 ratio for the `traceidratio` variants |
| `quarkus.otel.traces.suppress-non-application-uris` | `true` | hides `/q/*` and non-app URIs |
| `quarkus.otel.traces.suppress-application-uris` | — | comma-separated extra URIs to hide (runtime) |
| `quarkus.otel.traces.include-static-resources` | `false` | static resource spans |
| `quarkus.otel.bsp.schedule.delay` | `5s` | batch span processor flush delay |
| `quarkus.otel.bsp.max.queue.size` | `2048` | |
| `quarkus.otel.bsp.max.export.batch.size` | `512` | |
| `quarkus.otel.bsp.export.timeout` | `30s` | |

## Metrics

| Key | Default | Notes |
|---|---|---|
| `quarkus.otel.metric.export.interval` | `60s` | lower only in dev/test/debug |
| `quarkus.otel.exporter.otlp.metrics.temporality-preference` | `cumulative` | |
| `quarkus.otel.exporter.otlp.metrics.default-histogram-aggregation` | `explicit_bucket_histogram` | |

## Propagation, resource, limits

| Key | Default | Notes |
|---|---|---|
| `quarkus.otel.propagators` | `tracecontext,baggage` | |
| `quarkus.otel.resource.attributes` | — | `key1=val1,key2=val2`; do not set `service.name` here unless overriding |
| `quarkus.otel.service.name` | `${quarkus.application.name:unset}` | takes precedence over resource attributes and `quarkus.application.name` |
| `quarkus.otel.attribute.count.limit` | `128` | max attributes |
| `quarkus.otel.attribute.value.length.limit` | — | truncate attribute values |

## Default resource attributes (automatic)

| Attribute | Value |
|---|---|
| `service.name` | `quarkus.application.name` → artifactId fallback |
| `service.version` | artifact version (build time) |
| `host.name` | resolved at startup |
| `telemetry.sdk.language` / `telemetry.sdk.name` / `telemetry.sdk.version` | `java` / `opentelemetry` / SDK version |
| `webengine.name` / `webengine.version` | `Quarkus` / Quarkus version |

## Disablement cheat sheet

- Whole feature off, compile-time: `quarkus.otel.enabled=false`.
- All output off, telemetry still generated and propagated: `quarkus.otel.exporter.otlp.enabled=false`.
- One instrumentation off (e.g. client requests): `quarkus.otel.instrument.<name>=false`
  (see [`instrumentation.md`](instrumentation.md)).
- Volume, not switch: sampler (`parentbased_traceidratio` + `sampler-arg`) or URI suppression.