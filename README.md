# CSV Preflight

A pair of dependency-free command-line tools for checking CSV files before import. Both run locally and avoid printing cell values. `csv_preflight.py` gives a concise structural check; `csv_quality_report.py` creates a Markdown report with structural positions and counts. Neither validates business rules, column types, sensitive data, or compatibility with a particular importer.

This project was created with AI assistance. Automated tests cover representative cases for `csv_preflight.py`; the report utility includes a synthetic example. Review outputs before relying on either tool.

## Quick start

Requires Python 3.9 or newer; there are no third-party packages to install. [Download `csv_preflight.py`](https://raw.githubusercontent.com/DatumScribe/csv-preflight/master/csv_preflight.py), save it beside your CSV (or use its full path), then run:

```sh
python csv_preflight.py your-file.csv
```

With the included `example.csv`, the output is:

```text
Checked 2 data records. 0 structural issue(s).
```

To use the sample and other project files, [clone the repository](https://github.com/DatumScribe/csv-preflight):

```sh
git clone https://github.com/DatumScribe/csv-preflight.git
cd csv-preflight
python csv_preflight.py example.csv
```

Other examples:

```sh
python csv_preflight.py your-file.psv --delimiter "|"
python csv_preflight.py your-file.csv --required-header item --required-header quantity
```

For a tab delimiter, pass an actual tab character as the argument; shell quoting varies. Exit code 0 means no structural issues found, 1 means issues were found, and 2 means input could not be read or parsed. Blank data records are counted and reported as short records. Quoted line breaks are supported; record numbers and physical line numbers can differ. A clean result is not a guarantee that an import will succeed.

Use `--required-header` once for each header you want to check. Matching is case- and space-sensitive. For privacy, a missing-header message refers to its argument position rather than printing the header. For example, Shopify documents case-sensitive product CSV header names; choose the headers appropriate to your specific import from its [current instructions](https://help.shopify.com/en/manual/products/import-export/using-csv) (retrieved 2026-10-26). This tool is independent of Shopify and does not validate its full schema, product variants, or store state.

Run the included checks for `csv_preflight.py` with `python -m unittest discover -s tests` from this directory. That checker does not upload or modify files; its output may still reveal row counts and locations, so handle logs appropriately. The report tool writes a new Markdown file and is described below.

## Detailed report mode

Download [`csv_quality_report.py`](https://raw.githubusercontent.com/DatumScribe/csv-preflight/master/csv_quality_report.py) and run:

```sh
python csv_quality_report.py your-file.csv
```

By default, this writes a new `your-file.quality-report.md` beside the input and refuses to overwrite an existing file. It checks blank/repeated headers, record-width mismatches, blank cells, exact duplicate data rows, and optional exact required-header presence. Use `--required-header NAME` once per header. The report contains counts and row/column positions only; it omits header names, cell values, and file paths. Detailed positions are capped at 100 per finding type, with complete totals.

The report tool accepts UTF-8 (with or without BOM), comma-delimited files up to 10 MB, 100,000 data records, and 10,000 columns. It makes no network calls and does not modify the input; it creates a report file. It returns exit code 0 when a report was generated, even if it found issues, and 2 when input or output could not be processed. [Synthetic input](quality_report_example.csv) and [sample report](quality_report_example.md) are included.

## License

MIT; see LICENSE.
