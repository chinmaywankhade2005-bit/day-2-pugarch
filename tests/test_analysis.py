"""Tests for CSV/JSON loading and data quality/statistics reports."""

import json
from pathlib import Path
import tempfile
import unittest

from analysis.analyze_data import analyze, load_records


SAMPLE_DIR = Path(__file__).resolve().parents[1] / "analysis" / "data"


class AnalysisTests(unittest.TestCase):
    def test_csv_sample_metrics(self):
        report = analyze(load_records(SAMPLE_DIR / "employees.csv"))
        self.assertEqual(report["record_count"], 4)
        self.assertEqual(report["duplicate_records"], 1)
        self.assertEqual(report["missing_values"]["name"], 1)
        self.assertEqual(report["missing_values"]["salary"], 1)
        self.assertEqual(report["numeric_statistics"]["salary"]["count"], 3)
        self.assertAlmostEqual(report["numeric_statistics"]["salary"]["average"], 160000 / 3)
        self.assertEqual(report["numeric_statistics"]["salary"]["minimum"], 50000)
        self.assertEqual(report["numeric_statistics"]["salary"]["maximum"], 60000)
        self.assertEqual(report["category_statistics"]["department"]["IT"]["record_count"], 2)
        self.assertEqual(report["category_statistics"]["department"]["IT"]["numeric"]["salary"]["average"], 50000)

    def test_json_sample_metrics_match_csv(self):
        csv_report = analyze(load_records(SAMPLE_DIR / "employees.csv"))
        json_report = analyze(load_records(SAMPLE_DIR / "employees.json"))
        self.assertEqual(csv_report, json_report)

    def test_empty_dataset(self):
        self.assertEqual(analyze([]), {
            "record_count": 0, "missing_values": {}, "duplicate_records": 0,
            "numeric_statistics": {}, "category_statistics": {},
        })

    def test_json_records_wrapper_and_mixed_category_statistics(self):
        records = [{"group": "A", "score": 2}, {"group": "A", "score": 4}, {"group": "B", "score": 8}]
        report = analyze(records)
        self.assertEqual(report["category_statistics"]["group"]["A"]["numeric"]["score"]["average"], 3)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wrapped.json"
            path.write_text(json.dumps({"records": records}), encoding="utf-8")
            self.assertEqual(load_records(path), records)

    def test_missing_empty_malformed_and_unsupported_files(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            with self.assertRaises(FileNotFoundError):
                load_records(folder / "missing.json")
            empty_csv = folder / "empty.csv"
            empty_csv.write_text("", encoding="utf-8")
            self.assertEqual(load_records(empty_csv), [])
            broken_json = folder / "broken.json"
            broken_json.write_text("{oops", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid JSON"):
                load_records(broken_json)
            malformed_csv = folder / "bad.csv"
            malformed_csv.write_text("name,value\nA,1,extra\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "more values"):
                load_records(malformed_csv)
            with self.assertRaisesRegex(ValueError, "Unsupported"):
                load_records(folder / "notes.txt")


if __name__ == "__main__":
    unittest.main()
