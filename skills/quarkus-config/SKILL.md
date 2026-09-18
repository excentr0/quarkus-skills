---
name: quarkus-config
description: >-
  Adds typed configuration to a Quarkus application: @ConfigMapping interfaces,
  one-off @ConfigProperty values, defaults, optional settings, and profile-specific
  values (%dev. / %test. / %prod.) in application.properties.
  Use this skill whenever settings need to be added or externalized — a new feature
  needs its own configuration, hardcoded values should move to config, or existing
  configuration style must be followed.
  Russian phrases also trigger this: "добавь конфигурацию", "вынеси настройки
  в конфигурацию", "добавь параметр в application.properties", "конфиг-маппинг",
  "профили конфигурации", "настрой параметры приложения".
---

# Preflight — Project detection (before step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP
server or IDE integration is required.

Detect the project shape from the build files and configuration:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`;
   Gradle: `id("io.quarkus")` plugin. Quarkus 3.x targets Jakarta EE (`jakarta.*`) — never `javax.*`.
3. **Config file and format** — detect `src/main/resources/application.properties` or
   `application.yaml`/`application.yml` and record the actual file. If YAML is present, verify that
   the `quarkus-config-yaml` extension is present in the Maven/Gradle build; if it is missing, **STOP**
   and explain that the format cannot be used safely yet. If both formats exist, identify the
   authoritative file from the project's existing configuration or ask before writing. Use properties
   syntax only for `.properties`; translate matching examples into nested YAML for `.yaml`/`.yml`.
4. **Existing config style** — grep `@ConfigMapping` and `@ConfigProperty` in `src/main/java`.
   Record: which style the project already uses, the package config classes live in (`config`,
   `configuration`, or a feature package), and whether nested groups / `@WithDefault` are used.
5. **Existing custom prefix** — scan non-`quarkus.*`/non-`mp.*` keys in the detected config file
   (e.g. `app.*`, `order.*`): the project's own namespace. A new feature should follow it.
6. **Profiles in use** — which of `%dev.`, `%test.`, `%prod.` prefixes already appear, and for what
   (datasource, security, messaging).

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and
tell the user this skill targets Quarkus projects.

---

# Typed Configuration

Adds configuration the Quarkus way: a `@ConfigMapping` interface for grouped settings, or a single
`@ConfigProperty` for one-off values — plus the matching `application.properties` block with
profile-specific values.

> **CRITICAL: Code and properties ONLY from examples/ files. If no matching example -- STOP and ask user.**
> **CRITICAL: Never invent config keys for platform features (quarkus.*, mp.*) — verify them in `docs/quarkus-facts.md` or the official guide; application-specific keys are the user's choice.**
> **CRITICAL: For questions with a fixed set of choices, prefer your harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`) > its analogue > plain text list. Plain numbered text lists are the last resort when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 1–4 may already be answered by the user's prompt and prior turns. Re-asking what was already said is the #1 reason this skill feels slow.

---

## Defaults

| Option | Default | Notes |
|--------|---------|-------|
| configStyle | `mapping-interface` | `@ConfigMapping` for grouped settings; `@ConfigProperty` only for a single one-off value (see [`references/injection.md`](references/injection.md)) |
| prefix | `${featureKebab}` | kebab-case of the feature name (`OrderService` → `order`); follow the project's existing custom prefix when one exists |
| interface name | `${Feature}Config` | in the config package, or the feature's package if there is no config package |
| defaults | `@WithDefault` where a sensible default exists | required settings stay non-Optional — a missing required property failing startup is intended behavior |
| optional settings | `Optional<T>` / `OptionalInt` | absent property is fine, code must handle empty |
| secrets | environment variable reference (`${ENV_VAR}`) | never literal credential values in `application.properties` |
| profiles | `%dev.` / `%test.` / `%prod.` only where a value actually differs | an unprefixed value applies to all profiles |

### Auto-detected (no questions)

| Option | Source |
|--------|--------|
| buildTool | build file (preflight) |
| configFile | detected `.properties`, `.yaml`, or `.yml` file (preflight) |
| configStyle of the project | `@ConfigMapping` / `@ConfigProperty` usage in `src/main/java` (preflight) |
| prefix / package | existing custom keys and config classes (preflight) |

**Smart defaults:** If the user says "use defaults", "default settings", or similar — skip every
question whose default is marked as recommended. Only ask what is truly unknown (typically the
feature name when it cannot be derived from the request).

**Smart answer recognition:** When the user provides a value instead of choosing from a numbered
list, accept it directly (e.g. "the prefix should be `billing`" IS the prefix — do not re-ask).
Never ask a question the user already answered, even implicitly.

---

## Decision-making principle — context first, then ask

1. **Derive from context** — the request names the settings, the project shows the style and the
   prefix. Most decisions (style, prefix, package, defaults) are settled by the preflight.
2. **Confirm from existing code** — if the project already has `@ConfigMapping` interfaces, follow
   their shape (package, prefix style, whether nested groups are used) instead of the defaults here.
3. **Ask only real forks** — batch them into one structured-question call (max 3–4 questions):
   e.g. the feature/prefix name when unknown, or whether a settings group belongs in one interface
   or a nested group. Mark the recommended option `(Recommended)` and put it first.

---

## Step 0 — Read the request

Tell the user: `Step 0/5: Reading the request...`

**Do NOT call any tools in this step.**

From the conversation, list the settings the request implies and classify each one:

