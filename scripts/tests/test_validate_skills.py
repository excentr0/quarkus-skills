import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/validate_skills.py"
spec = importlib.util.spec_from_file_location("validate_skills", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class FrontmatterTests(unittest.TestCase):
    def test_parses_supported_quoted_and_folded_or_literal_values(self):
        cases = [
            ('name: "demo"\ndescription: >\n  line one\n  line two', "line one line two"),
            ("name: 'demo''s'\ndescription: >-\n  line one\n  line two", "line one line two"),
            ('name: demo\ndescription: |\n  line one\n  line two', "line one\nline two"),
            ('name: demo\ndescription: |-\n  line one\n  line two', "line one\nline two"),
        ]
        for frontmatter, expected in cases:
            with self.subTest(frontmatter=frontmatter):
                fields, body, error = validator.parse_frontmatter(f"---\n{frontmatter}\n---\nBody")
                self.assertIsNone(error)
                self.assertEqual(expected, fields["description"])
                self.assertEqual("Body", body)
        fields, _, error = validator.parse_frontmatter('---\nname: "quoted"\n---\nBody')
        self.assertIsNone(error)
        self.assertEqual("quoted", fields["name"])
        fields, _, error = validator.parse_frontmatter("---\nname: 'demo''s'\n---\nBody")
        self.assertIsNone(error)
        self.assertEqual("demo's", fields["name"])

    def test_rejects_unsupported_or_malformed_frontmatter_syntax(self):
        _, _, reproduced_error = validator.parse_frontmatter(
            "---\nname: demo\ndescription: [unterminated\n---\nBody")
        self.assertIn("unsupported YAML flow", reproduced_error)
        invalid = [
            "description: [unterminated",
            "description: {key: value}",
            "name: !tag value",
            "name: &anchor value",
            "name: *anchor",
            'name: "unterminated',
            'name: "quoted" trailing',
            "name: 'unterminated",
            'name: "unsupported\\escape"',
            "name:demo",
            "description: >- trailing",
            "description: |2",
            "description: |+",
            "description: value: trailing syntax",
            "name: demo\n  continuation",
        ]
        for line in invalid:
            with self.subTest(line=line):
                _, _, error = validator.parse_frontmatter(f"---\n{line}\n---\nBody")
                self.assertIsNotNone(error)

    def test_rejects_unclosed_and_duplicate_frontmatter(self):
        _, _, error = validator.parse_frontmatter("---\nname: demo\n")
        self.assertIn("missing closing", error)
        _, _, duplicate = validator.parse_frontmatter("---\nname: first\nname: second\ndescription: x\n---\nBody")
        self.assertIn("duplicate frontmatter key", duplicate)

    def test_strips_reference_banner_only(self):
        self.assertEqual(validator._strip_provenance_banner("> Local copy of `source`\n\ncontent\n"), "content\n")
        self.assertEqual(validator._strip_provenance_banner("content\n"), "content\n")


class StaticRuleTests(unittest.TestCase):
    def test_checklist_requires_final_nonempty_checkbox_section(self):
        self.assertIsNone(validator.checklist_error("## Step 6 -- Anti-hallucination checklist\n\n- [ ] Check source.\n"))
        self.assertIn("not the final section", validator.checklist_error("## Anti-hallucination checklist\n- [ ] Check\n## Later\ntext"))
        self.assertIn("no non-empty checkbox", validator.checklist_error("## Anti-hallucination checklist\ntext"))
        self.assertIn("empty or malformed", validator.checklist_error("## Anti-hallucination checklist\n- [ ] \n"))

    def test_exact_annotation_blocklist_does_not_match_bean_mapping(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            facts = root / "facts.md"
            facts.write_text("### Blocklist (must never appear in examples)\n`@Bean`, `@Repository`\n\n## Next\n")
            skill = root / "demo"
            example = skill / "examples/sample.md"
            example.parent.mkdir(parents=True)
            example.write_text("```java\n@BeanMapping(ignoreByDefault = true)\nPanacheRepository<?> repo;\n```\n")
            errors = []
            validator.validate_example_blocklist(skill, errors, facts)
            self.assertEqual([], errors)
            example.write_text("```java\n@Bean\nvoid bad() {}\n```\n")
            validator.validate_example_blocklist(skill, errors, facts)
            self.assertTrue(any("@Bean" in error for error in errors))
            example.write_text("```java\n@Parent\n@Nested\nvoid markers() {}\n```\n")
            neutral_errors = []
            validator.validate_example_blocklist(skill, neutral_errors, facts)
            self.assertEqual([], neutral_errors)

    def test_broken_own_reference_fails_isolated_package(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / "demo"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo\n---\n"
                "[Broken](references/missing.md)\n\n"
                "## Portable resources and sibling handoffs\nThis skill's relative references/ and examples/ are bundled. "
                "Repository-level docs/quarkus-facts.md is optional; if absent, verify claims against official docs. "
                "Before a sibling handoff, check availability. If missing, apply equivalent local instructions only when complete.\n\n"
                "## Anti-hallucination checklist\n- [ ] Verify the source.\n")
            errors = []
            validator.validate_standalone_copy(skill, errors, ROOT / "docs/quarkus-facts.md")
            self.assertTrue(any("bundled Markdown resource does not exist" in error for error in errors))

    def test_invalid_seed_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "seeds.json"
            path.write_text("{broken")
            errors = []
            validator.validate_eval_seeds({"demo"}, errors, path)
            self.assertTrue(any("invalid JSON" in error for error in errors))

    def test_negative_probe_cannot_be_its_own_allowed_companion(self):
        known = {path.parent.name for path in validator.discover_skill_paths(validator.SKILLS_ROOT)}
        data = json.loads(validator.EVALS_FILE.read_text(encoding="utf-8"))
        case = next(item for item in data if item["should_trigger"] is False)
        case["allowed_companions"].append(case["skill"])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "seeds.json"
            path.write_text(json.dumps(data))
            errors = []
            validator.validate_eval_seeds(known, errors, path)
        self.assertTrue(any("primary skill must not be an allowed companion" in error for error in errors))

    def test_discovery_excludes_workspace_variant(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("quarkus-demo", "quarkus-demo-workspace"):
                (root / name).mkdir()
                (root / name / "SKILL.md").write_text("---\n---\n")
            found = validator.discover_skill_paths(root)
        self.assertEqual(["quarkus-demo"], [path.parent.name for path in found])

    def test_execution_catalog_definitions_have_no_frozen_results(self):
        definitions = [{"id": f"check-{index}", "kind": "automated", "command": "python3 check.py",
                        "assertions": ["evidence"]} for index in range(5)]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "catalog.json"
            path.write_text(json.dumps(definitions))
            errors = []
            self.assertEqual(5, validator.validate_execution_catalog(path, errors))
            self.assertEqual([], errors)
            definitions[0]["status"] = "PASS"
            path.write_text(json.dumps(definitions))
            errors = []
            validator.validate_execution_catalog(path, errors)
        self.assertTrue(any("defines checks, not execution results" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
