---
name: quarkus-native-build
description: >-
  Builds and packages a Quarkus application for production: JVM fast-jar, uber-jar, native executable,
  or container image — via Maven, Gradle, or the Quarkus CLI. Detects the build tool and packaging
  extensions from the build file, picks the right mode, runs the build, and reports the produced
  artifact with the command to run it.
  Use this skill when the user wants to build, package, or ship a Quarkus app ("build the app",
  "package for production", "make a native image", "build a container image", "produce a jar",
  "quarkus:build", "why is the native build failing").
  Russian phrases also trigger this: "собери приложение", "билд", "сборка для прода",
  "нативный образ", "нативная сборка", "собери контейнер", "docker образ", "собери uber-jar".
---

# Native / production build

This skill produces a **production artifact**: fast-jar, uber-jar, native executable, or container
image. Dev mode (`quarkus:dev`) is a different workflow — if the user wants hot reload, that is
`references/build-modes.md` § "Dev mode" and nothing here applies.

A native build is **slow (minutes) and memory-hungry** — say so before starting one, and never
retry a failed native build "to see if it passes this time".

---

## Preflight — project detection

This skill is harness-agnostic: file tools plus shell commands — no MCP server or IDE integration.

1. **Build system** — `pom.xml` (+ `mvnw`) → Maven; `build.gradle`/`build.gradle.kts` (+ `gradlew`) → Gradle.
2. **Quarkus presence & version** — Maven: `io.quarkus.platform:quarkus-bom` import; Gradle: `io.quarkus` plugin.
3. **Packaging extensions already present** — `quarkus-container-image-docker` / `-jib` / `-podman`
   (container mode needs one); `quarkus-amazon-lambda` or similar alters the artifact — if present, say
   so rather than assuming a plain jar.
4. **Native configuration** — grep the build file and `application.properties` for `quarkus.native.*`
   (e.g. `quarkus.native.container-build`, `quarkus.native.builder-image`, `quarkus.package.type`).
   Existing settings override this skill's defaults.
5. **Container runtime** — needed for native container builds (`-Dquarkus.native.container-build=true`)
   and for the docker/podman image extensions, **not** for Jib. Check with
   `command -v docker podman` before promising a container-path build.
6. **Previous artifacts** — `target/quarkus-app/`, `target/*-runner`, `target/*-runner.jar`,
   `build/*-runner` indicate what was built before.

If there is no Quarkus build file, stop: this skill targets Quarkus projects.

---

## Build modes

| Mode | What you get | Maven command | Gradle command |
|---|---|---|---|
| **fast-jar** (default) | `target/quarkus-app/` — a directory layout started by `quarkus-run.jar` | `./mvnw quarkus:build` | `./gradlew quarkusBuild` |
| **uber-jar** | one runnable fat jar `target/*-runner.jar` | `./mvnw package -Dquarkus.package.type=uber-jar` | `./gradlew build -Dquarkus.package.type=uber-jar` |
| **native** | native executable `target/*-runner` (GraalVM/Mandrel) | `./mvnw package -Dnative` | `./gradlew build -Dquarkus.native.enabled=true` |
| **native, container build** | native executable built inside a builder container (no local GraalVM needed) | `./mvnw package -Dnative -Dquarkus.native.container-build=true` | `./gradlew build -Dquarkus.native.enabled=true -Dquarkus.native.container-build=true` |
| **container image** | OCI image in the local registry/daemon | `./mvnw package -Dquarkus.container-image.build=true` | `./gradlew build -Dquarkus.container-image.build=true` |

Exact per-tool commands (Gradle, Quarkus CLI, combined native + container, builder-image pinning) are
in [`references/build-modes.md`](references/build-modes.md) — copy from there, never reconstruct from
memory. Container-image specifics live in [`references/container-image.md`](references/container-image.md).

---

## Defaults

| Decision | Default | When to deviate |
|---|---|---|
| Mode | **fast-jar** — fast to build, needs a JVM at run time | user asked for native (startup/memory) or a container |
| Native base | container build (`-Dquarkus.native.container-build=true`) when no `native-image` on PATH | local GraalVM/Mandrel present → plain `-Dnative` is faster to iterate |
| Tests during build | run as the build does by default; skip with `-DskipTests` (Maven) / `-x test` (Gradle) only when the user wants the artifact quickly | never skip silently — a build with skipped tests must be reported as such |
| Container image type | whatever extension the project already has; else ask (Docker / Jib / Podman) | Jib needs no Docker daemon — prefer it when only a registry/CI build is wanted |
| Profile | the packaged artifact is a **production run**; `%prod.` properties apply | user wants to override at run time → pass `-Dquarkus.profile=<name>` when starting it |

---

## Decision-making — context first, then ask

