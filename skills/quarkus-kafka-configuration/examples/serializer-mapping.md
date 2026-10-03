# Serializer / deserializer mapping

Use this reference only after determining the payload type from a visible `@Incoming`, `@Outgoing`, or `@Channel` declaration, or from caller/source input for config-only work. Quarkus 3.20.3 serde autodetection requires a visible supported binding type and enabled `quarkus.messaging.kafka.serializer-autodetection.enabled`. If that evidence is absent, configure the serde explicitly from a verified type; ask if the type is unknown. The examples choose explicit serde configuration for POJOs as a policy, not because Quarkus can never autodetect them.

Verified against the Quarkus Kafka guide and Quarkus 3.20.3 serialization source (checked 2026-10-03). Do not extrapolate this class/default table to other versions without checking their guide/source.

## Type → (serializer, deserializer)

| Type | Serializer | Deserializer |
|---|---|---|
| `java.lang.String` | `org.apache.kafka.common.serialization.StringSerializer` | `org.apache.kafka.common.serialization.StringDeserializer` |
| `java.lang.Integer` | `org.apache.kafka.common.serialization.IntegerSerializer` | `org.apache.kafka.common.serialization.IntegerDeserializer` |
| `java.lang.Long` | `org.apache.kafka.common.serialization.LongSerializer` | `org.apache.kafka.common.serialization.LongDeserializer` |
| `java.lang.Double` | `org.apache.kafka.common.serialization.DoubleSerializer` | `org.apache.kafka.common.serialization.DoubleDeserializer` |
| `java.util.UUID` | `org.apache.kafka.common.serialization.UUIDSerializer` | `org.apache.kafka.common.serialization.UUIDDeserializer` |
| `java.lang.Void` (producer tombstone) | `org.apache.kafka.common.serialization.VoidSerializer` | — (do not infer a consumer autodetection handler) |
| Vert.x `JsonObject` / `JsonArray` | Quarkus autodetection when eligible, otherwise verify explicit serde | Quarkus autodetection when eligible, otherwise verify explicit serde |
| POJO — JSON-B flavour | `io.quarkus.kafka.client.serialization.JsonbSerializer` | concrete `io.quarkus.kafka.client.serialization.JsonbDeserializer<T>` subclass |
| POJO — Jackson flavour | `io.quarkus.kafka.client.serialization.ObjectMapperSerializer` | concrete `io.quarkus.kafka.client.serialization.ObjectMapperDeserializer<T>` subclass |

## Conditional serde selection

Omit `.value.serializer` / `.value.deserializer` (and `.key.*`) only when both conditions are confirmed:
1. An actual Java `@Outgoing`, `@Incoming`, or `@Channel Emitter<T>` declaration exposes the binding type.
2. `quarkus.messaging.kafka.serializer-autodetection.enabled` is enabled and the type is supported by the target Quarkus release.

For configuration-only work without a corresponding Java declaration, autodetection is not established: resolve the type from caller/project evidence, then add the appropriate explicit property. If the type is unknown, ask rather than assume `String`. `Void` is not in Quarkus 3.20.3's supported autodetection type list; its serializer is an explicit producer-side option, not an autodetection claim.

The POJO templates below intentionally show explicit JSON serde configuration. This is a configuration choice and does not claim auto-detection is impossible for POJOs in other qualifying setups.

## POJO deserializers

Jackson's `ObjectMapperDeserializer` template with `TypeReference` is used when the guide's configured POJO/generic shape calls for it. JSON-B concrete deserializers must pass a target type to the superclass; there is no no-argument constructor in Quarkus 3.20.3.

### JSON-B simple concrete class

```java
package ${packageName};

import io.quarkus.kafka.client.serialization.JsonbDeserializer;

public class ${ValueType}Deserializer extends JsonbDeserializer<${valueType}> {

    public ${ValueType}Deserializer() {
        super(${valueType}.class);
    }
}
```

Quarkus 3.20.3 `JsonbDeserializer` constructors accept `Class<T>` or `Type` (the latter also accepts a Jsonb instance). For generic collection payloads, use a `Type` value only when a concrete source-backed Type construction is available and verified; otherwise stop rather than substituting Jackson's `TypeReference` into JSON-B code. The checked source is [JsonbDeserializer.java, Quarkus 3.20.3](https://raw.githubusercontent.com/quarkusio/quarkus/3.20.3/extensions/kafka-client/runtime/src/main/java/io/quarkus/kafka/client/serialization/JsonbDeserializer.java).

