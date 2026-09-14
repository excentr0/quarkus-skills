# @QuarkusTest — service with a mocked dependency (Java)

## Insert Point

New file `src/test/java/${testPackage}/${ServiceName}Test.java`.

## Code

```java
package ${testPackage};

import io.quarkus.test.junit.QuarkusTest;
import io.quarkus.test.InjectMock;
import jakarta.inject.Inject;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;

@QuarkusTest
class ${ServiceName}Test {

    @Inject
    ${ServiceName} ${serviceVar};

    @InjectMock
    ${DependencyName} ${dependencyVar};

    @BeforeEach
    void stubDependency() {
        Mockito.when(${dependencyVar}.${dependencyMethod}(any()))
                .thenReturn(${stubbedValue});
    }

    @Test
    void ${serviceMethod}_${scenario}_returns${ExpectedOutcome}() {
        ${ReturnType} result = ${serviceVar}.${serviceMethod}(${input});

        assertEquals(${expectedValue}, result);
    }
}
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${testPackage}` | package of the service under test, mirrored into `src/test/java` | same as service package |
| `${ServiceName}` | service class simple name | — |
| `${serviceVar}` | decapitalized service name | — |
| `${DependencyName}` | the collaborator being mocked | slow/external dependency of the service |
| `${dependencyVar}` | decapitalized dependency name | — |
| `${dependencyMethod}` | method the service calls on the dependency | — |
| `${stubbedValue}` | value the stub returns | — |
| `${serviceMethod}` | method under test | — |
| `${scenario}` | what makes this case distinct | — |
| `${ReturnType}` | return type of the method under test | — |
| `${input}` | argument for the method under test | — |
| `${expectedValue}` | expected result | — |
| `${ExpectedOutcome}` | short outcome phrase for the test name | — |

## Notes

- `@InjectMock` needs the `quarkus-junit-mockito` extension (preflight step 3).
- The mock replaces the bean application-wide; stubs go in `@BeforeEach` so each test starts clean.
- Keep stubs to collaborators outside the class under test — mock the HTTP client, not the repository
  whose query the test is meant to exercise.
- A single `@BeforeEach` stub that every test inherits is a smell: move per-test stubs into the tests
  that actually need them.