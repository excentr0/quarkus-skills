# Channel configuration reference

Load when the task goes past the basic channel block: Dev Services, advanced connector attributes, batch
consumption, transactions, or programmatic channel config. All facts verified against the Quarkus Kafka guide
(quarkus.io/guides/kafka) and quarkus.io/guides/kafka-dev-services, Quarkus 3.x.

## Connector attributes (incoming channel)

Configured as `mp.messaging.incoming.<channel>.<attribute>=<value>`; any Kafka consumer property can be passed
through the same prefix (e.g. `max.poll.records`).

| Attribute | Default | Notes |
|---|---|---|
| `connector` | — | Must be `smallrye-kafka` for Kafka channels |
| `topic` | channel name | If neither `topic` nor `topics` is set, the channel name is used |
| `bootstrap.servers` (alias `kafka.bootstrap.servers`) | `localhost:9092` | Setting it disables Kafka Dev Services in dev/test |
| `group.id` | `quarkus.application.name` | `${quarkus.uuid}` gives a fresh group on every start |
| `key.deserializer` | `org.apache.kafka.common.serialization.StringDeserializer` | Only when the key side is not configured |
| `auto.offset.reset` | Kafka default | `earliest` + unique group id = re-read the topic from the beginning |
| `enable.auto.commit` | connector manages offsets | Set `false` when the app acks messages itself |
| `json.serialize.null-as-null` | `false` | `true` serializes `null` as JSON `null` (tombstones) instead of `"null"` |
| `health-enabled` / `health-readiness-enabled` | `true` | Health checks per channel |
| `partitions` | `1` | Number of consumer clients; affects generated `client.id` |

Outgoing channels use the same shape: `mp.messaging.outgoing.<channel>.connector=smallrye-kafka`,
`.topic`, `.bootstrap.servers`, `.value.serializer`, `.key.serializer`.

## Dev Services for Kafka

With `quarkus-messaging-kafka` present, Quarkus starts a Kafka broker automatically in dev and test mode —
no configuration needed. Dev Services is **disabled** automatically when `kafka.bootstrap.servers` is set or when
all channels define `bootstrap.servers` (in that case Quarkus assumes an external broker is intended).

| Property | Default | Purpose |
|---|---|---|
| `quarkus.kafka.devservices.enabled` | (auto) | Force enable/disable |
| `quarkus.kafka.devservices.port` | random | Fixed port |
| `quarkus.kafka.devservices.provider` | `upstream-kafka-native` | `redpanda`, `strimzi`, `kafka-native`, `upstream-kafka`, `upstream-kafka-native` |
| `quarkus.kafka.devservices.image-name` | provider-dependent | Custom image |
| `quarkus.kafka.devservices.shared` | `true` | Reuse a running container in dev mode |
| `quarkus.kafka.devservices.service-name` | `kafka` | Label value for sharing/discovery |
| `quarkus.kafka.devservices.topic-partitions.<topic>` | — | Create topics with a given partition count on startup |

Run `./mvnw quarkus:dev` to exercise the wiring against the auto-started broker. Tests get the same broker
under `@QuarkusTest`.

## Batch consumption

```java
@Incoming("prices")
public CompletionStage<Void> consumeBatch(Message<ConsumerRecords<String, Double>> records) {
    for (ConsumerRecord<String, Double> record : records.getPayload()) {
        // process each record; records.ack() commits the latest offsets of the batch
    }
    return records.ack();
}
```

## Streaming producer

```java
@Outgoing("out")
public Multi<Record<String, Double>> generate() {
    return Multi.createFrom().ticks().every(Duration.ofSeconds(1))
            .map(tick -> Record.of("my-key", random.nextDouble()));
}
```

## Programmatic channel configuration (escape hatch)

Instead of (or in addition to) `mp.messaging.*` properties, a channel's configuration map can be produced as a
CDI bean qualified with `@Identifier("<channel>")`:

```java
@Produces
@ApplicationScoped
@Identifier("my-configuration")
Map<String, Object> outgoing() {
    return Map.ofEntries(
            Map.entry("value.serializer", ObjectMapperSerializer.class.getName())
    );
}
```

Use only when the user explicitly asks for programmatic configuration — properties are the idiomatic default and
keep dev/test Dev Services wiring intact.

## Kafka + Hibernate transactions

When a database write and a Kafka send must succeed or fail together, use the transactional emitter
(`io.smallrye.reactive.messaging.kafka.transactions.KafkaTransactions`) and the `withTransaction` API:

```java
@Channel("kafka") KafkaTransactions<${valueType}> emitter;

@Transactional
public void post(${valueType} payload) {
    emitter.withTransaction(e -> {
        payload.persist();
        e.send(payload);
        return Uni.createFrom().voidItem();
    }).await().indefinitely();
}
```

Requires the channel to be configured for transactions; mention it as an advanced option and do not add it
unless the user asks for exactly-once style delivery.