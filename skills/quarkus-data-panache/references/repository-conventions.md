# Repository Conventions and Rules

Two parts: **detection** (substeps 2.1–2.5 — run them before writing code) and **implementation rules**
(applied after the conventions are resolved).

---

# Part A — Detection

Tell the user which substep you are on while running them: `Step 2.1/2.5: Finding existing repositories...`.

## Step 2.1: Find existing repositories

Grep for `PanacheRepository` across `src/main/java`. Pick 2–3 representative classes and read them in full.
If none exist (the project uses Active Record only), score the "repository style" convention as absent —
confidence is high, use the defaults, and skip to Part B when a repository is actually needed.

## Step 2.2: Score each convention

- **Base interface** — `PanacheRepository<Entity>` (fixes the ID type to `Long`) or
  `PanacheRepositoryBase<Entity, ID>` (custom ID type, e.g. `UUID`)? Default: match the entity's id type —
  `PanacheRepository` for `Long`, `PanacheRepositoryBase` otherwise
- **CDI scope** — is the repository annotated `@ApplicationScoped`? Default: `@ApplicationScoped` (required
  for injection into resources/services)
- **Injection style** — `@Inject` field or constructor parameter? Default: match the project; constructor
  injection is idiomatic in Quarkus (no extra no-args constructor is needed)
- **Query parameter style** — positional (`"name = ?1"`) or named (`"name = :name"` with a `Map`)?
  Default: positional for a single parameter; named `Map.of(...)` for several
- **Single-result return style** — `Optional<Entity>` via `firstResultOptional()` or nullable via
  `firstResult()`? Default: `Optional`
- **Method naming** — `findByXxx` / `listByXxx` / `countByXxx`? Default: match the project; if none exists —
  `findByXxx` for single results, `listByXxx` for collections, `countByXxx` for counts
- **Ordering** — `Sort` argument (`Sort.by("name")`) or inline `ORDER BY` in the query string? Default: `Sort`
- **Pagination exposure** — repository returns a `PanacheQuery<Entity>` for the caller to page, or takes page
  parameters and returns a list? Default: match the project; if none exists — return `PanacheQuery` for list
  endpoints and let the resource apply `Page.of(index, size)`
- **Native/named queries** — does the project use native queries (`#` prefix / `@NamedQuery`) alongside
  PanacheQL? Default: no — PanacheQL only, unless the project already does otherwise

## Step 2.3: Collect uncertain conventions

Score confidence only for conventions where the code contains relevant examples but the pattern is ambiguous
or inconsistent. If a convention is absent from the code — confidence is high, use the default without asking.
Collect all conventions where confidence < 80.

## Step 2.4: Ask developer

If there are uncertain conventions from step 2.3, ask the developer in a single prompt — use your harness's
structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`); if none is available, fall back to a
numbered list in plain text.

Example shape — adapt to what you actually found:

```json
{
  "questions": [
    {
      "header": "Pagination",
      "question": "How do repositories expose pagination?",
      "multiSelect": false,
      "options": [
        { "label": "Return PanacheQuery (Recommended)", "description": "The resource applies Page.of(index, size)" },
        { "label": "Page parameters", "description": "Repository takes page/size and returns the materialized list" }
      ]
    },
    {
      "header": "Return style",
      "question": "How is a not-found single result returned?",
      "multiSelect": false,
      "options": [
        { "label": "Optional (Recommended)", "description": "firstResultOptional() — callers handle empty explicitly" },
        { "label": "Nullable", "description": "firstResult() — may return null" }
      ]
    }
  ]
}
```

## Step 2.5: Summarize resolved conventions

Do NOT call any tools in this step — reason only from what you read and what the developer confirmed.

Output the full list of conventions from step 2.2 with the real project values filled in. This list is your
working contract for repository code written in this session.

---

# Part B — Implementation Rules

## Class skeleton

```java
package org.acme.repository;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class PersonRepository implements PanacheRepository<Person> {

    public Optional<Person> findByName(String name) {
        return find("name", name).firstResultOptional();
    }

    public List<Person> findAlive() {
        return list("status", Status.Alive);
    }

    public long countAlive() {
        return count("status", Status.Alive);
    }
}
```

For a non-`Long` identifier use `PanacheRepositoryBase<Person, UUID>` instead — the query API is identical.

## Query API available on `PanacheRepository` / `PanacheRepositoryBase`

| Method | Returns | Notes |
|---|---|---|
| `find(query, params...)` | `PanacheQuery<Entity>` | lazy — apply `.firstResultOptional()`, `.list()`, `.count()`, `.page(...)` |
| `list(query, params...)` | `List<Entity>` | eager |
| `count(query, params...)` | `long` | eager |
| `delete(query, params...)` | `long` | affected rows; requires a transaction |
| `update(query, params...)` | `long` | affected rows; requires a transaction |
| `findById(id)` | `Entity` or `null` | use `findByIdOptional(id)` for an `Optional` result |
| `listAll()` | `List<Entity>` | eager |
| `persist(entity)` | `void` | requires a transaction |
| `persistAndFlush(entity)` | `void` | flushes immediately — use when the id is needed at once |
| `delete(entity)` | `void` | requires a transaction |
| `flush()` | `void` | requires a transaction |

Use the `Optional` variants (`firstResultOptional`, `findByIdOptional`) when the project's return style is
`Optional` — do not wrap nullable results manually.

## Query rules

- Bind every value; never concatenate input into the query string
- Positional: `find("status = ?1 and name = ?2", status, name)`
- Named: `find("name = :name and status = :status", Map.of("name", name, "status", status))`
  (`java.util.Map`)
- Ordering: extra `Sort` argument — `list("status", Sort.by("name").descending(), status)`
- Pagination: `find("status", status).page(Page.of(index, size)).list()` — `Page.of` is 0-based;
  `query.count()` gives the total for building a page response
- Prefer returning `PanacheQuery<Entity>` when the caller (resource) decides page size, so the repository does
  not need page parameters
- Keep repository methods focused: one query per method; put multi-query orchestration in a service bean

## Transactions

Repository methods do not open transactions by themselves. Every write path must run inside an active
transaction — annotate the outermost resource or service method with `jakarta.transaction.Transactional`;
see [`transaction-conventions.md`](transaction-conventions.md) for placement rules.

## What not to do

- Do not call `getEntityManager()`/native SQL when a PanacheQL query expresses the same thing
- Do not add repository methods that duplicate Panache built-ins (`findById`, `listAll`, `count()` without a
  query, `deleteById`)
- Do not mix Active Record statics and repository methods for the same entity unless the project already does
