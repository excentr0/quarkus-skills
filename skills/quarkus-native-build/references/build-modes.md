# Build modes — command matrix

All commands assume the project root (where `pom.xml` / `build.gradle` lives). `./mvnw` and `./gradlew`
are the wrappers — use them, not a globally installed `mvn`/`gradle`.

## Mode matrix

| Mode | Maven | Gradle | Quarkus CLI |
|---|---|---|---|
| fast-jar (default) | `./mvnw quarkus:build` | `./gradlew quarkusBuild` | `quarkus build` |
| uber-jar | `./mvnw package -Dquarkus.package.type=uber-jar` | `./gradlew build -Dquarkus.package.type=uber-jar` | `quarkus build -Dquarkus.package.type=uber-jar` |
| native (local GraalVM/Mandrel) | `./mvnw package -Dnative` | `./gradlew build -Dquarkus.native.enabled=true` | `quarkus build --native` |
| native (container build) | `./mvnw package -Dnative -Dquarkus.native.container-build=true` | `./gradlew build -Dquarkus.native.enabled=true -Dquarkus.native.container-build=true` | `quarkus build --native -Dquarkus.native.container-build=true` |
| native + container image | `./mvnw package -Dnative -Dquarkus.native.container-build=true -Dquarkus.container-image.build=true` | same flags on `./gradlew build` | `quarkus build --native -Dquarkus.native.container-build=true -Dquarkus.container-image.build=true` |

`-Dnative` is shorthand for `-Dquarkus.native.enabled=true`; prefer the long form in Gradle commands
(the short form also works, but the long form is unambiguous in a build file context).

## Outputs

| Mode | Artifact |
|---|---|
| fast-jar | `target/quarkus-app/` — the runnable file is `target/quarkus-app/quarkus-run.jar` |
| uber-jar | `target/*-runner.jar` (one fat jar, e.g. `order-service-1.0.0-SNAPSHOT-runner.jar`) |
| native | `target/*-runner` (native executable, e.g. `order-service-1.0.0-SNAPSHOT-runner`) |
| container image | local image `<group>/<name>:<tag>` (defaults: artifact name + `1.0.0-SNAPSHOT`-style project version) |

Never report an artifact path without checking it exists — the jar/native names come from the project's
final name, not from this file.

## Native specifics

- **No local GraalVM/Mandrel?** Add `-Dquarkus.native.container-build=true` — the build runs inside a
  builder container. Requires a working container runtime (Docker or Podman) on PATH.
- **Builder image** — pin it only when needed: `-Dquarkus.native.builder-image=quay.io/quarkus/ubi9-quarkus-mandrel-builder-image:jdk-21`.
  Check the Quarkus version's default in the guide if the project pins nothing; do not invent a tag.
- **Memory** — the builder is memory-hungry. If it dies with an out-of-memory message, raise the limit
  with `-Dquarkus.native.native-image-xmx=<size>` (e.g. `4g`) instead of retrying unchanged.
- **Sources-only** (to inspect generated native sources): add `-Dquarkus.native.sources-only=true`.
- Native builds are slow: expect minutes, once. A fast incremental JVM build is the normal iteration
  path; native is for the final artifact.

## Tests during the build

- Maven: tests run by default in `package`. Skip when the user wants the artifact quickly:
  `-DskipTests` (compile, run nothing). Integration tests need the failsafe phase (`verify`), not
  plain `package`.
- Gradle: `build` runs `test`; skip with `-x test` (or `-x quarkusIntTest` if that task exists).
- Skipping tests is a decision, not a default — if it happens, the report must say so. To run
  `@QuarkusIntegrationTest` against the packaged artifact afterwards, use the `quarkus-run-tests` skill.

## Dev mode (not a production build)

| Tool | Command |
|---|---|
| Maven | `./mvnw quarkus:dev` |
| Gradle | `./gradlew quarkusDev` |
| CLI | `quarkus dev` |

Dev mode hot-reloads and starts Dev Services automatically. Do not use it to produce a deployable
artifact, and do not run it with production flags.

## Reading a failed native build

Native build logs are long. Extract, in this order:

1. The **last error block** above `BUILD FAILURE` (Maven) / `FAILURE: Build failed` (Gradle), which is
   usually the decisive one.
2. The failing **class or feature** — e.g. missing reflection registration, unsupported library,
   `Classes that should be initialized at run time got initialized during image building`.
3. The remedy class — for reflection: `@RegisterForReflection` or the relevant
   `quarkus.native.*` / `--initialize-at-build-time` configuration; for a missing tool: it is almost
   always a container runtime or builder-image problem, not code.

Report the decisive lines verbatim and the artifact was NOT produced. Never claim "should work now"
without a successful rerun.

## Build in a multi-module project

Build from the root (`./mvnw package -Dnative`) so the whole reactor runs, unless the user targets a
module: `./mvnw package -Dnative -pl order-service -am` (Maven) / `./gradlew :order-service:build`
(Gradle, with `-D` flags as needed). Mixed-module reactors can fail on a module that is not a Quarkus
app — check whether the failure is in the application module before blaming native compilation.