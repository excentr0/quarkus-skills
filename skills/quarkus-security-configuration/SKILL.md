---
name: quarkus-security-configuration
description: >
  Configures Quarkus security: authentication via OIDC (bearer tokens for APIs, authorization code
  flow for web apps) or MP-JWT, path-based HTTP permissions, and role-based authorization with
  @RolesAllowed / @Authenticated / SecurityIdentity.
  Use this skill when security needs to be created or changed: adding authentication to a REST API,
  securing endpoints by path or role, connecting quarkus-oidc to an identity provider, or explaining
  why a request returns 401/403.
  Triggers on explicit requests: "configure security", "add authentication", "add authorization",
  "secure the API", "add login", "set up OIDC", "set up Keycloak", "restrict endpoint to role".
  Russian phrases also trigger this: "настрой security", "добавь аутентификацию", "защити API",
  "настрой OIDC", "настрой Keycloak", "ограничь доступ по ролям".
---

# Preflight — Project detection (before step 0)

This skill is harness-agnostic: it uses only file tools and shell commands — no MCP server
or IDE integration is required.

Detect the project shape from the build files:

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import in `pom.xml`,
   version property `quarkus.platform.version` / `quarkus.version`; Gradle: `io.quarkus` plugin + `quarkusPlatform` version.
3. **Security extensions already present** — `quarkus-oidc` (OIDC), `quarkus-smallrye-jwt` (MP-JWT),
   `quarkus-security` (core annotations). Record extension presence separately from ordinary build
   dependencies; add only the missing Quarkus extensions with the detected Maven/Gradle command.
4. **Config file and format** — detect `src/main/resources/application.properties` or
   `application.yaml`/`application.yml`. If YAML is present, verify `quarkus-config-yaml` in the
   build; if it is missing, **STOP**. If both formats exist, identify the authoritative file or ask
   before writing. Generate properties syntax only for `.properties`, or nested YAML for YAML.
5. **Existing security configuration** — read the detected config file for `quarkus.oidc.*`,
   `quarkus.http.auth.*` keys; grep for `@RolesAllowed` / `@Authenticated` in `src/main/java`.
6. **Persistence stack** — only needed when the user's task also touches entities; security
   configuration itself does not depend on it.

If the project is not a Quarkus application (no Quarkus BOM/plugin in the build file) — stop and
tell the user this skill targets Quarkus projects.

---

# Quarkus Security Configuration

Configures authentication and authorization for a Quarkus application:

- **`application.properties`** — provider connection (`quarkus.oidc.*`) and path permissions
  (`quarkus.http.auth.permission.*`, `quarkus.http.auth.policy.*`).
- **Annotations on JAX-RS resources** — `@RolesAllowed`, `@Authenticated`, `@PermitAll`.

Quarkus has **no central security configuration class**: there is no filter chain and no
security-config bean to generate. This skill writes properties and annotations only. Generating a
configuration class is always wrong.

---

> **CRITICAL: Configuration ONLY from examples/ files. If no matching example -- STOP and ask user.**
> **CRITICAL: NEVER generate a security configuration class, filter chain, or security bean. Quarkus security is properties + annotations.**
> **CRITICAL: For questions with a fixed set of choices, prefer your harness's structured-question tool (e.g. `AskUserQuestion` / `ask_user_question`) > plain text list. Plain numbered text lists are the last resort when no interactive tool is available.**
> **CRITICAL: Read the conversation context BEFORE running Step 1.** Half the questions in Steps 2–3 may already be answered by the user's prompt and prior turns. Re-asking what was already said is the #1 reason this skill feels slow.

---

## Defaults

| Option | Default | Always ask? | Notes |
|--------|---------|-------------|-------|
| Authentication type | — | YES | main branching |
| Provider | Keycloak | NO | Dev Services can run Keycloak automatically in dev/test |
| Protected paths | `/*` → `authenticated` | NO | longest path wins; public paths get a separate `permit` rule |
| Role restrictions | none | NO | only when the user names roles |
| Permission/policy names | derived from the path segment (`api`, `admin`) + suffix | NO | e.g. `api-authn`, `admin-roles` |
| `auth-server-url` | existing config or user answer | YES for new config | free-form value, asked in plain text |
| `client-id` | existing config or user answer | YES for new config | free-form value, asked in plain text |
| Client secret | never asked | — | emitted as `${OIDC_CLIENT_SECRET}` env placeholder (see Secret handling) |
| Quarkus version | from the build file | NO | auto-detected |
| Language | Java | NO | Java-first repo |

