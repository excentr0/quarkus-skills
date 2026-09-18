# Quarkus Skills

**Quarkus Skills** — a curated set of skills that give AI agents verified, project-aware
instructions for working on Quarkus applications: exploring the project, changing the
Panache data model, adding migrations, creating DTOs and mappers, adding REST resources,
calling other services with REST clients, configuring typed configuration, security and
Kafka, and building, testing (writing and running), checking style, measuring coverage,
and mutation-testing the code.

Modeled after [Amplicode/spring-skills](https://github.com/Amplicode/spring-skills) — same
format (`SKILL.md` + `references/` + `examples/`), same anti-hallucination discipline —
but rewritten for Quarkus idioms and **fully harness-agnostic**: no IDE or MCP server is
required, only file tools and Maven/Gradle commands.

## Why It Matters

AI agents write plausible Quarkus code but often drift into "average GitHub project" style —
mixing Spring idioms (`@RestController`, `JpaRepository`, `Pageable`, `ResponseEntity`)
with Quarkus, inventing config keys, or ignoring the project's own conventions.

Quarkus Skills give the agent a narrower, Quarkus-aware model of work:

- extension- and build-file-driven preflight instead of guessed stack assumptions
- verified Quarkus APIs: Panache, `quarkus-rest`, `@ServerExceptionMapper`, OIDC, Reactive Messaging
- conventions scoring from the project's own code before generating anything
- code templates with explicit `${variables}` instead of hallucinated snippets

## What's Inside

| Skill | What it helps the agent do | Status |
|-------|-----------------------------|--------|
| [`quarkus-explore`](skills/quarkus-explore/SKILL.md) | Explore a Quarkus application and gather project context: stack, build system, extensions, domain entities, repositories, resources, config. | Ready |
| [`quarkus-planning`](skills/quarkus-planning/SKILL.md) | Create a structured implementation plan in `docs/plans/`: context gathering, approach selection, task decomposition. | Ready |
| [`quarkus-data-panache`](skills/quarkus-data-panache/SKILL.md) | Work with Panache entities (Active Record) and repositories, PanacheQL queries, transactions, reactive variant. | Ready |
| [`quarkus-crud-rest-controller`](skills/quarkus-crud-rest-controller/SKILL.md) | Create JAX-RS resources with CRUD endpoints backed by a Panache repository, optionally with DTOs, mapping, and pagination. | Ready |
| [`quarkus-dto-creator`](skills/quarkus-dto-creator/SKILL.md) | Create DTOs for entities: Java records or plain classes, with validation. | Ready |
| [`quarkus-mapper-creator`](skills/quarkus-mapper-creator/SKILL.md) | Create mappers between entities and DTOs via MapStruct (`quarkus-mapstruct`) or a custom converter. | Ready |
| [`quarkus-security-configuration`](skills/quarkus-security-configuration/SKILL.md) | Configure authentication and authorization: quarkus-oidc (bearer / code flow), path policies, `@RolesAllowed`. | Ready |
| [`quarkus-kafka-configuration`](skills/quarkus-kafka-configuration/SKILL.md) | Configure Kafka messaging: channels, `@Incoming`/`@Outgoing`/`@Channel`, serializers, Dev Services. | Ready |
| [`quarkus-rabbitmq-configuration`](skills/quarkus-rabbitmq-configuration/SKILL.md) | Configure RabbitMQ messaging: channels, queues/exchanges/routing keys, `@Incoming`/`@Outgoing`/`@Channel`, JSON payloads, Dev Services. | Ready |
| [`quarkus-opentelemetry-configuration`](skills/quarkus-opentelemetry-configuration/SKILL.md) | Add OpenTelemetry traces and metrics: extension, OTLP config, `@WithSpan`/`Tracer` spans, `Meter` metrics, Jaeger/LGTM Dev Service, InMemory test exporters. | Ready |
| [`quarkus-run-tests`](skills/quarkus-run-tests/SKILL.md) | Run Maven/Gradle tests: unit vs `@QuarkusTest` vs `@QuarkusIntegrationTest`, report compact results. | Ready |
| [`quarkus-test-writing`](skills/quarkus-test-writing/SKILL.md) | Write Quarkus tests: pick the right test type, detect test conventions, generate test code with Dev Services in mind. | Ready |
| [`quarkus-coverage`](skills/quarkus-coverage/SKILL.md) | Measure test coverage via `quarkus-jacoco` and report the number. | Ready |
| [`quarkus-mutation-testing`](skills/quarkus-mutation-testing/SKILL.md) | Set up and run PIT mutation testing, report the mutation score. | Ready |
| [`quarkus-checkstyle`](skills/quarkus-checkstyle/SKILL.md) | Set up and run Checkstyle via Maven/Gradle, report and triage violations by rule. | Ready |
| [`quarkus-db-migrations`](skills/quarkus-db-migrations/SKILL.md) | Add and evolve Flyway/Liquibase schema migrations: extensions, naming, `migrate-at-start`, multi-datasource. | Ready |
| [`quarkus-config`](skills/quarkus-config/SKILL.md) | Add typed configuration: `@ConfigMapping` / `@ConfigProperty`, profiles, secrets via env references. | Ready |
| [`quarkus-native-build`](skills/quarkus-native-build/SKILL.md) | Build and package: fast-jar, uber-jar, native executable, container image. | Ready |
| [`quarkus-rest-client`](skills/quarkus-rest-client/SKILL.md) | Create typed REST clients: `@RegisterRestClient` interfaces, mandatory base URL, mocking in tests. | Ready |

Skills are **Java-first** (Kotlin variants can be added later).

## How It Works

Each skill is a folder:

```text
skills/<name>/
├── SKILL.md        # entry point: frontmatter (name, description with triggers) + workflow steps
├── references/     # conventions and rules loaded on demand
└── examples/       # code skeletons and fragments with ${variable} placeholders
```

Skills follow shared principles:

- **Preflight, not guessing** — detect build system, Quarkus version, extensions, and persistence
  mode from the build files before generating anything.
- **Context first, then ask** — half of the questions are answered by the project code and
  conversation; only genuine decisions are asked, via the harness's structured-question tool.
- **Code only from examples** — every code fragment comes from an `examples/` file with explicit
  `${variables}`; if no example matches, the agent stops and asks instead of inventing code.
- **Anti-hallucination checklist** — every skill ends with one; Quarkus facts live in
  [`docs/quarkus-facts.md`](docs/quarkus-facts.md).

## Installation

Install all skills globally into your AI agent:

```bash
npx skills add excentr0/quarkus-skills -g
```

Then open a Quarkus project in your agent and give it a concrete task, for example:

```text
Explore this project and explain its domain model.
```

```text
Add a CRUD REST resource for Customer using DTOs and MapStruct.
```

## Local validation

```bash
python3 scripts/validate_skills.py
git diff --check
```

## License

No explicit license yet — treat as all-rights-reserved until a LICENSE is added.