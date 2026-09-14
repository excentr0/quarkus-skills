# Method Naming Conventions

## Default patterns

| Method type | Pattern | Example (Entity=Order, DTO=OrderDto) |
|-------------|---------|--------------------------------------|
| toEntity | `"toEntity"` | `toEntity` |
| toDto | `"to${DTO_NAME}"` | `toOrderDto` |
| partialUpdate | `"partialUpdate"` | `partialUpdate` |
| updateWithNull | `"updateWithNull"` | `updateWithNull` |

`${DTO_NAME}` is replaced with the DTO short class name (e.g. `OrderDto`).

## Parameter naming

| Parameter | Rule | Example |
|-----------|------|---------|
| entity param | decapitalized entity short name | `order` |
| DTO param | decapitalized DTO short name | `orderDto` |

## Collection method naming strategy

Default: LIKE_SINGLE (same name as single-item method).

Other strategies (configurable, but rarely changed):
- PLURALIZE: `toEntities`, `toOrderDtos`
- COLLECTION_TYPE: `toEntityList`, `toOrderDtoList`

## Custom mapper (CDI bean) method names

Custom mappers follow the same naming table — the only difference is that they are
instance methods on an `@ApplicationScoped` bean rather than abstract MapStruct methods:

```java
public Order toEntity(OrderDto orderDto) { ... }
public OrderDto toOrderDto(Order order) { ... }
```