**Smart defaults:** If user says "use defaults", "all defaults", "default settings",
or similar -- skip ALL questions where "Always ask?" = NO. Only ask mandatory questions.

**Smart answer recognition:** When user provides a value instead of choosing from a numbered
list, accept it directly. Examples:
- Question "Authentication type?" -> user answers "bearer" -> this IS the choice, don't show options
- Question "Client ID?" -> user answers "my-api" -> this IS the value, don't re-ask
- If user provides multiple answers in one message -> accept all, skip answered questions
- NEVER ask a question that the user already answered (even implicitly)

**Batch questions:** Group closely related questions into a single structured-question call
(up to 4 questions per call) when they:
- Belong to the same logical section (e.g. both are provider connection settings)
- Don't depend on each other's answers
- Have obvious defaults that the user can skip

Rules:
- Maximum **3-4 questions** per structured-question call
- Mark the recommended option with `(Recommended)` and place it first
- Never batch questions from DIFFERENT decision branches
- The primary branching question (authentication type) is always asked ALONE
- Prefer the structured-question tool for choices; fall back to plain text lists only if it is unavailable

---

## Decision-making principle — context first, then ask

Before asking the user **any** question, attempt to derive the answer from the context already
gathered: the build file, existing `application.properties`, existing resources and annotations,
prior turns of this conversation, and the user's original prompt. Only ask when the context yields
**no clear default** or when the choice is genuinely user-specific (authentication type, provider
URL, path rules, roles).

Hierarchy of decisions:

1. **Context is unambiguous → decide silently, do NOT ask.**
   Examples: Quarkus version from the build file; build system from the wrapper; existing
   `quarkus.oidc.*` values from the properties file; resource paths from `@Path` annotations;
   role names from existing `@RolesAllowed` usages; language = Java.

2. **Context gives a strong signal → state the decision + alternatives in one line, let the user override or stay silent.**
   Format:
   ```
   Will configure OIDC bearer-token authentication with Keycloak (quarkus-oidc is already in the build file).
   Alternatives: OIDC authorization code flow (web app), MP-JWT legacy. OK?
   ```
   The user can answer "ok" / "yes" / silence → accept; or name an alternative → switch.

3. **Context yields no clear default → ask with the structured-question tool, with the recommended option first.**
   Mark the recommended option with `(Recommended)` in its label and place it first. If no
   interactive choice tool is available, fall back to a plain text list.

4. **Context is fully empty for a critical input → ask plainly.**
   This applies to: authentication type (when no security extension hints at it),
   `auth-server-url`, `client-id`, path rules, roles.

### How to ask — prefer the structured-question tool

When a question must be asked, prefer the harness's structured-question tool over writing a
numbered list in the response body. Fall back to plain text only if no interactive choice tool
is available.

Rules for structured-question calls in this skill:

- Each call may contain up to **4 questions** that are independent of each other. Use this to
  batch related decisions in one round-trip.
- Each question has **2–4 options**. The tool auto-adds an "Other" choice for free-form input —
  never include it manually.
- Mark the recommended option by putting it **first** with `(Recommended)` appended to the label.
- `header` is a short chip label (e.g. "Auth Type", "Paths", "Roles").

When the structured-question tool is **not** the right tool:
- Free-form input with no enumerable set of options (e.g. provider URL, client ID, realm name,
  path patterns, role names) — ask in plain text.
- The "single confirmation line" from principle 2 — that is a plain yes/no, not an enumerated choice.

### Secret handling

**NEVER ask the user for credentials of any kind** (client secret, password, API key, token) —
not via the structured-question tool, not in plain text, not in any form. Secret values must not
enter the conversation. The env-var expansion `${OIDC_CLIENT_SECRET}` is written into `application.properties` and the
placeholder name is reported to the user after generation — see the "Client secret handling"
section of the variant's properties example.

The question lists in Steps 2–3 and in reference files are a **fallback** for case 4. They are
NOT a script to execute top-to-bottom. If a question's answer is already determined by
principles 1–3, **skip the question**.

For the exact placeholder shape, see each example's `## Variables` table and the "Client secret
handling" section of the variant's properties example (linked in Step 4).

---

## Step 0 -- Conversation context first (REQUIRED, no tool calls)

Before any file read or question, re-read the user's prompt and prior turns. Mark authentication,
provider, client, paths, roles, defaults, and prior project facts that are already answered; never
re-ask them. Read [`references/variant-selection.md`](references/variant-selection.md) for the full
context checklist before Steps 2–3.

