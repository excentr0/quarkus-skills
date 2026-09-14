# Traces properties

## Default (nothing to write)

Traces are **enabled by default** the moment `quarkus-opentelemetry` is on the classpath:
sampler `parentbased_always_on` (100% of requests), propagators `tracecontext,baggage`,
OTLP export to `http://localhost:4317` (protocol `grpc` on Quarkus 3.33 LTS; newer Quarkus
defaults to `http/protobuf` / port 4318). Write nothing unless one of the optional blocks applies.

`service.name` comes from `quarkus.application.name` (default: the artifactId); `service.version`
from the artifact version. Do not write them into `quarkus.otel.resource.attributes` unless the user
asks for an override.

## application.properties

```properties
# --- Traces are on by default. Nothing mandatory. ---

# --- Optional: sampling (only when the user asks to reduce volume) ---
# quarkus.otel.traces.sampler=parentbased_traceidratio
# quarkus.otel.traces.sampler-arg=0.1

# --- Optional: suppress spans for non-application URIs (default true; /q/* is suppressed) ---
# quarkus.otel.traces.suppress-non-application-uris=true
# quarkus.otel.traces.suppress-application-uris=/health,/ready
# quarkus.otel.traces.include-static-resources=false
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${samplerArg}` | user input | `0.1` in the example = ~10% sampled; skip the whole block unless sampling was requested |
| `${suppressPaths}` | user input | skip the `suppress-application-uris` line when the user has no specific URIs |

## Rules

- Sampler values (verified): `always_on`, `always_off`, `traceidratio`, `parentbased_always_on`,
  `parentbased_always_off`, `parentbased_traceidratio`. `sampler-arg` applies only to the
  `traceidratio` / `parentbased_traceidratio` variants (`0.0d`–`1.0d`).
- Suppression: `suppress-non-application-uris=true` (default) already hides `/q/*` endpoints and
  static assets from traces. `suppress-application-uris` takes a comma-separated list of extra URIs
  to hide; it is a *runtime* property.
- Do not write `quarkus.otel.traces.enabled=true` — it is the default and only adds noise.
- Production endpoint goes to [`dev-observability.md`](dev-observability.md) (OTLP block), not here.