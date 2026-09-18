# CRUD customization workflow

## Step 4 -- DTO and customization questions

Tell the user: `Step 4/6: Resolving DTO and customization...`

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

Warn: CREATE, PATCH and PATCH_MANY require the mapper to have `toEntity` and
`updateEntityMethodName` (the latter copying into an existing entity) methods in addition to `toDtoMethodName`.
quarkus-mapper-creator generates exactly this set with its defaults — keep the method names
consistent between the two skills.

**If no DTO exists for the entity:** delegate to the `quarkus-dto-creator` skill to create one.
That skill handles DTO generation and can hand off to `quarkus-mapper-creator` for the mapper
(conversion is inevitable for a REST resource). After both are created, return here and continue
with the path settings.

**If DTO exists but no mapper:** delegate to `quarkus-mapper-creator` to create one. After the
mapper is created, return here and continue.

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

### Method selection

By Step 0 you may already know which methods the user wants (e.g. "read-only", "only GET and
CREATE", "full CRUD"). If so, skip the question.

If unknown, ask with the structured-question tool:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Which CRUD methods to generate? | Methods | Full CRUD (Recommended): GET_LIST, GET_ONE, GET_MANY, CREATE, PATCH, PATCH_MANY, DELETE, DELETE_MANY / Standard CRUD: GET_LIST, GET_ONE, CREATE, PATCH, DELETE / Read-only: GET_LIST, GET_ONE / Custom: select individual methods |

Store the selected method set as `selectedMethods`. Step 5.3 generates only these methods,
skipping the rest.

---
