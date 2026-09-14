# Mocking in Quarkus Tests

## In @QuarkusTest — @InjectMock

Requires the `quarkus-junit5-mockito` extension.

- `@InjectMock ${DependencyName} ${dependencyVar};` as a test-class field
  (import `io.quarkus.test.InjectMock`; requires the `quarkus-junit-mockito` test dependency.
  The pre-3.x package `io.quarkus.test.junit.mockito.InjectMock` matches only older Quarkus).
- The mock **replaces the bean application-wide** for the duration of the test class — every injection
  point gets the mock, not just this field.
- Configure behaviour in `@BeforeEach` with `Mockito.when(...)`; each test method gets a fresh mock.
- `@InjectSpy ${DependencyName} ${dependencyVar};` wraps the **real** bean — use it when only one method
  should be stubbed and the rest must keep their real behaviour.

Use mocks for slow or external collaborators: HTTP clients, Kafka emitters, third-party services,
clock/time providers. Do not mock the class under test, its repository, or anything the test is supposed
to verify through.

## In plain unit tests — Mockito directly

No Quarkus imports at all:

```java
class ${ClassName}Test {

    private final ${DependencyName} ${dependencyVar} = Mockito.mock(${DependencyName}.class);
    private final ${ClassName} ${classVar} = new ${ClassName}(${dependencyVar});
}
```

- `@ExtendWith(MockitoExtension.class)` + `@Mock`/`@InjectMocks` is the project-consistent alternative
  when other unit tests already use it.
- Recent Mockito (5.x) mocks final classes without extra configuration; static methods still need
  `Mockito.mockStatic(...)` inside a try-with-resources block.

## What cannot be mocked

- **`@QuarkusIntegrationTest`** — the application runs in a different process: no CDI, so `@InjectMock`
  (and `@Inject`) silently does not work there. Integration tests reach the app only through its real
  interfaces (HTTP, messaging).
- **Quarkus build-time beans** (e.g. `SecurityIdentity`, datasource internals) are not mockable via
  `@InjectMock` — for security, use `@TestSecurity` (from `quarkus-test-security`) instead; for other
  build-time infrastructure, configure the real thing for tests rather than mocking it.

## Rules of thumb

- One mock per test class is usually enough; two or three is a smell that the class under test has too
  many collaborators.
- Prefer a hand-written fake when the collaborator's interface is small and the fake logic is obvious —
  fakes catch interface changes, mocks let them pass silently.
- Never stub a method the test does not exercise: unused stubs hide which behaviour was actually verified.