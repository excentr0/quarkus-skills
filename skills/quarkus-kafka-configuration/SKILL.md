---
name: quarkus-kafka-configuration
description: >
  Configures Kafka messaging in a Quarkus application: channel configuration in
  application.properties and, when needed, generated Kafka-specific
  Reactive Messaging beans (`@Incoming` / `@Outgoing` / `@Channel`). Use this skill when Kafka
  configuration needs to be created or extended, either standalone or as part of a larger task
  (e.g. before adding a Kafka `Emitter` producer or consumer).
  Triggers on: "configure kafka", "add kafka", "kafka channel", "kafka topic",
  "produce to kafka", "consume from kafka", "smallrye-kafka".
  Russian phrases also trigger this: "настрой kafka", "добавь kafka", "кафка",
  "канал kafka", "отправка сообщений в kafka", "чтение сообщений из kafka".
---

# Kafka Configuration

Wires the Quarkus Kafka extension (`quarkus-messaging-kafka`) through channels in
`application.properties` and, optionally, generates Reactive Messaging beans.
Ensures the extension dependency is on the classpath.

> **CRITICAL: Code ONLY from `examples/` files. If no matching example — STOP and ask user.**
> **CRITICAL: For questions with a fixed set of choices, use your harness's structured-question tool
> (e.g. `AskUserQuestion` / `ask_user_question`); fall back to a plain numbered list.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 2–3
> may already be answered by the user's prompt and prior turns.
> **CRITICAL: Broker disambiguation.** A request that only says Reactive Messaging, Emitter,
> `@Incoming`, `@Outgoing`, or message broker is not enough to choose Kafka. Ask one clarifying
> question to identify the broker before selecting this skill; never choose Kafka or RabbitMQ
> arbitrarily.

---

## Preflight — Project detection (before Step 0)

Harness-agnostic: file tools and shell commands only — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence** — Maven: `io.quarkus.platform:quarkus-bom` in `pom.xml`; Gradle: plugin `id("io.quarkus")`.
   If absent — stop: this skill targets Quarkus projects.
3. **Kafka extension** — `io.quarkus:quarkus-messaging-kafka` in the dependencies. Present or not — Step 4b fixes it.
4. **Existing wiring** — grep `src/main` for `mp.messaging.` (channel config) and
   `org.eclipse.microprofile.reactive.messaging` (`@Incoming`/`@Outgoing`/`@Channel`).
5. **Config files** — detect `src/main/resources/application.properties` or `.yaml`/`.yml` only when
   `quarkus-config-yaml` is present. If YAML is selected without that extension or the native YAML
   structure cannot be handled safely, stop instead of writing properties syntax into it.

---

## Two paths (Step 3 picks)

- **Path A — `path = properties`** (default when messaging beans already exist). Only channel
  configuration is written: `mp.messaging.<incoming|outgoing>.<channel>.connector=smallrye-kafka`, plus
  `.topic`, serializer/deserializer, `group.id`. No Java is generated. The connector maps each **channel**
  to a Kafka **topic**; `@Incoming`/`@Outgoing`/`@Channel` beans connect to channels by name.
- **Path B — `path = beans`**. Channel configuration **plus** a generated `@ApplicationScoped` messaging
  bean: a consumer method (`@Incoming`), a producer (`@Channel Emitter<T>`), or both. Serializer settings
  always stay in `application.properties` — the connector creates and configures the Kafka client, so there is
  no factory or template bean to declare. A programmatic channel-config escape hatch exists
  (`@Produces @Identifier("<channel>") Map<String, Object>`) — see
  [`references/channel-config-reference.md`](references/channel-config-reference.md); use it only when the
  user asks for programmatic config.

## Defaults

| Option | Default | Always ask? |
|---|---|---|
| `path` | `properties` when `@Incoming`/`@Outgoing`/`@Channel` beans already exist, else `beans` | YES — choose first |
| `valueType` (producer, i.e. outgoing) | `java.lang.String` | YES — only for Path B |
| `valueType` (consumer, i.e. incoming) | symmetric with producer | NO — only for Path B when asymmetric |
| `keyType` | none (value-only messages) | NO — only when the user mentions keys |
| `channelName` | `${typeKebab}-in` / `${typeKebab}-out` — `${typeKebab}` = kebab-case value type simple name (`OrderEvent` → `order-event`) | NO |
| `topic` | channel name (connector default: if `topic` is not set, the channel name is used) | NO |
| `group.id` | unset → `quarkus.application.name` (connector default) | YES — one question, "keep default" recommended |
| `bootstrap.servers` | connector default `localhost:9092` (alias `kafka.bootstrap.servers`) | NO — write only under `%prod.` when the user gives a real broker |
| `className` | `${ValueType}Messaging` (both), `${ValueType}Consumer` / `${ValueType}Producer` (single) | NO (Path B only) |
| `packageName` | main package (package of existing messaging beans, else root package) | NO (Path B only) |
| `language` | Java | NO — this repo's skills are Java-first |

