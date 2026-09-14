# Flat expression method (Java)

## Insert Point
Default method in mapper interface body. Added together with the
corresponding `@Mapping(target=..., expression="java(...)")` line on
`toDto` (see `examples/_fragments/to-dto-method/java.md`).

## Scope — collections only

This fragment applies **only** to flat **ToMany** fields (`List<Integer>
petIds`, `Set<Integer> specialtyIds`, etc.). For flat **ToOne** fields
(`Integer typeId`, `String typeName` flattened from `Pet.type`) do **not**
emit a helper method or `expression = ...`. Instead, use MapStruct
**dot-notation** in the regular `@Mapping(source, target)` annotation —
see `examples/_fragments/to-entity-method/java.md` ("With @Mapping
dot-notation for ToOne flat fields"). MapStruct generates the intermediate
`new PetType(); petType.id = ...;` itself.

## Code

```defaults
skip this fragment (only for DTOs with flat **collection** attributes where subDtoType == FLAT)
```

### Flat collection mapping method

```java
default ${collectionFqn}<${attrDtoTypeFqn}> ${functionName}(java.util.Collection<${mappedEntityFqn}> ${assocFieldName}) {
    return ${assocFieldName}.stream().map(${mappedEntityName} -> ${mappedEntityName}.${mappedAttrName})${toCollectionExpression};
}
```

The parameter type is always `java.util.Collection` — not the concrete
collection type from the entity field. The method only calls `.stream()`,
so the concrete type is irrelevant. This also avoids mismatches when the
entity getter returns a different collection type than the field declaration
(e.g. field is `Set<Specialty>` but getter returns `List<Specialty>`).

Where `${toCollectionExpression}`:
- `.toList()` for List on JDK 16+
- `.collect(java.util.stream.Collectors.toList())` for List on JDK < 16
- `.collect(java.util.stream.Collectors.toSet())` for Set

Panache note: `${mappedEntityName} -> ${mappedEntityName}.${mappedAttrName}` is a **lambda
over a public field** (`pet -> pet.id`) — Panache entities have no `getId()` for a method
reference. If the project's entities use private fields with getters, switch to
`${mappedEntityName}::get${mappedAttrNameCap}`.

## Naming rule (CRITICAL)

The helper function name is built from the entity association field name
and the flat DTO field name — **not** from the nested attribute name. This
guarantees uniqueness even when the same association is flattened in
multiple ways:

```text
${functionName} = ${assocFieldName} + "To" + capitalize(${flatDtoFieldName})
```

For example, if `Owner.pets` is flattened twice into `petIds` and
`petNames`, you get two distinct helpers `petsToPetIds` and `petsToPetNames`.
A naming scheme based on the nested attribute (`petsToId`, `petsToName`)
would NOT collide here either, but it does collide as soon as two
different flat fields use the same nested attribute on different
associations — so use the DTO-field-based scheme unconditionally.

## Worked examples

```java
// Vet.specialties: Set<Specialty> -> VetDto.specialtyIds: Set<Integer>
default Set<Integer> specialtiesToSpecialtyIds(Collection<Specialty> specialties) {
    return specialties.stream().map(specialty -> specialty.id).collect(java.util.stream.Collectors.toSet());
}

// Owner.pets: List<Pet> -> OwnerDto.petIds: List<Integer> (JDK 16+)
default List<Integer> petsToPetIds(Collection<Pet> pets) {
    return pets.stream().map(pet -> pet.id).toList();
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${functionName}` | `${assocFieldName} + "To" + capitalize(${flatDtoFieldName})` | e.g. `specialtiesToSpecialtyIds`, `petsToPetIds` |
| `${assocFieldName}` | name of the entity association field (the part of the flat name before `.`); also used as the parameter name | e.g. `specialties`, `pets` |
| `${flatDtoFieldName}` | name of the flattened collection field on the DTO (the `target` of the `@Mapping`) | e.g. `specialtyIds`, `petIds` |
| `${mappedEntityFqn}` | association target entity FQN | — |
| `${mappedEntityName}` | short entity name for the lambda parameter | e.g. `Specialty`, `Pet` |
| `${mappedAttrName}` | attribute name after `.` in the flat name (public field; usually `id`) | e.g. `id`, `name` |
| `${mappedAttrNameCap}` | capitalized attribute name for getter-based entities | e.g. `Id` |
| `${collectionFqn}` | `java.util.List` or `java.util.Set` (used for return type only; parameter is always `java.util.Collection`) | — |
| `${attrDtoTypeFqn}` | DTO field element type FQN | e.g. `java.lang.Integer` |