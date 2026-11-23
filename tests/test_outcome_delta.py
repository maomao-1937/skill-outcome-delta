import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_outcome_delta", ROOT / "skill_outcome_delta.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class OutcomeDeltaTests(unittest.TestCase):
    def runs(self):
        return [
            {"case_id":"a","condition":"baseline","success":False,"tokens":100,"duration_ms":1000},
            {"case_id":"a","condition":"with_skill","success":True,"tokens":130,"duration_ms":900},
            {"case_id":"b","condition":"baseline","success":True,"tokens":80,"duration_ms":800},
            {"case_id":"b","condition":"with_skill","success":True,"tokens":90,"duration_ms":850},
        ]

    def test_pairs_cases_and_computes_deltas(self):
        result = tool.compare(self.runs())
        self.assertEqual(result["paired_cases"], 2)
        self.assertEqual(result["summary"]["success_rate_delta_median"], 0.5)
        self.assertEqual(result["summary"]["median_tokens_delta"], 20)
        self.assertEqual(result["summary"]["median_duration_ms_delta"], -25)
        self.assertTrue(result["ok"])

    def test_unpaired_case_is_reported_and_fails(self):
        result = tool.compare(self.runs() + [{"case_id":"c","condition":"with_skill","success":True,"tokens":1,"duration_ms":1}])
        self.assertEqual(result["unpaired_cases"], ["c"])
        self.assertFalse(result["ok"])

    def test_no_pair_is_rejected(self):
        with self.assertRaises(ValueError): tool.compare(self.runs()[:1])

    def test_invalid_condition_is_rejected(self):
        rows = self.runs(); rows[0]["condition"] = "old"
        temp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False)
        try:
            temp.write(json.dumps({"runs": rows})); temp.close()
            with self.assertRaises(ValueError): tool.load_runs(temp.name)
        finally: Path(temp.name).unlink(missing_ok=True)

    def test_non_boolean_success_is_rejected(self):
        rows = self.runs(); rows[0]["success"] = 1
        temp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False)
        try:
            temp.write(json.dumps({"runs": rows})); temp.close()
            with self.assertRaises(ValueError): tool.load_runs(temp.name)
        finally: Path(temp.name).unlink(missing_ok=True)


if __name__ == "__main__": unittest.main()
