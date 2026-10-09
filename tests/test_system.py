"""Unit tests for the employee model, JSON repository, and management operations."""

import json
from pathlib import Path
import tempfile
import unittest

from system.employee import Employee
from system.manager import EmployeeManager
from system.repository import EmployeeRepository


class EmployeeSystemTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = Path(self.temp_dir.name) / "employees.json"
        self.repository = EmployeeRepository(self.path)
        self.manager = EmployeeManager(self.repository)

    def seed(self):
        self.manager.add(Employee("E02", "Ravi", "IT", 50000))
        self.manager.add(Employee("E01", "Asha", "Data", 60000))
        self.manager.add(Employee("E03", "Mina", "IT", 70000))

    def test_add_duplicate_update_delete_and_persistence(self):
        added = self.manager.add(Employee("E01", "Asha", "Data", 60000))
        self.assertEqual(added.name, "Asha")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.manager.add(Employee("e01", "Duplicate", "Data", 1))
        updated = self.manager.update("e01", name="Asha Patel", salary="65000")
        self.assertEqual((updated.name, updated.salary), ("Asha Patel", 65000.0))
        self.assertEqual(EmployeeManager(EmployeeRepository(self.path)).list_employees()[0].name, "Asha Patel")
        removed = self.manager.delete("E01")
        self.assertEqual(removed.employee_id, "E01")
        self.assertEqual(self.manager.list_employees(), [])

    def test_search_filter_sort_and_statistics(self):
        self.seed()
        self.assertEqual([item.employee_id for item in self.manager.search("ra")], ["E02"])
        self.assertEqual({item.employee_id for item in self.manager.filter_by_department("it")}, {"E02", "E03"})
        self.assertEqual([item.salary for item in self.manager.list_employees("salary", descending=True)], [70000, 60000, 50000])
        stats = self.manager.statistics()
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["average_salary"], 60000)
        self.assertEqual(stats["minimum_salary"], 50000)
        self.assertEqual(stats["maximum_salary"], 70000)
        self.assertEqual(stats["department_counts"], {"Data": 1, "IT": 2})

    def test_invalid_model_and_operation_inputs(self):
        for values in [("", "Name", "IT", 1), ("E1", " ", "IT", 1), ("E1", "Name", "IT", -1),
                       ("E1", "Name", "IT", "NaN")]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                Employee(*values)
        with self.assertRaises(ValueError):
            self.manager.search(" ")
        with self.assertRaises(ValueError):
            self.manager.filter_by_department("")
        with self.assertRaises(ValueError):
            self.manager.list_employees("unknown")
        with self.assertRaises(KeyError):
            self.manager.delete("missing")
        with self.assertRaises(KeyError):
            self.manager.update("missing", name="Nobody")
        self.assertEqual(self.manager.statistics()["average_salary"], None)

    def test_missing_file_starts_empty(self):
        self.assertEqual(self.repository.load(), [])

    def test_corrupt_json_and_non_list_root_are_reported(self):
        self.path.write_text("{not valid", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid JSON"):
            self.repository.load()
        self.path.write_text(json.dumps({"employee_id": "E1"}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "JSON list"):
            self.repository.load()

    def test_malformed_records_and_duplicate_ids_are_reported(self):
        self.path.write_text(json.dumps([{"employee_id": "E1"}]), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing fields"):
            self.repository.load()
        records = [Employee("E1", "One", "IT", 10).to_dict(), Employee("e1", "Two", "IT", 20).to_dict()]
        self.path.write_text(json.dumps(records), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate employee ID"):
            self.repository.load()


if __name__ == "__main__":
    unittest.main()
