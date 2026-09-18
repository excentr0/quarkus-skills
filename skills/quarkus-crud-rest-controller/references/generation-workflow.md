# CRUD generation workflow

## Step 5 -- Generate code

Tell the user: `Step 5/6: Generating code...`

WA work units, in order. Load each example file right before writing its code.

| WA | Step | Output | Example file |
|----|------|--------|--------------|
| WA1 | 5.1 | resource class skeleton | [`examples/_skeletons/java.md`](../examples/_skeletons/java.md) |
| WA2 | 5.2 | constructor injection | [`examples/_beans/injection/java.md`](../examples/_beans/injection/java.md) |
| WA3 | 5.3 | GET_LIST | [`examples/_methods/get-list/java.md`](../examples/_methods/get-list/java.md) |
| WA4 | 5.3 | GET_ONE | [`examples/_methods/get-one/java.md`](../examples/_methods/get-one/java.md) |
| WA5 | 5.3 | GET_MANY | [`examples/_methods/get-many/java.md`](../examples/_methods/get-many/java.md) |
| WA6 | 5.3 | CREATE | [`examples/_methods/create/java.md`](../examples/_methods/create/java.md) |
| WA7 | 5.3 | PATCH | [`examples/_methods/patch/java.md`](../examples/_methods/patch/java.md) |
| WA8 | 5.3 | PATCH_MANY | [`examples/_methods/patch-many/java.md`](../examples/_methods/patch-many/java.md) |
| WA9 | 5.3 | DELETE | [`examples/_methods/delete/java.md`](../examples/_methods/delete/java.md) |
| WA10 | 5.3 | DELETE_MANY | [`examples/_methods/delete-many/java.md`](../examples/_methods/delete-many/java.md) |
| WA11 | 5.4 | repository creation (only when none exists and the user agrees) | [`examples/_beans/repository/java.md`](../examples/_beans/repository/java.md) |

### 5.1 Create resource class (WA1)

Read `examples/_skeletons/java.md`.

Apply variable substitutions:
- `{packageName}` --> resourcePackage
- `{className}` --> resourceName
- `{requestPath}` --> basePath + resourcePath

Use the available file-writing tool to create `src/main/java/{package-path}/{resourceName}.java`.

### 5.2 Add bean injection (WA2)

Read `examples/_beans/injection/java.md`.

Add a constructor parameter for the repository. If DTO with mapper: also inject the mapper bean.
If PATCH or PATCH_MANY is selected: also inject the Jackson `ObjectMapper` bean
(`${ObjectMapperFqn}` resolved in Step 1).

Use the available file-editing tool to modify the resource class.

### 5.3 Add CRUD methods (WA3–WA10)

For each method in `selectedMethods` (from Step 4 method selection):

1. Determine the example file path: `examples/_methods/{method-name}/java.md`

2. Read the example file

3. Select the correct code variant based on:
   - DTO mode (no DTO vs with DTO)
   - For GET_LIST: pagination (yes/no), filter (with/without), sort (with/without), total count (with/without)
   - For CREATE: with/without `@Valid`
   - For DELETE: default (returns the deleted entity/DTO) vs strict (204 No Content, 404 when missing)
   - For PATCH / PATCH_MANY: DTO vs no DTO (the patch strategy is Jackson `ObjectMapper` in both)

4. Apply variable substitutions (ONLY variables declared in the Variables section)

5. **FQN handling (CRITICAL):** examples contain FQNs (e.g. `jakarta.ws.rs.GET`,
   `io.quarkus.panache.common.Page`, entity/DTO/repository FQNs). When writing the final file, you MUST:
   1. Replace every FQN in the body with its **short name**
   2. Collect every FQN you shortened and emit a corresponding `import` line right after the
      `package` statement, sorted, no duplicates
   3. Classes from the same package as the resource must NOT be imported
   4. Types from `java.lang` must NOT be imported
   5. FQNs that cannot be shortened unambiguously (same simple name from different packages) keep the FQN form

6. Use the available file-editing tool to insert the method into the resource class body

### 5.4 Create repository if missing (WA11)

Only when Step 3 found no repository for the entity and the user agreed to create one:

Read `examples/_beans/repository/java.md`. Use the available file-writing tool to create
`src/main/java/{package-path}/{RepoName}.java`.

---
