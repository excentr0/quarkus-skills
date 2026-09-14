# @QuarkusTest — REST endpoint happy path (Java)

## Insert Point

New file `src/test/java/${testPackage}/${ResourceName}Test.java`.

## Code

```java
package ${testPackage};

import io.quarkus.test.junit.QuarkusTest;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;

@QuarkusTest
class ${ResourceName}Test {

    private static final String BASE_PATH = "${basePath}";

    @Test
    void findById_${entityVar}_returns${EntityName}() {
        given()
                .when().get(BASE_PATH + "/{id}", ${idValue})
                .then()
                .statusCode(200)
                .body("${fieldName}", is(${expectedValue}));
    }

    @Test
    void create_${entityVar}_storesIt() {
        given()
                .contentType(ContentType.JSON)
                .body("""
                        {"${fieldName}": ${jsonValue}}
                        """)
                .when().post(BASE_PATH)
                .then()
                .statusCode(${createStatusCode});

        given()
                .when().get(BASE_PATH)
                .then()
                .statusCode(200)
                .body("$", hasSize(greaterThanOrEqualTo(1)));
    }
}
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${testPackage}` | package of the resource under test, mirrored into `src/test/java` | same as resource package |
| `${ResourceName}` | resource class simple name | from `@Path` class |
| `${basePath}` | the resource's class-level `@Path` value | from the resource source |
| `${entityVar}` | decapitalized entity name | — |
| `${EntityName}` | entity simple name | — |
| `${idValue}` | id of a row the test can rely on (seed data or created in `@BeforeEach`) | — |
| `${fieldName}` | a response field that breaks the test if mapping regresses | — |
| `${expectedValue}` | expected JSON value for that field | — |
| `${jsonValue}` | JSON literal for the create body (string values in quotes) | — |
| `${createStatusCode}` | the status the resource actually returns | `200` unless the resource returns `Response.status(CREATED)` |

## Notes

- Read the resource and DTO **before** filling the placeholders: the path, the body shape and the status
  code are the contract under test, not guesses.
- The create test leaves a row behind (Dev-Service DB state persists across the run) — add cleanup per
  [`../references/conventions.md`](../references/conventions.md) when the assertions depend on exact counts.
- rest-assured's base URL is configured by Quarkus automatically in `@QuarkusTest` — never set `baseURI`
  or a port here.