- **Application settings** (the user's own namespace, e.g. `billing.retry-count`) — the skill decides
  names and shape.
- **Platform settings** (`quarkus.*`, `mp.*`, e.g. datasource, OIDC, messaging) — the key must come
  from the official documentation; do not guess it. Security keys are owned by the
  [`quarkus-security-configuration`](../quarkus-security-configuration/SKILL.md) skill, Kafka
  channels by [`quarkus-kafka-configuration`](../quarkus-kafka-configuration/SKILL.md).

Also fix: which component consumes the values (a service, a resource, a client) — that decides the
injection style in Step 3.

---

## Step 1 — Detect the project's config style

Tell the user: `Step 1/5: Detecting config style...`

From the preflight, score each convention (1–100) and use the project's own style when the score is
high:

| Convention | Default when absent |
|---|---|
| Grouped settings — `@ConfigMapping` interface vs `@ConfigProperty` fields | `@ConfigMapping` |
| Config package — `config` / `configuration` / feature package | config package if one exists, else the feature's package |
| Prefix style — existing custom prefix reused for a new feature | new kebab-case prefix for the feature |
| Defaults — `@WithDefault` on mapping methods | required settings have no default |
| Nested groups — nested interfaces for sub-namespaces | flat interface until a second level is needed |

If the project has no existing config code at all, use the defaults — do not ask.

---

## Step 2 — Choose the config style

Tell the user: `Step 2/5: Choosing the config style...`

Follow [`references/config-mapping.md`](references/config-mapping.md) for the decision rules:

- **Two or more related settings → `@ConfigMapping` interface** (recommended): one type-safe group,
  injected as a bean.
- **Exactly one one-off value → `@ConfigProperty`** on the consuming bean — see
  [`references/injection.md`](references/injection.md).
- **May-be-missing value → `Optional<T>`**; required value → plain type (startup fails when missing —
  that is the desired validation, see [`references/profiles.md`](references/profiles.md)).

Ask the user (one batched structured-question call) only when a real fork remains — typically the
feature's prefix/name, or a mapping-vs-property disagreement with an existing project convention.

---

## Step 3 — Generate config code and properties

Tell the user: `Step 3/5: Generating configuration...`

Write to the config file selected in preflight. Use the properties examples unchanged for
`application.properties`; for `application.yaml`/`application.yml`, translate each key into the
corresponding nested YAML structure. If the YAML extension or an unambiguous authoritative file is
missing, stop and explain instead of writing properties syntax into the wrong file.

Use the matching example files — never write config code from scratch:

| What | Example |
|---|---|
| Mapping interface (minimal / with defaults and optional) | [`examples/mapping-interface.md`](examples/mapping-interface.md) |
| `application.properties` block (values + profiles + secret reference) | [`examples/properties.md`](examples/properties.md) |
| One-off `@ConfigProperty` injection (field and constructor) | [`examples/config-property.md`](examples/config-property.md) |

Then wire the values into the consuming component:

- Mapping interface: inject it like any CDI bean (`@Inject ${Feature}Config config;` or constructor
  parameter — a single constructor needs no `@Inject`).
- `@ConfigProperty`: add the field or constructor parameter on the bean that uses the value — do not
  create a separate holder class for one value.

---

## Step 4 — Profiles and secrets

Tell the user: `Step 4/5: Applying profiles...`

Follow [`references/profiles.md`](references/profiles.md):

- An unprefixed key applies to **all** profiles — do not duplicate it under `%dev.`/`%test.`/`%prod.`.
- Add a profile prefix only where the value differs: typically `%prod.` for the real datasource and
  external URLs (so Dev Services keep working in dev/test), `%test.` for test-only overrides.
- **Secrets are environment variable references** (`${ENV_VAR}`), never literal values — including in
  `%prod.` blocks.
- Mention in the report which keys are profile-specific and which are shared. Report only key names,
  profiles, and status; never echo resolved secret values (use `[REDACTED]`).

---

## Step 5 — Verify the configuration is live

Tell the user: `Step 5/5: Verifying...`

Prove the values actually reach the application — pick what the project supports:

- **Tests** — run the narrowest matching test with the detected build tool: Maven
  `./mvnw test -Dtest='${TestClass}'` or Gradle `./gradlew test --tests '${TestClass}'`.
- **Dev mode** — start `./mvnw quarkus:dev` (Maven) or `./gradlew quarkusDev` (Gradle) and observe
  the value in the startup log or endpoint response; stop dev mode afterwards.
- **Negative check** — for a required (non-Optional, no-default) setting, removing it must fail
  startup with a configuration error. Do not invent a different failure message; quote what is observed.

Report only the key, profile, and verification status (`set`, `missing`, or `not checked`). Never output
resolved values; redact any secret as `[REDACTED]`. If verification was skipped, state the exact reason.
Never claim a value is live without having seen its status.

---

## Anti-hallucination checklist

- [ ] Every `quarkus.*` / `mp.*` key was taken from the official documentation or `docs/quarkus-facts.md` — not invented.
- [ ] Application-specific keys follow the project's existing prefix, or the user approved the new one.
- [ ] Config style (`@ConfigMapping` vs `@ConfigProperty`) matches the project's convention or the documented default.
- [ ] `@WithDefault` / `Optional` usage matches whether the setting may legitimately be absent.
- [ ] No literal secret values anywhere — secrets are environment variable references.
- [ ] Unprefixed keys are not duplicated under all three profile prefixes.
- [ ] The verification step quotes an observed value (or states explicitly why it was skipped).
