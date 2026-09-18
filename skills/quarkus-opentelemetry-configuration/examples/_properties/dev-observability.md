# Dev-mode observability targets

Choose exactly ONE target per project. They are alternatives, not additions.

## 1. LGTM Dev Service (default recommendation)

Dependency `io.quarkus:quarkus-observability-devservices-lgtm` (see
[`../_dependencies/dependencies.md`](../_dependencies/dependencies.md)).

**Write NO OTLP endpoint properties.** The Dev Service starts a Grafana OTel LGTM container
(Grafana UI + Tempo traces + Prometheus metrics + Loki logs + OTel collector) in dev mode and
configures the OTLP endpoint itself (`quarkus.otel.exporter.otlp.endpoint=http://localhost:<port>`,
protocol `http/protobuf`) as runtime override properties.

- UI: watch the dev-mode log for `grafana.endpoint=http://localhost:<port>`, or open the Dev UI at
  `http://localhost:8080/q/dev-ui/extensions` and follow the Grafana link.
- Disable: `quarkus.observability.lgtm.enabled=false` (or `quarkus.observability.enabled=false`).
- Test mode: NOT started by default. Enable with `quarkus.observability.enabled-in-tests=true`
  when the user wants it in tests.

## 2. Jaeger (manual docker)

**Write endpoint properties only after checking the exact Quarkus version and collector protocol.**
Omit them only when the verified default endpoint and protocol match the container; otherwise write an
explicit endpoint together with its matching protocol. Give the user the command:

```bash
docker run --rm -it -p 16686:16686 -p 4317:4317 -p 4318:4318 jaegertracing/jaeger:latest
```

UI: `http://localhost:16686`. Ports: 16686 Jaeger UI, 4317 OTLP gRPC, 4318 OTLP HTTP.

## 3. Logging exporter (console debug output)

Dependency `io.opentelemetry:opentelemetry-exporter-logging`. Never use in production — write the
keys under `%dev.`:

```properties
%dev.quarkus.otel.traces.exporter=logging
%dev.quarkus.otel.metrics.exporter=logging
%dev.quarkus.otel.metric.export.interval=10000ms
```

## 4. Existing OTLP collector (user gave a URL)

```properties
%dev.quarkus.otel.exporter.otlp.endpoint=${collectorUrl}
%dev.quarkus.otel.exporter.otlp.protocol=${collectorProtocol}
```

## Production block (only when requested)

```properties
# --- OTLP export to the observability backend (prod) ---
%prod.quarkus.otel.exporter.otlp.endpoint=${collectorUrl}
%prod.quarkus.otel.exporter.otlp.protocol=${collectorProtocol}
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${collectorUrl}` | user input (plain free-form question) | no default — never invent a URL |
| `${collectorProtocol}` | user input or exact-version lookup | no generic default — resolve the protocol and matching port from the project's Quarkus version |

## Rules

- **Endpoint and protocol are written together, with the port matching the protocol:**
  `grpc` ↔ 4317, `http/protobuf` ↔ 4318. Defaults are version-scoped; check the exact project
  version before relying on one and never infer it from “newer Quarkus”.
- **Never write an unprefixed OTLP endpoint** when the LGTM Dev Service is in play — an explicit
  endpoint overrides the Dev Service's injected endpoint and breaks dev-mode export.
  Production addresses belong under `%prod.` (same discipline as broker addresses in the
  Kafka/RabbitMQ skills).
- Optional exporter extras (all verified keys): `quarkus.otel.exporter.otlp.headers=key1=value1,key2=value2`
  (e.g. `authorization=Bearer ${OTLP_AUTH_TOKEN}`), `quarkus.otel.exporter.otlp.timeout=10s` (default),
  `quarkus.otel.exporter.otlp.compression=gzip` (default: unset = disabled). Write only when the user asks.