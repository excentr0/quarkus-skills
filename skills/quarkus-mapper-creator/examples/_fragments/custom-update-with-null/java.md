# Custom updateWithNull method (Java)

## Insert Point
Instance method in the custom mapper class body (`@ApplicationScoped` bean).

## Code

```defaults
skip by default (only generated when user explicitly requests full update method)
```

### When UPDATE_WITH_NULL_VALUES requested

```java
public ${entityClassFqn} ${methodName}(${dtoClassFqn} ${dtoParamName}, ${entityClassFqn} ${entityParamName}) {
    ${entityParamName}.${field1} = ${dtoParamName}.${dtoField1Accessor};
    ${entityParamName}.${field2} = ${dtoParamName}.${dtoField2Accessor};
    return ${entityParamName};
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${methodName}` | naming pattern | `updateWithNull` |
| `${dtoParamName}` | decapitalized DTO short name | — |
| `${entityParamName}` | decapitalized entity short name | — |
| `${dtoClassFqn}` | DTO class FQN | — |
| `${entityClassFqn}` | entity class FQN | — |
| `${fieldNCap}` | capitalized entity field names (setter form) | — |
| `${dtoFieldNCap}` | capitalized DTO field names | — |
| `${dtoFieldNAccessor}` | `getX()` for class DTO, `x()` for record DTO | — |

## Accessor style

Public-field (Panache) bodies assign directly (`pet.name = ...`). Private-field entities
use setters: `${entityParamName}.set${fieldNCap}(...)`.