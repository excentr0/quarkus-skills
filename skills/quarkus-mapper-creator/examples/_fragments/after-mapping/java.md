# @AfterMapping method (Java)

## Insert Point
Default method in mapper interface body.

## Code

```defaults
skip this fragment (only added when entity has non-owner OneToOne/OneToMany with mappedBy + sub-DTO)
```

### OneToMany association

```java
@org.mapstruct.AfterMapping
default void link${entityAttrNameCapitalized}(@org.mapstruct.MappingTarget ${entityClassFqn} ${entityParamName}) {
    ${entityParamName}.${entityAttrName}.forEach(${unpluralizedAttrName} -> ${unpluralizedAttrName}.${inverseAttributeName} = ${entityParamName});
}
```

### OneToOne association

```java
@org.mapstruct.AfterMapping
default void link${entityAttrNameCapitalized}(@org.mapstruct.MappingTarget ${entityClassFqn} ${entityParamName}) {
    ${attrTypeEntityFqn} ${entityAttrName} = ${entityParamName}.${entityAttrName};
    if (${entityAttrName} != null) {
        ${entityAttrName}.${inverseAttributeName} = ${entityParamName};
    }
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${entityAttrName}` | entity association attribute name | e.g. `children`, `address` |
| `${entityAttrNameCapitalized}` | capitalized | e.g. `Children`, `Address` |
| `${entityParamName}` | decapitalized entity short name | e.g. `order` |
| `${entityClassFqn}` | entity class FQN | — |
| `${inverseAttributeName}` | mappedBy attribute name (non-capitalized, direct field) | e.g. `parent`, `order` |
| `${unpluralizedAttrName}` | unpluralized attr name (OneToMany only) | e.g. `child` |
| `${attrTypeEntityFqn}` | association target entity FQN (OneToOne only) | — |

## Accessor style

The bodies above assume **Panache style**: public fields, so the inverse side is linked by
direct assignment (`child.parent = order`). If the entity source declares private fields
with accessors, use the setter form instead: `${unpluralizedAttrName}.set${inverseAttributeNameCapitalized}(${entityParamName})`.
Decide once from the entity source and keep it consistent.