import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("template_renderer", ROOT / "scripts/run_template_fixture.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class RendererTests(unittest.TestCase):
    def test_requires_template_heading(self):
        path = ROOT / "skills/quarkus-crud-rest-controller/examples/_methods/patch/java.md"
        with self.assertRaisesRegex(ValueError, "missing heading"):
            renderer.Renderer().fence(path, "## heading-that-does-not-exist")

    def test_rejects_unresolved_template_variables(self):
        with self.assertRaisesRegex(ValueError, "unresolved template variables"):
            renderer.substitute("value=${unknown}", {})

    def test_extracts_nested_heading_fence(self):
        path = ROOT / "skills/quarkus-crud-rest-controller/examples/_fragments/patch-field/java.md"
        source = renderer.Renderer().fence(path, "## int", "### Type check")
        self.assertIn("canConvertToInt", source)
        self.assertNotIn("entity.", source)

    def test_report_guard_rejects_missing_zero_all_skipped_and_failed_reports(self):
        cases = [
            (None, "no fresh XML reports"),
            ('<testsuite tests="0" failures="0" errors="0" skipped="0"/>', "invalid report counts"),
            ('<testsuite tests="-1" failures="0" errors="0" skipped="0"/>', "invalid report counts"),
            ('<testsuite tests="2" failures="-1" errors="1" skipped="0"/>', "invalid report counts"),
            ('<testsuite tests="2" failures="1" errors="-1" skipped="0"/>', "invalid report counts"),
            ('<testsuite tests="2" errors="0" skipped="0"/>', "invalid report counts"),
            ('<testsuite tests="2" failures="0" skipped="0"/>', "invalid report counts"),
            ('<testsuite tests="1" failures="0" errors="0" skipped="2"/>', "invalid report counts"),
            ('<testsuite tests="2" failures="0" errors="0" skipped="2"/>', "all report tests skipped"),
            ('<testsuite tests="2" failures="1" errors="0" skipped="0"/>', "test failures/errors"),
        ]
        for xml, message in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as temp:
                report = Path(temp) / "reports"
                if xml is not None:
                    report.mkdir()
                    (report / "TEST-case.xml").write_text(xml)
                with self.assertRaisesRegex(RuntimeError, message):
                    renderer.report_counts(report)

    def test_generate_removes_preexisting_report_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "rendered"
            stale = output / "target/surefire-reports/TEST-stale.xml"
            stale.parent.mkdir(parents=True)
            stale.write_text('<testsuite tests="1" failures="0" errors="0" skipped="0"/>')
            original = renderer.OUT
            try:
                renderer.OUT = output
                renderer.generate()
            finally:
                renderer.OUT = original
            self.assertFalse((output / "target/surefire-reports").exists())
            manifest = json.loads((output / "render-inputs.json").read_text())
            paths = {item["path"] for item in manifest}
            self.assertIn("skills/quarkus-mapper-creator/examples/_fragments/partial-update-method/java.md", paths)

    def test_report_guard_accepts_executed_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            report = Path(temp)
            (report / "TEST-case.xml").write_text('<testsuite tests="2" failures="0" errors="0" skipped="0"/>')
            self.assertEqual((2, 0, 0), renderer.report_counts(report))

    def test_rejects_undeclared_placeholder_in_selected_fragment(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "example.md"
            path.write_text("# Example\n## Code\n```java\nvoid method() { ${unknown}; }\n```\n## Variables\n| Variable | Source |\n|---|---|\n| `${known}` | value |\n")
            with self.assertRaisesRegex(ValueError, "undeclared placeholders"):
                renderer.render_fence(path, "## Code")


if __name__ == "__main__":
    unittest.main()
