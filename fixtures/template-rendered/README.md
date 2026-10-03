# Template-rendered Quarkus fixture

Run from the repository root with a JDK 21 and Maven 3.9.x:

```sh
python3 scripts/run_template_fixture.py
```

The fixture uses Quarkus 3.20.3 with core MapStruct API/processor 1.6.3 and CDI mapper generation. The Quarkiverse `quarkus-mapstruct` extension is not included in this fixture: the only attempted candidate, 1.1.0, fails Quarkus augmentation against 3.20.3 because `io.quarkus.deployment.dev.RecompilationDependenciesBuildItem` is missing. The failed trial and its executed/skipped counts are preserved at `target/compatibility-trial-quarkus-mapstruct-1.1.0.log`; it is not a test pass. This fixture verifies JVM CDI-generated mapper core only; native-image reflection registration and extension-provided dev-mode recompilation are unverified. No other extension version is claimed compatible.

The rendered test app includes separate public-field no-DTO, DTO/MapStruct, and private-field/setter resources. Fixture repositories explicitly sort the batch query results by generated ID so the rollback tests can witness a valid first mutation before the invalid later row; this test-only ordering is not production repository guidance. The tests assert the validator observed those mutations and then query both rows after the HTTP transaction has rolled back.

Rendered sources, input hashes and Maven logs are disposable under `target/rendered/`; source Markdown and checked-in fixture inputs are not overwritten. Java fixture is Maven-only; Gradle is not included.
