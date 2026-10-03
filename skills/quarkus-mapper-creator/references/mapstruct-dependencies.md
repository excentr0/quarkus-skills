# MapStruct dependency workflow

## Step 5 -- Add MapStruct dependencies (automatic, MapStruct variant only)


For Custom mapper: skip this step entirely. Custom mappers have no
external dependencies.

For MapStruct: check `${presentDeps}` and add missing pieces to the
project's build file.

### Core artifacts and optional extension

| Artifact ID | Group ID | Role |
|-------------|----------|------|
| `quarkus-mapstruct` | `io.quarkiverse.mapstruct` | Optional Quarkiverse integration for native registration/dev-mode recompilation; add only after verifying compatibility with the target Quarkus release |
| `mapstruct` | `org.mapstruct` | MapStruct annotations API (implementation scope) |
| `mapstruct-processor` | `org.mapstruct` | annotation processor that generates the mapper implementation |

Core MapStruct/CDI mapping requires the annotations API and processor, not the Quarkiverse extension. Preserve a compatible existing extension; do not add an incompatible one just to create a mapper. Native/dev-mode integration must be verified separately.

### Maven: the annotation processor MUST be configured explicitly

The `quarkus-mapstruct` extension only reads `@Mapper`/`@MapperConfig` annotations
(native registration, dev-mode recompilation) — it does **not** run the MapStruct
processor. Add it to `maven-compiler-plugin`:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <annotationProcessorPaths>
            <path>
                <groupId>org.mapstruct</groupId>
                <artifactId>mapstruct-processor</artifactId>
                <version>${mapstruct.version}</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

If the project already configures `annotationProcessorPaths`, insert the
`<path>` entry into the existing list — do not replace other processors
(Lombok, Quarkus `quarkus-extension-processor`, etc. must survive).

### Gradle

Inside the existing `dependencies { … }` block:

```groovy
implementation("org.mapstruct:mapstruct:${mapstructVersion}")
annotationProcessor("org.mapstruct:mapstruct-processor:${mapstructVersion}")
```

Only for a verified compatible Quarkiverse integration, add separately:

```groovy
implementation("io.quarkiverse.mapstruct:quarkus-mapstruct:${quarkusMapstructVersion}")
```

(Groovy DSL: single quotes / `implementation 'org.mapstruct:mapstruct:…'`.)

### Versions

Do NOT hardcode blindly. In order:
1. Reuse versions already present in the project (build file, parent POM,
   `gradle/libs.versions.toml` version catalogue) — MapStruct and its processor
   must share one version.
2. If absent: `org.mapstruct:mapstruct` — a current stable line is `1.6.x`
   (e.g. `1.6.3`), keep `mapstruct` and `mapstruct-processor` in lockstep.
3. The optional `io.quarkiverse.mapstruct:quarkus-mapstruct` extension is NOT managed by the Quarkus platform BOM. Check its source/release compatibility against the detected Quarkus version, then verify with that project's BOM; do not select the latest version blindly. In the Java 21 fixture, extension 1.1.0 fails augmentation on Quarkus 3.20.3 (`RecompilationDependenciesBuildItem` is missing). Core MapStruct 1.6.3 API/processor with CDI passed on that target without the extension. Other extension versions and native/dev-mode integration were not tested. If extension-specific features are required and no compatible release is verified, stop and report the compatibility blocker.

Use the available file-editing tool with `${buildFile}` as the target path. Make the
edit minimally — insert new entries into the existing blocks, do not rewrite
the file.

### No properties needed

Mapper creation does not write any `application.properties` entries.

Report: "Created mapper ${className} in package ${packageName}. Type: ${mapperType}. Methods: ${list of methods}."

---
