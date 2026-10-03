# PATCH scalar field fragment (Java)

For each exposed scalar field, append exactly one source-derived type-check block to `${patchTypeChecks}`. In no-DTO mode, append its matching write block to `${patchAssignments}`. The checker reads but never mutates; all checkers run in `assertPatchAllowed` before any entity mutation. DTO mode uses the same checker against the API DTO field types, and does not emit field assignments here.

All fences below are executable templates after substituting the declared variables. `entity` is the no-DTO helper parameter and `patchNode` is its JSON input.

## String

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull() && !value.isTextual()) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type");
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}value.textValue()${fieldWriteSuffix} }
}
```

## Boolean

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull() && !value.isBoolean()) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type");
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}value.booleanValue()${fieldWriteSuffix} }
}
```

## int

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull() && (!value.isIntegralNumber() || !value.canConvertToInt())) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type or range");
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}value.intValue()${fieldWriteSuffix} }
}
```

## long

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull() && (!value.isIntegralNumber() || !value.canConvertToLong())) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type or range");
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}value.longValue()${fieldWriteSuffix} }
}
```

## double

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull() && (!value.isNumber() || !java.lang.Double.isFinite(value.doubleValue()))) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type or range");
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}value.doubleValue()${fieldWriteSuffix} }
}
```

## BigDecimal (JSON string representation)

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull()) {
        if (!value.isTextual()) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type");
        try { new java.math.BigDecimal(value.textValue()); }
        catch (java.lang.NumberFormatException e) { throw new jakarta.ws.rs.BadRequestException("Invalid patch field value"); }
    }
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}new java.math.BigDecimal(value.textValue())${fieldWriteSuffix} }
}
```

## UUID (JSON string representation)

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull()) {
        if (!value.isTextual()) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type");
        try { java.util.UUID.fromString(value.textValue()); }
        catch (java.lang.IllegalArgumentException e) { throw new jakarta.ws.rs.BadRequestException("Invalid patch field value"); }
    }
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}java.util.UUID.fromString(value.textValue())${fieldWriteSuffix} }
}
```

## Enum (JSON string representation)

### Type check
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (!value.isNull()) {
        if (!value.isTextual()) throw new jakarta.ws.rs.BadRequestException("Invalid patch field type");
        try { java.lang.Enum.valueOf(${enumTypeFqn}.class, value.textValue()); }
        catch (java.lang.IllegalArgumentException e) { throw new jakarta.ws.rs.BadRequestException("Invalid patch field value"); }
    }
}
```

### no-DTO write
```java
if (patchNode.has("${fieldName}")) {
    com.fasterxml.jackson.databind.JsonNode value = patchNode.get("${fieldName}");
    if (value.isNull()) { ${nullAssignment} }
    else { ${fieldWritePrefix}${enumTypeFqn}.valueOf(value.textValue())${fieldWriteSuffix} }
}
```

For primitive targets, `${nullAssignment}` is the complete statement `throw new jakarta.ws.rs.BadRequestException("Null is not allowed for this field");`. For nullable references it is the complete field/setter statement assigning null. `${fieldWritePrefix}` and `${fieldWriteSuffix}` form an assignment or setter invocation: public field example `entity.name = ` and `;`; setter example `entity.setName(` and `);`. Derive these from the real source; never assume accessors. Do not use coercive `asInt()` / `asBoolean()`. All conversion failures use generic sanitized client messages. Other target types are unsupported and require stopping generation.

## Variables
| Variable | Source |
|---|---|
| `${fieldName}` | exact JSON property name from source/Jackson contract |
| `${fieldWritePrefix}` | verified LHS/call prefix for the target (for example `entity.name = ` or `entity.setName(`) |
| `${fieldWriteSuffix}` | verified assignment/call suffix (for example `;` or `);`) |
| `${nullAssignment}` | complete null assignment statement or primitive-null rejection statement |
| `${enumTypeFqn}` | actual enum type FQN; enum variant only |
| `${javaType}` | actual declaration; selects this exact type fragment |
