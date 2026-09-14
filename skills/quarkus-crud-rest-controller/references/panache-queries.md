# Panache Queries, Pagination, Filtering, Sorting

Quarkus has no Specification / Criteria-builder API for repositories. All of this skill's
list endpoints use **PanacheQuery** and **PanacheQL** fragments instead.

---

## 1. PanacheQuery basics

`PanacheRepository<T>` provides:

| Call | Returns |
|------|---------|
| `findAll()` | `PanacheQuery<T>` — all rows |
| `find("field = ?1", value)` | `PanacheQuery<T>` — filtered |
| `list("field = ?1", value)` | `List<T>` — filtered, no pagination |
| `listAll()` | `List<T>` |
| `list("id in ?1", ids)` | `List<T>` — collection parameter |
| `count()` | `long` — row count |
| `delete("id in ?1", ids)` | `long` — deleted row count |
| `findByIdOptional(id)` | `Optional<T>` |

PanacheQL fragments are query strings without `SELECT`/`FROM`: `"name = ?1"`,
`"name like ?1"`, `"status = ?1 ORDER BY name"`, `"id in ?1"`.
Positional parameters are 1-based (`?1`, `?2`). Named parameters (`:name`) are also supported.

---

## 2. Pagination

```java
repo.findAll()
    .page(Page.of(pageIndex, pageSize))   // io.quarkus.panache.common.Page
    .list();
```

- `pageIndex` is **0-based** — the first page is `Page.of(0, 20)`.
- `PanacheQuery.page(...)` returns the query (fluent) — assign or chain it.
- A `PanacheQuery` can report pagination state: `pageCount()`, `hasNextPage()`, `nextPage()`,
  `lastPage()`, `firstResult()`/`maxResults()`.

Expose pagination as two query params with defaults:

```java
@QueryParam("page") @DefaultValue("0") int page,
@QueryParam("size") @DefaultValue("20") int size
```

---

## 3. Sorting

```java
import io.quarkus.panache.common.Sort;

repo.findAll()
    .page(Page.of(page, size), Sort.by("name"))          // ascending
    .page(Page.of(page, size), Sort.by("createdAt").descending())
```

If a `sort` query parameter is exposed, **never** pass the raw string through to `Sort.by`
unvalidated — accept only an allow-list of sortable field names and fall back to the default
field otherwise. The examples use a fixed field and do not expose `sort` by default.

---

## 4. Filtering without Specifications

One optional filter — branch between `findAll()` and a PanacheQL query:

```java
PanacheQuery<Product> query = (name == null || name.isBlank())
        ? repo.findAll()
        : repo.find("name like ?1", "%" + name + "%");
```

**Multiple optional filters** — accumulate the fragment and bind every value as a parameter
(never concatenate user input into the query string):

```java
StringBuilder where = new StringBuilder();
Map<String, Object> params = new HashMap<>();

if (name != null && !name.isBlank()) {
    where.append(where.isEmpty() ? "" : " and ").append("name like :name");
    params.put("name", "%" + name + "%");
}
if (status != null) {
    where.append(where.isEmpty() ? "" : " and ").append("status = :status");
    params.put("status", status);
}

PanacheQuery<Product> query = where.isEmpty()
        ? repo.findAll()
        : repo.find(where.toString(), params);
```

`repo.find(query, Map<String, Object>)` binds named parameters — the Map overload is the
parameterized way to bind a dynamic set of named parameters.

---

## 5. Total count

- `repo.count()` — total rows, no filter.
- `query.count()` — rows matching the PanacheQL query, **ignoring pagination** — this is the
  right call for a page's total.
- To expose it without inventing a page DTO, return `jakarta.ws.rs.core.Response` with the
  `X-Total-Count` header:

```java
PanacheQuery<Product> query = repo.findAll().page(Page.of(page, size));
return Response.ok(query.list())
        .header("X-Total-Count", query.count())
        .build();
```

`query.count()` runs an extra `COUNT` query on every request — enable total count only when the
user asks for it.

---

## 6. Transactions

Panache writes (`persist`, `persistAndFlush`, `delete`, entity mutation) require an active
transaction: annotate the write method with `@jakarta.transaction.Transactional`. Mutating a
managed entity inside a transaction is enough — no explicit `save`/`update` call exists in
Panache; changes are flushed on commit.

---

## 7. Traps

- Page index is 0-based; `/api/products?page=1&size=20` is the **second** page.
- `?1` positional parameters bind in order — mismatched order silently returns wrong rows.
- Never build PanacheQL by concatenating user input; always bind values via `?N`, `:name`, or the
  `Map` overload.
- `list("id in ?1", ids)` with an empty collection: an `IN ()` query matches nothing — decide
  explicitly what empty `ids` should return (the examples return an empty list).
- `delete("query", params)` deletes without loading entities — prefer it for DELETE_MANY; it does
  not fire per-entity callbacks/validators.
