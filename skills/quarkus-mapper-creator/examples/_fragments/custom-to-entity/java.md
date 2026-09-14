# Custom toEntity method (Java)

## Insert Point
Instance method in the custom mapper class body (`@ApplicationScoped` bean).

## Code

```defaults
Always generated for Custom mapper.
```

### Standard form

Extract every DTO value into a local first, then construct
the entity and assign its fields. This mirrors `custom-to-dto` and is the
canonical style. **Use this form by default.**

```java
public ${entityClassFqn} ${methodName}(${dtoClassFqn} ${dtoParamName}) {
    ${dtoFieldType1} ${dtoParamName}${dtoField1Cap} = ${dtoParamName}.${dtoField1Accessor};
    ${dtoFieldType2} ${dtoParamName}${dtoField2Cap} = ${dtoParamName}.${dtoField2Accessor};
    ${entityClassFqn} ${entityParamName} = new ${entityClassFqn}();
    ${entityParamName}.${field1} = ${dtoParamName}${dtoField1Cap};
    ${entityParamName}.${field2} = ${dtoParamName}${dtoField2Cap};
    return ${entityParamName};
}
```

### `${dtoFieldNAccessor}` — record vs class

- DTO is a regular **class** → use the getter: `getName()`, `getTypeId()`, …
- DTO is a Java **record** → use the **record component accessor**, no
  `get` prefix: `name()`, `typeId()`, …

Use the bare-component form for records and the
`getX()` form for classes. The choice is determined statically
from the DTO declaration: a `public record PetDto(...)` always uses the
component-accessor form.

### Entity field assignment — record vs class and accessor style

The bodies above assign **public fields directly** (`pet.name = ...`) — the Panache
convention. If the entity source declares private fields with setters, use
`${entityParamName}.set${field1Cap}(...)` instead. Decide once from the entity source
and stay consistent.

### Flat ToOne — JPA stub pattern

When the DTO contains **flat fields** from a ToOne association (e.g. only
the id, or id+name extracted from `Pet.type`), do NOT call a repository or
fetch the association. Build a **stub** of the association entity, set
ONLY the flat fields, and assign it. JPA treats the stub as a known-id
reference; loading the real row is the persistence layer's job.

```java
public Pet toEntity(PetDto petDto) {
    String petDtoName = petDto.getName();
    PetType petType = new PetType();
    petType.id = petDto.getTypeId();
    Pet pet = new Pet();
    pet.name = petDtoName;
    pet.type = petType;
    return pet;
}
```

If multiple flat fields come from the same association (`typeId` and
`typeName`), set them on the same stub:

```java
PetType petType = new PetType();
petType.id = petDto.getTypeId();
petType.name = petDto.getTypeName();
pet.type = petType;
```

Caveat: the stub is safe for a non-cascaded `@ManyToOne` (plain FK) association. If the
association cascades, or the persistence context rejects a detached instance, resolve the
real entity in the service layer via the Panache repository and keep the mapper pure.

### Java Record + flat ToOne (combined)

```java
public Pet toEntity(PetDto petDto) {
    String petDtoName = petDto.name();
    PetType petType = new PetType();
    petType.id = petDto.typeId();
    Pet pet = new Pet();
    pet.name = petDtoName;
    pet.type = petType;
    return pet;
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${methodName}` | naming pattern | `toEntity` |
| `${dtoParamName}` | decapitalized DTO short name | e.g. `petDto` |
| `${entityParamName}` | decapitalized entity short name | e.g. `pet` |
| `${dtoClassFqn}` | DTO class FQN | — |
| `${entityClassFqn}` | entity class FQN | — |
| `${fieldNCap}` | capitalized entity field names (setter form / local names) | — |
| `${dtoFieldNCap}` | capitalized DTO field names (used in local var name) | — |
| `${dtoFieldNAccessor}` | `getX()` for class DTO, `x()` for record DTO | — |
| `${dtoFieldTypeN}` | DTO field types | — |