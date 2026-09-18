# Metrics properties

## application.properties

```properties
# --- OpenTelemetry metrics (MANDATORY, write explicitly — see the drift note) ---
quarkus.otel.metrics.enabled=true

# --- Optional: faster export in dev so dashboards fill sooner (default is 60s) ---
# %dev.quarkus.otel.metric.export.interval=10s
```

## Why explicit

`quarkus.otel.metrics.enabled` has a version-scoped default. Writing `true` explicitly is correct
across the supported branches — the skill never relies on an unverified default.

## Production block (only when production config was requested)

```properties
%prod.quarkus.otel.exporter.otlp.metrics.endpoint=${collectorUrl}
# Add a signal-specific protocol key only after verifying it in the exact Quarkus version.
# For a shared collector, use quarkus.otel.exporter.otlp.protocol from dev-observability.md.
```

Only the metrics-specific lines differ from traces: the generic
`quarkus.otel.exporter.otlp.endpoint` (see [`dev-observability.md`](dev-observability.md)) covers
both signals; use the per-signal `...metrics.endpoint` / `...traces.endpoint` keys only when the
traces and metrics go to **different** collectors.

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${collectorProtocol}` | user input or exact-version lookup | no generic default — always verify the protocol and matching port before writing an endpoint |
| `${collectorUrl}` | user input | must include the port matching the verified protocol; do not infer a port from an unverified default |

## Rules

- `quarkus.otel.metric.export.interval` default: `60s`. Only lower it under `%dev.`/`%test.` or for
  the logging exporter — never in `%prod.` without a reason (it multiplies export traffic).
- Metric names and attribute keys should follow the OpenTelemetry semantic conventions when an
  equivalent convention exists; do not invent a parallel name for a standardized one.
- The metrics created here are exported **only via OTLP** — there is no `/q/metrics` endpoint for
  them (that endpoint belongs to Micrometer/Prometheus).