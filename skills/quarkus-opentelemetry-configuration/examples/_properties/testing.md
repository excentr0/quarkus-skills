# Testing properties (%test. profile)

```properties
# --- Speed up telemetry in @QuarkusTest so assertions do not wait for export ---
%test.quarkus.otel.bsp.schedule.delay=100
%test.quarkus.otel.metric.export.interval=100ms

# --- Optional: silence failed OTLP export attempts in tests (no collector running) ---
# %test.quarkus.otel.exporter.otlp.enabled=false
```

## Notes

- The speed-up keys are the pattern used by Quarkus's own OpenTelemetry integration tests:
  `quarkus.otel.bsp.schedule.delay` (default 5s → 100ms) flushes spans almost immediately;
  `quarkus.otel.metric.export.interval` (default 60s → 100ms) makes metrics visible to the
  InMemory exporter fast. Telemetry still goes through the normal batching path.
- `quarkus.otel.exporter.otlp.enabled=false` disables Quarkus's **built-in OTLP senders** only;
  telemetry is still generated and contexts propagated. The InMemory exporters (CDI-produced) keep
  working. Uncomment only when test logs fill with connection-refused noise.
- Do NOT write a `%test.quarkus.otel.exporter.otlp.traces.endpoint` — pointing tests at a
  nonexistent collector achieves nothing; use the InMemory exporters instead
  (see [`../_testing/in-memory-exporters.md`](../_testing/in-memory-exporters.md)).
- The LGTM Dev Service does not start in tests by default; leave it that way unless the user asks.