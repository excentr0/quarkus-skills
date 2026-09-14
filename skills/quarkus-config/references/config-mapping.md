# Config mapping interfaces

## 1. When to use a mapping interface

Use `@ConfigMapping` for **two or more related settings** that are read as a group (a feature's
settings, a client's connection settings, limits, timeouts). For a single one-off value prefer
`@ConfigProperty` — see [`injection.md`](injection.md).

A mapping interface is type-safe, documented by its own shape, and injected like any CDI bean.
The recommended alternative to scattered `@ConfigProperty` fields.

## 2. Prefix and keys

`@ConfigMapping(prefix = "server")` maps method names to properties under that prefix:

```java
@ConfigMapping(prefix = "server")
public interface ServerConfig {

    String host();      // -> server.host

    int port();         // -> server.port
}
```

```properties
server.host=localhost
server.port=8080
```

- The prefix comes from the feature name (kebab-case), or from the project's existing custom prefix.
- Method name = the rest of the key (`port` → `server.port`). For multi-word method names, write the
  property key explicitly in the properties file — do not rely on a guessed name transformation.
- Never invent a `quarkus.*` prefix for application settings — `quarkus.*` and `mp.*` are reserved
  for platform configuration.

## 3. Nested groups

Sub-namespaces are nested interfaces — the **method name** that returns the nested interface becomes
the next key segment (the interface's own name does not affect the key):

```java
@ConfigMapping(prefix = "server")
public interface ServerConfig {

    String host();

    int port();

    Log log();

    interface Log {
        boolean enabled();   // -> server.log.enabled

        String suffix();     // -> server.log.suffix
    }
}
```

```properties
server.log.enabled=true
server.log.suffix=.log
```

Use a nested group when a feature group outgrows ~5 flat settings or has an obvious sub-topic
(logging under `server.log.*`). Do not nest preemptively.

## 4. Defaults and renames

```java
@ConfigMapping(prefix = "${prefix}")
public interface ${Feature}Config {

    @WithDefault("8080")
    int port();

    @WithDefault("3")
    int retryCount();

    @WithName("optional.int")
    OptionalInt optionalInt();
}
```

- `@WithDefault` prevents a startup error when the property is absent — use it only where a sensible
  default genuinely exists.
- `@WithName` decouples the property key from the method name — use it when the key must differ.

## 5. Optional values

- `Optional<String>`, `OptionalInt`, etc. — the property may be absent; the consumer must handle the
  empty case.
- Everything that is **not** Optional and has no `@WithDefault` is required: a missing property fails
  startup (`NoSuchElementException` → `ConfigurationException`). That is intended validation — do not
  add a default just to silence it unless the value really is optional.

## 6. Lists

`List<String>` (and other element types) map from comma-separated values:

```properties
${prefix}.allowed-hosts=alpha.example.com,beta.example.com
```

## 7. Environment variables override properties

Environment variables take precedence over `application.properties`; the mapping is mechanical:
`server.host` ← `SERVER_HOST`, `${prefix}.${fieldName}` ← uppercased with dots replaced by
underscores. That is why secrets should be injected as environment variables, never committed.

## 8. Where the interface lives

- In the project's config package (`config` / `configuration`) when one exists — follow it.
- Otherwise in the feature's package (next to the service that consumes the settings).
- One interface per feature group; do not build a god-config interface for the whole application.

## 9. Missing property behavior (verification lever)

Startup validation is a feature: a required setting that is absent stops the application with a
configuration error. Use that in the skill's verification step as the negative check.

## 10. Common mistakes

- Making everything `Optional` (or giving everything a default) — required settings lose their
  startup validation.
- Duplicating keys across `%dev.`/`%test.`/`%prod.` when the unprefixed value already applies to all.
- Inventing `quarkus.*` keys for application-specific settings.
- A mapping interface with a single method — a `@ConfigProperty` on the consumer is simpler.
- Prefix colliding with an existing feature's prefix.
