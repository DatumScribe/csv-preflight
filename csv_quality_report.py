#!/usr/bin/env python3
"""Write a structural CSV report without copying cell values into it."""

import argparse
import csv
import sys
from pathlib import Path


MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_DATA_RECORDS = 100_000
MAX_COLUMNS = 10_000
MAX_DETAIL_LINES = 100


class InputProblem(Exception):
    """An input or output problem safe to summarize without echoing paths."""


def inspect_csv(path: Path, required_headers: tuple[str, ...]) -> dict:
    try:
        size_bytes = path.stat().st_size
    except OSError as error:
        raise InputProblem(type(error).__name__) from None
    if size_bytes > MAX_FILE_BYTES:
        raise InputProblem("FileTooLarge")

    csv.field_size_limit(MAX_FILE_BYTES)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle, delimiter=",", strict=True)
            try:
                header = next(reader)
            except StopIteration:
                return {
                    "size_bytes": size_bytes,
                    "header": [],
                    "empty_header": True,
                    "blank_headers": [],
                    "blank_header_count": 0,
                    "duplicate_headers": [],
                    "duplicate_header_count": 0,
                    "required_missing": list(range(1, len(required_headers) + 1)),
                    "records": 0,
                    "width_issues": [],
                    "width_issue_count": 0,
                    "blank_cells": [],
                    "blank_cell_count": 0,
                    "duplicate_rows": [],
                    "duplicate_row_count": 0,
                }

            if len(header) > MAX_COLUMNS:
                raise InputProblem("TooManyColumns")

            blank_header_positions = [
                index for index, value in enumerate(header, 1) if not value.strip()
            ]
            first_header_position: dict[str, int] = {}
            duplicate_headers: list[tuple[int, int]] = []
            duplicate_header_count = 0
            for index, value in enumerate(header, 1):
                normalized = value.strip().casefold()
                if not normalized:
                    continue
                if normalized in first_header_position:
                    duplicate_header_count += 1
                    if len(duplicate_headers) < MAX_DETAIL_LINES:
                        duplicate_headers.append((first_header_position[normalized], index))
                else:
                    first_header_position[normalized] = index

            required_missing = [
                index
                for index, requested in enumerate(required_headers, 1)
                if requested not in header
            ]
            seen_rows: dict[tuple[str, ...], int] = {}
            width_issues: list[tuple[int, int]] = []
            blank_cells: list[tuple[int, int]] = []
            duplicate_rows: list[tuple[int, int]] = []
            width_issue_count = 0
            blank_cell_count = 0
            duplicate_row_count = 0
            record_count = 0

            for row in reader:
                record_count += 1
                if record_count > MAX_DATA_RECORDS:
                    raise InputProblem("TooManyRecords")
                if len(row) > MAX_COLUMNS:
                    raise InputProblem("TooManyColumns")

                if len(row) != len(header):
                    width_issue_count += 1
                    if len(width_issues) < MAX_DETAIL_LINES:
                        width_issues.append((record_count, len(row)))

                for column, value in enumerate(row, 1):
                    if not value.strip():
                        blank_cell_count += 1
                        if len(blank_cells) < MAX_DETAIL_LINES:
                            blank_cells.append((record_count, column))

                row_key = tuple(row)
                if row_key in seen_rows:
                    duplicate_row_count += 1
                    if len(duplicate_rows) < MAX_DETAIL_LINES:
                        duplicate_rows.append((seen_rows[row_key], record_count))
                else:
                    seen_rows[row_key] = record_count

            return {
                "size_bytes": size_bytes,
                "header": header,
                "empty_header": not header,
                "blank_headers": blank_header_positions[:MAX_DETAIL_LINES],
                "blank_header_count": len(blank_header_positions),
                "duplicate_headers": duplicate_headers,
                "duplicate_header_count": duplicate_header_count,
                "required_missing": required_missing,
                "records": record_count,
                "width_issues": width_issues,
                "width_issue_count": width_issue_count,
                "blank_cells": blank_cells,
                "blank_cell_count": blank_cell_count,
                "duplicate_rows": duplicate_rows,
                "duplicate_row_count": duplicate_row_count,
            }
    except InputProblem:
        raise
    except (OSError, UnicodeError, csv.Error) as error:
        raise InputProblem(type(error).__name__) from None


