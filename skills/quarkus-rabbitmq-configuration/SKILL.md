---
name: quarkus-rabbitmq-configuration
description: >
  Configures RabbitMQ messaging in a Quarkus application: channel configuration in
  application.properties (`smallrye-rabbitmq` connector, queues/exchanges/routing keys)
  and, when needed, generated @Incoming / @Outgoing / @Channel messaging beans.
  Use this skill when RabbitMQ configuration needs to be created or extended, either
  standalone or as part of a larger task (e.g. before adding an Emitter producer or an
  @Incoming consumer).
  Triggers on: "configure rabbitmq", "add rabbitmq", "rabbitmq queue", "rabbitmq exchange",
  "routing key", "produce to rabbitmq", "consume from rabbitmq", "smallrye-rabbitmq",
  "Emitter", "Reactive Messaging", "message broker", "amqp".
  Russian phrases also trigger this: "настрой rabbitmq", "добавь rabbitmq", "кролик",
  "очередь rabbitmq", "exchange rabbitmq", "роутинг кей", "отправка сообщений в rabbitmq",
  "чтение сообщений из rabbitmq", "брокер сообщений".
---

# RabbitMQ Configuration

Wires the Quarkus RabbitMQ extension (`quarkus-messaging-rabbitmq`) through channels in
`application.properties` and, optionally, generates Reactive Messaging beans. Ensures the
extension dependency is on the classpath.

> **CRITICAL: Code ONLY from `examples/` files. If no matching example — STOP and ask user.**
> **CRITICAL: For questions with a fixed set of choices, use your harness's structured-question tool
> (e.g. `AskUserQuestion` / `ask_user_question`); fall back to a plain numbered list.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 2–3
> may already be answered by the user's prompt and prior turns.

---

## Preflight — Project detection (before Step 0)

Harness-agnostic: file tools and shell commands only — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence** — Maven: `io.quarkus.platform:quarkus-bom` in `pom.xml`; Gradle: plugin `id("io.quarkus")`.
   If absent — stop: this skill targets Quarkus projects.
3. **RabbitMQ extension** — `io.quarkus:quarkus-messaging-rabbitmq` in the dependencies.
   Present or not — Step 4b fixes it.
4. **Existing wiring** — grep `src/main` for `mp.messaging.` (channel config) and
   `org.eclipse.microprofile.reactive.messaging` (`@Incoming`/`@Outgoing`/`@Channel`).
5. **Config files** — `src/main/resources/application.properties` (or `.yaml` if `quarkus-config-yaml` is present).

## Two paths (Step 3 picks)

- **Path A — `path = properties`** (default when messaging beans already exist). Only channel
  configuration is written: `mp.messaging.<incoming|outgoing>.<channel>.connector=smallrye-rabbitmq`
  plus queue/exchange names and binding attributes. No Java is generated. An **incoming** channel maps
  to a RabbitMQ **queue** (consumed from it); an **outgoing** channel maps to a RabbitMQ **exchange**
  (published to it). Queue/exchange names default to the channel name; the incoming queue is bound to
  its exchange with `routing-keys`. `@Incoming`/`@Outgoing`/`@Channel` beans connect to channels by name.
- **Path B — `path = beans`**. Channel configuration **plus** a generated `@ApplicationScoped` messaging
  bean: a consumer method (`@Incoming`), a producer (`@Channel Emitter<T>`), or both. There are **no
  serializer configuration keys** — the connector converts payloads automatically (see
  [`examples/serialization-mapping.md`](examples/serialization-mapping.md)); a consumer of JSON POJOs
  receives `io.vertx.core.json.JsonObject` and maps it. Advanced per-message control (routing key,
  headers) goes through message metadata — see
  [`examples/producer-bean.md`](examples/producer-bean.md).

## Defaults

