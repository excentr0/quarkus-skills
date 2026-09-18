# Mapper generation workflow

## Step 4 -- Generate code

Tell the user: `Step 4/5: Generating mapper...`

Determine the reference file based on mapper type:
- MapStruct + Java -> read [`references/mapstruct-java.md`](../references/mapstruct-java.md)
- Custom + Java -> read [`references/custom-java.md`](../references/custom-java.md)

Read the corresponding reference file and follow its Generation order exactly.

### Building @Mapping annotations

Read [`references/mapping-annotations.md`](../references/mapping-annotations.md) for rules on how to
build `@Mapping` annotations.

Compare entity fields from `${entityDetails}` with DTO fields from `${dtoFields}`:
1. Match DTO fields to entity fields by name
2. For fields with different names, add `@Mapping(source, target)`
3. For association ID fields (e.g. `customerId` -> `customer.id`), add appropriate mapping
4. For flat fields (e.g. `customerName` -> `customer.name`), add expression or source.target mapping

### Reading skeleton and fragments

1. Read the skeleton file from `examples/_skeletons/{variant}-java.md`
2. Apply variable substitutions
3. Write the file to `src/main/java/${packagePath}/${className}.java`
4. For each fragment in the generation order:
   - Check if the fragment's condition is met
   - Read the fragment from `examples/_fragments/${fragment-name}/java.md`
   - Apply variable substitutions
   - Insert/edit into the created file

### Variable substitution rules
- `${packageName}` -> from Step 1 context or user answer
- `${className}` -> from user answer or default `${EntityName}Mapper`
- `${entityClassFqn}` -> entity FQN from context
- `${dtoClassFqn}` -> DTO FQN from context
- `${entityParamName}` -> decapitalized entity short name
- `${dtoParamName}` -> decapitalized DTO short name
- `${methodName}` -> from naming conventions (see [`references/method-naming.md`](../references/method-naming.md))
- **NEVER substitute anything not listed in the Variables section of the example file**
- **NEVER add imports, methods, or code not in the example**
- **FQN handling (CRITICAL):** examples contain FQNs (e.g. `org.mapstruct.Mapper`,
  `org.mapstruct.Mapping`, `org.mapstruct.ReportingPolicy`,
  `org.mapstruct.MappingConstants.ComponentModel.CDI`, entity/DTO FQNs). When
  writing the final file, you MUST:
  1. Replace every FQN in the body with its **short name**
     (e.g. `@org.mapstruct.Mapper(...)` -> `@Mapper(...)`,
     `org.mapstruct.ReportingPolicy.IGNORE` -> `ReportingPolicy.IGNORE`,
     `${entityClassFqn}` -> entity short name, `${dtoClassFqn}` -> DTO short name).
  2. Collect every FQN you shortened and emit a corresponding `import` line
     right after the `package` statement, sorted, no duplicates.
  3. Classes from the same package as the mapper (entity, DTO if collocated)
     must NOT be imported — just use the short name.
  4. Types from `java.lang` must NOT be imported.
  5. The IDE will NOT optimize imports for you — the file is saved as-is.

### Entity accessors — Panache convention (CRITICAL)

Panache entities declare **public fields**; there are no getters/setters.
In custom mapper bodies and helper methods use **direct field access**:
- read: `pet.name`, `pet.type.id` (not `pet.getName()`, not `pet.getType().getId()`)
- write: `pet.name = ...` (not `pet.setName(...)`)
- flat collections: `.map(specialty -> specialty.id)` (there is no `getId()` to point a method reference at)

Exception: if the entity source declares `private` fields with getters/setters
(classic JPA style), use those accessors instead. Decide once from the entity
source in Step 2 (${entityAccessors}) and stay consistent.

DTO accessors depend on the DTO declaration form:
- `public record OrderDto(String name, ...)` → component accessors: `orderDto.name()`
- regular class → getters: `orderDto.getName()`

### Reactive projects

If the project uses `quarkus-hibernate-reactive-panache`, the entity style and
the mapper code are identical — mapping is synchronous. Call the mapper inside
the reactive chain (`.map(mapper::toDto)`); never block on it.

---
