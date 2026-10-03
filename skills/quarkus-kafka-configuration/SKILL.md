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

Before rejecting the project or selecting a command, identify the target module. Inspect its build file plus root/parent build configuration for inherited Quarkus BOM/plugin, dependency management, and version properties/catalogs; use the target Maven module's effective POM when inheritance remains unclear. Prefer the project root wrapper with module selection (`-pl`/`-am` for Maven, `:module:task` for Gradle). If the wrapper is absent, check installed `mvn`/`gradle` and its version; if no usable tool is available, report a blocker/NOT RUN rather than calling the project invalid.


Harness-agnostic: file tools and shell commands only — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence** — Maven: `io.quarkus.platform:quarkus-bom` in `pom.xml`; Gradle: plugin `id("io.quarkus")`.
   If absent — stop: this skill targets Quarkus projects.
3. **Kafka extension** — `io.quarkus:quarkus-messaging-kafka` in the dependencies. Present or not — Step 4b fixes it.
4. **Existing wiring** — grep `src/main` for `mp.messaging.` (channel config) and actual Java
   `@Incoming`/`@Outgoing`/`@Channel` declarations. Serializer autodetection requires a visible typed
   declaration with a supported payload type and enabled `quarkus.messaging.kafka.serializer-autodetection.enabled`;
   config-only work cannot infer autodetection from a channel property.
5. **Config files** — detect `src/main/resources/application.properties` or `.yaml`/`.yml` only when
   `quarkus-config-yaml` is present. If YAML is selected without that extension or the native YAML
   structure cannot be handled safely, stop instead of writing properties syntax into it.

---

## Two paths (Step 3 picks)

- **Path A — `path = properties`** (default when messaging beans already exist). Write base channel
  configuration (`connector`, and `topic` only when needed); add serializer/deserializer properties only
  when the conditional rules below require them. No Java is generated. The connector maps each **channel**
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

**Smart defaults.** If the user says "use defaults" / "all defaults" / "minimal configuration", choose the path first and skip resolved choices. Ask for value type in Path A only when no typed Java binding/caller input exists and explicit serde config is required; Path B asks only unresolved type inputs. Never let "defaults" imply a hidden payload type.

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
3. **No clear default → structured question** with the recommended option first. Choose `path` first; ask for value type whenever required by the selected path and not established by source/caller. Ask `group.id` only when its default is unsuitable.
4. **Empty for a critical input → ask plainly.** Path B producer `valueType`; the handling behavior for a
   generated consumer (see Step 5).

## Step 0 — Conversation context (mental, no tool calls)


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
| smart defaults | "use defaults", "all defaults" → choose path and derive types; ask only unresolved explicit-serde/bean types |

Tick → skip the corresponding question. Do not announce Step 0.

## Step 1 — Gather context (file reads + greps, no MCP)


| Source | Variables extracted |
|---|---|
| `pom.xml` / `build.gradle(.kts)` | `buildFile`, `buildTool`, `quarkusVersion`, `presentDeps`, `mainPackage` (from source tree), module list |
| detected config file (`.properties` or YAML) | `existingProps` — `mp.messaging.*`, `kafka.bootstrap.servers`, `quarkus.messaging.kafka.serializer-autodetection.enabled`, and `%dev.`/`%prod.` keys; read the selected format and redact passwords, tokens, auth headers, and credential-bearing URLs before retaining or reporting values |
| grep `mp\.messaging\.` under `src/main` | `existingChannels` — channel names already configured, with direction |
| grep `@Incoming\|@Outgoing\|@Channel` under `src/main/java` | `existingMessagingBeans` — class FQNs + file paths + the channel names each one uses |

**Multi-module projects.** If the build has several modules, score each by (+1) `quarkus-messaging-kafka`
in its deps, (+1) any `mp.messaging.*` key in its property files. Exactly one module with score ≥ 1 →
select silently. Two or more, or all-zero → ask which module, then re-gather for that module.

