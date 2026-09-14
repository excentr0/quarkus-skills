# Detect Project Conventions

How to derive the project's own conventions from source files before generating anything.
Follow substeps 1.1 → 1.5 in order. Do not skip or reorder them.

---

## Step 1.1: Gather convention evidence

Read 2–3 representative `@Path` resources (prefer ones in the same domain area) and the build file.
For each convention below, note what the code actually shows.

---

## Step 1.2: Score each convention

For each convention, determine the answer from the code and assign a confidence score (1–100).
If a convention is simply absent from the code (e.g. no paginated endpoint exists yet) — the
confidence is high (90): use the default without asking.

General conventions:

- **Resource class naming** — `XxxResource` (Quarkus idiom) vs `XxxEndpoint` / other. Default: `XxxResource`
- **Resource package** — the package where existing `@Path` classes live; is there a `.rest` / `.api` segment? Default: same package as existing resources
- **Class-level path style** — leading slash (`/api/products`) vs no slash (`api/products`); is there a common prefix (`/api`, `/rest`, none) across resources? Default: `/api` prefix
- **Resource path segment** — pluralized entity name (`/products`), kebab-case, or singular? Default: pluralized decapitalized entity name
- **Method-level paths** — `@Path("/{id}")` on detail methods vs a separate `@Path` per method; is `/{id}` used consistently? Default: `/{id}` on GET_ONE / PATCH / DELETE
- **Path parameter annotation** — `@PathParam("id")` (explicit name) vs relying on parameter name; Default: explicit `@PathParam("id")`
- **Query parameter defaults** — `@DefaultValue("0")` / `@DefaultValue("20")` present? What page size does the project use? Default: `page=0`, `size=20`
- **Response wrapper** — do endpoints return raw entities/DTOs, or a wrapper (`Response`, page record, `X-Total-Count`)? Default: raw entity/DTO; `X-Total-Count` only when the user asks
- **Validation placement** — `@Valid` on resource method parameters, or validation only inside services? Default: `@Valid` on the resource parameter when the type has constraints

Persistence & transactions (score separately):

- **Repository pattern** — `PanacheRepository` / `PanacheRepositoryBase` beans, Active Record statics, or both? Default: `PanacheRepository`
- **Repository annotation** — `@ApplicationScoped` present on repositories? Default: yes
- **Transaction placement** — `@Transactional` on resource methods, on `@ApplicationScoped` service beans, or both? Default: on resource methods for this skill
- **Service layer** — does the project route writes through a service bean instead of the resource? Default: no service layer for CRUD
- **Delete semantics** — returns the deleted entity (default), returns 204 No Content, or soft delete? Default: return the deleted entity
- **Patch strategy** — Jackson `ObjectMapper` merge (the only strategy in this skill); does the project use a different convention (e.g. dedicated PATCH DTO)? Default: `ObjectMapper.readerForUpdating`

Error handling conventions (score separately):

- **Not-found handling** — `jakarta.ws.rs.NotFoundException` thrown directly, or mapped through `@ServerExceptionMapper`? Default: throw `NotFoundException`
- **Exception mapper presence** — is there a global `@ServerExceptionMapper` bean that turns exceptions into an error body? If yes, still throw `NotFoundException`; the mapper shapes the response
- **Error body shape** — what do existing error responses look like? Report it, do not invent one

DTO conventions (score separately — only relevant when DTO mode is selected):

- **DTO style** — `record` vs plain class. Default: record
- **DTO naming** — `XxxDto`, `XxxRestDto`, `XxxResponse`? Default: `{EntityName}Dto`
- **DTO package** — `.dto`, `.rest.dto`, alongside the resource? Default: same convention as existing DTOs
- **Mapper style** — MapStruct `@Mapper(componentModel = "cdi")` interfaces vs custom `@ApplicationScoped` converters. Default: MapStruct when `hasMapStruct`, else custom converter
- **Mapper method names** — align with quarkus-mapper-creator defaults: `to${DtoShortName}` / `toEntity` / `partialUpdate` (copy-into-existing). Detect actual names from existing mapper interfaces.

---

## Step 1.3: Collect uncertain conventions

Collect all conventions where confidence < 80. For each, formulate a question with explicit
answer options; put the default value first (marked as "Recommended").

---

## Step 1.4: Ask developer

If there are any uncertain conventions from step 1.3, ask the developer with the harness's
structured-question tool — combine all questions into a single call (max 4 questions per call).

Example question shape:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| What base path do the existing resources use? | Base path | `/api` (Recommended) — matches existing resources / No prefix — class paths start at the root / Other |

If the structured-question tool is unavailable, fall back to a numbered text list with the
recommended option first.

---

## Step 1.5: Record the outcome

Write the resolved conventions into a short list that Step 4 of the skill uses for the
one-line confirmation:

```text
Conventions: ProductResource in org.acme.product (no .rest segment), base path /api,
pluralized paths, page=0/size=20, @Transactional on resource methods, NotFoundException on missing,
DTO records named XxxDto in .dto, MapStruct mapper with toDto/toEntity/updateEntity.
```
