# Consumer bean (`@Incoming`) — Java

Used by Step 5 of [`../SKILL.md`](../SKILL.md) when `path = beans` and the task needs a consumer.

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 3 | main package of the module |
| `${className}` | Step 3 | `${ValueType}Consumer` (or `${ValueType}Messaging`) |
| `${inChannel}` | Step 2/4a | `${typeKebab}-in` |
| `${valueType}` | Step 2 | `java.lang.String` |
| `${ValueType}` | simple name of `${valueType}` | `String` |
| `${keyType}` | Step 2 | absent — keyed variant only |

## Code — default (value-only messages)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import org.eclipse.microprofile.reactive.messaging.Incoming;

@ApplicationScoped
public class ${className} {

    @Incoming("${inChannel}")
    public void consume${ValueType}(${valueType} payload) {
        // handle the incoming record
    }
}
```

## Code — keyed messages (only when `keyType` is set)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import org.eclipse.microprofile.reactive.messaging.Incoming;

import io.smallrye.reactive.messaging.kafka.Record;

@ApplicationScoped
public class ${className} {

    @Incoming("${inChannel}")
    public void consume${ValueType}(Record<${keyType}, ${valueType}> record) {
        ${valueType} payload = record.value();
        // handle the incoming record
    }
}
```

`record.key()` may be `null` for records without a key; `record.value()` may be `null` for tombstones.

## Variants (pick at most one, mention in the report)

- **Async acknowledgement** — declare the method as `public CompletionStage<Void> consume${ValueType}(...)`
  (or `Uni<Void>`) when the handling is asynchronous; returning the stage lets Reactive Messaging acknowledge
  after completion.
- **Explicit ack** — take `org.eclipse.microprofile.reactive.messaging.Message<${valueType}>` as the parameter
  and return `message.ack()` when the connector must be told when to commit.
- **Batch consumption** — `Message<ConsumerRecords<${keyType}, ${valueType}>>` with `records.ack()`; see
  [`../references/channel-config-reference.md`](../references/channel-config-reference.md).

## Body rule

The method body is business logic. Fill it only from the user's stated task (persist a Panache entity, call a
service, forward to another channel, …). If the task does not specify handling — keep the single comment line
and report the stub. Never invent business logic, retries, or error handling that was not asked for.