- **NEVER ask a question that the user already answered (even implicitly).**

---

## Step 1 -- Gather context (automatic, no questions)

Tell the user: `Step 1/5: Gathering project context...`

Call **file tools** (in parallel where possible). Do NOT call MCP tools.

| Tool call | What to extract | Variable names |
|------|----------------|---------------|
| read the build file (`pom.xml` / `build.gradle` / `build.gradle.kts`) | Quarkus version, security extensions present (`quarkus-oidc`, `quarkus-smallrye-jwt`, `quarkus-security`), build file type, number of modules | quarkusVersion, buildFile, presentExtensions |
| glob `src/main/resources/application.{properties,yaml,yml}` | path(s) to the config file | propsFile |
| read the detected config file | existing `quarkus.oidc.*`, `quarkus.http.auth.*` keys — **redact secret values** | existingAuthConfig |
| grep `@Path` in `src/main/java` | resource classes and their base paths | resources |
| grep `@RolesAllowed`, `@Authenticated`, `@PermitAll`, `@DenyAll` in `src/main/java` | existing annotations and role names in use | existingAnnotations, existingRoles |
| grep `SecurityIdentity`, `JsonWebToken` in `src/main/java` | existing identity/token injection usage | existingIdentityUsage |

- **Secret redaction:** if any config value looks like a credential (`secret`, `password`,
  `token`, `key` keys), replace only the value with `[REDACTED]` before it enters the report. During
  verification report only the key, profile, and status (`set`, `missing`, or `not checked`), never
  the resolved value.
- If multi-module project (more than one module in the build file): ask which module to use,
  then re-read the module-specific build file and config file.
- If `existingAuthConfig` is not empty:
  - Warn user: "Project already configures security: {keys}. Extend it or replace it?"
  - If the user chooses **extend** — merge: keep existing keys, add only missing ones, never
    duplicate a key.
  - If the user chooses **replace** — show the keys that will be overwritten and confirm before writing.
- If `existingRoles` is not empty — use those role names to suggest values when asking about
  role restrictions in Step 3.
- If the same `@Path` resource is already annotated with security annotations — note it, and
  do not re-annotate without asking.

---

## Step 2 -- Authentication type

Tell the user: `Step 2/5: Choosing authentication type...`

Read [`references/variant-selection.md`](references/variant-selection.md) for the authentication
matrix. Select OIDC bearer, OIDC web-app/code flow, or MP-JWT from explicit user intent/context; ask
only when the type is genuinely unresolved.

---

## Step 3 -- Variant-specific questions (inline)

Tell the user: `Step 3/5: Collecting variant settings...`

Read [`references/variant-selection.md`](references/variant-selection.md) for the selected variant's
question matrix and ask only unresolved settings. **NEVER ask the user for credentials**; use the inline
secret-handling rules above.

---

## Step 4 -- Generate configuration

Tell the user: `Step 4/5: Generating configuration...`

**No class is generated.** Quarkus security is configuration (properties) plus annotations
on existing resources. Do not create new Java classes unless the user explicitly asks for a
custom mechanism (out of scope — ask instead).

1. Read the variant reference file. Collect: property blocks, annotation fragments, permission rules.

2. Compose the configuration from the variant's example. Write to the detected config file:
   use the properties block unchanged for `application.properties`, or translate it into nested YAML
   for `application.yaml`/`application.yml`. If the selected format cannot be supported safely,
   stop rather than writing a properties block into a YAML file.

   Compose the properties from the variant's properties example:
   [`oidc-service`](examples/_properties/oidc-service/properties.md),
   [`oidc-web-app`](examples/_properties/oidc-web-app/properties.md), or
   [`smallrye-jwt`](examples/_properties/smallrye-jwt/properties.md):
   - Apply variable substitutions (ONLY variables declared in the Variables section)
   - Include ONLY the lines that match the user's chosen options — skip commented-out optional lines
     whose condition is not met

3. Build the path permission rules (see [`references/common-rules.md`](references/common-rules.md) → Path permissions):
   - Public paths -> a `permit` rule (`quarkus.http.auth.permission.{name}.paths={paths}`,
     `.policy=permit`)
   - Everything else -> an `authenticated` rule on `/*`
   - Role-restricted paths -> a named policy: `quarkus.http.auth.policy.{policy}.roles-allowed={roles}`
     referenced by `quarkus.http.auth.permission.{name}.policy={policy}`
   - **Permission precedence is by longest matching path, NOT by order in the file.** Never claim that
     moving a block changes precedence. When two rules tie on path length, the more restrictive one
     applies (method-specific rules beat rules without methods).

