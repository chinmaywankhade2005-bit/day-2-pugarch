"""Read a CSV or JSON dataset and report data quality and descriptive statistics."""

import argparse
import csv
import json
import math
from pathlib import Path
import sys


MISSING_TOKENS = {"", "na", "n/a", "null", "none"}


def _is_missing(value):
    return value is None or (isinstance(value, str) and value.strip().casefold() in MISSING_TOKENS)


def _load_json(path):
    try:
        with path.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}.") from exc
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        payload = payload["records"]
    if not isinstance(payload, list):
        raise ValueError("JSON input must be a list of record objects or an object with a 'records' list.")
    if any(not isinstance(record, dict) for record in payload):
        raise ValueError("Every JSON record must be an object.")
    return payload


def _load_csv(path):
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            if reader.fieldnames is None:
                return []
            headers = [header.strip() if header else "" for header in reader.fieldnames]
            if any(not header for header in headers):
                raise ValueError("CSV header names cannot be empty.")
            if len(set(headers)) != len(headers):
                raise ValueError("CSV header names must be unique after trimming whitespace.")
            records = []
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(f"CSV row {line_number} has more values than the header.")
                records.append({header: row.get(original) for header, original in zip(headers, reader.fieldnames)})
            return records
    except csv.Error as exc:
        raise ValueError(f"Invalid CSV data: {exc}.") from exc


def load_records(path):
    path = Path(path)
    suffix = path.suffix.casefold()
    if suffix == ".json":
        return _load_json(path)
    if suffix == ".csv":
        return _load_csv(path)
    raise ValueError("Unsupported file type. Provide a .csv or .json file.")


def _number(value):
    if _is_missing(value) or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _canonical_value(value):
    if isinstance(value, dict):
        return {key: _canonical_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_canonical_value(item) for item in value]
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def analyze(records):
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ValueError("Records must be a list of objects.")
    columns = sorted({key for record in records for key in record}, key=str.casefold)
    missing_values = {column: sum(_is_missing(record.get(column)) for record in records) for column in columns}
    seen = set()
    duplicate_count = 0
    for record in records:
        fingerprint = json.dumps(_canonical_value(record), sort_keys=True, ensure_ascii=False, default=str)
        if fingerprint in seen:
            duplicate_count += 1
        else:
            seen.add(fingerprint)

    numeric_fields = []
    category_fields = []
    for field in columns:
        present = [record.get(field) for record in records if not _is_missing(record.get(field))]
        converted = [_number(value) for value in present]
        if present and all(value is not None for value in converted):
            numeric_fields.append(field)
        elif present:
            category_fields.append(field)

    def numeric_summary(rows):
        summary = {}
        for field in numeric_fields:
            values = [number for row in rows if (number := _number(row.get(field))) is not None]
            if values:
                summary[field] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "minimum": min(values),
                    "maximum": max(values),
                }
        return summary

    category_statistics = {}
    for field in category_fields:
        groups = {}
        for row in records:
            value = row.get(field)
            label = "<missing>" if _is_missing(value) else str(value).strip()
            groups.setdefault(label, []).append(row)
        category_statistics[field] = {
            label: {"record_count": len(rows), "numeric": numeric_summary(rows)}
            for label, rows in sorted(groups.items(), key=lambda pair: pair[0].casefold())
        }

    return {
        "record_count": len(records),
        "missing_values": missing_values,
        "duplicate_records": duplicate_count,
        "numeric_statistics": numeric_summary(records),
        "category_statistics": category_statistics,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="Path to a .csv or .json dataset")
    args = parser.parse_args(argv)
    try:
        report = analyze(load_records(args.file))
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
