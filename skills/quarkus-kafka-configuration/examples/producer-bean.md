# Producer bean (`@Channel Emitter` / `@Outgoing`) — Java

Used by Step 5 of [`../SKILL.md`](../SKILL.md) when `path = beans` and the task needs a producer.

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 3 | main package of the module |
| `${className}` | Step 3 | `${ValueType}Producer` (or `${ValueType}Messaging`) |
| `${outChannel}` | Step 2/4a | `${typeKebab}-out` |
| `${valueType}` | Step 2 | `java.lang.String` |
| `${ValueType}` | simple name of `${valueType}` | `String` |
| `${keyType}` | Step 2 | absent — keyed variant only |
| `${emitterFieldName}` | derived | `emitter` |

## Code — default (imperative producer)

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
    Emitter<${valueType}> ${emitterFieldName};

    public void send${ValueType}(${valueType} payload) {
        ${emitterFieldName}.send(payload);
    }
}
```

The `send` method is the application-facing entry point — call it from a JAX-RS resource or a service. Do not
expose the emitter itself beyond the bean.

## Code — keyed messages (only when `keyType` is set)

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;

import io.smallrye.reactive.messaging.kafka.Record;

@ApplicationScoped
public class ${className} {

    @Inject
    @Channel("${outChannel}")
    Emitter<Record<${keyType}, ${valueType}>> ${emitterFieldName};

    public void send${ValueType}(${keyType} key, ${valueType} payload) {
        ${emitterFieldName}.send(Record.of(key, payload));
    }
}
```

## Code — forwarding (streaming) producer

Use when the task is "consume from channel A, publish to channel B" rather than an on-demand send:

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;

import org.eclipse.microprofile.reactive.messaging.Incoming;
import org.eclipse.microprofile.reactive.messaging.Outgoing;

@ApplicationScoped
public class ${className} {

    @Incoming("${inChannel}")
    @Outgoing("${outChannel}")
    public ${valueType} forward${ValueType}(${valueType} payload) {
        // transform the payload if the task requires it
        return payload;
    }
}
```

This variant needs **both** channels configured (incoming and outgoing). A `Multi<${valueType}>` return type is
the streaming-generator variant — use it only when the user asks for a periodic/generated stream.

## Notes

- `Emitter` is the Quarkus way to send records on demand — inject it where the record is produced; there is
  no template-style class to declare.
- `send` with a payload returns a `CompletionStage<Void>` (await it only if the caller must know the outcome);
  `emitter.send(Message.of(payload))` is the explicit-message overload.
- Call `emitter.complete()` only for finite streams — not for a regular application producer.