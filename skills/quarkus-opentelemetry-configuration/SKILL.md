---
name: quarkus-opentelemetry-configuration
description: >
  Adds OpenTelemetry observability to a Quarkus application: the quarkus-opentelemetry
  extension, OTLP configuration for traces and metrics, custom spans (@WithSpan, Tracer)
  and custom metrics (Meter: Counter / Histogram / Gauge), automatic instrumentation
  coverage (HTTP, REST, gRPC, Kafka/messaging, JDBC), dev-mode observability
  (LGTM Dev Service, Jaeger, logging exporter), and InMemory-exporter test setup.
  Use this skill whenever tracing or metrics need to be added, enabled, configured, or
  explained in a Quarkus project — even when the user just says "add observability",
  "spans are not showing up", or names a backend like Jaeger / Grafana / Tempo / OTel collector.
  Triggers on: "opentelemetry", "otel", "tracing", "traces", "spans", "metrics",
  "quarkus-opentelemetry", "OTLP", "Jaeger", "Grafana LGTM", "@WithSpan", "Micrometer",
  "observability".
  Russian phrases also trigger this: "настрой opentelemetry", "добавь трейсинг",
  "включи метрики", "добавь opentelemetry", "трейсинг в jaeger", "отправка метрик в otel",
  "спаны не видны", "метрики не приходят", "настрой observability".
---

# Quarkus OpenTelemetry Configuration

Wires the Quarkus OpenTelemetry extension (`quarkus-opentelemetry`) for **traces and metrics**:
extension dependency, `application.properties` (OTLP export, sampling, suppression), optional
custom instrumentation code (spans, metrics), dev-mode observability targets, and the
InMemory-exporter test setup. Ensures the extension dependency is on the classpath.

> **CRITICAL: Code ONLY from `examples/` files. If no matching example — STOP and ask user.**
> **CRITICAL: Config keys ONLY from `examples/_properties/` and `references/config-reference.md`.**
>   `quarkus.otel.*` keys are easy to hallucinate; never invent a key that is not listed there.
> **CRITICAL: For questions with a fixed set of choices, use your harness's structured-question tool
>   (e.g. `AskUserQuestion` / `ask_user_question`); fall back to a plain numbered list.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Most questions in Step 2
>   may already be answered by the user's prompt and prior turns.

---

## Preflight — Project detection (before Step 0)

Harness-agnostic: file tools and shell commands only — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence** — Maven: `io.quarkus.platform:quarkus-bom` in `pom.xml`; Gradle: plugin `id("io.quarkus")`.
   If absent — stop: this skill targets Quarkus projects.
3. **OTel extension** — `io.quarkus:quarkus-opentelemetry` in the dependencies. Present or not — Step 3 fixes it.
4. **Micrometer presence** — `io.quarkus:quarkus-micrometer` in the dependencies; grep for
   `io.micrometer` imports (`MeterRegistry`, `@Counted`, `@Timed`). If present, read
   [`references/micrometer-interop.md`](references/micrometer-interop.md) before proposing anything —
   there are three Micrometer/OTel combinations and they must not be mixed blindly.
5. **Existing wiring** — grep `src/main` for `quarkus.otel.` (config) and
   `io.opentelemetry` (`@WithSpan`, `Tracer`, `Meter`, `SpanBuilder`).
6. **Config files** — `src/main/resources/application.properties` (or `.yaml` if `quarkus-config-yaml` is present).

## Two paths (Step 2 picks per signal)

- **Path A — `path = properties`** (default). Extension + `application.properties` only. The extension
  instruments HTTP endpoints, REST clients, gRPC, Kafka/messaging, Vert.x and (opted-in) JDBC
  automatically — see [`references/instrumentation.md`](references/instrumentation.md). Traces need **no
  configuration at all** after the dependency; metrics need one line (`quarkus.otel.metrics.enabled=true`).
- **Path B — `path = code`**. Application-generated spans and metrics in business beans:
  `@WithSpan`-annotated methods, `Tracer`-based manual spans, `Meter`-based counters/histograms/gauges.
  Code comes only from [`examples/_spans/`](examples/_spans/with-span.md) and
  [`examples/_metrics/`](examples/_metrics/otel-api.md).

The two paths combine freely; a typical "add opentelemetry" task is Path A for both signals, plus
Path B when the user names concrete things to measure ("count orders created").

## Defaults

