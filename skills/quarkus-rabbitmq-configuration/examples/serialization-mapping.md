# Payload serialization / deserialization mapping

Load when the payload type is not a plain `String` or when the user asks about JSON handling.
All facts verified against the Quarkus RabbitMQ guide (quarkus.io/guides/rabbitmq-reference),
Quarkus 3.x.

## Outgoing — how the connector converts a payload to the RabbitMQ message body

There are **no serializer configuration keys** — conversion is automatic, driven by the payload type:

| Payload type | RabbitMQ body | `content_type` |
|---|---|---|
| `String`, primitives, `UUID` | String value | `text/plain` |
| `io.vertx.core.json.JsonObject` / `io.vertx.core.json.JsonArray` | Serialized string | `application/json` |
| `byte[]` | Binary | `application/octet-stream` |
| `io.vertx.mutiny.core.buffer.Buffer` | Binary | `application/octet-stream` |
| Any other class (POJO) | JSON via the built-in Json Mapper | `application/json` |

If the payload cannot be serialized to JSON, the message is nacked.

## Incoming — what the consumer receives

The method parameter type must match how the body arrives:

| Incoming body (`content_type`) | Parameter type |
|---|---|
| `text/plain` | `String` (or the primitive/`UUID` the text represents) |
| `application/json` | `io.vertx.core.json.JsonObject` — map with `payload.mapTo(MyType.class)` |
| binary | `byte[]` |

Do **not** declare the POJO as the parameter type for JSON bodies — the connector hands over a
`JsonObject`, and the map happens in the consumer method (see
[`consumer-bean.md`](consumer-bean.md), "JSON POJO payload" variant).

When the broker-side producer does not set `content_type`, force JSON handling with the channel
attribute `content-type-override=application/json` (incoming).

## POJO notes

- The POJO is serialized to JSON automatically for outgoing messages — no `JsonbSerializer`/
  `ObjectMapperSerializer` configuration exists or is needed (that is the Kafka connector's mechanism,
  not RabbitMQ's).
- For **native executables**, annotate the POJO with `@RegisterForReflection`
  (`io.quarkus.runtime.annotations.RegisterForReflection`) so Quarkus keeps the class/fields for
  reflection (`mapTo` on the consumer side needs it too).
- `mapTo` uses Vert.x's JSON Databind (Jackson under the hood): the POJO needs a no-args constructor
  and standard getters/setters (or public fields).

## Quick pairing recipe

| Producer payload | Consumer parameter |
|---|---|
| `String` | `String` |
| POJO (e.g. `OrderEvent`) | `JsonObject` + `.mapTo(OrderEvent.class)` |
| `byte[]` | `byte[]` |
| `JsonObject` | `JsonObject` (no re-map needed) |

Keep producer and consumer sides symmetric for the same channel; when they are not, state the
mismatch in the report.