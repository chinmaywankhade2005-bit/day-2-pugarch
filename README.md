# Day 2 — Python Development

This project follows the Day 2 requirements in the supplied 10-Day Intern Technical Training and Domain Assessment program. It covers Python syntax and data types, collections, conditions and loops, functions, lambdas and comprehensions, modules, exceptions, file handling, classes and objects, inheritance, encapsulation, and virtual environments.

## Problem statement

Small employee datasets need reliable record management and basic quality checks. This assignment provides a local CLI for maintaining employee records and a separate reader for summarizing CSV or JSON datasets.

## Deliverables

| Folder | Contents |
| --- | --- |
| `exercises/` | Runnable fundamentals example and OOP/file-handling example, plus practice notes |
| `system/` | Employee Management CLI with Add, Update, Delete, Search, department Filter, Sort, Statistics, JSON persistence, validation, and error handling |
| `analysis/` | CSV/JSON reader reporting record count, missing values, exact duplicate rows, numeric summaries, and category-wise summaries; includes sample datasets |
| `tests/` | Standard-library automated tests for management and analysis behavior |

The employee record has an ID, name, department, and non-negative salary. Employee IDs are unique without regard to case. The management system uses JSON. The independent analysis utility reads CSV or JSON. The included sample datasets intentionally contain a duplicate row and missing values so the analysis report demonstrates those checks.

## Features

- Add, update, delete, search, filter by department, list/sort, and summarize employee records.
- Persist employee changes in a JSON file, with validation and readable persistence errors.
- Analyze row counts, missing values, repeated full records, numeric statistics, and category groups from CSV or JSON.
- Practice Python fundamentals, OOP, and JSON file handling in small runnable examples.

## Technology stack

- Python 3.14.6 and its standard library (`dataclasses`, `json`, `csv`, `argparse`, `pathlib`, and `unittest`).
- PowerShell commands shown below use the already-created Windows virtual environment.

## Architecture and data design

- `system.employee` defines the validated, immutable `Employee` record.
- `system.repository` reads and writes JSON. `system.manager` implements record operations and statistics. `system.cli` handles menu input and output.
- `analysis.analyze_data` loads CSV or JSON records and computes a JSON-serializable report. The analysis utility does not change its input file.
- The app's JSON database is a list of employee objects. The required fields are `employee_id`, `name`, `department`, and `salary`; the ID is case-insensitively unique and salary is a finite, non-negative number.

There is no network service or HTTP API in this command-line assignment, so API documentation and environment variables do not apply. The interface is terminal text; screenshots are not applicable.

## Requirements

- Python 3.14.6; only the Python standard library is used.
- No package installation is needed. The existing project `venv` is sufficient.
- Run commands from the `day-02` directory.

## Installation

No installation steps or package downloads are required. Use the existing venv interpreter directly as shown below. If you recreate the environment later, create it with Python 3.14.6; the project has no third-party requirements.

## Environment variables

None. The database path is supplied with the optional `--data` argument instead of an environment variable.

## Run the exercises

```powershell
.\venv\Scripts\python.exe .\exercises\fundamentals.py
.\venv\Scripts\python.exe .\exercises\oop_and_files.py
```

The fundamentals exercise prompts for a mark after printing examples. The OOP/file exercise writes and reads a temporary JSON file, then removes its temporary directory automatically.

## Run the Employee Management CLI

```powershell
.\venv\Scripts\python.exe -m system.cli
```

The default JSON database is `system/data/employees.json`. Supply a different path with `--data`:

```powershell
.\venv\Scripts\python.exe -m system.cli --data .\my_employees.json
```

Menu options are Add employee, Update employee, Delete employee, Search employees, Filter by department, List and sort employees, Show statistics, and Exit. Search checks ID, name, and department without case sensitivity. Sorting supports ID, name, department, or salary in ascending or descending order. Statistics include employee count, average/minimum/maximum salary, and department counts.

The JSON database is a list of objects with this shape:

```json
[
  {
    "employee_id": "E001",
    "name": "Asha Rao",
    "department": "Data",
    "salary": 60000.0
  }
]
```

A missing database starts as an empty employee list. Invalid JSON, invalid record shapes, duplicate IDs in a file, unreadable files, invalid menu choices, and invalid employee values produce readable errors. Saving uses a temporary file followed by replacement to reduce the chance of leaving a partially written database if a save fails.

## Run the CSV/JSON analysis exercise

```powershell
.\venv\Scripts\python.exe .\analysis\analyze_data.py .\analysis\data\employees.csv
.\venv\Scripts\python.exe .\analysis\analyze_data.py .\analysis\data\employees.json
```

The JSON input can be a list of objects or an object containing a `records` list. CSV input uses the first row as headers. Missing-value counts treat blank strings, `NA`, `N/A`, `null`, and `none` (case-insensitive) as missing. Duplicate count is the number of repeated full records after the first occurrence. Numeric summaries report count, average, minimum, and maximum for columns whose non-missing values are all finite numbers. Other non-empty columns are treated as categories; each category group includes its record count and numeric summaries. The report is printed as JSON. Invalid or unsupported files exit with a concise error.

## Run tests

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests cover employee validation and all management operations, persistence and reload, duplicate IDs, missing/corrupt/malformed JSON, search/filter/sort/statistics, CSV and JSON analysis, missing values, duplicates, category summaries, empty input, malformed rows, and unsupported extensions.

## Challenges and solutions

- **Persistence can be damaged by partial writes:** the repository writes a complete temporary JSON file in the destination folder and replaces the target only after serialization succeeds.
- **CSV values arrive as text while JSON values retain types:** analysis safely attempts finite numeric conversion and ignores missing or non-numeric values in numeric summaries.
- **A malformed record should not silently disappear:** management loading reports the record number and reason; analysis rejects malformed file structures with a useful error.
- **Missing data and duplicate data need explicit rules:** analysis documents its missing-value tokens and counts exact repeated records after their first occurrence.

## Future improvements

- Add pagination and more flexible multi-field sorting for larger employee datasets.
- Add an export option for management records and department-level salary summaries.
- Add richer analysis options, such as choosing category and numeric columns from command-line flags.
- Add integration tests for complete interactive menu sessions.
