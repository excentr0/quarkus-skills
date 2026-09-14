# Config mapping interface (Java)

Used by Step 3 of [`../SKILL.md`](../SKILL.md) when `configStyle = mapping-interface`.

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 1/3 | project's config package, else the feature's package |
| `${Feature}` | Step 2 | feature name in PascalCase (`Billing`, `Order`) |
| `${prefix}` | Step 2 | kebab-case feature name (`billing`, `order`) — or the project's existing custom prefix |
| `${fieldType}` | Step 0 | value type of the setting (`String`, `int`, `Duration`, `URI`, …) |
| `${fieldName}` | Step 0 | method name of the setting (`host`, `retryCount`) |
| `${defaultValue}` | Step 0 | value from the request — only when a sensible default exists |
| `${optionalFieldType}` / `${optionalFieldName}` | Step 0 | may-be-absent setting (optional variant only) |
| `${Nested}` / `${nested}` | Step 0 | nested-group interface name and its method name (nested variant only) |
| `${nestedFieldType}` / `${nestedFieldName}` | Step 0 | setting inside the nested group (nested variant only) |

## Code — minimal interface

```java
package ${packageName};

import io.smallrye.config.ConfigMapping;

@ConfigMapping(prefix = "${prefix}")
public interface ${Feature}Config {

    ${fieldType} ${fieldName}();
}
```

## Code — with a default and an optional setting

```java
package ${packageName};

import java.util.Optional;

import io.smallrye.config.ConfigMapping;
import io.smallrye.config.WithDefault;

@ConfigMapping(prefix = "${prefix}")
public interface ${Feature}Config {

    @WithDefault("${defaultValue}")
    ${fieldType} ${fieldName}();

    Optional<${optionalFieldType}> ${optionalFieldName}();
}
```

## Code — nested group (only when a sub-topic exists)

```java
package ${packageName};

import io.smallrye.config.ConfigMapping;

@ConfigMapping(prefix = "${prefix}")
public interface ${Feature}Config {

    ${fieldType} ${fieldName}();

    ${Nested} ${nested}();

    interface ${Nested} {

        ${nestedFieldType} ${nestedFieldName}();   // -> ${prefix}.${nested}.${nestedFieldName}
    }
}
```

Nested groups and their rules: [`../references/config-mapping.md`](../references/config-mapping.md).

## Notes

- Keys map mechanically to method names: `@ConfigMapping(prefix = "billing")` + `String host()` →
  `billing.host`. For multi-word settings write the key (e.g. `billing.retry-count`) explicitly in the
  properties file next to the interface method that reads it.
- A required (non-Optional, no-default) setting failing startup when absent is intended validation.
- The interface is injected like a CDI bean — see [`../references/injection.md`](../references/injection.md).