| Option | Default | Always ask? |
|---|---|---|
| `signals` | both (`traces` + `metrics`) | YES — unless the prompt names them ("add traces", "enable metrics") |
| `instrumentation` (custom code) | `none` — rely on auto-instrumentation | YES — none / spans / metrics / both |
| `devObservability` | `lgtm` (Grafana OTel LGTM Dev Service) | YES — lgtm / jaeger / logging-exporter / external |
| `prodEndpoint` | skip `%prod.` block | NO — only when the user wants production/deploy config |
| `sampler` | `parentbased_always_on` (default; all requests traced) | NO — only when the user mentions sampling |
| `jdbcTelemetry` | off unless user asks | NO — offer when a JDBC datasource is present |
| `testSetup` | skipped (only when the user asks for tests) | NO |
| `language` | Java | NO — this repo's skills are Java-first |

**Smart defaults.** If the user says "use defaults" / "minimal configuration" → skip every
`Always ask = NO` question; ask only `signals` + `instrumentation` + `devObservability`.

**Smart answer recognition.** "traces to jaeger", "посчитай заказы", "no collector in prod yet" —
accept direct answers without re-asking. Several answers in one message → accept all.

**Batch questions.** Group related questions into ONE structured-question call (up to 4 questions).
Recommended option first, marked `(Recommended)`.

## Decision-making — context first, then ask

For every input: derive from the build file, `application.properties`, existing OTel/Micrometer code,
prior turns, and the user's prompt. Only ask when context yields no clear default.

1. **Context unambiguous → decide silently.** `language`, extension presence, service name
   (defaults to `quarkus.application.name` → artifactId), Micrometer-interop reading.
2. **Strong signal → one-line confirmation.** State the decision; user can accept silently.
   Used for: enabling JDBC spans when a datasource exists, reusing an existing `Tracer`-using bean.
3. **No clear default → structured question**, recommended option first.
   Used for: `instrumentation`, `devObservability`, `signals` (when the prompt is ambiguous).
4. **Empty for a critical input → ask plainly.** Production OTLP endpoint (free-form value) when
   the user asks for production config.

## Step 0 — Conversation context (mental, no tool calls)

Tell the user: `Step 0/7: Analyzing conversation context...`

Re-read the user's prompt and prior turns; tick off everything already stated:

| Input | Signal in the prompt |
|---|---|
| `signals` | "traces", "tracing", "spans" → traces; "metrics" → metrics; "opentelemetry"/"observability" without a signal → both |
| `instrumentation` | "count X", "measure X", "track X", "посчитай X" → metrics code; "span for X", "trace X" → spans code |
| `devObservability` | "jaeger" → jaeger; "grafana" → lgtm; "show in console" → logging-exporter; "we have a collector" → external |
| `prodEndpoint` | "production", "deploy", "k8s" → ask for the collector URL |
| `sampler` | "sample 10%", "reduce traces", "не все запросы" → sampler question |
| `jdbcTelemetry` | "sql spans", "database traces", "db queries" → jdbc telemetry |
| `testSetup` | "test", "assert spans", "проверить спаны" → testing step |
| smart defaults | "use defaults" → ask only `signals` + `instrumentation` + `devObservability` |

Tick → skip the corresponding question. Do not announce Step 0.

## Step 1 — Gather context (file reads + greps, no MCP)

Tell the user: `Step 1/7: Gathering context...`

| Source | Variables extracted |
|---|---|
| `pom.xml` / `build.gradle(.kts)` | `buildTool`, `quarkusVersion`, `presentDeps`, `mainPackage`, artifact version |
| `application.properties` (read fully) | `existingProps` — all `quarkus.otel.*`, `quarkus.datasource.*`, `quarkus.micrometer.*` keys |
| grep `io\.opentelemetry` under `src/main/java` | `existingOtelCode` — classes already using `@WithSpan`/`Tracer`/`Meter` (reuse them, do not duplicate) |
| grep `quarkus\.otel\.` under `src/main/resources` | `existingOtelProps` — keys already written; overwrite in place, never duplicate |
| datasources | `hasDatasource` — `quarkus.datasource.*` present → JDBC telemetry becomes a sensible offer |

**Multi-module projects.** If the build has several modules, score each by (+1) `quarkus-opentelemetry`
in its deps, (+1) any `quarkus.otel.*` key. Exactly one module with score ≥ 1 → select silently. Two or
more, or all-zero → ask which module, then re-gather for that module.

**Derived:**
- `otelExtensionPresent` — skip the Step 3 dependency add if true.
- `micrometerPresent` — `quarkus-micrometer` (or a registry) in deps; changes the metrics advice (see
  [`references/micrometer-interop.md`](references/micrometer-interop.md)).
