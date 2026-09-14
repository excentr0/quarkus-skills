# Custom Mapper -- Java

A custom mapper is a plain CDI bean (`@ApplicationScoped`) with hand-written
conversion methods. It has no external dependencies and no generated code.

## Skeleton
Read `examples/_skeletons/custom-java.md`. Write the file to `src/main/java/${packagePath}/${className}.java`.

## Generation order

1. Create file from skeleton (`@ApplicationScoped` class)
2. Add toDto method from `examples/_fragments/custom-to-dto/java.md`
   - For each DTO field: extract value from the entity into a local variable
   - Create DTO via constructor call with all extracted variables
   - Return the DTO
3. Add toEntity method from `examples/_fragments/custom-to-entity/java.md`
   - For each direct DTO field: extract value into a local using the DTO accessor (`getX()` for class DTOs, `x()` for record DTOs)
   - Create new entity instance
   - Assign entity fields (direct public-field assignment for Panache entities, setters for private-field entities)
   - For flat ToOne fields: build a JPA stub of the association entity (`PetType petType = new PetType(); petType.id = ...;`) and assign it to the parent field
   - Return the entity
4. If UPDATE_WITH_NULL_VALUES requested: add from `examples/_fragments/custom-update-with-null/java.md`
   - Takes both DTO and entity as parameters
   - Assigns entity fields from DTO getter values
   - Returns the entity

## Injection

Because the mapper is an `@ApplicationScoped` bean, consumers inject it instead of
calling statics:

```java
@Path("/orders")
public class OrderResource {

    private final OrderMapper orderMapper;

    public OrderResource(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }
}
```

(One constructor → `@Inject` is optional in Quarkus. A field `@Inject OrderMapper orderMapper;`
works too.)

## Method body construction

**toDto method:**
- Init expressions: `${DtoFieldType} ${entityParam}${FieldCap} = ${entityParam}.${fieldAccessor};` for each DTO field
  - Panache entity: `${entityParam}.name` (direct field access)
  - Private-field entity: `${entityParam}.getName()`
- Result: `new ${DtoClassFqn}(${entityParam}${Field1Cap}, ${entityParam}${Field2Cap}, ...)`

**toEntity method:**
- For each direct DTO field: `${DtoFieldType} ${dtoParam}${DtoFieldCap} = ${dtoParam}.${dtoFieldAccessor};`
  - `${dtoFieldAccessor}` = `get${DtoFieldCap}()` for class DTO, `${dtoFieldName}()` for record DTO
- Init: `${EntityClassFqn} ${entityParam} = new ${EntityClassFqn}();`
- For each direct field: `${entityParam}.${fieldName} = ${dtoParam}${DtoFieldCap};`
  (private-field entities: `${entityParam}.set${FieldCap}(${dtoParam}${DtoFieldCap});`)
- For each flat ToOne assoc with fields {f1, f2, ...} from `${Assoc}`:
  - `${Assoc} ${assocVar} = new ${Assoc}();`
  - `${assocVar}.${f1} = ${dtoParam}.${f1Accessor};`
  - `${assocVar}.${f2} = ${dtoParam}.${f2Accessor};`
  - `${entityParam}.${assocField} = ${assocVar};`
- Return: `${entityParam}`

**updateWithNull method:**
- Body: same assignment pattern as toEntity, but the entity is a parameter (not new)
- Return: `${entityParam}`

## Flat ToOne — JPA stub pattern

When the DTO contains **flat fields** from a ToOne association (e.g. only the id,
or id+name extracted from `Pet.type`), do NOT call a repository or fetch the
association. Build a **stub** of the association entity, set ONLY the flat fields,
and assign it:

```java
PetType petType = new PetType();
petType.id = petDto.typeId();
Pet pet = new Pet();
pet.name = petDto.name();
pet.type = petType;
```

Caveat: use the stub only for associations **without cascade** (`@ManyToOne` with a
plain FK). If the association cascades, or if a detached instance is rejected by
the persistence context, resolve the real entity in the service layer and keep the
mapper pure.

## Method naming

Same defaults as MapStruct variant (see `references/mapstruct-java.md`).