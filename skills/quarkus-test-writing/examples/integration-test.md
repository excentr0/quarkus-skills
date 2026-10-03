# Packaged-artifact integration test

Use `@QuarkusIntegrationTest` only when verifying the packaged application (for example, its HTTP contract as launched from the built artifact). This is a black-box test: do not inject CDI beans or use `@InjectMock`; exercise the public interface over HTTP. Do not assume a parent `@QuarkusTest` test class is injectable or required.

```java
package ${testPackage};

import io.quarkus.test.junit.QuarkusIntegrationTest;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.equalTo;

@QuarkusIntegrationTest
class ${TargetClass}IT {
    @Test
    void ${methodName}() {
        given()
                .when().get("${verifiedPath}")
                .then()
                .statusCode(${expectedStatus})
                .body("${verifiedJsonPath}", equalTo(${expectedValue}));
    }
}
```

## Variables
| Variable | Source |
|---|---|
| `${testPackage}` | package used by existing test sources |
| `${TargetClass}` | target/resource-derived test class name |
| `${methodName}` | descriptive test method name |
| `${verifiedPath}` | path read from the actual resource |
| `${expectedStatus}` | status required by the requested contract and source |
| `${verifiedJsonPath}` | response JSON path read from DTO/resource contract |
| `${expectedValue}` | type-correct literal from the requested contract/source |

Keep assertions tied to the requested behavior. Use the existing integration-test base only if repository source proves it is compatible with `@QuarkusIntegrationTest` and does not require CDI injection. Test data must be provisioned through an integration-compatible mechanism already configured in the project; otherwise ask before inventing infrastructure.