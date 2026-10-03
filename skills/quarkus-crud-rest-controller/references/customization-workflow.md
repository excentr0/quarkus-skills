# CRUD customization workflow

## Step 4 -- DTO and customization questions


### Method selection

Resolve `selectedMethods` before DTO/mapper resolution. Use caller choices and context first; ask only if unresolved.

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Which CRUD methods to generate? | Methods | Full CRUD (Recommended): GET_LIST, GET_ONE, GET_MANY, CREATE, PATCH, PATCH_MANY, DELETE, DELETE_MANY / Standard CRUD: GET_LIST, GET_ONE, CREATE, PATCH, DELETE / Read-only: GET_LIST, GET_ONE / Custom: select individual methods |

Store `selectedMethods`; downstream mapper requirements are derived from this set, never assumed in advance.

By Step 0 you may already know the DTO mode if the user mentioned it (e.g. "with DTO", "without
DTO", "use entity directly", "map to ProductDto"). If so, skip the question and proceed.

If unknown, ask with the structured-question tool:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Use DTO for mapping? | DTO mode | Yes, use DTO (Recommended): select existing or create new via `quarkus-dto-creator` / No, use entity directly |

### If DTO selected:

Grep for DTO files (`record`/class names containing `{EntityName}Dto` or `{EntityName}RestDto`)
and mapper beans (`@org.mapstruct.Mapper` interfaces, or custom converter classes) related to the
entity.

**If existing DTO + mapper found:** ask the user to select them. Extract:
- `DtoFqn`, `dtoVar`, `dtoVarPlural`
- `MapperFqn` -- FQN of the mapper bean
- `mapperFieldName` -- decapitalized mapper class name
- `toDtoMethodName` -- mapper method entity-->DTO (default per quarkus-mapper-creator: `to${DtoShortName}`, e.g. `toOrderDto`)
- `toEntityMethodName` -- mapper method DTO-->entity (default: `toEntity`)
- `updateEntityMethodName` -- mapper method that copies a DTO into an existing entity (default per quarkus-mapper-creator: `partialUpdate`)

Derive `requiredMethods` only for selected operations: CREATE needs `toEntity` when it consumes a DTO (and `toDtoMethodName` only if its actual response path returns a DTO); PATCH/PATCH_MANY need `toDtoMethodName` and `updateEntityMethodName`. Do not require the update method for unselected PATCH operations. The standalone mapper default is `partialUpdate=false`; never claim otherwise or change that default. For PATCH, hand off entity/DTO FQNs, accessors, mutable scalar fields/types, null semantics, exact required method names, and the safe strategy (`SET_TO_NULL` plus explicit mutable-only mappings). Preserve caller-approved inputs without re-asking. Check existing mapper callbacks/custom logic for protected-field mutation; stop if safety is uncertain.

For PATCH/PATCH_MANY derive the allowlist from entity and DTO sources; exclude id, version, server-managed fields and associations. Ask only about materially ambiguous mutable fields/null semantics. Unsupported field types stop generation.

If no DTO exists for the entity, apply the `quarkus-dto-creator` workflow to create it. Skill activation does not authorize a subagent: mechanically hand off only when the caller/operator and environment permit delegation; otherwise read and follow the skill directly.
That skill handles DTO generation and can hand off to `quarkus-mapper-creator` for the mapper
(conversion is inevitable for a REST resource). After both are created, return here and continue
with the path settings.

**If DTO exists but no mapper:** apply the `quarkus-mapper-creator` workflow with the known entity/DTO contract. Mechanically hand off only when caller/operator and environment permit delegation; otherwise read and follow the skill directly. Then continue here.

### Path, pagination, filter & sort settings

Apply the **Decision-making principle**. These settings almost always have good defaults
derivable from context — use principle 2 (one-line confirmation) unless the user explicitly asked
for customization:

```text
Will create `{EntityName}Resource` in `{resourcePackage}` at `{basePath}/{entityVarPlural}`, page/size pagination, no filter, no total count. OK?
```

The user can answer "ok" / "yes" / silence → accept all defaults; or override specific values →
apply only those overrides.

Only fall back to individual questions when the user explicitly asked for fine-grained control
("custom paths", "configure pagination") or when context yields no clear defaults.

If the user selects a filter: ask for the filterable field(s). Extract `filterFieldName` and
`filterParamName` (default: the field name). Filters are **PanacheQL** fragments — there is no
Specification API in Quarkus; see [`references/panache-queries.md`](../references/panache-queries.md).

If the user selects sorting: extract `sortFieldName` (default: the entity's first non-ID field,
confirmed by the user).

If the user selects total count: GET_LIST returns
`jakarta.ws.rs.core.Response` with an `X-Total-Count` header.

**Transaction placement:** if the project consistently routes writes through `@ApplicationScoped`
service beans, note that this skill generates writes directly on the resource with
`@jakarta.transaction.Transactional` (as in the examples). Ask the user whether to keep
resource-only writes; if they require a service layer, STOP — no service-layer examples exist here.

**Validation:** only generate `@jakarta.validation.Valid` when `hasValidation` is true AND the
annotated parameter's class (entity or DTO) actually carries constraints.

---