- `quarkusVersion` — drives the version-drift notes (see the drift box in Step 4).

## Step 2 — All questions in ONE batch

Tell the user: `Step 2/7: Asking all questions...`

Ask everything in a single structured-question call (up to 4 questions). Pre-fill from context, skip
already-answered:

1. **Which signals?** — `traces + metrics` (Recommended), `traces only`, `metrics only`.
2. **Custom instrumentation code?** — `none, auto-instrumentation only` (Recommended),
   `spans (business operations)`, `metrics (counters/histograms)`, `both`.
3. **Dev-mode observability target?** — `LGTM Dev Service` (Recommended — starts Grafana + Tempo +
   Prometheus + collector automatically in dev mode), `Jaeger (docker run)`, `logging exporter (console, debug)`,
   `existing OTLP collector (specify URL)`.
4. **Production config?** — `skip for now` (Recommended), `add %prod. block (specify collector URL)`.

If the user asked for exactly one thing ("включи метрики") — Step 2 shrinks to one question
(`instrumentation`) or zero when that is also stated.

## Step 3 — Dependencies

Tell the user: `Step 3/7: Adding dependencies...`

Per [`examples/_dependencies/dependencies.md`](examples/_dependencies/dependencies.md):

| When | Artifact |
|---|---|
| always (traces and/or metrics) | `io.quarkus:quarkus-opentelemetry` |
| `devObservability = lgtm` | `io.quarkus:quarkus-observability-devservices-lgtm` (Maven: `provided` scope) |
| `devObservability = logging-exporter` | `io.opentelemetry:opentelemetry-exporter-logging` |
| `testSetup = true` | `io.opentelemetry:opentelemetry-sdk-testing` (test scope) |

Prefer `./mvnw quarkus:add-extension -Dextensions="opentelemetry"` / `./gradlew addExtension --extensions="opentelemetry"`;
match the project's existing dependency style (BOM-managed, no versions). If `otelExtensionPresent`,
skip and say so.

## Step 4 — Write configuration

Tell the user: `Step 4/7: Writing configuration...`

Compose `application.properties` **only** from
[`examples/_properties/`](examples/_properties/traces.md) blocks:

1. **Traces** — nothing required (on by default with the extension). Add the optional blocks
   (sampler, suppression) only when the user's answers demand them.
2. **Metrics** — when `signals` includes metrics, always write
   `quarkus.otel.metrics.enabled=true` **explicitly**, even on Quarkus versions where it defaults
   to true (see drift box).
3. **Dev observability** — per the chosen target:
   - `lgtm` → no endpoint properties at all (the Dev Service injects the endpoint itself);
   - `jaeger` → nothing in properties either (default OTLP endpoint `localhost:4317` already matches
     the Jaeger container); report the `docker run` command;
   - `logging-exporter` → `exporter=logging` + short `metric.export.interval` under `%dev.`;
   - `external` → the user's URL, written under `%dev.`/as asked.
4. **Production** — when requested: `%prod.quarkus.otel.exporter.otlp.endpoint=<collector>` **plus**
   `quarkus.otel.exporter.otlp.protocol` with the **matching port** (see drift box). Never write an
   OTLP endpoint unprefixed when a Dev Service is in play (it would override the Dev Service's
   endpoint in dev mode) — same discipline as broker addresses in the Kafka/RabbitMQ skills.

**Version drift box — read before writing endpoint/protocol keys:**

| Key | Quarkus 3.33 LTS (2026-03) | Newer main (3.39+) |
|---|---|---|
| `quarkus.otel.exporter.otlp.protocol` default | `grpc` → port **4317** | `http/protobuf` → port **4318** |
| `quarkus.otel.metrics.enabled` default | **false** (tech preview) | true |

Therefore: always write `quarkus.otel.metrics.enabled=true` explicitly, and when writing an endpoint
always write `protocol` next to it with the port matched to the protocol (`grpc` ↔ 4317,
`http/protobuf` ↔ 4318). Never rely on these defaults.

Overwrite existing keys in place; never delete unrelated keys or duplicate a key. YAML flavour
(`application.yaml` with `quarkus-config-yaml`): nest the same keys.

## Step 5 — Generate instrumentation code (Path B only)

Tell the user: `Step 5/7: Generating instrumentation code...`

1. Pick examples per need:
   - spans → [`examples/_spans/with-span.md`](examples/_spans/with-span.md) (annotation-driven) and/or
     [`examples/_spans/manual-span.md`](examples/_spans/manual-span.md) (explicit `Tracer` control);
   - metrics → [`examples/_metrics/otel-api.md`](examples/_metrics/otel-api.md) (Counter / Histogram / Gauge).
