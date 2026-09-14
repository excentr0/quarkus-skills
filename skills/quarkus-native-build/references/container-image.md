# Container images

Container images are produced by a Quarkus **container-image extension** — without one, adding
`-Dquarkus.container-image.build=true` does nothing (or fails), it does not conjure an image.

## Extension choice

| Extension | Needs a Docker daemon? | When to choose it |
|---|---|---|
| `quarkus-container-image-docker` | yes (Docker CLI + daemon) | default when the project already uses Docker |
| `quarkus-container-image-jib` | no — builds the image without a daemon | CI/registry builds, or no Docker locally |
| `quarkus-container-image-podman` | yes (Podman) | the project runs Podman instead of Docker |

Adding an extension:

| Tool | Command |
|---|---|
| Maven | `./mvnw quarkus:add-extension -Dextensions="quarkus-container-image-docker"` |
| Gradle | `./gradlew addExtension --extensions="quarkus-container-image-docker"` |
| CLI | `quarkus ext add quarkus-container-image-docker` |

Or add the dependency by hand with the project's version management (Quarkus BOM covers the `io.quarkus`
artifacts — no explicit version needed).

## Build commands

| Goal | Maven |
|---|---|
| JVM image (fast-jar inside) | `./mvnw package -Dquarkus.container-image.build=true` |
| Native image | `./mvnw package -Dnative -Dquarkus.native.container-build=true -Dquarkus.container-image.build=true` |
| Push to a registry | add `-Dquarkus.container-image.push=true` (registry credentials come from the standard Docker/Podman config; the container-image guide documents the explicit credential properties — check it before naming any key) |

Gradle and the CLI accept the same `-Dquarkus.container-image.*` flags.

## Properties (`application.properties`)

```properties
quarkus.container-image.group=registry.example.com/my-team
quarkus.container-image.name=order-service
quarkus.container-image.tag=1.0.0
```

- `group` is the registry/repository path without the image name (defaults to the project's group id).
- `name` defaults to the application name; `tag` defaults to the project version.
- Set these in the build file's `%prod.` block only if the values differ per environment — otherwise
  plain properties are fine (they affect the image build, not runtime behaviour).
- Do not invent other `quarkus.container-image.*` keys — check the container-image guide or the
  extension's config for what exists.

## Runtime prerequisite check

Before promising either a native container build or a docker/podman image build, verify the runtime
exists:

```bash
command -v docker podman
```

- Nothing found → the container paths are unavailable. Either use Jib (no daemon) or tell the user what
  to install — do not run the build and let it fail at the end of a long native compile.
- Podman-only host with the Docker extension → the build expects a Docker-compatible socket; prefer the
  podman extension or Jib instead of forcing it.

## Verify the image

```bash
docker images | grep '<name>'
docker run -i --rm -p 8080:8080 <group>/<name>:<tag>
```

Then hit the app's health endpoint (`http://localhost:8080/q/health` when `quarkus-smallrye-health` is
present) or any known endpoint. An image that builds but does not start is not a successful deliverable —
report what was actually verified.

## Report shape

```text
Build: Maven · container image (docker extension)
Image: registry.example.com/my-team/order-service:1.0.0
Run: docker run -i --rm -p 8080:8080 registry.example.com/my-team/order-service:1.0.0
Verified: container starts, GET /q/health → 200
```

Report the full image reference (registry + group + name + tag). "Image built" without a reference
leaves the user unable to run or push it.