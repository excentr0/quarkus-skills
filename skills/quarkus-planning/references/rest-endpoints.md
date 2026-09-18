> Local copy of `quarkus-explore/references/rest-endpoints.md` — keep the two in sync when editing.

# Summarize REST Endpoints

How to build the REST API summary from JAX-RS resource files.

## Step 1 — Locate resources

- grep for `@Path` across `src/main/java` (classes annotated with `jakarta.ws.rs.Path`).
- Quarkus naming: `XxxResource`. A single `@jakarta.ws.rs.ApplicationPath` class (rare in Quarkus)
  may set a global prefix.

## Step 2 — Extract per resource

1. **Base path** — class-level `@Path("/orders")`.
2. **Methods** — for each method: HTTP verb annotation (`@GET`, `@POST`, `@PUT`, `@DELETE`, `@PATCH`),
   method-level `@Path` (if any), parameter types (`@PathParam`, `@QueryParam`), request body type,
   return type (record/DTO/entity).
3. **Serialization** — `@Produces/@Consumes(MediaType.APPLICATION_JSON)`; records are serialized by
   quarkus-rest-jackson automatically.
4. **Validation** — `@Valid` on parameters → `quarkus-hibernate-validator` is expected in the build.
5. **Security** — `@RolesAllowed`, `@PermitAll` annotations; combine with
   `quarkus.http.auth.permission.*` rules from `application.properties`.
6. **Exception mapping** — `@ServerExceptionMapper` (per-resource or global `@ApplicationScoped`
   mapper bean); note which HTTP error codes the API actually returns.
7. **Transactions** — `jakarta.transaction.Transactional` on write methods (Panache writes need it).

## Step 3 — Emit the summary

```text
REST API (order area):
- GET /orders — list, paginated (page/size query params), returns List<OrderDto>
- POST /orders — create, body OrderDto (@Valid), returns OrderDto, @Transactional
- GET /orders/{id} — one order, 404 via NotFoundException
- DELETE /orders/{id} — @RolesAllowed("admin")
```

## Common traps

- `@Path` values may be template variables — `@Path("{id}")` + `@PathParam`.
- A method parameter without annotation (single POJO/record param) is the request body; a parameter
  with `@PathParam`/`@QueryParam` is not the body.
- Quarkus REST supports `Uni<T>` return types — a resource may be reactive; note it if you see `Uni`.
- Do not report an endpoint unless you saw both the verb annotation and its `@Path` context.