| Option | Default | Always ask? |
|---|---|---|
| `valueType` (producer, i.e. outgoing payload) | `java.lang.String` | YES — always ask |
| `valueType` (consumer) | symmetric with producer; POJO consumers take `JsonObject` + `mapTo` | NO — symmetric unless user says otherwise |
| `path` | `properties` when `@Incoming`/`@Outgoing`/`@Channel` beans already exist, else `beans` | YES |
| `channelName` | `${typeKebab}-in` / `${typeKebab}-out` — `${typeKebab}` = kebab-case value type simple name (`OrderEvent` → `order-event`) | NO |
| `queueName` (incoming) | channel name (connector default) | NO — write `.queue.name` only when the queue differs |
| `exchangeName` (outgoing) | channel name (connector default; `""` = default exchange) | NO — write `.exchange.name` only when the exchange differs |
| `exchangeType` | `topic` (connector default; also `direct`, `fanout`, `headers`) | NO — write `.exchange.type` only when the user names a non-default type |
| `routingKeys` | `#` (connector default) | NO — write `.routing-keys` only when the user names routing keys |
| `failureStrategy` | `reject` (connector default; also `fail`, `accept`) | NO — only when the user mentions failure handling |
| `existingInfrastructure` | app declares queue/exchange itself | NO — when the user says the queue/exchange already exists (ops-provisioned), write `.queue.declare=false` / `.exchange.declare=false` |
| `broker host/port/credentials` | unset → Dev Services for RabbitMQ in dev/test | NO — write only under `%prod.` when the user gives a real broker |
| `className` | `${ValueType}Messaging` (both), `${ValueType}Consumer` / `${ValueType}Producer` (single) | NO (Path B only) |
| `packageName` | main package (package of existing messaging beans, else root package) | NO (Path B only) |
| `language` | Java | NO — this repo's skills are Java-first |

**Smart defaults.** If the user says "use defaults" / "all defaults" / "minimal configuration" → skip every
`Always ask = NO` question. Only ask the mandatory ones (`valueType` producer, `path`) plus anything the user
mentioned non-default.

