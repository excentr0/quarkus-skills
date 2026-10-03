# DTO interaction workflow

## Step 0 — Conversation context first (REQUIRED, no tool calls)


Before any file read, before any question, **re-read the user's prompt and the prior turns of this
conversation** and extract whatever is already stated. This step costs nothing and prevents the most
common failure mode of this skill — asking the user something they already said.

Build a mental checklist of inputs and tick off everything the user has already provided, explicitly
or implicitly:

| Input | Look for in the prompt / context |
|---|---|
| **entity** | a class name (`Order`, `Customer`, `ScheduleTemplate`); "for X"; an open file; a file path; a recently discussed entity in this conversation |
| **purpose** | "for REST", "for API", "for mapping", "projection", "for service" — drives field selection and the mapper question |
| **fields** | "all fields", "only id and name", "without password", "with associations", "flat" |
| **variant** | "record", "plain class", "immutable", "with setters" |
| **mapper** | "and mapper", "with mapper", "only DTO", "no mapper" |
| **className** | "name it `OrderSummaryDto`", "class `Foo`" |
| **package** | "in package `…`", "next to the resource" |
| **smart defaults** | "use defaults", "all defaults", "default settings", "as usual" |
| **sub-DTO shape** | "nested", "separate class", "only id", "flat" |
| **prior project facts** | extensions, persistence mode, DTO style — already known if discussed earlier in this conversation; do not re-fetch |

For every input that is **explicitly or strongly implicitly answered**: mark it as decided and skip the
corresponding question in Steps 2–7. Do NOT ask "what entity?" if the user wrote "create DTO for
Order" — `Order` is the answer. Do NOT ask "record or class?" if the user wrote "make a record for
Order" — record is the answer.

Do not attribute a caller-supplied task contract or plan to the user as a statement of intent. However, explicit constraints and already-approved decisions in that contract are authoritative workflow inputs: preserve them and do not re-ask them. Ask only when an actual user-intent choice remains unresolved.

Step 0 is internal context gathering; do not announce it as a mechanical progress step.

---
## Step 3 — Attribute selection


**Default: include every scalar attribute and every association** (with the sub-DTO defaults from
[`references/sub-dto.md`](../references/sub-dto.md)). Ask only when context signals that the user wants something narrower.

### Decide from context (preferred over asking)

Use the **purpose** captured in Step 0 to pick a sensible default set:

| Purpose signal | Default field set |
|---|---|
| "for REST", "for API", "for response" | all scalars + all associations expanded (NEW_NESTED_CLASS for ToMany, FLAT id for ToOne) — the response shape, including related data |
| "projection", "summary", "list view", "for list" | scalars only, ToOne associations as Flat id, ToMany excluded |
| "for mapping", "for service", "for storage" | all scalars + all associations expanded |
| "only id and name" / explicit field list | exactly what the user named, nothing else |
| no purpose signal | all scalars + all associations expanded (richest reasonable default) |

If the chosen default matches the user's apparent intent, **do not ask**. Just generate. State the
choice in the one-line confirmation form (principle 2) at most.

### When to ask

Ask only if:
- the user explicitly said "choose fields" / "ask about fields" / "fine-tune settings", OR
- the entity has many fields, the purpose signal is ambiguous, AND the user did not say "use defaults".

When asking, use the structured-question tool with `multiSelect: true`:

| Question | Header | Options (first = recommended) |
|----------|--------|-------------------------------|
| Which fields to include in DTO `${Entity}Dto`? | Fields | All fields + associations (Recommended) / Scalars only / Only id and name / Specify manually |

For each **association** included, apply the sub-DTO defaults from [`references/sub-dto.md`](../references/sub-dto.md). Do NOT ask
per-association unless the user explicitly requested fine-grained control. Per-field overrides
(rename, extra/removed validations) live in [`references/generation-workflow.md`](../references/generation-workflow.md)
and [`references/validation.md`](../references/validation.md).

---
## Step 4 — Variant selection


Apply the **Decision-making principle** from [`SKILL.md`](../SKILL.md) (context first, then ask). The variant is almost always derivable from context —
explicit asking should be the exception, not the default.

| Context | Action | Variant |
|---|---|---|
| Project's existing DTOs are records, user gave no mutability signal | decide silently | [`references/java-record.md`](../references/java-record.md) |
| Project's existing DTOs are plain classes | decide silently (project convention wins) | [`references/java-plain.md`](../references/java-plain.md) |
| User explicitly said "record" | decide silently | [`references/java-record.md`](../references/java-record.md) |
| User explicitly said "plain class" / "mutable" / "with setters" | decide silently | [`references/java-plain.md`](../references/java-plain.md) |
| User explicitly said "Lombok" | see [`references/lombok-note.md`](../references/lombok-note.md) — follow the project's existing Lombok style if any; do not invent an annotation set | project style |
| No signal at all, no existing DTOs in the project | decide silently (record is the Quarkus default) and mention it in the one-line confirmation from principle 2 | [`references/java-record.md`](../references/java-record.md) |

Only fall back to the full numbered question when **none** of the rows above matches AND the user has
not said "use defaults". Even then, prefer the "all variants with the default marked" format from
principle 3 over an iterative question.

Map the answer to a variant:
- record → [`references/java-record.md`](../references/java-record.md)
- plain class → [`references/java-plain.md`](../references/java-plain.md)
- Lombok → [`references/lombok-note.md`](../references/lombok-note.md)

---
## Step 5 — Variant-specific questions


Follow the variant-specific questions from the selected reference file. Only ask if the user did NOT say
"all defaults". Records need essentially no questions (immutability is built in); plain-class questions
are batched per [`references/java-plain.md`](../references/java-plain.md).

---
