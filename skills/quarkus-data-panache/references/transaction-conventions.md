# Transaction Conventions and Rules

Two parts: **detection** (substeps 3.1–3.5 — run them before writing code) and **implementation rules**.

---

# Part A — Detection

Tell the user which substep you are on while running them: `Step 3.1/3.5: Finding transaction boundaries...`.

## Step 3.1: Find existing transaction usage

Grep for `jakarta.transaction.Transactional` and `Transactional` imports across `src/main/java`. For each
hit, note the annotated method's enclosing class and layer (resource / service / repository / other), and
whether the method is a read or a write path. Read 2–3 annotated methods in full.

## Step 3.2: Score each convention

- **Placement layer** — where does `@Transactional` sit: JAX-RS resource methods, CDI service methods,
  repository methods, or mixed? Default: service methods for multi-step units of work; a single-step CRUD
  resource method may carry the annotation directly. Repository methods never carry it
- **Annotation scope** — class-level `@Transactional` or method-level? Default: method-level (class-level
  makes read paths transactional implicitly)
- **Read paths** — are read-only methods annotated too? Default: no — reads do not need a transaction;
  annotate only write paths
- **TxType usage** — plain `@Transactional` (REQUIRED) or explicit types
  (`REQUIRES_NEW`, `NOT_SUPPORTED`, ...)? Default: plain `@Transactional`; a nested `REQUIRES_NEW` boundary
  is only justified when the project already uses one
- **Unit of work** — does one transaction wrap the whole operation (all Panache writes together) or does
  each repository call manage its own? Default: one transaction around the whole unit of work

## Step 3.3: Collect uncertain conventions

Score confidence only where examples exist but are ambiguous or inconsistent. Absent usage — confidence is
high, use the defaults. Collect all conventions with confidence < 80.

## Step 3.4: Ask developer

If there are uncertain conventions from step 3.3, ask in a single prompt — use your harness's
structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`); fall back to a numbered plain-text
list if none is available.

Example shape — adapt to what you found:

```json
{
  "questions": [
    {
      "header": "Tx placement",
      "question": "Where do transaction boundaries live in this project?",
      "multiSelect": false,
      "options": [
        { "label": "Service methods (Recommended)", "description": "Multi-step units of work are annotated on the service bean" },
        { "label": "Resource methods", "description": "@Transactional sits on the JAX-RS resource method" },
        { "label": "Mixed", "description": "Both layers carry annotations depending on the operation" }
      ]
    }
  ]
}
```

## Step 3.5: Summarize resolved conventions

Do NOT call any tools in this step — reason only from what you read and what the developer confirmed.

Output the full list of conventions from step 3.2 with the real project values filled in. This list is your
working contract for transactional code written in this session.

---

# Part B — Implementation Rules

## The annotation

```java
import jakarta.transaction.Transactional;

@Transactional
public OrderDto createOrder(OrderDto dto) {
    // ... multiple Panache writes, all in one transaction
}
```

- Import from `jakarta.transaction` — never from a framework-specific package (check the import line you add)
- The default (REQUIRED) semantics join an ongoing transaction or start one — the plain annotation covers
  almost every case; add an explicit `TxType` only to match an existing project pattern

## Placement rules

- Every Panache write (`persist`, `persistAndFlush`, `update`, `delete`, `flush`) runs inside an active
  transaction — annotate the **outermost** method of the unit of work, not each repository call
- One unit of work = one transaction: if an operation performs several writes, they belong to the same
  annotated method so a failure rolls the whole operation back
- Reads do not need a transaction — but lazy-loaded relations must be resolved inside one (or fetched with a
  join) before the entity leaves the boundary, otherwise `LazyInitializationException` follows
- Repository methods never carry `@Transactional`; the boundary belongs to the resource/service layer
- Class-level `@Transactional` is a last resort — it silently wraps read paths too; prefer method-level

## Interceptor caveat (CDI)

`@Transactional` is applied by a CDI interceptor. A call from one method to another annotated method **on the
same bean** bypasses the interceptor and no transaction starts. If the unit of work lives in a service bean,
either:

- annotate the entry method and keep all work inside it, or
- move the transactional logic into a separate CDI bean and inject it

Never rely on self-invocation for a transaction boundary.

## Boundaries and long transactions

- Keep remote calls (HTTP clients, messaging) outside the transaction — do not hold a database transaction
  open across network I/O
- Resolve everything the response needs (relations, DTO mapping) before the annotated method returns
- Do not open a transaction in a `@Incoming` consumer method just to read; only write paths need one

## Reactive projects

If the project uses `quarkus-hibernate-reactive-panache`, read [`reactive.md`](reactive.md) before adding
transaction boundaries — blocking-style assumptions do not translate onto the event loop.

## What not to do

- Do not manage transactions manually (`UserTransaction` begin/commit) when annotation interception is
  available — only keep manual control if the project already uses it
- Do not annotate getters, mappers, or DTO conversion methods
- Do not add `@Transactional` to a method that performs no writes