**Smart defaults.** If the user says "use defaults" / "all defaults" / "minimal configuration" → skip every
`Always ask = NO` question and choose the path first. Ask value types only if the selected path is Path B;
otherwise ask no bean-type questions. Ask anything else the user mentioned non-default.

**Smart answer recognition.** When the user provides a value directly ("publish `OrderEvent`", "consume
`PaymentEvent`", "group `orders`"), accept it without asking again. Several answers in one message → accept all.

**Batch questions.** Group related questions into ONE structured-question call (up to 4–5 questions).
Recommended option first, marked `(Recommended)`.

## Decision-making — context first, then ask

For every input: try to derive it from the build file, `application.properties`, existing messaging beans,
prior turns, and the user's prompt. Only ask when context yields no clear default.

1. **Context unambiguous → decide silently.** `language`, `packageName`, `bootstrap.servers` handling,
   channel names derived from the type, single `application.properties` file.
2. **Strong signal → one-line confirmation.** State the decision and alternatives; the user can accept
   silently. Used for: reusing an existing messaging bean class, topic names defaulting to channel names.
3. **No clear default → structured question** with the recommended option first. Choose `path` first;
   only for Path B ask `valueType` and then `group.id` (keep-default option first).
4. **Empty for a critical input → ask plainly.** Path B producer `valueType`; the handling behavior for a
   generated consumer (see Step 5).

## Step 0 — Conversation context (mental, no tool calls)

Tell the user: `Step 0/6: Analyzing conversation context...`

Re-read the user's prompt and prior turns; tick off everything already stated:

| Input | Signal in the prompt |
|---|---|
| `valueType` (outgoing) | "publish `X`", "send `X`", "emit `X`", "produce `X`" |
| `valueType` (incoming) | "consume `X`", "read `X`", "@Incoming receives `X`" |
| `keyType` | "keyed by `Y`", "key as `Y`", "with key `Y`" |
| `channelName` / `topic` | "channel `X`", "topic `X`", "from topic `X`" |
| `group.id` | "consumer group `X`", "group id …" |
| `path` | "just add config", "only properties", "create a consumer/producer", "add an Emitter" |
| `className` / `packageName` | "name it `FooMessaging`", "in package …" |
| smart defaults | "use defaults", "all defaults" → ask only `valueType` + `path` |

Tick → skip the corresponding question. Do not announce Step 0.

## Step 1 — Gather context (file reads + greps, no MCP)

Tell the user: `Step 1/6: Gathering context...`

| Source | Variables extracted |
|---|---|
| `pom.xml` / `build.gradle(.kts)` | `buildFile`, `buildTool`, `quarkusVersion`, `presentDeps`, `mainPackage` (from source tree), module list |
| detected config file (`.properties` or YAML) | `existingProps` — `mp.messaging.*`, `kafka.bootstrap.servers`, and `%dev.`/`%prod.` keys; read the selected format and redact passwords, tokens, auth headers, and credential-bearing URLs before retaining or reporting values |
| grep `mp\.messaging\.` under `src/main` | `existingChannels` — channel names already configured, with direction |
| grep `@Incoming\|@Outgoing\|@Channel` under `src/main/java` | `existingMessagingBeans` — class FQNs + file paths + the channel names each one uses |

**Multi-module projects.** If the build has several modules, score each by (+1) `quarkus-messaging-kafka`
in its deps, (+1) any `mp.messaging.*` key in its property files. Exactly one module with score ≥ 1 →
select silently. Two or more, or all-zero → ask which module, then re-gather for that module.

**Derived:**
- `kafkaExtensionPresent` — `presentDeps` contains `io.quarkus:quarkus-messaging-kafka`. Skip Step 4b if true.
- `singleConfigFile` — exactly one detected application config file (`.properties`/`.yaml`/`.yml`). Skip the config-file question if true.
- `existingBootstrapServers` — value of `kafka.bootstrap.servers` or `mp.messaging.<dir>.<ch>.bootstrap.servers` if present, else `null`; redact credentials if an endpoint contains them.
- `existingGroupId` — value of any `mp.messaging.incoming.<ch>.group.id` if present, else `null`.
- `existingBeanClasses` — from `existingMessagingBeans`; carries FQN, file path, declared channels. Used in Step 3.
- `orphanChannels` — channels referenced in code (`@Incoming`/`@Outgoing`/`@Channel`) but absent from
  `existingChannels` → they are missing config; this skill's job is to add it.

## Step 2 — All questions in ONE batch

Tell the user: `Step 2/6: Asking all questions...`

Ask the path question first, then ask only the questions that apply to that path. Pre-fill from context
and skip already-answered:

1. **Where to put the wiring?** — detected config file only (Path A) / detected config file + messaging bean
   (Path B, Recommended when no `@Incoming`/`@Outgoing`/`@Channel` bean exists yet)

If Path A is selected, skip producer/consumer value types and bean-target questions. If Path B is selected, ask:

2. **Producer value type?** — options: `java.lang.String` (Recommended), `java.lang.Integer`,
   `java.lang.Long`, `java.util.UUID`, `Custom (specify FQN)`
3. **Consumer value type?** — same options; pre-select the producer answer (symmetric) unless the user
   indicated otherwise
4. **Consumer group id?** — `keep connector default (quarkus.application.name)` (Recommended) /
   `specify` (plain value). Pre-fill silently if `existingGroupId` is non-null.
5. **Channel and topic names?** — only when a name cannot be derived: default channel is
   `${typeKebab}-in` / `${typeKebab}-out`, default topic = channel name. Skip when the user named them.

If the user says "use defaults" — choose the path first, skip type questions for Path A, and for Path B
use `java.lang.String` after confirming the producer value type.

## Step 3 — Bean target (Path B only)

Tell the user: `Step 3/6: Picking bean target...`

If `existingBeanClasses` is non-empty, apply Decision principle 2 (one-line confirmation), naming the class:

> Project already has messaging code in `${class.fqn}`. Add the new consumer/producer there? (Yes/No)

- **Yes** → `beanTarget = existing`. Reuse the class's `packageName`, `className`, and file path; Step 5
  appends the method/field with the available file-editing tool instead of creating a file.
- **No (or no existing beans)** → `beanTarget = new`:
  - `className` — default `${ValueType}Messaging` for both directions, `${ValueType}Consumer` for a consumer
    only, `${ValueType}Producer` for a producer only. On file collision append a numeric suffix.
  - `packageName` — default = package of existing messaging beans; else the root package; ask only if the
    project has several candidate packages.

Usually answered silently from context.

## Step 4 — Write channel configuration + add dependency

Tell the user: `Step 4/6: Writing channel configuration...`

### 4a. Channel configuration

Always write a channel block per direction that the task needs. Substitute `connector` and `topic` always;
add serializer keys per [`examples/serializer-mapping.md`](examples/serializer-mapping.md).

Incoming (consumer):

```properties
mp.messaging.incoming.${inChannel}.connector=smallrye-kafka
mp.messaging.incoming.${inChannel}.topic=${inTopic}
mp.messaging.incoming.${inChannel}.value.deserializer=${valueDeserializer}
```

Outgoing (producer):

```properties
mp.messaging.outgoing.${outChannel}.connector=smallrye-kafka
mp.messaging.outgoing.${outChannel}.topic=${outTopic}
mp.messaging.outgoing.${outChannel}.value.serializer=${valueSerializer}
```

Rules (all verified — see the checklist):

- **Built-in types** (`String`, `Integer`, `Long`, `Double`, `UUID`, `Void`, Vert.x `JsonObject`): omit the
  serializer/deserializer keys — Quarkus autodetects them from `@Incoming`/`@Outgoing`/`@Channel` declarations.
  Add them explicitly only when the user asks for explicitness.
- **POJO/custom types**: never omit — write the deserializer key for the consumer side and the serializer key
  for the producer side (rows for POJOs in `examples/serializer-mapping.md`).
- `.topic=` is required only when the topic differs from the channel name (the connector defaults topic to the
  channel name). Write it anyway when the user named a topic explicitly.
- `.group.id=` — write only when the user chose `specify`, or when the project has more than one incoming
  channel and the default (`quarkus.application.name`, shared by all consumers) is not intended.
- **Never write unprefixed `bootstrap.servers`/`kafka.bootstrap.servers`** — it disables Dev Services for Kafka
  in dev/test. A real broker address goes under the production profile:
  `%prod.kafka.bootstrap.servers=${bootstrapServers}`. Reuse an existing non-secret endpoint only when it is
already an environment-variable reference or an explicitly non-secret local endpoint; never copy a redacted credential.
- **Keys**: `mp.messaging.outgoing.${outChannel}.key.serializer=${keySerializer}` and
  `mp.messaging.incoming.${inChannel}.key.deserializer=${keyDeserializer}` only when `keyType` is set.
- Overwrite existing keys in place; never delete unrelated keys or duplicate a key.
- YAML flavour (`application.yaml` when `quarkus-config-yaml` is present): nest the same keys under
  `mp.messaging.incoming.<channel>` — the `.yaml` equivalents are in
  [`examples/serializer-mapping.md`](examples/serializer-mapping.md).
- Profile overrides (`%dev.`, `%test.`) are allowed for topic names/offsets; keep broker addresses out of the
  default profile (see above).

### 4b. Extension dependency

If `kafkaExtensionPresent = true`, skip. Otherwise add `io.quarkus:quarkus-messaging-kafka`:

```bash
./mvnw quarkus:add-extension -Dextensions="quarkus-messaging-kafka"
```

or add the extension to the detected build file directly (Gradle: `implementation("io.quarkus:quarkus-messaging-kafka")`),
matching the project's existing dependency style (BOM-managed, no `<version>`). Do not pass ordinary
non-Quarkus dependencies to the extension command.

## Step 5 — Generate messaging beans (Path B only)

Tell the user: `Step 5/6: Generating messaging beans...`

1. Pick the example per direction:
   - consumer → [`examples/consumer-bean.md`](examples/consumer-bean.md)
   - producer → [`examples/producer-bean.md`](examples/producer-bean.md)
   - both → both files; put both beans in the single `${className}` class.
2. Substitute the variables listed in the template (`${packageName}`, `${className}`, channel names, types,
   keyed variant only when `keyType` is set).
3. **Handling body is business logic.** Fill the consumer method body only from the user's stated task (e.g.
   persist a Panache entity, call a service, forward to another channel). If the task does not specify handling
   — keep the single comment line from the example and say so in the report. Never invent business logic.
