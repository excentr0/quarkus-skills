# Artifacts and how to run them

## Where the build leaves things

| Path | Mode | What it is |
|---|---|---|
| `target/quarkus-app/` | fast-jar | directory layout: `quarkus-run.jar`, `lib/`, `app/`, `quarkus/` |
| `target/quarkus-app/quarkus-run.jar` | fast-jar | the only jar to run — the others in the directory are not executable |
| `target/*-runner.jar` | uber-jar | self-contained runnable jar |
| `target/*-runner` | native | native executable (no `.jar`, no JVM needed) |
| `build/quarkus-app/…`, `build/*-runner` | Gradle equivalents | same layout under `build/` |

Maven `clean` wipes all of it; Gradle `clean` likewise. Do not report a path before checking it.

## Run

| Mode | Command |
|---|---|
| fast-jar | `java -jar target/quarkus-app/quarkus-run.jar` |
| uber-jar | `java -jar target/<name>-runner.jar` |
| native | `./target/<name>-runner` |
| container image | `docker run -i --rm -p 8080:8080 <group>/<name>:<tag>` |

Notes:

- Run the artifact from the **project root** (or with an absolute path) — the fast-jar reads relative
  `quarkus-app/lib` beside `quarkus-run.jar`, and native binaries may resolve sibling files the same way.
- The packaged artifact is a **production run**: `%prod.` config applies, Dev Services do not start,
  hot reload does not exist. To run with a different profile:
  `java -Dquarkus.profile=staging -jar target/quarkus-app/quarkus-run.jar`. Point to external config with
  the standard Quarkus mechanisms (`application.properties` inside `config/`, environment variables,
  `-D` overrides) — never edit the built jar.
- The HTTP port comes from `quarkus.http.port` (default `8080`). If the app is configured for another
  port, report that port, not 8080 out of habit.

## Sanity check after starting

1. The process prints a startup line with a time — native startup is typically tens of milliseconds,
   JVM startup a few hundred; both are fine.
2. Hit a known endpoint: `/q/health` when `quarkus-smallrye-health` is present (it returns
   `{"status":"UP"}`), otherwise any real route of the app.
3. Stop it afterwards unless the user asked to keep it running — do not leave orphaned processes behind
   from a build task.

```bash
java -jar target/quarkus-app/quarkus-run.jar &
curl -s http://localhost:8080/q/health
kill %1
```

## Reporting template

```text
Build: Maven · fast-jar
Artifact: target/quarkus-app/quarkus-run.jar
Run: java -jar target/quarkus-app/quarkus-run.jar
Verified: started on 8080, GET /q/health → {"status":"UP"}
Tests: ran as part of the build (12 passed)
```

Adapt the mode line and drop the verification lines you did not perform — every claimed verification
must have actually happened. If tests were skipped, say `Tests: skipped (-DskipTests)`; the reader must
be able to tell a full build from a quick packaging run.