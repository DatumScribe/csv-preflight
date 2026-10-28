#!/usr/bin/env python3
"""Check CSV structure locally without printing cell contents."""
import argparse
import csv
import sys
from pathlib import Path


def inspect(path: Path, delimiter: str = ',', required_headers: tuple[str, ...] = ()) -> tuple[list[str], int]:
    issues: list[str] = []
    count = 0
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.reader(handle, delimiter=delimiter, strict=True)
        try:
            header = next(reader)
        except StopIteration:
            return ['File is empty; expected a header row.'], 0
        if not header:
            return ['Header row is empty.'], 0
        for index, name in enumerate(header, 1):
            if not name.strip():
                issues.append(f'Header column {index} is blank.')
        seen: set[str] = set()
        for index, name in enumerate(header, 1):
            normalized = name.strip().casefold()
            if normalized and normalized in seen:
                issues.append(f'Header column {index} duplicates an earlier header (ignoring case and surrounding spaces).')
            seen.add(normalized)
        for index, required in enumerate(required_headers, 1):
            if required not in header:
                issues.append(f'Required header argument {index} is missing (exact case and spacing required).')
        for row in reader:
            count += 1
            if len(row) != len(header):
                issues.append(f'Record {count + 1} ending near physical line {reader.line_num} has {len(row)} fields; expected {len(header)}.')
    return issues, count


def main() -> int:
    parser = argparse.ArgumentParser(description='Check CSV structure on your own machine. Cell values are not printed.')
    parser.add_argument('path', type=Path, help='UTF-8 CSV file to check')
    parser.add_argument('--delimiter', default=',', help='single-character field delimiter (default: comma)')
    parser.add_argument('--required-header', action='append', default=[], metavar='NAME', help='require an exact header; repeat for multiple names')
    args = parser.parse_args()
    if len(args.delimiter) != 1 or args.delimiter in '\r\n"':
        parser.error('delimiter must be one character other than a quote or newline')
    if any(not name.strip() for name in args.required_header):
        parser.error('required headers must not be blank')
    try:
        issues, rows = inspect(args.path, args.delimiter, tuple(args.required_header))
    except (OSError, UnicodeError, csv.Error) as error:
        # Do not include the exception message: it can contain private file paths or data.
        print(f'Could not read or parse input ({type(error).__name__}). Check encoding, file access, and CSV quoting.', file=sys.stderr)
        return 2
    print(f'Checked {rows} data records. {len(issues)} structural issue(s).')
    for issue in issues:
        print(f'- {issue}')
    return 1 if issues else 0


if __name__ == '__main__':
    raise SystemExit(main())