2. Substitute the `${variables}` from each template.
3. **Business wiring is task logic.** What gets counted, timed, or wrapped in a span comes from the
   user's task ("count created orders" → instrument the order-creation service method). If the task
   does not name a target — create the example bean with comment stubs and say so in the report;
   never invent business logic.
4. If `existingOtelCode` contains a fitting bean → read the file first and append the annotation or
   instrument inside it (merge imports); do not create a duplicate bean.
5. Detect indentation: `.editorconfig` → sample an existing source file → fallback 4 spaces.
   Emit one `import` per unique FQN; keep the project's import grouping.

## Step 6 — Test setup (only when the user asked for tests)

Tell the user: `Step 6/7: Setting up OTel test support...`

Follow [`examples/_testing/in-memory-exporters.md`](examples/_testing/in-memory-exporters.md):
`opentelemetry-sdk-testing` test dependency, `@Produces @Singleton InMemorySpanExporter` (and
`InMemoryMetricExporter` when metrics are on), speed-up keys under `%test.`, assertions via
`getFinishedSpanItems()` / `getFinishedMetricItems()`. For `@QuarkusIntegrationTest`, follow the
REST-extraction pattern in the same file. If the project has the `quarkus-test-writing` skill
available, hand the rest of the test file over to it.

## Step 7 — Report

Tell the user: `Step 7/7: Reporting...`

Match the user's conversation language. Include:

- Files written/edited and the exact keys / beans added.
- Extension state: added / already present.
- **How to see the data** for the chosen target:
  - `lgtm` → run `./mvnw quarkus:dev`; the Grafana endpoint appears in the dev-mode log
    (`grafana.endpoint=http://localhost:<port>`) and in Dev UI (`/q/dev-ui/extensions`).
  - `jaeger` → start the container (command in
    [`examples/_properties/dev-observability.md`](examples/_properties/dev-observability.md)), UI at
    `http://localhost:16686`.
  - `logging-exporter` → spans/metrics print to the app console.
- Auto-instrumentation already covering the project (HTTP endpoints, REST client calls,
  Kafka/messaging channels, JDBC when enabled — list what the project actually has).
- Effective defaults stated: sampler `parentbased_always_on` (100% traced); metric export interval 60s;
  traces on with zero config.
- Any stubbed business logic left in generated beans, and remaining questions.

## Anti-hallucination checklist

- [ ] `quarkus-opentelemetry` is present in the build file (added if it was missing); no other OTel
      artifact was invented (Quarkiverse exporters exist only for legacy Jaeger/Azure/Google Cloud —
      not invented on demand).
- [ ] Every `quarkus.otel.*` key written exists in `references/config-reference.md` (or an
      `examples/_properties/` file) — no invented keys, no invented defaults.
- [ ] `quarkus.otel.metrics.enabled=true` was written explicitly when metrics are used; the skill did
      not claim metrics work "by default".
- [ ] Every endpoint written together with `protocol`, and the port matches the protocol
      (grpc ↔ 4317, http/protobuf ↔ 4318). No unprefixed OTLP endpoint when a Dev Service is active.
- [ ] Traces: no config was written when nothing needed changing (they are on by default).
- [ ] Spans code uses only `io.opentelemetry.instrumentation.annotations.{WithSpan,SpanAttribute,AddingSpanAttributes}`
      on CDI bean methods and `io.opentelemetry.api.trace.{Tracer,Span,Scope}` — no Micrometer
      annotation presented as OTel (`@Counted`/`@Timed` are Micrometer-only).
- [ ] Metrics code uses `io.opentelemetry.api.metrics.{Meter,LongCounter,LongHistogram}` +
      `io.opentelemetry.api.common.{Attributes,AttributeKey}`; histogram bucket advice is inclusive;
      no unbounded attribute values (cardinality).
- [ ] Micrometer advice (if any) follows `references/micrometer-interop.md` — the three Micrometer
      paths were not mixed; `/q/metrics` was never called the OTel metrics endpoint.
- [ ] Test exporters are `io.opentelemetry.sdk.testing.exporter.InMemory{Span,Metric}Exporter` with the
      `opentelemetry-sdk-testing` dependency in test scope; speed-up keys came from the examples file.
- [ ] Keys, indentation, and import style match the project's existing files.
- [ ] No business logic was invented inside generated spans/metrics code.