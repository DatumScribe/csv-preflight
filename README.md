# CSV Preflight

A small, dependency-free command-line check for CSV files before import. It runs on your computer and reports structural problems without printing cell values. It checks blank or repeated headers, inconsistent record widths, and optionally whether specified headers are present exactly. It does not validate business rules, column types, sensitive data, or compatibility with a particular importer. It reads UTF-8 (with or without a BOM).

This project was created with AI assistance. Automated tests cover representative cases; please review outputs before relying on them.

## Run

Requires Python 3.9 or newer. Download `csv_preflight.py` and run:

```sh
python csv_preflight.py example.csv
python csv_preflight.py example.psv --delimiter "|"
python csv_preflight.py example.csv --required-header item --required-header quantity
```

For a tab delimiter, pass an actual tab character as the argument; shell quoting varies. Exit code 0 means no structural issues found, 1 means issues were found, and 2 means input could not be read or parsed. Blank data records are counted and reported as short records. Quoted line breaks are supported; record numbers and physical line numbers can differ. A clean result is not a guarantee that an import will succeed.

Use `--required-header` once for each header you want to check. Matching is case- and space-sensitive. For privacy, a missing-header message refers to its argument position rather than printing the header. For example, Shopify documents case-sensitive product CSV header names; choose the headers appropriate to your specific import from its [current instructions](https://help.shopify.com/en/manual/products/import-export/using-csv) (retrieved 2026-10-26). This tool is independent of Shopify and does not validate its full schema, product variants, or store state.

Run the included checks with `python -m unittest discover -s tests` from this directory. No files are uploaded, modified, or retained by the tool. Its output may still reveal row counts and locations, so handle logs appropriately.

## License

MIT; see LICENSE.
