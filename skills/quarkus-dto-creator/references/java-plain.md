# Java Plain Class DTO

## Conditions
- language = Java
- variant = `java-plain` (chosen when the user wants mutability/setters, or the project's existing
  DTOs are plain classes, or the user explicitly said "plain class")

## Generation Order

1. **Skeleton:** read `examples/_skeletons/java/class.md` — create the file.
2. **Class Javadoc:** read `examples/_fragments/javadoc/java/javadoc.md` ("Top-level Java class"
   variant) — insert immediately above the `public class ${className} {` line. Always generated.
3. **Fields:** read `examples/_fragments/fields/java.md` — add fields to the class body.
4. **Constructors:** read `examples/_fragments/constructor/java/all-args.md` — add after fields.
   - When `isMutable=false` AND `allArgsConstructor=true` → only the all-args constructor.
   - When `isMutable=true` → **BOTH** the no-args constructor AND the all-args constructor are
     emitted, even if the user did not explicitly ask for the no-args one.
5. **Getters + setters:**
   - When `isMutable=false`: read `examples/_fragments/getters-setters/java/getters.md` and emit
     getters in field order, after the constructor(s).
   - When `isMutable=true AND fluentSetters=false`: emit getters and setters **interleaved**
     (`getX, setX, getY, setY, …`) — see `examples/_fragments/getters-setters/java/setters.md` for the
     layout. Do NOT emit all getters first and then all setters.
   - When `isMutable=true AND fluentSetters=true`: emit getters as a single block (not interleaved),
     then all fluent setters from `examples/_fragments/fluent-setters/java/fluent-setters.md`.
6. **equals/hashCode** (when equalsHashCode=true): read
   `examples/_fragments/equals-hashcode/java/equals-hashcode.md`. Add after getters/setters.
7. **toString** (when toString=true): read `examples/_fragments/tostring/java/tostring.md` — add after
   equals/hashCode.
8. **@JsonIgnoreProperties** (when jsonIgnoreUnknownProperties=true AND `quarkus-rest-jackson` is in the
   build): read `examples/_fragments/json-ignore/java/json-ignore.md` — add the annotation on the class.
9. **Serializable** (when the user asked for it): read
   `examples/_fragments/serializable/java/serializable.md` — modify the class declaration.
10. **Nested classes** (for each attribute with subDtoType=NEW_NESTED_CLASS):
    - read `examples/_fragments/nested-class/java/nested-class.md` — add the inner class;
    - apply `examples/_fragments/javadoc/java/javadoc.md` ("Nested class" variant) above the
      `public static class …` line — short name + import;
    - recursively generate the inner class contents using the same Generation Order (Javadoc, fields,
      constructor, getters, equals, toString, …).

## Variant-Specific Questions

Prefer the harness's structured-question tool for all questions below; fall back to plain text only if
the tool is unavailable. Batch independent questions into one call (up to 4 questions per call).

**Batch 1** — basic settings (3 questions):

| Question | Header | Options (first = default) |
|----------|--------|--------------------------|
| Mutable DTO (with setters)? | Mutable | No (Recommended) / Yes |
| Fluent setters (return this)? | Fluent | No (Recommended) / Yes |
| Constructor with all fields? | Constructor | Yes (Recommended) / No |

Note: the fluent setters question is only asked when mutable=true.

**Batch 2** — standard methods (3 questions):

| Question | Header | Options (first = default) |
|----------|--------|--------------------------|
| equals() and hashCode()? | Equals | Yes (Recommended) / No |
| toString()? | ToString | Yes (Recommended) / No |
| @JsonIgnoreProperties(ignoreUnknown=true)? | JsonIgnore | No (Recommended) / Yes |

## Validation Rules
- At least one of allArgsConstructor or mutable must be true (otherwise fields cannot be initialized)
- fluentSetters is only available when mutable=true

## Notes
- There is no Hibernate-proxy equals variant for DTOs — a DTO is never a Hibernate proxy. The
  proxy-safe equals/hashCode pattern belongs to entities, not to this skill.
- If the project's existing DTOs use Lombok, follow the project style instead — see
  `references/lombok-note.md`.