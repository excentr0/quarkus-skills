# Metrics properties

## application.properties

```properties
# --- OpenTelemetry metrics (MANDATORY, write explicitly — see the drift note) ---
quarkus.otel.metrics.enabled=true

# --- Optional: faster export in dev so dashboards fill sooner (default is 60s) ---
# %dev.quarkus.otel.metric.export.interval=10s
```

## Why explicit

`quarkus.otel.metrics.enabled` defaults to **false** on Quarkus 3.33 LTS ("metrics are disabled by
default ... tech preview"); newer Quarkus versions flipped the default to true. Writing `true`
explicitly is correct on both — the skill never relies on this default.

## Production block (only when production config was requested)

```properties
%prod.quarkus.otel.exporter.otlp.metrics.endpoint=${collectorUrl}
%prod.quarkus.otel.exporter.otlp.metrics.protocol=${collectorProtocol}
```

Only the metrics-specific lines differ from traces: the generic
`quarkus.otel.exporter.otlp.endpoint` (see [`dev-observability.md`](dev-observability.md)) covers
both signals; use the per-signal `...metrics.endpoint` / `...traces.endpoint` keys only when the
traces and metrics go to **different** collectors.

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${collectorProtocol}` | user input | `grpc` (port 4317) on Quarkus 3.33 LTS; `http/protobuf` (port 4318) on newer Quarkus — always write the protocol next to the endpoint so the port matches |
| `${collectorUrl}` | user input | must include the matching port (`http://otel-collector:4317` for grpc) |

## Rules

- `quarkus.otel.metric.export.interval` default: `60s`. Only lower it under `%dev.`/`%test.` or for
  the logging exporter — never in `%prod.` without a reason (it multiplies export traffic).
- Metric names and attribute keys should follow the OpenTelemetry semantic conventions when an
  equivalent convention exists; do not invent a parallel name for a standardized one.
- The metrics created here are exported **only via OTLP** — there is no `/q/metrics` endpoint for
  them (that endpoint belongs to Micrometer/Prometheus).