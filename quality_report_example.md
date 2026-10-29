# CSV Structural Readiness Report

This example uses synthetic data only.

This report checks file structure only. It does not guarantee that an import will succeed.

## Input summary

- File size: 139 bytes
- Encoding: UTF-8 or UTF-8 with BOM
- Delimiter: comma
- Header columns: 4
- Data records: 6
- Required headers requested: 0
- Record positions below count data rows only and exclude the header.

## Findings

- Blank header positions: 0
- Repeated header positions (trimmed, case-insensitive): 0
- Record-width mismatches: 1
  - Record 6: 3 fields; expected 4.
- Blank cells: 1
  - Record 3, column 4.
- Exact duplicate data rows after the first occurrence: 0
- Requested headers not found exactly: 0

Header names, input values, file paths, and other input content are not included in this report.