4. Apply annotation fragments to the resources the user wants restricted:
   - Read the fragment for each feature the user's rules need — available fragments:
     [`roles-allowed`](examples/_annotations/roles-allowed/java.md),
     [`authenticated-and-permit`](examples/_annotations/authenticated-and-permit/java.md),
     [`identity-injection`](examples/_annotations/identity-injection/java.md),
     [`jwt-injection`](examples/_annotations/jwt-injection/java.md)
   - Add the annotation **and its import** to the resource class or method that the user targeted
   - Include ONLY the fragments that match the user's rules (e.g. `@RolesAllowed` only when roles
     were specified; `JsonWebToken`/`SecurityIdentity` injection only when the user needs identity data)
   - Do not reformat, reorder, or otherwise modify the resource file beyond the inserted lines

5. Variable substitution rules:
   - `${variableName}` placeholders are declared in each example's `## Variables` table — substitute
     only those, and only with values from Step 0/1/3
   - `${OIDC_CLIENT_SECRET}` is **NOT** a template variable: it is a real environment-variable
     expansion in `application.properties` — copy it verbatim, never substitute it
   - **NEVER add imports, properties, annotations, or code not present in an example**
   - **FQN only in imports, clean code in body.** Examples may contain fully qualified names inline
     (e.g. `@jakarta.annotation.security.RolesAllowed`). When generating code, extract FQNs into
     import statements and use short class names in the code body.

6. Report to the user: property keys written, permissions created, annotations applied, and the
   env-var placeholders that must be set (see Step 5).

---

## Step 5 -- Dependencies & properties (automatic)

Tell the user: `Step 5/5: Adding dependencies and properties...`

1. Read [`examples/_dependencies/oidc.md`](examples/_dependencies/oidc.md) (variants 1–2) or
   [`examples/_dependencies/smallrye-jwt.md`](examples/_dependencies/smallrye-jwt.md) (variant 3)
2. For each artifact NOT in `presentExtensions`:
   - **Preferred:** report the Quarkus command to the user and/or run it —
     `./mvnw quarkus:add-extension -Dextensions="quarkus-oidc"` (Gradle:
     `./gradlew addExtension --extensions="quarkus-oidc"`)
   - **Fallback:** edit the build file directly using the Maven/Gradle block from the dependency example file
3. Read the variant-specific properties example (linked in Step 4)
4. Write/append to the config file found in Step 1 — merge with existing keys, never duplicate a
   key, keep unrelated keys untouched. Report only key names, profiles, and verification status;
   redact any resolved secret as `[REDACTED]`.
5. Quarkus reloads configuration on the next dev-mode start — there is no build-model refresh step.
   Tell the user to restart `quarkus:dev` / `quarkusDev` after adding an extension.
6. Report: "Added extensions: [list]. Wrote to [detected config file]: [keys]. Added permissions: [rules]."
7. If the generated properties contain the `${OIDC_CLIENT_SECRET}` placeholder, list it explicitly
   and instruct the user to set the environment variable before running the app (shell `export`,
   IDE run configuration, or a deployment secret store). **Never ask the user for the secret value
   itself** — secrets must not enter the conversation history.

---

## Anti-hallucination checklist

Before writing ANY configuration, check all of the following:
- [ ] No security configuration class, filter chain, or security bean was generated — Quarkus security is properties + annotations only
- [ ] Every property key comes from an examples/_properties file (cite which one)
- [ ] No invented config keys, no invented custom prefixes (`quarkus.*` keys are framework-defined)
- [ ] Built-in policy values are exactly `permit`, `deny`, `authenticated`
- [ ] Permission precedence was NOT described as order-dependent — longest path wins
- [ ] Every annotation comes from an examples/_annotations file (cite which one)
- [ ] Only declared variables were substituted; `${OIDC_CLIENT_SECRET}` was copied verbatim
- [ ] Secrets were never requested, never written literally, never echoed from existing config
- [ ] Provider URL and client ID came from the user or existing config — not invented
- [ ] Role names match `existingRoles` or explicit user input — not invented
- [ ] `@RolesAllowed` / `@PermitAll` / `@DenyAll` imports are `jakarta.annotation.security`; `@Authenticated` is `io.quarkus.security`
- [ ] External `auth-server-url` is written with the `%prod.` prefix so Dev Services keep working in dev/test
- [ ] Existing config keys and unrelated resource code were not modified beyond the requested change
- [ ] Imports were derived from FQNs used in the examples (no extra, no missing)