The request plus the build file answer most questions. Ask only genuine forks, in **one batch**
(single structured-question call, e.g. `AskUserQuestion` / `ask_user_question`; numbered list as the
last resort):

- **artifact kind** — fast-jar vs native vs container image (ask only when the request does not imply one)
- **native toolchain** — local GraalVM/Mandrel vs container build (ask only when it is not detectable and
  both are plausible)
- **container-image extension** — Docker vs Jib vs Podman (ask only when none is configured yet)
- **tests** — run them as part of the build, or skip for a quick artifact

Drop any question the conversation already answers. "Build the app" with a plain project usually means
fast-jar — say what you are building instead of asking.

---

## Step 0 — Read the request (no tools)

Tell the user: `Step 0/4: Reading the request...`

**Do NOT call any tools in this step.**

Fix from the request: **goal** (which artifact), **why** (deploy, local run, image push, CI), and
whether a previous build failed. "Build the app" → fast-jar. "Ship it" / "для прода" with no other
signal → fast-jar for the JVM path, and say that native is available if startup/memory matter.

---

## Step 1 — Gather context

Tell the user: `Step 1/4: Gathering context...`

Read the build file (packaging extensions, `quarkus.native.*`, `quarkus.package.type`), check for the
container runtime (`command -v docker podman`) if a container path is plausible, and look at what the
previous build left in `target/` / `build/`. State the findings in three lines:

```text
### Context:
- Build: Maven (./mvnw), Quarkus 3.20, packaging: defaults (fast-jar)
- Container runtime: docker present; no container-image extension yet
- Previous artifacts: target/quarkus-app/ from an earlier fast-jar build
```

---

## Step 2 — Choose the mode and resolve the command

Tell the user: `Step 2/4: Resolving the build command...`

Turn the goal + context into one concrete command from [`references/build-modes.md`](references/build-modes.md)
(and [`references/container-image.md`](references/container-image.md) for image mode). Rules:

- Respect existing `quarkus.native.*` / `quarkus.package.type` settings — do not contradict the project.
- Native without `native-image` on PATH → add `-Dquarkus.native.container-build=true` (and pin the
  builder image only if the project or the user requires a specific one).
- Container image but no `quarkus-container-image-*` extension → that is a genuine fork: ask which of
  Docker / Jib / Podman before adding an extension.
- Say what the command will produce and how long it should take (native: minutes).

---

## Step 3 — Run the build

Tell the user: `Step 3/4: Building (this may take a while)...`

If your harness supports subagents, delegate the run to ONE subagent and have it return only the
outcome (exit status, artifact paths, key error lines on failure) — a native build log must not flood
the conversation. Otherwise run it directly and capture the tail.

- A build that takes minutes is normal; do not kill it early and do not start a second one in parallel.
- **On failure** — report the first real error verbatim (native-image errors are long; extract the
  decisive line(s) and the failing class/feature), not the whole log. See
  [`references/build-modes.md`](references/build-modes.md) § "Reading a failed native build".
- Never retry a failed build unchanged; a retry needs a reason (raised memory limit, fixed code, added
  native profile config).

---

## Step 4 — Verify the artifact and report

Tell the user: `Step 4/4: Reporting the artifact...`

Verify the file exists at the expected path before reporting it (see
[`references/run-output.md`](references/run-output.md) for the path per mode) — a green exit code with
no artifact is not a successful build. Report compactly:

```text
Build: Maven · native (container build)
Artifact: target/order-service-1.0.0-SNAPSHOT-runner (native executable)
Run: ./target/order-service-1.0.0-SNAPSHOT-runner
Started in ~0.03s (Quarkus prints it) — check GET http://localhost:8080/q/health
```

For a container image report the image reference (`<group>/<name>:<tag>`), not just "image built".
State when tests were skipped, and state the mode explicitly — "build succeeded" alone can hide that
the user got a fast-jar instead of a native binary.

If the artifact must be exercised before it counts as working, the black-box test path is
[`../quarkus-run-tests/SKILL.md`](../quarkus-run-tests/SKILL.md) (integration type).

---

## Anti-hallucination checklist

- [ ] The build command matches the project's actual build tool and existing `quarkus.native.*` /
      `quarkus.package.type` settings.
- [ ] Module/artifact names in reported paths come from the real `target/` or `build/` listing.
- [ ] Native container builds were offered only after confirming a container runtime is available
      (or explicitly flagged as a requirement).
- [ ] Reported artifact paths were checked with `ls` — not assumed from the command.
- [ ] Skipped tests (if any) are stated in the report.
- [ ] Failure reports quote the decisive error lines verbatim; nothing was invented as "probably fixed".
- [ ] The report names the mode (fast-jar / uber-jar / native / image) and how to run the artifact.