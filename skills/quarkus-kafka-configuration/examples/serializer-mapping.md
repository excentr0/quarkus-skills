# Serializer / deserializer mapping

Drives Step 4a (channel configuration) of [`../SKILL.md`](../SKILL.md). One lookup per type actually used by
the task: `valueType`/`keyType` on the outgoing side, `valueType`/`keyType` on the incoming side. Each type
resolves against the same table.

Verified against the Quarkus Kafka guide (quarkus.io/guides/kafka, Quarkus 3.x):
class names below are real classes shipped by `org.apache.kafka:kafka-clients` (built-in types) or by
`quarkus-messaging-kafka` itself (JSON variants).

## Type → (serializer, deserializer)

| Type | Serializer | Deserializer |
|---|---|---|
| `java.lang.String` | `org.apache.kafka.common.serialization.StringSerializer` | `org.apache.kafka.common.serialization.StringDeserializer` |
| `java.lang.Integer` | `org.apache.kafka.common.serialization.IntegerSerializer` | `org.apache.kafka.common.serialization.IntegerDeserializer` |
| `java.lang.Long` | `org.apache.kafka.common.serialization.LongSerializer` | `org.apache.kafka.common.serialization.LongDeserializer` |
| `java.lang.Double` | `org.apache.kafka.common.serialization.DoubleSerializer` | `org.apache.kafka.common.serialization.DoubleDeserializer` |
| `java.util.UUID` | `org.apache.kafka.common.serialization.UUIDSerializer` | `org.apache.kafka.common.serialization.UUIDDeserializer` |
| `java.lang.Void` (tombstone) | `org.apache.kafka.common.serialization.VoidSerializer` | — |
| POJO — JSON-B flavour | `io.quarkus.kafka.client.serialization.JsonbSerializer` | concrete subclass of `io.quarkus.kafka.client.serialization.JsonbDeserializer<${valueType}>` |
| POJO — Jackson flavour | `io.quarkus.kafka.client.serialization.ObjectMapperSerializer` | concrete subclass of `io.quarkus.kafka.client.serialization.ObjectMapperDeserializer<${valueType}>` |

## Autodetection — when the keys can be omitted

Quarkus autodetects serializer and deserializer classes from the declarations it can see (`@Incoming` method
signature, `@Outgoing` return type, `@Channel Emitter<T>` generic type) for built-in types and for Vert.x
`JsonObject`/`JsonArray`. Consequences for this skill:

- **Built-in types** (first six rows): omit `.value.serializer` / `.value.deserializer` / `.key.*` — the
  connector picks the `org.apache.kafka.common.serialization.*` counterpart. The incoming connector also
  defaults `key.deserializer` to `StringDeserializer` when the key side is not configured at all.
- **POJO/custom types**: never rely on autodetection — write the explicit keys. Deserialization additionally
  needs a concrete subclass so the target type is known at runtime (next section).

## POJO deserializers must be concrete subclasses

Both JSON flavours need a subclass because the generic deserializer cannot infer the target type from a bare
class name:

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

JSON-B flavour is analogous: extend `JsonbDeserializer<${valueType}>` (a no-arg constructor suffices; add a
`TypeReference` constructor only if collections are involved). Serializers (`JsonbSerializer`,
`ObjectMapperSerializer`) can be referenced directly — no subclass needed.

## Jackson flavour: custom `ObjectMapper`

`ObjectMapperSerializer`/`ObjectMapperDeserializer` use the Quarkus-managed `ObjectMapper`. To supply a custom
one, produce it as a CDI bean with the `@Identifier("kafka")` qualifier:

```java
@Singleton
public class ObjectMapperProducer {

    @Produces
    @Identifier("kafka")
    ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
```

Without that producer, the default Quarkus `ObjectMapper` (including all `ObjectMapperCustomizer` beans) is used.

## Property block templates

### Path A — config only (`.properties`)

```properties
mp.messaging.incoming.${inChannel}.connector=smallrye-kafka
mp.messaging.incoming.${inChannel}.topic=${inTopic}
mp.messaging.incoming.${inChannel}.value.deserializer=${valueDeserializer}
mp.messaging.outgoing.${outChannel}.connector=smallrye-kafka
mp.messaging.outgoing.${outChannel}.topic=${outTopic}
mp.messaging.outgoing.${outChannel}.value.serializer=${valueSerializer}
```

### Path A — config only (`.yaml`, with `quarkus-config-yaml`)

```yaml
mp:
  messaging:
    incoming:
      ${inChannel}:
        connector: smallrye-kafka
        topic: ${inTopic}
        value:
          deserializer: ${valueDeserializer}
    outgoing:
      ${outChannel}:
        connector: smallrye-kafka
        topic: ${outTopic}
        value:
          serializer: ${valueSerializer}
```

### Keyed channels (only when `keyType` is set)

```properties
mp.messaging.outgoing.${outChannel}.key.serializer=${keySerializer}
mp.messaging.incoming.${inChannel}.key.deserializer=${keyDeserializer}
```

### Consumer group (only when the user chose `specify`)

```properties
mp.messaging.incoming.${inChannel}.group.id=${groupId}
```

Omitted `group.id` means the connector default: `quarkus.application.name`.

### Production broker address (never unprefixed)

```properties
%prod.kafka.bootstrap.servers=${bootstrapServers}
```

An unprefixed `kafka.bootstrap.servers` (or `bootstrap.servers` on every channel) disables Kafka Dev Services
in dev/test.

## Extra channel attributes worth knowing

| Attribute | Meaning |
|---|---|
| `json.serialize.null-as-null=true` | Serialize `null` as JSON `null` instead of the string `"null"` — needed for tombstones on compacted topics |
| `auto.offset.reset=earliest` | Start from the beginning of the topic; combine with a unique `group.id` (`${quarkus.uuid}` gives a new group on every start) to re-read everything |
| `enable.auto.commit=false` | Let Reactive Messaging manage offset commits itself (the connector's recommended setting when it handles acknowledgement) |
| `bootstrap.servers` (alias `kafka.bootstrap.servers`) | Broker address; connector default is `localhost:9092` |

Behavior on existing keys: overwrite the value in place, do not append a duplicate, leave unrelated keys untouched.