### Jackson generic POJO example

```java
package ${packageName};

import io.quarkus.kafka.client.serialization.ObjectMapperDeserializer;
import com.fasterxml.jackson.core.type.TypeReference;

public class ${ValueType}Deserializer extends ObjectMapperDeserializer<${valueType}> {

    public ${ValueType}Deserializer() {
        super(new TypeReference<${valueType}>() {});
    }
}
```

Use the guide's concrete serializer/deserializer class for the selected JSON flavour. Do not mix JSON-B and Jackson deserializer constructors.

## Minimal channel blocks

### `.properties`

```properties
mp.messaging.incoming.${inChannel}.connector=smallrye-kafka
mp.messaging.outgoing.${outChannel}.connector=smallrye-kafka
```

Add topic only when it differs from channel name or was explicitly requested:

```properties
# OPTIONAL: only when topic differs from the channel name or caller explicitly selected it
mp.messaging.incoming.${inChannel}.topic=${inTopic}
mp.messaging.outgoing.${outChannel}.topic=${outTopic}
```

### YAML (`quarkus-config-yaml` present)

```yaml
mp:
  messaging:
    incoming:
      ${inChannel}:
        connector: smallrye-kafka
    outgoing:
      ${outChannel}:
        connector: smallrye-kafka
```

Add this topic fragment only when required by the rule above:

```yaml
# OPTIONAL: include only when topic differs from channel name or caller explicitly selected it
mp:
  messaging:
    incoming:
      ${inChannel}:
        topic: ${inTopic}
    outgoing:
      ${outChannel}:
        topic: ${outTopic}
```

## Explicit serde additions (conditional)

Include only when no eligible typed binding is visible or autodetection is disabled, and the payload type is known. These are optional additions, not part of every channel block.

### `.properties`

```properties
# OPTIONAL: incoming only, when explicit deserialization is required
mp.messaging.incoming.${inChannel}.value.deserializer=${valueDeserializer}
# OPTIONAL: outgoing only, when explicit serialization is required
mp.messaging.outgoing.${outChannel}.value.serializer=${valueSerializer}
```

### YAML (`quarkus-config-yaml` present)

```yaml
# OPTIONAL: incoming only, when explicit deserialization is required
mp:
  messaging:
    incoming:
      ${inChannel}:
        value:
          deserializer: ${valueDeserializer}
# OPTIONAL: outgoing only, when explicit serialization is required
    outgoing:
      ${outChannel}:
        value:
          serializer: ${valueSerializer}
```

### Keyed channels (only when a source/caller-backed `keyType` is set)

```properties
mp.messaging.outgoing.${outChannel}.key.serializer=${keySerializer}
mp.messaging.incoming.${inChannel}.key.deserializer=${keyDeserializer}
```

YAML equivalents follow the same condition; nest keys under each channel's `key.serializer` / `key.deserializer`.

## Other optional settings

### Consumer group (only when user selects a specific group)

```properties
mp.messaging.incoming.${inChannel}.group.id=${groupId}
```

Omitted `group.id` uses the connector default. The application name default is verified for the scoped Quarkus Kafka guide; do not write a group ID unless selected/needed.

### Production broker address (never unprefixed in shared config)

```properties
%prod.kafka.bootstrap.servers=${bootstrapServers}
```

An unprefixed broker address can disable Kafka Dev Services in dev/test. Keep production broker configuration under `%prod.` and redact credentials.

## Source

- [Quarkus 3.20.3 Kafka guide](https://github.com/quarkusio/quarkus/blob/3.20.3/docs/src/main/asciidoc/kafka.adoc), checked 2026-10-03.
- [Quarkus 3.20.3 JsonbDeserializer source](https://raw.githubusercontent.com/quarkusio/quarkus/3.20.3/extensions/kafka-client/runtime/src/main/java/io/quarkus/kafka/client/serialization/JsonbDeserializer.java), checked 2026-10-03.
