# Plain JUnit 5 — business logic (Java)

## Insert Point

New file `src/test/java/${testPackage}/${ClassName}Test.java`.

## Code

```java
package ${testPackage};

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class ${ClassName}Test {

    private final ${ClassName} ${classVar} = new ${ClassName}();

    @Test
    void ${methodName}_${happyScenario}_returns${ExpectedOutcome}() {
        assertEquals(${expectedValue}, ${classVar}.${methodName}(${input}));
    }

    @ParameterizedTest(name = "{0} -> {1}")
    @CsvSource({
            "${input1}, ${expected1}",
            "${input2}, ${expected2}"
    })
    void ${methodName}_variousInputs_returnsExpected(${InputType} input, ${ReturnType} expected) {
        assertEquals(expected, ${classVar}.${methodName}(input));
    }

    @Test
    void ${methodName}_${invalidScenario}_throws() {
        assertThrows(${ExceptionType}.class, () -> ${classVar}.${methodName}(${invalidInput}));
    }
}
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `${testPackage}` | package of the class under test, mirrored into `src/test/java` | same as main package |
| `${ClassName}` | class under test | class with logic and no CDI dependencies |
| `${classVar}` | decapitalized class name | — |
| `${methodName}` | method under test | — |
| `${happyScenario}` / `${invalidScenario}` | short scenario names | — |
| `${ExpectedOutcome}` | short outcome phrase for the test name | — |
| `${InputType}` / `${ReturnType}` | parameter and return types of the method | — |
| `${input}`, `${input1}`, `${input2}`, `${invalidInput}` | arguments for the method | — |
| `${expectedValue}`, `${expected1}`, `${expected2}` | expected results | — |
| `${ExceptionType}` | exception the method throws on invalid input | — |

## Notes

- No Quarkus annotations at all — no container, no Dev Services, runs in milliseconds. Use this for every
  class that does not need CDI.
- If construction needs collaborators, pass plain Mockito mocks (see
  [`../references/mocking.md`](../references/mocking.md)); do not switch to `@QuarkusTest` just to get
  injection.
- `@CsvSource` values are parsed as strings — quote them in the CSV when the parameter is a string and the
  text contains commas.