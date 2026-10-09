"""JSON persistence for employee records."""

import json
import os
from pathlib import Path
import tempfile

from .employee import Employee


class EmployeeRepository:
    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as stream:
                payload = json.load(stream)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {self.path}: {exc.msg} (line {exc.lineno}).") from exc
        except OSError as exc:
            raise OSError(f"Could not read {self.path}: {exc}") from exc
        if not isinstance(payload, list):
            raise ValueError("Employee data must be a JSON list.")
        employees = []
        seen_ids = set()
        for index, record in enumerate(payload, start=1):
            try:
                employee = Employee.from_dict(record)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid employee record #{index}: {exc}") from exc
            if employee.employee_id.casefold() in seen_ids:
                raise ValueError(f"Duplicate employee ID in data file: {employee.employee_id}.")
            seen_ids.add(employee.employee_id.casefold())
            employees.append(employee)
        return employees

    def save(self, employees):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=self.path.parent,
                prefix=f".{self.path.name}.", suffix=".tmp", delete=False,
            ) as stream:
                temp_path = Path(stream.name)
                json.dump([employee.to_dict() for employee in employees], stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            temp_path.replace(self.path)
        except OSError as exc:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            raise OSError(f"Could not save {self.path}: {exc}") from exc