4. Detect indentation: `.editorconfig` → sample an existing source file → fallback 4 spaces.
5. FQN handling: emit one `import` per unique FQN used; skip `java.lang` and same-package classes; keep the
   project's import grouping (third-party block, then `java.*`).
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
- Effective defaults stated: topic = channel name (when `.topic` was omitted); `group.id` =
  `quarkus.application.name` (when omitted).
- How to try it: `./mvnw quarkus:dev` (Maven) or `./gradlew quarkusDev` (Gradle) — Dev Services starts
  a Kafka broker automatically in dev/test because no `bootstrap.servers` is configured (say explicitly if
  that is not the case, e.g. a `%prod.` address or an existing broker config disables it).
- If the consumer body was left as a comment stub — say so and ask what the handling should be.
- `orphanChannels` that remain unconfigured, if any.

## Anti-hallucination checklist

- [ ] `quarkus-messaging-kafka` is present in the build file (added if it was missing); no other messaging
      artifact was invented.
- [ ] (De)serializer FQNs come from `examples/serializer-mapping.md` rows matching the actual types — not from memory.
- [ ] Built-in types rely on autodetection; every POJO/custom type has an explicit serializer or deserializer key.
- [ ] POJO deserializers are concrete subclasses (`JsonbDeserializer` / `ObjectMapperDeserializer` subclasses) —
      the generic deserializer class is never configured directly.
- [ ] Every channel referenced by `@Incoming`/`@Outgoing`/`@Channel` has a matching
      `mp.messaging.<direction>.<channel>.connector=smallrye-kafka` line.
- [ ] `group.id` is written only for incoming channels, and the default (`quarkus.application.name`) is stated
      when omitted.
- [ ] `bootstrap.servers` / `kafka.bootstrap.servers` is never written unprefixed (it disables Kafka Dev
      Services); a real address appears only under `%prod.`.
- [ ] Bean classes are `@ApplicationScoped`; `@Channel` fields carry `@Inject`; imports are Jakarta EE /
      Quarkus only (never the pre-Jakarta namespace).
- [ ] Messaging code is Reactive Messaging only (`@Incoming`/`@Outgoing`/`@Channel`) — no listener or
      template types from other frameworks.
- [ ] Keys, indentation, and import style match the project's existing files.
- [ ] No business logic was invented inside a consumer method body.