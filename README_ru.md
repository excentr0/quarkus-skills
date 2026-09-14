# Quarkus Skills

**Quarkus Skills** — набор skills для AI-агентов, работающих с Quarkus-приложениями:
исследование проекта, изменение модели данных на Panache, миграции БД, создание DTO
и мапперов, REST-ресурсы, вызов внешних сервисов через REST-клиенты, конфигурация,
security и Kafka, сборка, тесты (написание и запуск), checkstyle, покрытие и
mutation-тестирование.

Набор смоделирован по образцу [Amplicode/spring-skills](https://github.com/Amplicode/spring-skills) —
тот же формат (`SKILL.md` + `references/` + `examples/`) и та же антигаллюцинаторная дисциплина, —
но переписан под идиомы Quarkus и **не зависит от IDE**: работает только с файловыми инструментами
и командами Maven/Gradle.

## Зачем это нужно

AI-агенты пишут правдоподобный Quarkus-код, но часто тянут в него Spring-стиль
(`@RestController`, `JpaRepository`, `Pageable`, `ResponseEntity`), придумывают несуществующие
config-ключи и игнорируют локальные соглашения проекта.

Skills дают агенту узкую, Quarkus-aware модель работы:

- префлайт по build-файлам: версия Quarkus, расширения, режим персистентности
- проверенные API: Panache, `quarkus-rest`, `@ServerExceptionMapper`, OIDC, Reactive Messaging
- скоринг соглашений по коду самого проекта перед генерацией
- код только из `examples/`-файлов с `${переменными}` — без выдуманных сниппетов

## Состав

| Skill | Что делает | Статус |
|-------|------------|--------|
| [`quarkus-explore`](skills/quarkus-explore/SKILL.md) | Исследование проекта: стек, расширения, сущности, репозитории, ресурсы, конфигурация. | Ready |
| [`quarkus-planning`](skills/quarkus-planning/SKILL.md) | Структурированный план имплементации в `docs/plans/`. | Ready |
| [`quarkus-data-panache`](skills/quarkus-data-panache/SKILL.md) | Сущности (Active Record) и репозитории Panache, PanacheQL, транзакции, reactive-вариант. | Ready |
| [`quarkus-crud-rest-controller`](skills/quarkus-crud-rest-controller/SKILL.md) | JAX-RS ресурс с CRUD на Panache-репозитории, с DTO и пагинацией по выбору. | Ready |
| [`quarkus-dto-creator`](skills/quarkus-dto-creator/SKILL.md) | DTO: Java record или обычный класс, с валидацией. | Ready |
| [`quarkus-mapper-creator`](skills/quarkus-mapper-creator/SKILL.md) | Мапперы entity↔DTO: MapStruct (`quarkus-mapstruct`) или кастомный конвертер. | Ready |
| [`quarkus-security-configuration`](skills/quarkus-security-configuration/SKILL.md) | Аутентификация/авторизация: quarkus-oidc (bearer / code flow), path-политики, `@RolesAllowed`. | Ready |
| [`quarkus-kafka-configuration`](skills/quarkus-kafka-configuration/SKILL.md) | Kafka: каналы, `@Incoming`/`@Outgoing`/`@Channel`, сериализаторы, Dev Services. | Ready |
| [`quarkus-run-tests`](skills/quarkus-run-tests/SKILL.md) | Запуск тестов: unit / `@QuarkusTest` / `@QuarkusIntegrationTest`, компактный отчёт. | Ready |
| [`quarkus-test-writing`](skills/quarkus-test-writing/SKILL.md) | Написание тестов: выбор типа, конвенции проекта, генерация тестов с учётом Dev Services. | Ready |
| [`quarkus-coverage`](skills/quarkus-coverage/SKILL.md) | Покрытие через `quarkus-jacoco` и отчёт числом. | Ready |
| [`quarkus-mutation-testing`](skills/quarkus-mutation-testing/SKILL.md) | PIT mutation-тестирование и оценка мутационного скора. | Ready |
| [`quarkus-checkstyle`](skills/quarkus-checkstyle/SKILL.md) | Подключение и запуск Checkstyle (Maven/Gradle), триаж нарушений по правилам. | Ready |
| [`quarkus-db-migrations`](skills/quarkus-db-migrations/SKILL.md) | Схемные миграции Flyway/Liquibase: расширения, нейминг, `migrate-at-start`, мультидатасорсы. | Ready |
| [`quarkus-config`](skills/quarkus-config/SKILL.md) | Типизированная конфигурация: `@ConfigMapping` / `@ConfigProperty`, профили, секреты через env. | Ready |
| [`quarkus-native-build`](skills/quarkus-native-build/SKILL.md) | Сборка и упаковка: fast-jar, uber-jar, native, container image. | Ready |
| [`quarkus-rest-client`](skills/quarkus-rest-client/SKILL.md) | Типизированные REST-клиенты: `@RegisterRestClient`, конфигурация, мокирование в тестах. | Ready |

Skills ориентированы на **Java** (Kotlin-варианты можно добавить позже).

## Формат скилла

```text
skills/<name>/
├── SKILL.md        # входная точка: frontmatter (name, description с триггерами) + шаги workflow
├── references/     # соглашения и правила, загружаемые по требованию
└── examples/       # скелеты кода и фрагменты с ${переменными}
```

Принципы:

- **Префлайт вместо догадок** — стек, версия Quarkus, расширения и режим персистентности
  определяются по build-файлам.
- **Контекст, потом вопросы** — половина вопросов закрывается кодом проекта и историей диалога;
  спрашиваются только реальные развилки (через структурированный вопрос-инструмент харнесса).
- **Код только из examples** — нет подходящего примера → агент останавливается и спрашивает,
  а не выдумывает.
- **Анти-галлюцинационный чеклист** — в конце каждого скилла; проверенные факты —
  в [`docs/quarkus-facts.md`](docs/quarkus-facts.md).

## Установка

```bash
npx skills add <your-org>/quarkus-skills -g
```

Затем откройте Quarkus-проект в агенте и дайте конкретную задачу, например:
«Добавь CRUD REST-ресурс для Customer с DTO и MapStruct».