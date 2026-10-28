import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'csv_preflight.py'


class PreflightTests(unittest.TestCase):
    def run_file(self, data, *options):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as folder:
            path = Path(folder) / 'input.csv'
            path.write_bytes(data)
            return subprocess.run([sys.executable, str(SCRIPT), str(path), *options], capture_output=True, text=True)

    def test_valid_quoted_newline_and_bom(self):
        result = self.run_file(b'\xef\xbb\xbfa,b\n"one\ntwo",3\n')
        self.assertEqual(result.returncode, 0)
        self.assertIn('1 data records', result.stdout)

    def test_duplicate_empty_header_and_short_record(self):
        result = self.run_file(b'Name, name ,\nsecret,2\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('3 structural issue(s)', result.stdout)
        self.assertNotIn('secret', result.stdout)

    def test_malformed_and_bad_encoding(self):
        for data in (b'a,b\n"unclosed,2', b'a,b\n\xff,2'):
            self.assertEqual(self.run_file(data).returncode, 2)

    def test_empty_file_and_custom_delimiter(self):
        self.assertEqual(self.run_file(b'').returncode, 1)
        self.assertEqual(self.run_file(b'a|b\n1|2\n', '--delimiter', '|').returncode, 0)

    def test_required_headers_are_exact_and_values_are_private(self):
        data = b'Handle,Title\nprivate-product,Example\n'
        good = self.run_file(data, '--required-header', 'Handle', '--required-header', 'Title')
        self.assertEqual(good.returncode, 0)
        missing = self.run_file(data, '--required-header', 'handle', '--required-header', ' Title')
        self.assertEqual(missing.returncode, 1)
        self.assertIn('2 structural issue(s)', missing.stdout)
        self.assertNotIn('private-product', missing.stdout)
        self.assertNotIn('handle', missing.stdout)
        self.assertEqual(self.run_file(data, '--required-header', ' ').returncode, 2)


if __name__ == '__main__':
    unittest.main()
