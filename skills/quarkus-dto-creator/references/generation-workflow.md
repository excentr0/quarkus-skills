# DTO generation workflow

## Step 6 — Generate code

Tell the user: `Step 6/7: Generating DTO...`

1. Determine the target path: `src/main/java/${packagePath}/${className}.java`.

2. Follow the **Generation Order** from the selected reference file.

3. Before writing, check for a **name collision**: glob/grep the target package for
   `${className}.java` / `record ${className}` / `class ${className}`. If the name is taken — for the
   parent DTO ask the user for another name; for a sub-DTO auto-suffix with a number
   (`${SubDtoName}1`, `${SubDtoName}2`, …) until the name is free.

4. For each generation step:

   **If skeleton (new file):**
   - read the skeleton `.md` from `examples/_skeletons/`
   - apply variable substitutions
   - use the available file-writing tool to create the file

   **If fragment:**
   - read the fragment `.md` from `examples/_fragments/`
   - read the Insert Point to know WHERE to insert
   - use the available file-editing tool to insert code at the specified point
   - apply variable substitutions

5. Variable substitution rules:
   - `${packageName}` → detected DTO package or user choice
   - `${className}` → from the user or the default `${EntityName}Dto`
   - field-level variables → from the entity source (Step 2)
   - **NEVER substitute anything not listed in Variables**
   - **NEVER add imports, methods, or code not in the example**
   - **FQN handling (CRITICAL):** examples contain FQNs (e.g. `java.util.List`,
     `jakarta.validation.constraints.NotNull`). When writing the final file, you MUST:
     1. Replace every FQN in the body with its **short name**
        (`java.util.List<Integer>` → `List<Integer>`, `@jakarta.validation.constraints.NotNull` → `@NotNull`).
     2. Collect every FQN you shortened and emit a corresponding `import` line right after the
        `package` statement, sorted, no duplicates.
     3. Types from `java.lang` (`String`, `Long`, …) must NOT be imported and must appear as short names.
     4. Classes from the same package as the DTO must NOT be imported.
     5. **Javadoc `{@link …}` references — UNIFORM:** generate **short name + import** for **every**
        shape: top-level class, top-level record, nested static class, nested record, and separate-file
        sub-DTO (`NEW_CLASS`). There is no asymmetry. Always shorten the entity reference and always add
        the corresponding `import` line (unless the entity is in the same package).
     6. **Group imports** in two blocks separated by ONE blank line:
        - **Block 1** — all third-party / project imports together: `jakarta.*`, `com.fasterxml.*`,
          `org.hibernate.*`, project packages, etc. (alphabetical inside the block).
        - **(blank line)**
        - **Block 2** — `java.*` and `javax.*` (alphabetical).
        Do NOT split block 1 into per-package sub-blocks.
     The final file must contain short names in the body (including every Javadoc `{@link …}`) and a
     clean, grouped import block at the top.

6. For **sub-DTOs** (`subDtoType=NEW_CLASS`): create a separate file by repeating Steps 6.1–6.5
   recursively for the sub-entity.

7. For **nested classes/records** (`subDtoType=NEW_NESTED_CLASS`): add the inner declaration to the
   parent DTO file, then fill it following the same fragment rules.

8. **Nested record inside a record parent — MANDATORY:** when the parent DTO is a Java record, every
   `NEW_NESTED_CLASS` association MUST be emitted as a nested `public record` inside the parent record's
   body. The skill MUST NOT silently fall back to `NEW_CLASS` (separate file) just because the
   record-form fragment looks shorter. The full procedure is in [`references/java-record.md`](../references/java-record.md) Step 6 and
   [`examples/_fragments/nested-class/java/nested-class.md`](../examples/_fragments/nested-class/java/nested-class.md) ("Java record" variant). If those
   instructions seem ambiguous to you, that is a bug in this skill — fix the docs, do NOT work around it
   by changing the `subDtoType`.

---
## Reactive projects

If `persistenceMode = reactive` (`quarkus-hibernate-reactive-panache` in the build):

- The **DTO shape does not change** — the same records/classes, the same generation order.
- Entity loading APIs return `Uni<...>` (`Order.findById(id)` → `Uni<Order>`), so the conversion happens
  inside the reactive chain (`map(...)` / `flatMap(...)`) and resource methods return `Uni<OrderDto>`.
- Mention this in one line when the mapper delegation happens, so the mapper is used in the reactive
  pipeline rather than on a blocking path.

---
## Indentation

The skill MUST detect the project's indentation style — never hardcode tabs or spaces. Detection order:

1. **`.editorconfig`** at the project root (or any parent of the target file's directory). For Java
   files, look up the `[*.java]` or `[*]` section and read `indent_style` (`tab` or `space`) and
   `indent_size` / `tab_width`.
2. **Sample existing Java files** in the target DTO package (or the nearest ancestor package that
   contains Java files). Detect whether the leading whitespace on indented lines uses `\t` or spaces, and
   how many.
3. **Default to 4-space** if neither source is conclusive.

Whatever style is chosen, apply it **uniformly** to every line of every generated fragment (fields,
constructors, getters/setters, equals/hashCode, toString, nested classes/records). Never mix tabs and
spaces inside the same file.

---
## Per-field options

The skill must support the following per-field controls:

- **Field rename** (`fieldNameOverride`): the DTO field name can differ from the entity attribute name.
  Mapper generation still maps it from the original attribute.
- **Add validations** (`extraValidations`): add `jakarta.validation` constraints on top of the ones
  inherited from the entity. The allowed constraints depend on the field type — see
  [`references/validation.md`](../references/validation.md).
- **Remove inherited validations** (`removedValidations`): drop any constraint that came from the
  entity field.
- **Edit annotation parameters** (`message`, `min`, `max`, `regexp`, …): all parameters of every
  constraint are editable.

These options never appear unless the user explicitly asks for "fine-tune field settings",
"per-field validation" or similar. By default the skill just inherits everything from the entity.

---
