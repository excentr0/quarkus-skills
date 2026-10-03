import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("routing_trace_evaluator", ROOT / "scripts/evaluate_routing_traces.py")
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)

SEEDS = [
    {"id": "positive", "expected_reads": ["quarkus-explore"], "allowed_companions": [],
     "expected_handoffs": ["quarkus-planning"], "expected_stop_decision": False},
    {"id": "negative", "expected_reads": [], "allowed_companions": []},
]


class CapturedTraceTests(unittest.TestCase):
    def test_synthetic_matching_trace_passes_without_claiming_real_routing(self):
        report = evaluator.evaluate_data(SEEDS, [
            {"case_id": "positive", "skill_reads": ["quarkus-explore"], "handoffs": ["quarkus-planning"], "stop_decision": False},
            {"case_id": "negative", "skill_reads": []},
        ], scope="Synthetic unit-test traces only; not measured routing evidence.")
        self.assertEqual("PASS", report["status"])
        self.assertEqual(2, report["summary"]["pass"])
        self.assertIn("Synthetic unit-test", report["scope"])

    def test_wrong_skill_or_unexpected_companion_fails(self):
        report = evaluator.evaluate_data(SEEDS, [
            {"case_id": "positive", "skill_reads": ["quarkus-config"]},
            {"case_id": "negative", "skill_reads": ["quarkus-kafka-configuration"]},
        ])
        self.assertEqual("FAIL", report["status"])
        self.assertEqual(2, report["summary"]["fail"])

    def test_missing_empty_duplicate_unknown_and_invalid_traces_never_pass(self):
        cases = [
            (None, "captured trace file missing"),
            ([], None),
            ([{"case_id": "positive", "skill_reads": []}, {"case_id": "positive", "skill_reads": []}], None),
            ([{"case_id": "not-a-seed", "skill_reads": []}], None),
            ([{"case_id": "positive", "skill_reads": "not-a-list"}], None),
        ]
        for traces, trace_error in cases:
            with self.subTest(traces=traces, error=trace_error):
                report = evaluator.evaluate_data(SEEDS, traces, trace_error=trace_error)
                self.assertNotEqual("PASS", report["status"])
                self.assertGreater(report["summary"]["notrun"], 0)

    def test_unrecorded_expected_handoff_or_stop_is_notrun(self):
        report = evaluator.evaluate_data(SEEDS, [
            {"case_id": "positive", "skill_reads": ["quarkus-explore"]},
            {"case_id": "negative", "skill_reads": []},
        ])
        self.assertEqual("NOTRUN", report["status"])
        self.assertEqual("NOTRUN", report["cases"][0]["status"])

    def test_negative_probe_allows_correct_companion_but_forbids_primary_in_both_directions(self):
        rabbit = "quarkus-rabbitmq-configuration"
        kafka = "quarkus-kafka-configuration"
        seeds = [
            {"id": "rabbit-probe-kafka-task", "skill": rabbit, "should_trigger": False,
             "expected_reads": [], "allowed_companions": [kafka, "quarkus-explore", "quarkus-config"]},
            {"id": "rabbit-probe-kafka-task-forbidden", "skill": rabbit, "should_trigger": False,
             "expected_reads": [], "allowed_companions": [kafka, "quarkus-explore", "quarkus-config"]},
            {"id": "kafka-probe-rabbit-task", "skill": kafka, "should_trigger": False,
             "expected_reads": [], "allowed_companions": [rabbit, "quarkus-explore", "quarkus-config"]},
            {"id": "kafka-probe-rabbit-task-forbidden", "skill": kafka, "should_trigger": False,
             "expected_reads": [], "allowed_companions": [rabbit, "quarkus-explore", "quarkus-config"]},
        ]
        traces = [
            {"case_id": "rabbit-probe-kafka-task", "skill_reads": [kafka]},
            {"case_id": "rabbit-probe-kafka-task-forbidden", "skill_reads": [rabbit]},
            {"case_id": "kafka-probe-rabbit-task", "skill_reads": [rabbit]},
            {"case_id": "kafka-probe-rabbit-task-forbidden", "skill_reads": [kafka]},
        ]
        report = evaluator.evaluate_data(seeds, traces)
        self.assertEqual(["PASS", "FAIL", "PASS", "FAIL"], [case["status"] for case in report["cases"]])

    def test_recorded_handoff_and_stop_decision_are_compared(self):
        report = evaluator.evaluate_data(SEEDS, [
            {"case_id": "positive", "skill_reads": ["quarkus-explore"], "handoffs": [], "stop_decision": True},
            {"case_id": "negative", "skill_reads": []},
        ])
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("handoff mismatch" in mismatch or "stop decision mismatch" in mismatch
                            for mismatch in report["cases"][0]["mismatches"]))


if __name__ == "__main__":
    unittest.main()