**Derived:**
- `kafkaExtensionPresent` — `presentDeps` contains `io.quarkus:quarkus-messaging-kafka`. Skip Step 4b if true.
- `singleConfigFile` — exactly one detected application config file (`.properties`/`.yaml`/`.yml`). Skip the config-file question if true.
- `serdeAutodetectionEnabled` — resolved from `quarkus.messaging.kafka.serializer-autodetection.enabled`; usable only when enabled and a supported payload type is visible in an actual Java binding.
- `existingBootstrapServers` — value of `kafka.bootstrap.servers` or `mp.messaging.<dir>.<ch>.bootstrap.servers` if present, else `null`; redact credentials if an endpoint contains them.
- `existingGroupId` — value of any `mp.messaging.incoming.<ch>.group.id` if present, else `null`.
- `existingBeanClasses` — from `existingMessagingBeans`; carries FQN, file path, declared channels. Used in Step 3.
- `orphanChannels` — channels referenced in code (`@Incoming`/`@Outgoing`/`@Channel`) but absent from
  `existingChannels` → they are missing config; this skill's job is to add it.

## Step 2 — All questions in ONE batch


Ask the path question first, then ask only the questions that apply to that path. Pre-fill from context
and skip already-answered:

1. **Where to put the wiring?** — detected config file only (Path A) / detected config file + messaging bean
   (Path B, Recommended when no `@Incoming`/`@Outgoing`/`@Channel` bean exists yet)

If Path A is selected, skip bean-target questions. Derive serde type from a visible typed Java binding or caller input; if no declaration exists and explicit serde config is needed, ask for the relevant incoming/outgoing type. If Path B is selected, ask:

2. **Producer value type?** — options: `java.lang.String` (Recommended), `java.lang.Integer`,
   `java.lang.Long`, `java.util.UUID`, `Custom (specify FQN)`
3. **Consumer value type?** — same options; pre-select the producer answer (symmetric) unless the user
   indicated otherwise
4. **Consumer group id?** — `keep connector default (quarkus.application.name)` (Recommended) /
   `specify` (plain value). Pre-fill silently if `existingGroupId` is non-null.
5. **Channel and topic names?** — only when a name cannot be derived: default channel is
   `${typeKebab}-in` / `${typeKebab}-out`, default topic = channel name. Skip when the user named them.

If the user says "use defaults", choose the path first. Path A still needs a source/caller-derived type when no typed binding is visible and explicit serde settings are needed; do not silently assume String. For Path B, derive type from visible declarations or ask when unresolved.

## Step 3 — Bean target (Path B only)


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


### 4a. Channel configuration

Always write a channel block per direction that the task needs. Substitute `connector` and `topic` always;
add serializer keys per [`examples/serializer-mapping.md`](examples/serializer-mapping.md).

Incoming (consumer, minimal base block):

```properties
mp.messaging.incoming.${inChannel}.connector=smallrye-kafka
```

Outgoing (producer, minimal base block):

```properties
mp.messaging.outgoing.${outChannel}.connector=smallrye-kafka
```

Add `.topic=${inTopic}` / `.topic=${outTopic}` only when the topic is explicitly chosen or differs from the channel name. Add serde keys only under the conditions in the serializer-mapping reference below.

Rules (all verified — see the checklist):

- **Typed declarations present:** omit serde properties only when the actual declaration exposes a supported type AND serializer autodetection is enabled. Never infer typed declarations from config alone. `Void` is not in the supported autodetection list.
- **Config-only/no visible typed declaration:** configure serde explicitly from a type supplied by the caller or verified elsewhere in project sources; if the payload type is unknown, ask. For supported built-in types explicit serializer/deserializer classes are in the mapping table.
- **POJO/custom types:** the templates choose explicit serde classes as this skill's policy; this is not a claim that Quarkus can never autodetect them. JSON-B custom deserialization requires a concrete typed subclass; use only the verified supported forms.
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

## Portable resources and sibling handoffs

This skill's relative `references/` and `examples/` are bundled with its directory. Repository-level `docs/quarkus-facts.md` is optional when the skill is installed alone; if absent, verify version-sensitive claims against official versioned documentation/source or the actual project dependencies. Before a sibling-skill handoff, check whether that sibling is available. If missing, say so and apply equivalent local instructions only when the complete relevant example is available; never pretend to read a missing file. Skill activation/handoff alone does not authorize a child agent; delegate mechanically only when caller/operator permission and environment support are both present.

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