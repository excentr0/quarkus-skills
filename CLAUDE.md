# CLAUDE.md

Guidance for working in this repository.

## Layout

- `skills/<name>/SKILL.md` — skill entry point (frontmatter: `name`, `description` with trigger phrases EN + RU).
- `skills/<name>/references/*.md` — conventions/rules loaded on demand by the skill.
- `skills/<name>/examples/**/*.md` — code skeletons and fragments with `${variable}` placeholders.
- `docs/quarkus-facts.md` — verified Quarkus facts. Skills must not contradict it; update it when adding new facts.

## Rules

- Skills are Java-first. No IDE/MCP server dependency (unlike Amplicode spring-skills) — everything works with plain file tools and Maven/Gradle commands.
- Never mention Spring APIs in skill code examples. See the blocklist in `docs/quarkus-facts.md`.
- Every skill ends with an anti-hallucination checklist.

## Version bump

The plugin version lives in `.claude-plugin/plugin.json` (single source; no other manifests exist here).
