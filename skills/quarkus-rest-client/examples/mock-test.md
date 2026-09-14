# Mocking the REST client in a test (Java)

## Insert Point
New test class under `src/test/java`, same package as the class under test.

## Code

```java
package ${testPackage};

import io.quarkus.test.InjectMock;
import io.quarkus.test.junit.QuarkusTest;
import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.is;

@QuarkusTest
class ${TestClassName} {

    @InjectMock
    @RestClient
    ${ClientName} ${clientVar};

    @Test
    void ${testMethodName}() {
        Mockito.when(${clientVar}.${operationMethod}(${stubArg})).thenReturn(${stubbedValue});

        given()
                .when().get("${resourcePath}")
                .then()
                .statusCode(200)
                .body("${jsonPath}", is(${expectedValue}));
    }
}
```

## Variables
| Variable | Source | Default |
|----------|--------|---------|
| `${testPackage}` | project context | package of the class under test |
| `${TestClassName}` | project context | `{ConsumerClassName}Test` |
| `${ClientName}` | Step 4 | `{ServiceName}Client` |
| `${clientVar}` | — | decapitalized client name |
| `${operationMethod}` | Step 4 | client method exercised by the test |
| `${stubArg}` | test scenario | the exact argument the production code passes |
| `${stubbedValue}` | test scenario | a DTO instance / value returned by the stub |
| `${resourcePath}` | project context | local endpoint calling the client |
| `${jsonPath}` / `${expectedValue}` | test scenario | response assertion |

## Notes
- Requires `quarkus-junit-mockito` (`hasInjectMock` in the preflight).
- `import io.quarkus.test.InjectMock` is the Quarkus 3.x package; on pre-3.0 projects the
  annotation lived in `io.quarkus.test.junit.mockito.InjectMock` — match the import already used
  by the project's tests when a test suite exists.
- The mock replaces the client bean **application-wide** for the duration of the test class; each
  test method gets a fresh mock, so re-stub in `@BeforeEach` when several tests need it.
- `@QuarkusIntegrationTest` starts the application out-of-process: `@InjectMock` does not exist
  there — point the configuration at a real stub instance instead.
- When only the HTTP contract matters, rest-assured assertions can be dropped and the consumer
  service called directly.
