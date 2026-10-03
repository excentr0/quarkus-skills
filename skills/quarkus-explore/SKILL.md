---
name: quarkus-explore
description: >
  Explores a Quarkus application and builds primary context: tech stack,
  build system, Quarkus version, extensions, CDI beans, Panache entities and
  repositories, REST resources, configuration, and tests.
  Triggers on explicit requests: "explore project", "describe project", "project overview",
  "what is this project", "project structure", "tech stack", "give me context about the project".
  Russian phrases also trigger this: "изучи проект", "опиши проект", "структура проекта",
  "контекст проекта", "что за проект".
---

# Explore Application

Collect only the project context needed for the current request. Reuse accurate findings already established in this conversation; refresh only stale or uncertain facts.

## Detect project and target

Before rejecting the project or selecting a command, identify the target module. Inspect its build file plus root/parent build configuration for inherited Quarkus BOM/plugin, dependency management, and version properties/catalogs; use the target Maven module's effective POM when inheritance remains unclear. Prefer the project root wrapper with module selection (`-pl`/`-am` for Maven, `:module:task` for Gradle). If the wrapper is absent, check installed `mvn`/`gradle` and its version; if no usable tool is available, report a blocker/NOT RUN rather than calling the project invalid.


Use the target class/file named by the caller first. Otherwise identify a focused target from the requested feature and search its likely package before broadening. Treat predicted class names and domain terms only as search hints: they are not discovered project facts or new business requirements.

Inspect the relevant build file/module for Maven or Gradle, Quarkus version, extensions and persistence mode. In a multi-module build, identify the target module before reading its sources. Persistence modes:
- `quarkus-hibernate-orm-panache`: synchronous Hibernate ORM Panache.
- `quarkus-hibernate-reactive-panache`: reactive Panache; report its reactive API shape when relevant.
- `quarkus-hibernate-orm` without a Panache extension: plain Hibernate ORM; JPA entities/mappings may still exist, but do not claim Panache repositories or query APIs.
- Neither ORM/Panache mode: no such persistence layer was detected.

Locate Java types through both imported short names and fully qualified references. For entities, search for `@Entity` and `@jakarta.persistence.Entity`, inspect imports, and also inspect classes extending `PanacheEntity`/`PanacheEntityBase`; confirm by reading each match. For repositories, search `PanacheRepository` and `PanacheRepositoryBase` in imported and FQN forms, then read generic type arguments. Do not rely on FQN-only text searches.

## Focused read plan

Choose one short plan of relevant paths, for example: target source, directly referenced DTO/mapper/repository/service, relevant REST resource, build/module file, and a configuration or migration file only when the request needs it. Read the smallest set that resolves the next task input. Load only applicable bundled references, using normal file reads; it is valid to read additional selected references while executing the plan:

- [Extension glossary](references/extension-glossary.md) for extension identification.
- [Entity description](references/entity-description.md) for entity facts.
- [REST endpoint summary](references/rest-endpoints.md) for relevant HTTP routes.

Do not enumerate every possible path with INCLUDE/SKIP decisions or present a full ritualized plan. Actual file reads, greps, and globs are allowed while loading references and gathering context.

## Search and stop

Make at most two focused search passes. A second pass is justified only by a concrete unresolved question that blocks the next action; use the first pass's evidence to target it. Stop when the inputs for the next action are known, or when a focused pass produces no new evidence. State unresolved facts explicitly rather than continuing speculative searches.

Report compactly: relevant facts with source path and a short evidence snippet, then clearly separate confirmed facts, hypotheses, and unknowns. Redact secret values in all output. Do not dump full file contents/search result sets, invent implicit business requirements, or use subjective confidence/coverage scores. Only raise a possible requirement as a question when it materially affects the requested behavior.

## Portable resources and sibling handoffs

This skill's relative `references/` and `examples/` are bundled with its directory. Repository-level `docs/quarkus-facts.md` is optional when the skill is installed alone; if absent, verify version-sensitive claims against official versioned documentation/source or the actual project dependencies. Before a sibling-skill handoff, check whether that sibling is available. If missing, say so and apply equivalent local instructions only when the complete relevant example is available; never pretend to read a missing file. Skill activation/handoff alone does not authorize a child agent; delegate mechanically only when caller/operator permission and environment support are both present.

## Anti-hallucination checklist

- [ ] Quarkus version and extension list came from the relevant build file/module.
- [ ] Persistence mode (sync Panache, reactive Panache, plain ORM, or none) was confirmed before persistence claims.
- [ ] Entity/repository discovery checked imported short and fully qualified forms; findings were confirmed by reading source.
- [ ] Entity fields and endpoint verb/path claims came from actual source files.
- [ ] Secrets were redacted in the report.
- [ ] Every reported fact has a source path and evidence; hypotheses and unknowns are labeled.
