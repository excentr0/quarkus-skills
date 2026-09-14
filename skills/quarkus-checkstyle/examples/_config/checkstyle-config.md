# Starter ruleset (config/checkstyle/checkstyle.xml)

## Insert Point

New file `config/checkstyle/checkstyle.xml` in the project root (the path Gradle looks up by default).

## Code

```xml
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC
        "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
        "https://checkstyle.org/dtds/configuration_1_3.dtd">
<module name="Checker">
    <property name="charset" value="UTF-8"/>

    <!-- file-level checks live directly under Checker -->
    <module name="LineLength">
        <property name="max" value="120"/>
    </module>
    <module name="FileTabCharacter"/>

    <!-- tree-level checks must be wrapped in TreeWalker -->
    <module name="TreeWalker">
        <module name="UnusedImports"/>
        <module name="AvoidStarImport"/>
        <module name="NeedBraces"/>
        <module name="WhitespaceAround"/>
        <module name="OneStatementPerLine"/>
    </module>

    <module name="SuppressionFilter">
        <property name="file" value="config/checkstyle/suppressions.xml"/>
        <!-- include this module only when a suppressions file exists -->
    </module>
</module>
```

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `max` (LineLength) | project convention | `120` |
| module list | keep the starter set small; add rules when a real problem appears | the six above |

## Notes

- This is a **starter**, not a maximal ruleset: every added rule is a future argument. Grow it when the
  codebase slips, not preemptively.
- `google_checks.xml` (bundled with the plugin) is much stricter and a legitimate alternative when the
  user wants a known public standard instead of a project-owned file.
- All `TreeWalker`-level modules must be inside the `<module name="TreeWalker">` block — placing
  `UnusedImports` directly under `Checker` is a config error, not a style violation.
- `SuppressionFilter` with a missing suppressions file fails the whole run — either create both files
  together or omit the module.