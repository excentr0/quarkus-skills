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

## Code — default (text payloads: `String`, primitives, `UUID`)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import org.eclipse.microprofile.reactive.messaging.Incoming;

@ApplicationScoped
public class ${className} {

    @Incoming("${inChannel}")
    public void consume${ValueType}(${valueType} payload) {
        // handle the incoming message
    }
}
```

## Code — JSON POJO payload (`${valueType}` is a POJO)

The connector delivers JSON bodies as `io.vertx.core.json.JsonObject`; map to the business type with
`.mapTo(...)`. Never declare the POJO as the method parameter type.

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import org.eclipse.microprofile.reactive.messaging.Incoming;

import io.vertx.core.json.JsonObject;

@ApplicationScoped
public class ${className} {

    @Incoming("${inChannel}")
    public void consume${ValueType}(JsonObject payload) {
        ${valueType} value = payload.mapTo(${valueType}.class);
        // handle the incoming message
    }
}
```

The `content_type` of the incoming message must be `application/json` (the producer's connector sets it
automatically for POJO payloads). When the broker side does not set it, use the channel's
`content-type-override` attribute in `application.properties`.

## Variants (pick at most one, mention in the report)

- **Inbound metadata (routing key, headers, content type)** — take
  `org.eclipse.microprofile.reactive.messaging.Message<${valueType}>` as the parameter and read
  `IncomingRabbitMQMetadata` from it:

  ```java
  package ${packageName};

  import java.util.Optional;

  import jakarta.enterprise.context.ApplicationScoped;

  import org.eclipse.microprofile.reactive.messaging.Incoming;
  import org.eclipse.microprofile.reactive.messaging.Message;

  import io.smallrye.reactive.messaging.rabbitmq.IncomingRabbitMQMetadata;

  @ApplicationScoped
  public class ${className} {

      @Incoming("${inChannel}")
      public void consume${ValueType}(Message<${valueType}> incoming) {
          Optional<IncomingRabbitMQMetadata> metadata =
                  incoming.getMetadata(IncomingRabbitMQMetadata.class);
          ${valueType} payload = incoming.getPayload();
          // metadata.ifPresent(meta -> meta.getRoutingKey()); meta.getHeader("my-header", String.class)
          // handle the incoming message
      }
  }
  ```

  Available getters (all `Optional`-wrapped): `getRoutingKey()`, `getContentType()`,
  `getCorrelationId()`, `getDeliveryMode()`, `getPriority()`, `getReplyTo()`, `getTimestamp(ZoneId)`,
  `getHeader(String, Class)`, `getHeaders()`.

- **Explicit acknowledgement** — return `incoming.ack()` from the method (return type
  `java.util.concurrent.CompletionStage<Void>` or `io.smallrye.mutiny.Uni<Void>`) when the connector must
  be told when the processing finished; with plain `void` methods the connector acknowledges on its own.

- **Blocking handling** (synchronous work such as JDBC calls) — annotate the method with
  `@Blocking` (`io.smallrye.reactive.messaging.annotations.Blocking`) on top of `@Incoming`; the method
  runs on a worker thread instead of the event loop.

## Body rule

The method body is business logic. Fill it only from the user's stated task (persist a Panache entity,
call a service, forward to another channel, …). If the task does not specify handling — keep the single
comment line and report the stub. Never invent business logic, retries, or error handling that was not
asked for.