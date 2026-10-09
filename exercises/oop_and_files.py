"""Runnable OOP and file-handling exercise using only the standard library."""

import json
from pathlib import Path
import tempfile


class StaffMember:
    """Base class with an encapsulated, validated salary attribute."""

    def __init__(self, name, salary):
        self.name = self._validate_name(name)
        self.salary = salary

    @staticmethod
    def _validate_name(name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name cannot be empty.")
        return name.strip()

    @property
    def salary(self):
        return self.__salary

    @salary.setter
    def salary(self, value):
        try:
            amount = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Salary must be numeric.") from exc
        if amount < 0:
            raise ValueError("Salary cannot be negative.")
        self.__salary = amount

    def to_dict(self):
        return {"name": self.name, "salary": self.salary, "role": self.role}

    @property
    def role(self):
        return "staff"


class Developer(StaffMember):
    """Subclass that demonstrates inheritance and method overriding."""

    @property
    def role(self):
        return "developer"


def main():
    team = [StaffMember("Mina", 48000), Developer("Arun", 62000)]
    records = [member.to_dict() for member in team]
    # Context managers close the temporary file even if JSON writing fails.
    with tempfile.TemporaryDirectory(prefix="day02-oop-") as folder:
        path = Path(folder) / "team.json"
        with path.open("w", encoding="utf-8") as stream:
            json.dump(records, stream, indent=2)
        with path.open("r", encoding="utf-8") as stream:
            loaded = json.load(stream)
    for record in loaded:
        print(f"{record['name']} | {record['role']} | salary={record['salary']:.2f}")


if __name__ == "__main__":
    main()
