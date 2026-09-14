# Producer bean — Java

Used by Step 5 of [`../SKILL.md`](../SKILL.md) when `path = beans` and the task needs a producer.

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 3 | main package of the module |
| `${className}` | Step 3 | `${ValueType}Producer` (or `${ValueType}Messaging`) |
| `${outChannel}` | Step 2/4a | `${typeKebab}-out` |
| `${valueType}` | Step 2 | `java.lang.String` |
| `${ValueType}` | simple name of `${valueType}` | `String` |

## Code — imperative producer (`Emitter`, recommended for REST/service code)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;

@ApplicationScoped
public class ${className} {

    @Inject
    @Channel("${outChannel}")
    Emitter<${valueType}> emitter;

    public void send${ValueType}(${valueType} payload) {
        emitter.send(payload);
    }
}
```

`emitter.send(payload)` returns `java.util.concurrent.CompletionStage<Void>` — return it when the caller
wants back-pressure or completion; otherwise ignore it.

## Code — streaming producer (`@Outgoing`)

Only when the task generates messages continuously (scheduled ticks, stream transformation) — not for
on-request sending:

```java
package ${packageName};

import java.time.Duration;

import jakarta.enterprise.context.ApplicationScoped;

import org.eclipse.microprofile.reactive.messaging.Outgoing;

import io.smallrye.mutiny.Multi;

@ApplicationScoped
public class ${className} {

    @Outgoing("${outChannel}")
    public Multi<${valueType}> produce() {
        // generate the outgoing stream
    }
}
```

## Variants (pick at most one, mention in the report)

- **Routing key / headers / properties per message** — send a `Message` with
  `OutgoingRabbitMQMetadata`; the connector publishes to the channel's exchange using the metadata
  routing key (falls back to the channel's `default-routing-key` attribute, otherwise none):

  ```java
  package ${packageName};

  import jakarta.enterprise.context.ApplicationScoped;
  import jakarta.inject.Inject;

  import org.eclipse.microprofile.reactive.messaging.Channel;
  import org.eclipse.microprofile.reactive.messaging.Emitter;
  import org.eclipse.microprofile.reactive.messaging.Message;
  import org.eclipse.microprofile.reactive.messaging.Metadata;

  import io.smallrye.reactive.messaging.rabbitmq.OutgoingRabbitMQMetadata;

  @ApplicationScoped
  public class ${className} {

      @Inject
      @Channel("${outChannel}")
      Emitter<${valueType}> emitter;

      public void send${ValueType}(${valueType} payload, String routingKey) {
          OutgoingRabbitMQMetadata metadata = new OutgoingRabbitMQMetadata.Builder()
                  .withRoutingKey(routingKey)
                  .build();
          emitter.send(Message.of(payload, Metadata.of(metadata)));
      }
  }
  ```

  The builder also supports `.withHeader(String, Object)` and `.withTimestamp(java.time.ZonedDateTime)`.

- **Fixed routing key for the whole channel** — no code change: set
  `mp.messaging.outgoing.${outChannel}.default-routing-key=${routingKey}` in `application.properties`.

## Body rule

Generated methods contain no business logic. `emitter.send(...)` lines are the wiring itself; anything
beyond that comes only from the user's stated task. Never invent payloads, retries, or error handling
that was not asked for.