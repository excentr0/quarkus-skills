# Lombok in Quarkus Projects (note)

Lombok works in Quarkus (`org.projectlombok:lombok` + annotation processor configuration in the build),
but it is **not idiomatic** — Java records cover the immutable-DTO use case without an extra
dependency, and Quarkus 3.x requires Java 17+ so records are always available.

Rules for this skill:

- **Default:** generate `java-record` DTOs. Do not propose Lombok.
- **If the project already uses Lombok for its DTOs** (existing `@Data`/`@Value`/`@Getter` classes are
  visible in the DTO package): follow the project's existing style — read one existing Lombok DTO in
  the project and mirror its annotation set. The project's own DTO is the example to follow; this skill
  deliberately ships no Lombok fragments, because inventing an annotation combination is exactly the
  kind of guess the anti-hallucination rules forbid.
- **If the user explicitly asks for Lombok** in a project that does not use it yet: state in one line
  that records are the Quarkus-idiomatic alternative, and proceed with Lombok only if the user confirms
  — mirroring the annotation style of any existing Lombok class in the project.
- Lombok-generated DTOs still need explicit Bean Validation annotations (`@NotNull`, …) on the fields —
  Lombok does not generate them.

This note replaces the full Lombok variant: no Lombok skeletons, field fragments, or annotation
decision trees are maintained for Quarkus.