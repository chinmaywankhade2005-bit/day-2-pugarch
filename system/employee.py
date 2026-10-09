"""Validated employee record used by the management application."""

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class Employee:
    employee_id: str
    name: str
    department: str
    salary: float

    def __post_init__(self):
        for field_name in ("employee_id", "name", "department"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name.replace('_', ' ').title()} cannot be empty.")
            object.__setattr__(self, field_name, value.strip())
        if isinstance(self.salary, bool):
            raise ValueError("Salary must be a number.")
        try:
            salary = float(self.salary)
        except (TypeError, ValueError) as exc:
            raise ValueError("Salary must be a number.") from exc
        if not math.isfinite(salary) or salary < 0:
            raise ValueError("Salary must be a finite, non-negative number.")
        object.__setattr__(self, "salary", salary)

    @classmethod
    def from_dict(cls, record):
        if not isinstance(record, dict):
            raise ValueError("Each employee record must be a JSON object.")
        required = {"employee_id", "name", "department", "salary"}
        missing = required - record.keys()
        if missing:
            raise ValueError(f"Employee record is missing fields: {', '.join(sorted(missing))}.")
        return cls(**{key: record[key] for key in required})

    def to_dict(self):
        return asdict(self)
