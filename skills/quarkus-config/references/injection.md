# Injecting configuration

## 1. Mapping interface vs `@ConfigProperty`

| Situation | Use |
|---|---|
| Two or more related settings, read as a group | `@ConfigMapping` interface (see [`config-mapping.md`](config-mapping.md)) |
| Exactly one one-off value on one bean | `@ConfigProperty` on that bean |
| May-be-missing value | `Optional<T>` in either style |
| Values used in many places | mapping interface — one type, injected where needed |

A mapping interface is a CDI bean: inject the interface, never re-read the properties by hand.

```java
@ApplicationScoped
public class ${className} {

    @Inject
    ${Feature}Config config;   // or a constructor parameter
}
```

## 2. `@ConfigProperty` — field injection

```java
@ApplicationScoped
public class ${className} {

    @Inject
    @ConfigProperty(name = "${propertyKey}")
    ${fieldType} ${fieldName};
}
```

- `name` is the full key (`${prefix}.${fieldName}`), not a short name.
- Add `defaultValue` only when the value may legitimately be absent:
  `@ConfigProperty(name = "${propertyKey}", defaultValue = "${defaultValue}")`.
- Do not create a separate holder class for one value — declare it on the bean that uses it.

## 3. `@ConfigProperty` — constructor injection

```java
@ApplicationScoped
public class ${className} {

    private final ${fieldType} ${fieldName};

    @Inject
    public ${className}(@ConfigProperty(name = "${propertyKey}") ${fieldType} ${fieldName}) {
        this.${fieldName} = ${fieldName};
    }
}
```

With a single constructor, `@Inject` is not required in Quarkus — follow the project's existing style.

## 4. Optional values

```java
@Inject
@ConfigProperty(name = "${propertyKey}")
Optional<${fieldType}> ${fieldName};
```

The property may be absent; the code must handle the empty case explicitly. Prefer this over a
made-up default when "absent" has a distinct meaning for the feature.

## 5. Missing required property

A non-Optional, non-defaulted property that is absent at startup fails the application with a
configuration error (`NoSuchElementException` → `ConfigurationException`). That failure is the
intended validation for genuinely required settings — see the verification step in
[`../SKILL.md`](../SKILL.md).

## 6. Common mistakes

- Reading a property that exists only under `%prod.` in dev mode (or vice versa) — check the profile
  block when a value is unexpectedly missing.
- `@ConfigProperty` without `name` — there is no convention-based key derivation in Quarkus for it.
- Injecting a mapping interface that was never annotated `@ConfigMapping`.
- Duplicating the same value in two places instead of centralizing it in one mapping interface.
