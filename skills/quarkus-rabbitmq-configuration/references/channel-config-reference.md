# Channel configuration reference

Load when the task goes past the basic channel block: Dev Services, existing infrastructure, DLQ,
broker credentials/TLS, metadata API, or programmatic client options. All facts verified against the
Quarkus RabbitMQ guides (quarkus.io/guides/rabbitmq-reference, quarkus.io/guides/rabbitmq-dev-services,
quarkus.io/guides/rabbitmq), Quarkus 3.x.

## Contents

- [Connector attributes (incoming)](#connector-attributes-incoming)
- [Connector attributes (outgoing)](#connector-attributes-outgoing)
- [Existing infrastructure](#existing-infrastructure)
- [Dev Services for RabbitMQ](#dev-services-for-rabbitmq)
- [Dead-letter queueing](#dead-letter-queueing)
- [Broker access and credentials](#broker-access-and-credentials)
- [TLS](#tls)
- [Health reporting](#health-reporting)
- [Custom client options (escape hatch)](#custom-client-options-escape-hatch)

## Connector attributes (incoming)

Configured as `mp.messaging.incoming.<channel>.<attribute>=<value>`. The channel maps to a RabbitMQ
queue; the queue is bound to the exchange named by `exchange.name` (default: channel name) with
`routing-keys`.

| Attribute | Default | Notes |
|---|---|---|
| `connector` | — | Must be `smallrye-rabbitmq` |
| `queue.name` | channel name | Queue to consume from |
| `queue.declare` | `true` | Declares the queue **and its binding**; `false` for ops-provisioned queues |
| `queue.durable` | `true` | |
| `queue.exclusive` / `queue.auto-delete` | `false` | |
| `queue.x-queue-type` | `classic` | `quorum`, `classic`, `stream` (only when the app declares the queue) |
| `queue.x-queue-mode` | `default` | `lazy`, `default` |
| `queue.ttl` | — | ms a message stays undelivered before it is dead |
| `queue.single-active-consumer` | `false` | |
| `exchange.name` | channel name | Exchange the queue is bound to; `""` = default exchange |
| `exchange.type` | `topic` | `direct`, `fanout`, `headers`, `topic` |
| `exchange.declare` / `exchange.durable` / `exchange.auto-delete` | `true` / `true` / `false` | |
| `routing-keys` | `#` | Comma-separated routing keys binding the queue to the exchange |
| `failure-strategy` | `reject` | `fail`, `accept`, `reject` — applied when a message is nacked |
| `auto-acknowledgement` | `false` | `true` = delivery counts as acknowledgement |
| `broadcast` | `false` | Dispatch to multiple subscribers |
| `max-outstanding-messages` | — | Cap on unacknowledged messages in flight |
| `connection-count` | `1` | Multiple connections, e.g. for sharded queues |
| `content-type-override` | — | Force a MIME type on incoming messages |
| `host` / `port` / `username` / `password` | global values | Per-channel broker access (aliases `rabbitmq-host` etc.); setting these per channel can disable Dev Services when every channel defines them |

## Connector attributes (outgoing)

Configured as `mp.messaging.outgoing.<channel>.<attribute>=<value>`. The channel maps to a RabbitMQ
exchange; messages are published to it with the per-message routing key (`OutgoingRabbitMQMetadata`)
or `default-routing-key`.

| Attribute | Default | Notes |
|---|---|---|
| `connector` | — | Must be `smallrye-rabbitmq` |
| `exchange.name` | channel name | Published-to exchange; `""` = default exchange |
| `exchange.type` | `topic` | `direct`, `fanout`, `headers`, `topic` |
| `exchange.declare` | `true` | `false` for ops-provisioned exchanges |
| `exchange.durable` / `exchange.auto-delete` | `true` / `false` | |
| `default-routing-key` | (empty) | Fixed routing key when no per-message metadata |
| `default-ttl` | — | ms a message may stay undelivered |
| `max-inflight-messages` | `1024` | Concurrent writes to RabbitMQ |
| `host` / `port` / `username` / `password` | global values | Per-channel broker access (aliases `rabbitmq-host` etc.) |

Both directions also accept Vert.x RabbitMQ client tuning (`connection-timeout` 60000,
`requested-heartbeat` 60, `reconnect-attempts` 100, `reconnect-interval` 10, `virtual-host` `/`,
`automatic-recovery-enabled` `false`) and `tracing.enabled` `true`.

## Existing infrastructure

When ops provisioned the queue/exchange, write the name **and** `declare=false`:

```properties
mp.messaging.incoming.people.connector=smallrye-rabbitmq
mp.messaging.incoming.people.queue.name=people
mp.messaging.incoming.people.queue.declare=false

mp.messaging.outgoing.people.connector=smallrye-rabbitmq
mp.messaging.outgoing.people.exchange.name=people
mp.messaging.outgoing.people.exchange.declare=false
```

Without `queue.declare=false` the connector tries to declare the queue/binding and fails if it exists
with different arguments (e.g. durability mismatch).

## Dev Services for RabbitMQ

With `quarkus-messaging-rabbitmq` present, Quarkus starts a RabbitMQ broker automatically in dev and
test mode. Dev Services is **disabled** automatically when `rabbitmq-host` or `rabbitmq-port` is set,
or when all channels define `host`/`port`.

| Property | Default | Purpose |
|---|---|---|
| `quarkus.rabbitmq.devservices.enabled` | (auto) | Force enable/disable |
| `quarkus.rabbitmq.devservices.port` | random | AMQP port |
| `quarkus.rabbitmq.devservices.http-port` | random | Management plugin UI port |
| `quarkus.rabbitmq.devservices.image-name` | `docker.io/library/rabbitmq:3.12-management` | Only official `rabbitmq` images |
| `quarkus.rabbitmq.devservices.shared` | `true` | Reuse a running container (label `quarkus-dev-service-rabbitmq`) |
| `quarkus.rabbitmq.devservices.service-name` | `rabbitmq` | Label value for sharing/discovery |

Infrastructure can be pre-provisioned on the Dev Services broker for tests:

```properties
quarkus.rabbitmq.devservices.exchanges.my-exchange.type=topic          # default 'direct'
quarkus.rabbitmq.devservices.exchanges.my-exchange.durable=true
quarkus.rabbitmq.devservices.queues.my-queue.durable=true
quarkus.rabbitmq.devservices.bindings.a-binding.source=my-exchange     # default: binding name
quarkus.rabbitmq.devservices.bindings.a-binding.routing-key=some-key   # default '#'
quarkus.rabbitmq.devservices.bindings.a-binding.destination=my-queue   # default: binding name
```

(`.destination-type=queue` is the default; `vhost` defaults to `/`.) Run `./mvnw quarkus:dev` to
exercise the wiring against the auto-started broker; `@QuarkusTest` gets the same broker.

## Dead-letter queueing

On an incoming channel, `auto-bind-dlq=true` declares a DLQ and binds it to the DLX:

| Attribute | Default |
|---|---|
| `auto-bind-dlq` | `false` |
| `dead-letter-queue-name` | `<queue-name>.dlq` |
| `dead-letter-exchange` | `DLX` |
| `dead-letter-exchange-type` | `direct` |
| `dead-letter-routing-key` | queue name |
| `dlx.declare` | `false` |
| `dead-letter-queue-type` / `dead-letter-queue-mode` | `classic` / `default` |

Use only when the user asks for dead-lettering.

## Broker access and credentials

Global keys: `rabbitmq-host` (default `localhost`), `rabbitmq-port` (5672),
`rabbitmq-username`, `rabbitmq-password`; per-channel attributes `host`/`port`/`username`/`password`
with the same aliases. `virtual-host` defaults to `/`.

**Never write these unprefixed** — they disable Dev Services for RabbitMQ in dev/test. Real broker
addresses belong under `%prod.`:

```properties
%prod.rabbitmq-host=rabbit.example.com
%prod.rabbitmq-port=5672
%prod.rabbitmq-username=app
%prod.rabbitmq-password=${RABBITMQ_PASSWORD}
```

## TLS

Per-channel TLS configuration name plus Quarkus TLS registry keys:

```properties
quarkus.tls.your-tls-config.trust-store.pem.certs=ca.crt
mp.messaging.incoming.prices.tls-configuration-name=your-tls-config
```

Legacy per-channel keys (`ssl`, `trust-all`, `trust-store-path`, `trust-store-password`) also exist.
Load this section only when the user asks for TLS.

## Health reporting

With `quarkus-smallrye-health`, the connector contributes readiness/liveness per channel; disable per
channel with `health-enabled=false` (also `health-readiness-enabled`).

## Custom client options (escape hatch)

Produce a `RabbitMQOptions` bean and reference it by name:

```java
@Produces
@Named("my-named-options")
RabbitMQOptions options() {
    return new RabbitMQOptions().setHost("rabbit.example.com").setAutomaticRecoveryEnabled(true);
}
```

```properties
mp.messaging.incoming.prices.client-options-name=my-named-options
```

Use only when the user explicitly asks for programmatic client configuration — properties are the
idiomatic default and keep Dev Services wiring intact.

## Direct RabbitMQ client (out of scope)

`io.quarkiverse.rabbitmqclient:quarkus-rabbitmq-client` exposes the raw RabbitMQ Java client. This
skill does not use it; if the user explicitly wants the raw client API rather than Reactive
Messaging, say so and configure it manually per the Quarkiverse docs.

# Detailed channel configuration workflow

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
  [`examples/serialization-mapping.md`](../examples/serialization-mapping.md)).
- **Consumer of a JSON POJO** takes `io.vertx.core.json.JsonObject` and calls `.mapTo(${ValueType}.class)`
  — do not declare the POJO as the method parameter type (see
  [`examples/consumer-bean.md`](../examples/consumer-bean.md)).
- **Broker access**: `rabbitmq-host`, `rabbitmq-port`, `rabbitmq-username`, `rabbitmq-password` are global
  keys; per-channel equivalents are `host`, `port`, `username`, `password`.
  **Never write them unprefixed** — it disables Dev Services for RabbitMQ in dev/test. A real broker goes
  under the production profile: `%prod.rabbitmq-host=${brokerHost}` (plus `%prod.rabbitmq-port=5672` and
  `%prod.rabbitmq-username`/`%prod.rabbitmq-password` when the broker requires auth). Reuse only an existing non-secret endpoint or environment-variable reference; never copy a redacted username, password, or token.
- Per-channel `host`/`port` also disable Dev Services when every channel defines them — avoid per-channel
  broker keys unless the user asks for mixed brokers.
- Overwrite existing keys in place; never delete unrelated keys or duplicate a key.
- YAML flavour (`application.yaml` when `quarkus-config-yaml` is present): nest the same keys under
  `mp.messaging.incoming.<channel>` / `mp.messaging.outgoing.<channel>`.
- Profile overrides (`%dev.`, `%test.`) are allowed for queue/exchange names; keep broker addresses out
  of the default profile (see above).
