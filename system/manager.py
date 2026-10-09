"""Employee operations and validation rules."""

from .employee import Employee


class EmployeeManager:
    def __init__(self, repository):
        self.repository = repository

    def _employees(self):
        return self.repository.load()

    def add(self, employee):
        if not isinstance(employee, Employee):
            raise TypeError("employee must be an Employee instance.")
        records = self._employees()
        if any(item.employee_id.casefold() == employee.employee_id.casefold() for item in records):
            raise ValueError(f"Employee ID already exists: {employee.employee_id}.")
        records.append(employee)
        self.repository.save(records)
        return employee

    def update(self, employee_id, *, name=None, department=None, salary=None):
        records = self._employees()
        index = self._find_index(records, employee_id)
        current = records[index]
        updated = Employee(
            employee_id=current.employee_id,
            name=current.name if name is None else name,
            department=current.department if department is None else department,
            salary=current.salary if salary is None else salary,
        )
        records[index] = updated
        self.repository.save(records)
        return updated

    def delete(self, employee_id):
        records = self._employees()
        index = self._find_index(records, employee_id)
        removed = records.pop(index)
        self.repository.save(records)
        return removed

    def search(self, query):
        query = str(query).strip().casefold()
        if not query:
            raise ValueError("Search text cannot be empty.")
        return [employee for employee in self._employees()
                if query in employee.employee_id.casefold()
                or query in employee.name.casefold()
                or query in employee.department.casefold()]

    def filter_by_department(self, department):
        department = str(department).strip()
        if not department:
            raise ValueError("Department cannot be empty.")
        return [employee for employee in self._employees()
                if employee.department.casefold() == department.casefold()]

    def list_employees(self, sort_by="name", descending=False):
        keys = {
            "id": lambda item: item.employee_id.casefold(),
            "name": lambda item: item.name.casefold(),
            "department": lambda item: item.department.casefold(),
            "salary": lambda item: item.salary,
        }
        if sort_by not in keys:
            raise ValueError("Sort field must be id, name, department, or salary.")
        return sorted(self._employees(), key=keys[sort_by], reverse=bool(descending))

    def statistics(self):
        employees = self._employees()
        if not employees:
            return {"count": 0, "average_salary": None, "minimum_salary": None,
                    "maximum_salary": None, "department_counts": {}}
        salaries = [employee.salary for employee in employees]
        departments = {}
        for employee in employees:
            departments[employee.department] = departments.get(employee.department, 0) + 1
        return {
            "count": len(employees),
            "average_salary": sum(salaries) / len(salaries),
            "minimum_salary": min(salaries),
            "maximum_salary": max(salaries),
            "department_counts": dict(sorted(departments.items(), key=lambda pair: pair[0].casefold())),
        }

    @staticmethod
    def _find_index(records, employee_id):
        if not isinstance(employee_id, str) or not employee_id.strip():
            raise ValueError("Employee ID cannot be empty.")
        wanted = employee_id.strip().casefold()
        for index, employee in enumerate(records):
            if employee.employee_id.casefold() == wanted:
                return index
        raise KeyError(f"Employee not found: {employee_id}.")
