# What to exclude from mutation testing

Exclude code with **no behaviour worth asserting on**; keep anything with a branch, a computation or a
decision — even when it is currently untested. A missing test must stay visible in the report; a getter
must not.

## Put the set to the user in one questionnaire

The exclusion set decides what the score means, so it is the user's call rather than a default this
skill imposes silently. Ask with a single structured-question call (your harness's tool — e.g.
`AskUserQuestion` / `ask_user_question`; a numbered list is the fallback), not one question per turn.
Drop a question the request already answers.

Only the last column reaches the user — the `Becomes` column is for you. Every description has to name
the patterns it will write: approving "configuration wiring" is not approving globs nobody was shown.

**Q1 · header `Noise`** · `multiSelect: true` — code that carries no behaviour to assert on. Recommend
all three: without them the first report is dominated by mutants nobody would ever write a test for,
and a report read once is a report abandoned.

| Option | Becomes | Description to show the user |
|--------|---------|------------------------------|
| Configuration wiring | `excludedClasses = ['*Config', '*Configuration', '*Properties']` | Configuration mapping classes and wiring, not behaviour — nobody tests how a config bean is assembled. Excludes `*Config`, `*Configuration`, `*Properties`. |
| Mappers and other generated code | `excludedClasses = ['*MapperImpl', '*_']` | Written by a code generator, so testing it tests the generator. Excludes `*MapperImpl` (MapStruct) and `*_` (JPA metamodel). |
| Accessors and Object boilerplate | `excludedMethods = ['equals', 'hashCode', 'toString', 'get*', 'set*', 'is*']` | A getter just hands back a field. Excludes `equals`, `hashCode`, `toString`, `get*`, `set*`, `is*` — which also skips real logic named that way, like `getDiscountedPrice()`. |

**Q2 · header `Layers`** · `multiSelect: true` — which layers should be left out of the measured set,
because their tests are `@QuarkusTest`/`*IT` suites that cannot drive PIT? Selecting one narrows
`targetClasses`: the score then describes the part of the code the driving suite is actually responsible
for, and the report names what was left out. Left in, such a layer counts as untested however well
tested it is.

| Option | What marks the layer | Description to show the user |
|--------|----------------------|------------------------------|
| REST resources | `@Path` classes / `*Resource` | Tested by HTTP tests that boot the application — slow suites that are not driving this analysis, so they report as untested. Drops `*Resource` from `targetClasses`. |
| Panache repositories | `*Repository` | Usually an interface with no code of yours to change, where the mutation run is a no-op; concrete repos with real query logic are worth keeping — check before excluding. |

**Q3 · header `Annotation`** — a marker annotation lets a single class or method be skipped from the
code itself, which is the only way to carve out something no name pattern captures. Offer to create one.

| Option | Becomes | Description to show the user |
|--------|---------|------------------------------|
| Add `@DoNotMutate` (Recommended) | a `DoNotMutate` annotation in the project's root package; no PIT setting needed | Creates a `DoNotMutate` annotation in your root package; mark a class or a method with it. No build setting needed. |
| Add one under a name I will type | the same annotation under that name, plus a `features` entry registering it | Same, under a name you type here. Also adds a `features` entry to the PIT config registering that name. |
| Skip it | nothing | No annotation is created. Exclusions stay in the build file only, all visible in one place. |

```java
package org.acme;

@Retention(RetentionPolicy.CLASS)   // RUNTIME works too; SOURCE is invisible to PIT
@Target({ElementType.TYPE, ElementType.METHOD})
public @interface DoNotMutate {
}
```text

`DoNotMutate`, `Generated` and `CoverageIgnore` are recognised by PIT with no configuration at all,
which is why the first option needs none. A name of your own has to be registered, and the parameter
**replaces** those three rather than adding to them — dropping them stops `@DoNotMutate` from working,
with no error, just a moved score:

```xml
<features>
  <param>+fann(annotation[TypedName] annotation[DoNotMutate] annotation[Generated] annotation[CoverageIgnore])</param>
</features>
```

The same setting on Gradle: `features = ['+fann(annotation[TypedName] annotation[DoNotMutate] annotation[Generated] annotation[CoverageIgnore])']`.

If that option comes back without a name, ask for it in one short follow-up. Never invent one: an
annotation the user did not name is a class they did not ask for.

## After the answers

Write the chosen globs into the PIT config, grouped by the question they came from, so a later reader
can tell which entries were a decision about noise and which were a decision about what is being
measured.

## Judging a single candidate (a question, or a change request)

**Reject the candidate** — stop and say so, do not add the entry — when it:

- **has a branch, a computation or a decision.** That is what mutation testing is for. Untested logic
  must stay visible in the report; excluding it to tidy up the score is the one move this rule exists
  to prevent. Services, validators, filters and interceptors belong here — only their accessors are noise;
- is covered by a PIT default filter (a record, an enum, a generated accessor);
- is outside `targetClasses` already, so it was never mutated;
- is matched by an existing glob. Check the glob, not the class name: `*Config` matches only names
  ending in `Config`, so `ConfigLoader` is NOT covered by it.

**Choose the narrowest form that works** — everything in this table removes the mutant from the report:

| Mechanism | Unit | Effect |
|-----------|------|--------|
| `targetClasses` | glob on the FQN | the inclusion boundary — anything outside is never mutated |
| `excludedClasses` | glob on the FQN | subtracts from `targetClasses`: one class, or a whole package (`org.acme.web.*`) |
| `excludedMethods` | glob on the method name | the same method across every class, which is how accessors are handled |
| a marker annotation | class or method | carves out a single element from the code itself |
| `mutators` | mutation operator | drops a kind of mutant rather than a piece of code |

Match the candidate to the narrowest one that fits:

| Candidate | Form |
|-----------|------|
| a whole class with no behaviour worth asserting | `excludedClasses` glob |
| accessors or `Object` boilerplate across many classes | `excludedMethods` glob |
| one method inside a class that must stay mutated | a marker annotation on that method |
| a whole layer the driving suite cannot reach | narrow `targetClasses` — and say which layers that leaves unmeasured |

Prefer a glob over listing classes one by one only when the name pattern is the reason for exclusion
(`*MapperImpl`). A glob chosen for brevity will silently swallow the next class that happens to match.

## Apply, then measure the delta

Keep the per-class numbers from the run before the edit, apply the change, re-run, and compare: the
target class or method must be gone from the report, and **no other class may lose mutants**. If the
total mutant count dropped by more than the target accounts for, the glob is too wide — narrow it and
measure again.

Last: update the memory entry's `mutated` line (`references/configuration.md` §5) so the next run does
not start from a stale description.
