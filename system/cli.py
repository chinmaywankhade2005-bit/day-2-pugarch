"""Interactive command-line interface for the employee management system."""

import argparse
from pathlib import Path

from .employee import Employee
from .manager import EmployeeManager
from .repository import EmployeeRepository


def _prompt_nonempty(label):
    while True:
        value = input(label).strip()
        if value:
            return value
        print("This value cannot be empty.")


def _prompt_salary(label="Salary: "):
    while True:
        raw = input(label).strip()
        try:
            return Employee("validation", "Validation", "Validation", raw).salary
        except ValueError as exc:
            print(exc)


def _print_employees(employees):
    if not employees:
        print("No employees found.")
        return
    print(f"{'ID':<12} {'Name':<24} {'Department':<20} {'Salary':>14}")
    print("-" * 72)
    for item in employees:
        print(f"{item.employee_id:<12} {item.name:<24} {item.department:<20} {item.salary:>14,.2f}")


def _add(manager):
    employee = Employee(
        _prompt_nonempty("Employee ID: "),
        _prompt_nonempty("Name: "),
        _prompt_nonempty("Department: "),
        _prompt_salary(),
    )
    manager.add(employee)
    print(f"Added employee {employee.employee_id}.")


def _update(manager):
    employee_id = _prompt_nonempty("Employee ID to update: ")
    print("Leave a field blank to keep its current value.")
    name = input("New name: ").strip() or None
    department = input("New department: ").strip() or None
    raw_salary = input("New salary: ").strip()
    salary = None
    if raw_salary:
        try:
            salary = Employee("validation", "Validation", "Validation", raw_salary).salary
        except ValueError as exc:
            print(exc)
            return
    manager.update(employee_id, name=name, department=department, salary=salary)
    print(f"Updated employee {employee_id}.")


def _statistics(manager):
    stats = manager.statistics()
    print(f"Employee count: {stats['count']}")
    if not stats["count"]:
        print("No salary statistics are available yet.")
        return
    print(f"Average salary: {stats['average_salary']:,.2f}")
    print(f"Minimum salary: {stats['minimum_salary']:,.2f}")
    print(f"Maximum salary: {stats['maximum_salary']:,.2f}")
    print("Employees by department:")
    for department, count in stats["department_counts"].items():
        print(f"  {department}: {count}")


def run(manager):
    actions = {
        "1": ("Add employee", lambda: _add(manager)),
        "2": ("Update employee", lambda: _update(manager)),
        "3": ("Delete employee", lambda: print(f"Deleted {manager.delete(_prompt_nonempty('Employee ID to delete: ')).employee_id}.")),
        "4": ("Search employees", lambda: _print_employees(manager.search(_prompt_nonempty("Search ID, name, or department: ")))),
        "5": ("Filter by department", lambda: _print_employees(manager.filter_by_department(_prompt_nonempty("Department: ")))),
        "6": ("List and sort employees", lambda: _print_employees(manager.list_employees(
            input("Sort by id/name/department/salary [name]: ").strip().lower() or "name",
            input("Descending? (y/N): ").strip().casefold() in {"y", "yes"},
        ))),
        "7": ("Show statistics", lambda: _statistics(manager)),
    }
    while True:
        print("\nEmployee Management System")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("8. Exit")
        choice = input("Choose 1-8: ").strip()
        if choice == "8":
            print("Goodbye.")
            return
        action = actions.get(choice)
        if action is None:
            print("Choose a menu option from 1 to 8.")
            continue
        try:
            action[1]()
        except (ValueError, KeyError, OSError, TypeError) as exc:
            print(f"Could not complete that action: {exc}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path,
        default=Path(__file__).resolve().parent / "data" / "employees.json",
        help="JSON file used to store employee records (default: system/data/employees.json)",
    )
    args = parser.parse_args(argv)
    manager = EmployeeManager(EmployeeRepository(args.data))
    try:
        run(manager)
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled. Goodbye.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