**Smart answer recognition.** When the user provides a value directly ("publish `OrderEvent`", "consume
`PaymentEvent`", "queue `orders-processed`"), accept it without asking again. Several answers in one
message → accept all.

**Batch questions.** Group related questions into ONE structured-question call (up to 4–5 questions).
Recommended option first, marked `(Recommended)`.

## Decision-making — context first, then ask

For every input: try to derive it from the build file, `application.properties`, existing messaging beans,
prior turns, and the user's prompt. Only ask when context yields no clear default.

1. **Context unambiguous → decide silently.** `language`, `packageName`, broker-access handling,
   channel names derived from the type, single `application.properties` file.
2. **Strong signal → one-line confirmation.** State the decision and alternatives; the user can accept
   silently. Used for: reusing an existing messaging bean class, queue/exchange names defaulting to
   channel names.
3. **No clear default → structured question** with the recommended option first. Used for: `valueType`,
   `path`, existing infrastructure (declare vs pre-provisioned).
4. **Empty for a critical input → ask plainly.** Producer `valueType`; the handling behavior for a
   generated consumer (see Step 5).

## Step 0 — Conversation context (mental, no tool calls)

Tell the user: `Step 0/6: Analyzing conversation context...`

Re-read the user's prompt and prior turns; tick off everything already stated:

| Input | Signal in the prompt |
|---|---|
| `valueType` (outgoing) | "publish `X`", "send `X`", "emit `X`", "produce `X`" |
| `valueType` (incoming) | "consume `X`", "read `X`", "@Incoming receives `X`" |
| `channelName` / queue / exchange | "channel `X`", "queue `X`", "exchange `X`", "to/from queue `X`" |
| `exchangeType` | "topic exchange", "fanout", "direct exchange" |
| `routingKeys` | "routing key `X`", "bind with key `X`" |
| `existingInfrastructure` | "queue already exists", "ops created the exchange", "don't declare" |
| `path` | "just add config", "only properties", "create a consumer/producer", "add an Emitter" |
| broker | "broker at `host`", "prod broker", credentials |
| `className` / `packageName` | "name it `FooMessaging`", "in package …" |
| smart defaults | "use defaults", "all defaults" → ask only `valueType` + `path` |

Tick → skip the corresponding question. Do not announce Step 0.

## Step 1 — Gather context (file reads + greps, no MCP)

Tell the user: `Step 1/6: Gathering context...`

| Source | Variables extracted |
|---|---|
| `pom.xml` / `build.gradle(.kts)` | `buildFile`, `buildTool`, `quarkusVersion`, `presentDeps`, `mainPackage` (from source tree), module list |
| `application.properties` (read fully) | `existingProps` — all `mp.messaging.*`, `rabbitmq-host`/`rabbitmq-port`/`rabbitmq-username`/`rabbitmq-password`, `%dev.`/`%prod.` prefixed keys |
| grep `mp\.messaging\.` under `src/main` | `existingChannels` — channel names already configured, with direction |
| grep `@Incoming\|@Outgoing\|@Channel` under `src/main/java` | `existingMessagingBeans` — class FQNs + file paths + the channel names each one uses |

**Multi-module projects.** If the build has several modules, score each by (+1) `quarkus-messaging-rabbitmq`
in its deps, (+1) any `mp.messaging.*` key in its property files. Exactly one module with score ≥ 1 →
select silently. Two or more, or all-zero → ask which module, then re-gather for that module.

**Derived:**
- `rabbitmqExtensionPresent` — `presentDeps` contains `io.quarkus:quarkus-messaging-rabbitmq`. Skip Step 4b if true.
- `singlePropsFile` — exactly one `application.properties`. Skip the props-file question if true.
- `existingBrokerAccess` — values of `rabbitmq-host`/`rabbitmq-port`/`rabbitmq-username`/`rabbitmq-password`
  or any channel `host`/`port` if present, else `null`.
- `existingBeanClasses` — from `existingMessagingBeans`; carries FQN, file path, declared channels. Used in Step 3.
- `orphanChannels` — channels referenced in code (`@Incoming`/`@Outgoing`/`@Channel`) but absent from
  `existingChannels` → they are missing config; this skill's job is to add it.

## Step 2 — All questions in ONE batch

Tell the user: `Step 2/6: Asking all questions...`

Ask everything in a single structured-question call (up to 5 questions). Pre-fill from context, skip
already-answered:

1. **Outgoing payload type?** — options: `java.lang.String` (Recommended), `io.vertx.core.json.JsonObject`,
   `java.util.UUID`, `Custom POJO (specify FQN — sent as JSON)`
2. **Where to put the wiring?** — `application.properties only` (Path A) / `application.properties + messaging bean`
   (Path B, Recommended when no `@Incoming`/`@Outgoing`/`@Channel` bean exists yet)
3. **Queue/exchange names?** — only when a name cannot be derived: default queue (incoming) and exchange
   (outgoing) = channel name. Skip when the user named them.
4. **Who declares the RabbitMQ infrastructure?** — `the app declares queue/exchange` (Recommended, connector
   defaults) / `already provisioned (declare=false)` — ask only when the user's prompt is ambiguous about
   existing infrastructure
5. **Production broker?** — `Dev Services in dev/test, real broker later` (Recommended) / `configure real
   broker address now` (plain value; written under `%prod.`)

If the user says "use defaults" — skip type and name questions, default outgoing type to
`java.lang.String`, and ask only `valueType` (confirm) + `path`.

## Step 3 — Bean target (Path B only)

Tell the user: `Step 3/6: Picking bean target...`

If `existingBeanClasses` is non-empty, apply Decision principle 2 (one-line confirmation), naming the class:

> Project already has messaging code in `${class.fqn}`. Add the new consumer/producer there? (Yes/No)

- **Yes** → `beanTarget = existing`. Reuse the class's `packageName`, `className`, and file path; Step 5
  appends the method/field with your edit tool instead of creating a file.
- **No (or no existing beans)** → `beanTarget = new`:
  - `className` — default `${ValueType}Messaging` for both directions, `${ValueType}Consumer` for a consumer
    only, `${ValueType}Producer` for a producer only. On file collision append a numeric suffix.
  - `packageName` — default = package of existing messaging beans; else the root package; ask only if the
    project has several candidate packages.

Usually answered silently from context.

## Step 4 — Write channel configuration + add dependency

Tell the user: `Step 4/6: Writing channel configuration...`

### 4a. Channel configuration

Always write a channel block per direction that the task needs. The **channel name must match the
`@Incoming`/`@Outgoing`/`@Channel` value** exactly.

Incoming (consumer — mapped to a queue):

```properties
mp.messaging.incoming.${inChannel}.connector=smallrye-rabbitmq
```

Outgoing (producer — mapped to an exchange):

```properties
mp.messaging.outgoing.${outChannel}.connector=smallrye-rabbitmq
```

Add the following keys **only when they differ from the connector defaults**:

- `.queue.name=${queueName}` (incoming) — only when the queue name differs from the channel name; the
  connector consumes from the queue named after the channel otherwise.
- `.exchange.name=${exchangeName}` (outgoing, or incoming when the queue must bind to a differently named
  exchange) — only when the exchange differs from the channel name.
- `.exchange.type=${exchangeType}` — only when the user named a non-default type (`topic` is the
  connector default; `direct`, `fanout`, `headers` are also valid).
- `.routing-keys=${routingKeys}` (incoming) — comma-separated list the queue is bound to the exchange
  with; connector default is `#`. Write it when the user named routing keys or the exchange type is
  `direct` (exact-match keys).
- `.default-routing-key=${routingKey}` (outgoing) — only when the user names a fixed routing key.
- **Existing infrastructure** (queue/exchange already provisioned by ops): write
  `.queue.name=${queueName}` + `.queue.declare=false` (incoming) and
  `.exchange.name=${exchangeName}` + `.exchange.declare=false` (outgoing).

Rules (all verified — see the checklist):

- **No serializer/deserializer keys exist** — unlike Kafka, the RabbitMQ connector has no
  `value.serializer`/`value.deserializer` attributes. Never write them. Payload conversion is automatic:
  `String`/primitives → text; `JsonObject`/`JsonArray`/POJO → JSON; `byte[]` → binary (full table in
  [`examples/serialization-mapping.md`](examples/serialization-mapping.md)).
- **Consumer of a JSON POJO** takes `io.vertx.core.json.JsonObject` and calls `.mapTo(${ValueType}.class)`
  — do not declare the POJO as the method parameter type (see
  [`examples/consumer-bean.md`](examples/consumer-bean.md)).
- **Broker access**: `rabbitmq-host`, `rabbitmq-port`, `rabbitmq-username`, `rabbitmq-password` are global
  keys; per-channel equivalents are `host`, `port`, `username`, `password`.
  **Never write them unprefixed** — it disables Dev Services for RabbitMQ in dev/test. A real broker goes
  under the production profile: `%prod.rabbitmq-host=${brokerHost}` (plus `%prod.rabbitmq-port=5672` and
  `%prod.rabbitmq-username`/`%prod.rabbitmq-password` when the broker requires auth). Pre-fill silently
  from `existingBrokerAccess` when present.
- Per-channel `host`/`port` also disable Dev Services when every channel defines them — avoid per-channel
  broker keys unless the user asks for mixed brokers.
- Overwrite existing keys in place; never delete unrelated keys or duplicate a key.
- YAML flavour (`application.yaml` when `quarkus-config-yaml` is present): nest the same keys under
  `mp.messaging.incoming.<channel>` / `mp.messaging.outgoing.<channel>`.
- Profile overrides (`%dev.`, `%test.`) are allowed for queue/exchange names; keep broker addresses out
  of the default profile (see above).

### 4b. Extension dependency

If `rabbitmqExtensionPresent = true`, skip. Otherwise add `io.quarkus:quarkus-messaging-rabbitmq`:

```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-messaging-rabbitmq"
```

or add the dependency to the build file directly (Gradle: `implementation("io.quarkus:quarkus-messaging-rabbitmq")`),
matching the project's existing dependency style (BOM-managed, no `<version>`).

## Step 5 — Generate messaging beans (Path B only)

Tell the user: `Step 5/6: Generating messaging beans...`

1. Pick the example per direction:
   - consumer → [`examples/consumer-bean.md`](examples/consumer-bean.md)
   - producer → [`examples/producer-bean.md`](examples/producer-bean.md)
   - both → both files; put both beans in the single `${className}` class.
2. Substitute the variables listed in the template (`${packageName}`, `${className}`, channel names,
   types). For a POJO `valueType` the consumer example switches to the `JsonObject` + `mapTo` variant.
3. **Handling body is business logic.** Fill the consumer method body only from the user's stated task
   (e.g. persist a Panache entity, call a service, forward to another channel). If the task does not
   specify handling — keep the single comment line from the example and say so in the report. Never
   invent business logic.
4. Detect indentation: `.editorconfig` → sample an existing source file → fallback 4 spaces.
5. FQN handling: emit one `import` per unique FQN used; skip `java.lang` and same-package classes; keep
   the project's import grouping (third-party block, then `java.*`). Metadata classes come from
   `io.smallrye.reactive.messaging.rabbitmq.*` — exact imports are in the examples.
6. Write step:
   - `beanTarget = new` → write the full file under `${sourceRoot}`, at the package path derived from
     `${packageName}` (`${className}.java`).
   - `beanTarget = existing` → read the target file first, then append before the closing brace and merge
     imports without duplicates. Do not create a second file.

## Step 6 — Report

Tell the user: `Step 6/6: Reporting...`

Match the user's conversation language. Include:
- Path taken (config-only vs config + beans).
- Files written/edited (paths) and the keys / beans added.
- Extension: added / already present.
- Effective defaults stated: queue/exchange names = channel names (when `.queue.name`/`.exchange.name`
  were omitted); exchange type `topic` (when omitted); routing binding `#` (when `.routing-keys` was
  omitted); infrastructure declared by the app (or `declare=false` where written).
- How to try it: `./mvnw quarkus:dev` — Dev Services starts a RabbitMQ broker automatically in dev/test
  because no `rabbitmq-host`/`rabbitmq-port` is configured (say explicitly if that is not the case, e.g.
  a `%prod.` address disables it). Management UI is available on the random `http-port` in dev.
- If the consumer body was left as a comment stub — say so and ask what the handling should be.
- `orphanChannels` that remain unconfigured, if any.

## Anti-hallucination checklist

- [ ] `quarkus-messaging-rabbitmq` is present in the build file (added if it was missing); no other
      messaging artifact was invented (not `quarkus-messaging-kafka`, not the Quarkiverse
      `quarkus-rabbitmq-client`).
- [ ] Every channel block sets `.connector=smallrye-rabbitmq` — never `smallrye-amqp`, `smallrye-kafka`,
      or any other connector value.
- [ ] No serializer/deserializer keys were written — the RabbitMQ connector has none; JSON conversion is
      automatic and the POJO consumer takes `JsonObject` + `.mapTo(...)`.
- [ ] `.queue.name` / `.exchange.name` written only when the name differs from the channel name; for
      pre-provisioned infrastructure both the name and `.queue.declare=false` / `.exchange.declare=false`
      are written.
- [ ] Every channel referenced by `@Incoming`/`@Outgoing`/`@Channel` has a matching
      `mp.messaging.<direction>.<channel>.connector=smallrye-rabbitmq` line.
- [ ] `rabbitmq-host` / `rabbitmq-port` / `rabbitmq-username` / `rabbitmq-password` are never written
      unprefixed (they disable RabbitMQ Dev Services); a real broker appears only under `%prod.`.
- [ ] Bean classes are `@ApplicationScoped`; `@Channel` fields carry `@Inject`; imports are Jakarta EE /
      Quarkus / MicroProfile Reactive Messaging only (never the pre-Jakarta namespace).
- [ ] Metadata classes are imported from `io.smallrye.reactive.messaging.rabbitmq.*`
      (`IncomingRabbitMQMetadata`, `OutgoingRabbitMQMetadata`) and
      `org.eclipse.microprofile.reactive.messaging.{Message,Metadata}` — not invented FQNs.
- [ ] Messaging code is Reactive Messaging only (`@Incoming`/`@Outgoing`/`@Channel`) — no listener or
      template types from other frameworks.
- [ ] `@Blocking` (io.smallrye.reactive.messaging.annotations.Blocking) is used only for blocking
      consumer handling the user asked for (e.g. synchronous DB calls).
- [ ] Keys, indentation, and import style match the project's existing files.
- [ ] No business logic was invented inside a consumer method body.