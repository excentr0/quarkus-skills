# Suppressions (config/checkstyle/suppressions.xml)

## Insert Point

New file `config/checkstyle/suppressions.xml`, wired via the `SuppressionFilter` module in
`config/checkstyle/checkstyle.xml`.

## Code

```xml
<?xml version="1.0"?>
<!DOCTYPE suppressions PUBLIC
        "-//Checkstyle//DTD SuppressionFilter Configuration 1.2//EN"
        "https://checkstyle.org/dtds/suppressions_1_2.dtd">
<suppressions>
    <!-- generated sources carry their own formatting -->
    <suppress files="[\\/]target[\\/]generated-sources[\\/].*" checks=".*"/>
    <!-- long lines in test fixtures are legitimate -->
    <suppress files="TestData\.java" checks="LineLength" lines="42-60"/>
</suppressions>
```

Wiring fragment for the ruleset:

```xml
    <module name="SuppressionFilter">
        <property name="file" value="config/checkstyle/suppressions.xml"/>
    </module>
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `files` pattern | the exact file or directory glob the violation came from | narrowest pattern that covers it |
| `checks` | the rule id from the report (`LineLength`, `UnusedImports`, ...) | `.*` only for generated code |
| `lines` | line range, when only part of a file is affected | omit for whole-file suppression |

## Notes

- Suppression is a decision, not a cleanup: always show the fragment to the user and name the rule it
  silences before committing it.
- Prefer the narrowest form: exact file + exact rule. `files=".*" checks=".*"` disables Checkstyle
  entirely while pretending it runs.
- Generated code directories (`target/generated-sources`, build output) are the one case where a broad
  pattern is correct — the code is not edited by humans.
- File patterns are **regular expressions matched against the path**, not shell globs: `\.` for a dot,
  `[\\/]` for a separator.