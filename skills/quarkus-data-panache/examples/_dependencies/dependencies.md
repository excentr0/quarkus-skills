# Dependencies

## Blocking Panache (default)

Maven — the versions come from the Quarkus BOM, never specify them explicitly:

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-orm-panache</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-jdbc-postgresql</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-validator</artifactId>
</dependency>
```

Gradle:

```kotlin
implementation("io.quarkus:quarkus-hibernate-orm-panache")
implementation("io.quarkus:quarkus-jdbc-postgresql")
implementation("io.quarkus:quarkus-hibernate-validator")
```

Preferred way to add: `./mvnw quarkus:add-extension -Dextensions="hibernate-orm-panache,jdbc-postgresql,hibernate-validator"`
(Gradle: `./gradlew addExtension --extensions="..."`).

## Reactive Panache (only when the project is reactive)

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-reactive-panache</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-reactive-pg-client</artifactId>
</dependency>
```

Do not add both blocking and reactive Panache unless the project already contains both — mixing them in one
call chain is a bug.

## Migrations (only when the project uses them)

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-flyway</artifactId>
</dependency>
```

If Flyway or Liquibase is present, schema changes go into a migration file — never into
`quarkus.hibernate-orm.database.generation`.