def render_report(result: dict, required_header_count: int) -> str:
    lines = [
        "# CSV Structural Readiness Report",
        "",
        "This report checks file structure only. It does not guarantee that an import will succeed.",
        "",
        "## Input summary",
        "",
        f"- File size: {result['size_bytes']} bytes",
        "- Encoding: UTF-8 or UTF-8 with BOM",
        "- Delimiter: comma",
        f"- Header columns: {len(result['header'])}",
        f"- Data records: {result['records']}",
        f"- Required headers requested: {required_header_count}",
        "- Record positions below count data rows only and exclude the header.",
        "",
        "## Findings",
        "",
    ]

    if result["empty_header"]:
        lines.append("- Header row: empty or missing.")
    lines.append(f"- Blank header positions: {result['blank_header_count']}")
    if result["blank_headers"]:
        lines.append("  - Columns: " + ", ".join(map(str, result["blank_headers"])) + ".")
    if result["blank_header_count"] > len(result["blank_headers"]):
        lines.append(
            f"  - {result['blank_header_count'] - len(result['blank_headers'])} more omitted."
        )

    duplicate_header_count = result["duplicate_header_count"]
    lines.append(
        f"- Repeated header positions (trimmed, case-insensitive): {duplicate_header_count}"
    )
    for first, repeated in result["duplicate_headers"][:MAX_DETAIL_LINES]:
        lines.append(f"  - Column {repeated} repeats column {first}.")
    lines.append(
        "  - Further header details omitted."
        if duplicate_header_count > MAX_DETAIL_LINES
        else ""
    )
    if lines[-1] == "":
        lines.pop()

    lines.append(f"- Record-width mismatches: {result['width_issue_count']}")
    for record, actual_fields in result["width_issues"]:
        lines.append(f"  - Record {record}: {actual_fields} fields; expected {len(result['header'])}.")
    if result["width_issue_count"] > len(result["width_issues"]):
        lines.append(
            f"  - {result['width_issue_count'] - len(result['width_issues'])} more omitted."
        )

    lines.append(f"- Blank cells: {result['blank_cell_count']}")
    for record, column in result["blank_cells"]:
        lines.append(f"  - Record {record}, column {column}.")
    if result["blank_cell_count"] > len(result["blank_cells"]):
        lines.append(f"  - {result['blank_cell_count'] - len(result['blank_cells'])} more omitted.")

    lines.append(
        "- Exact duplicate data rows after the first occurrence: "
        f"{result['duplicate_row_count']}"
    )
    for first, repeated in result["duplicate_rows"]:
        lines.append(f"  - Record {repeated} repeats record {first}.")
    if result["duplicate_row_count"] > len(result["duplicate_rows"]):
        lines.append(
            f"  - {result['duplicate_row_count'] - len(result['duplicate_rows'])} more omitted."
        )

    lines.append(f"- Requested headers not found exactly: {len(result['required_missing'])}")
    for argument_position in result["required_missing"]:
        lines.append(f"  - Requested header argument {argument_position}.")

    lines.extend(
        [
            "",
            "Header names, input values, file paths, and other input content are not included in this report.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a CSV structure report without including cell values."
    )
    parser.add_argument("input", type=Path, help="UTF-8 comma-delimited CSV file (maximum 10 MB)")
    parser.add_argument("--required-header", action="append", default=[], metavar="NAME")
    parser.add_argument("--output", type=Path, help="new report path; defaults beside the input")
    args = parser.parse_args()

    if any(not header.strip() for header in args.required_header):
        parser.error("required header names must not be blank")

    output = args.output or args.input.with_suffix(".quality-report.md")
    try:
        if args.input.resolve() == output.resolve():
            raise InputProblem("OutputWouldReplaceInput")
        if output.exists():
            raise InputProblem("OutputAlreadyExists")
        result = inspect_csv(args.input, tuple(args.required_header))
        with output.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(render_report(result, len(args.required_header)))
    except InputProblem as error:
        print(f"Could not create report ({error}).", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Could not create report ({type(error).__name__}).", file=sys.stderr)
        return 2

    print("Report generated. Input values are not included.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
