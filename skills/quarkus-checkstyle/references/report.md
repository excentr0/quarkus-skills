# Reading and Reporting Checkstyle Results

## Where the results are

| Build tool | Result XML | HTML |
|---|---|---|
| Maven | `target/checkstyle-result.xml` | `target/site/checkstyle.html` |
| Gradle | `build/reports/checkstyle/main.xml`, `test.xml` | `build/reports/checkstyle/main.html`, `test.html` |

## What the XML looks like

```xml
<?xml version="1.0" encoding="UTF-8"?>
<checkstyle version="10.x">
  <file name="/path/to/src/main/java/org/acme/OrderResource.java">
    <error line="42" column="9" severity="error"
           message="Line is longer than 120 characters (found 128)."
           source="com.puppycrawl.tools.checkstyle.checks.sizes.LineLengthCheck"/>
  </file>
</checkstyle>
```

- One `<error>` element = one violation. `source` ends with the rule class (`LineLengthCheck`) — the
  rule name shown to the user is that class name minus the `Check` suffix.
- `severity` is `error`, `warning`, or `info`. Report `error` always; `info` only if the user asks.
- A `<file>` with no `<error>` children is clean — do not mention it.
- Files with zero violations but a `Checkstyle` parse `<exception>` (e.g. unparsable Java) must be
  reported as failures of the check itself, not as "no violations".

## Compact report format

```text
### Checkstyle: 17 violations in 6 files

| Rule         | Count | Example                                  |
|--------------|-------|------------------------------------------|
| LineLength   | 9     | OrderResource.java:42 (128 > 120)        |
| UnusedImports| 4     | OrderMapper.java:3                       |
| NeedBraces   | 4     | OrderService.java:88                     |

Result file: target/checkstyle-result.xml
```

Rules: counts are exact from the XML; the example column shows the first occurrence per rule; the total
is the sum of `<error>` elements.

## Gate result

When the run used the `check` goal / gate mode:

- non-zero exit code + violations in the XML → `build failed: N violations`;
- non-zero exit code + no violations → report the actual build error (plugin resolution, config file not
  found, Checkstyle engine download failure) — it is not a style result;
- zero exit code → clean, say so plainly.

## Honesty rules

- Never invent violations, counts, or `file:line` coordinates — every reported item must exist in the XML.
- If the result file does not exist after the run, the check did not execute: report the reason (wrong
  goal, task skipped, config missing) instead of reporting "no violations".
- If the project has an existing baseline of violations, say the number — do not present a legacy backlog
  as if the last change introduced it.