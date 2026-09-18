# CRUD context gathering

## Step 1 -- Gather minimal project context (automatic, no questions)

Tell the user: `Step 1/6: Gathering project context...`

Read only the files whose content is **actually consumed** by a later step. Do not pre-read
"in case we need it" — every variable here must have a concrete downstream user.

| File operation | Variable | Used for |
|----------------|----------|----------|
| read `pom.xml` / `build.gradle(.kts)` | `presentDeps`, `buildFile`, `hasRestJackson`, `hasValidation`, `hasMapStruct` | feature gates, Step 6 dependency edits |
| glob `src/main/java/**/*.java`, then grep `@jakarta.ws.rs.Path` | `resources` (class name, class-level `@Path`, package) | Step 4 path-conflict detection, naming/basePath/package conventions |
| grep `@jakarta.ws.rs.Path` values in `resources` | `existingBasePaths` | basePath + resourcePath defaults |
| read `src/main/resources/application.properties` | `securityRules` | optional: if `/api` paths are protected or open (informational for the report) |

From the resource scan, derive `mainPackage` (package of existing resources, or the root package
of `src/main/java` sources).

For the full convention-scoring procedure (ID strategy, DTO style, mapper naming, transactional
placement), follow [`references/detect-conventions.md`](../references/detect-conventions.md).

Determine the build-related flags:
- `hasRestJackson` — `io.quarkus:quarkus-rest-jackson` (or `quarkus-rest` + a JSON provider) in the build file.
- `hasValidation` — `io.quarkus:quarkus-hibernate-validator` in the build file.
- `hasMapStruct` — `io.quarkiverse.mapstruct:quarkus-mapstruct` and `org.mapstruct:mapstruct` in the build file.
- **Jackson package resolution:** check the build file for Jackson dependencies. `com.fasterxml.jackson.*` →
  `JsonNodeFqn = com.fasterxml.jackson.databind.JsonNode`, `ObjectMapperFqn = com.fasterxml.jackson.databind.ObjectMapper`,
  `JsonProcessingExceptionFqn = com.fasterxml.jackson.core.JsonProcessingException`.
  If the project carries a different Jackson major (`tools.jackson.*`), resolve the three FQNs to that package instead.
  **Never hardcode blindly — always resolve from the project's dependencies.**

That is the entire Step 1. **Do NOT** fetch:
- the entity list — needed only if the user did not name an entity in their prompt. Defer to Step 2 as a lazy fallback.
- repositories — depends on knowing the entity, which happens in Step 2. Defer to Step 3 as a lazy fallback.
- entity details — depends on knowing the entity. Defer to Step 2.
- DTOs / mappers — depend on knowing the entity AND the DTO decision. Defer to Step 4.

If the project is multi-module (more than one module with `pom.xml` / `build.gradle` and Quarkus
extensions): ask which module to use, then repeat this step scoped to that module.

---
