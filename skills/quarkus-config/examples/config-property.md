# One-off `@ConfigProperty` injection (Java)

Used by Step 3 of [`../SKILL.md`](../SKILL.md) when `configStyle = config-property`.

## Variables

| Variable | Source | Default |
|---|---|---|
| `${packageName}` | Step 1/3 | package of the consuming bean |
| `${className}` | Step 0 | the CDI bean that uses the value |
| `${propertyKey}` | Step 2 | full key (`${prefix}.${fieldName}`) |
| `${fieldType}` / `${fieldName}` | Step 0 | value type and camelCase field name |
| `${defaultValue}` | Step 0 | only when the value may legitimately be absent |

## Code — field injection, required value

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class ${className} {

    @Inject
    @ConfigProperty(name = "${propertyKey}")
    ${fieldType} ${fieldName};
}
```

## Code — field injection with a default

```java
    @Inject
    @ConfigProperty(name = "${propertyKey}", defaultValue = "${defaultValue}")
    ${fieldType} ${fieldName};
```

## Code — constructor injection

```java
package ${packageName};

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class ${className} {

    private final ${fieldType} ${fieldName};

    @Inject
    public ${className}(@ConfigProperty(name = "${propertyKey}") ${fieldType} ${fieldName}) {
        this.${fieldName} = ${fieldName};
    }
}
```

## Code — optional value

```java
    @Inject
    @ConfigProperty(name = "${propertyKey}")
    java.util.Optional<${fieldType}> ${fieldName};
```

## Notes

- Exactly one setting → this style; two or more related settings → a `@ConfigMapping` interface
  (see [`mapping-interface.md`](mapping-interface.md)).
- A required `@ConfigProperty` missing at startup fails the application — that is intended; add
  `defaultValue` only if the setting is genuinely optional.
- With a single constructor, `@Inject` is not required in Quarkus — follow the project's style.
