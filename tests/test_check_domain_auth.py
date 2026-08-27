import contextlib
import importlib.util
import io
import pathlib
import sys
import unittest
from unittest import mock


SCRIPT_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_domain_auth.py"
)
SPEC = importlib.util.spec_from_file_location("check_domain_auth", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class DomainAuthTests(unittest.TestCase):
    def test_normalize_domain_is_python_38_compatible(self):
        self.assertEqual(
            MODULE.normalize_domain("https://Example.COM/path"),
            "example.com",
        )

    def test_query_failed_detects_error_records(self):
        self.assertTrue(MODULE.query_failed(["ERROR: synthetic failure"]))
        self.assertFalse(MODULE.query_failed([]))
        self.assertFalse(MODULE.query_failed(["v=spf1 -all"]))

    def test_dns_errors_are_not_reported_as_found_or_not_found(self):
        output = io.StringIO()
        argv = [
            "check_domain_auth.py",
            "example.com",
            "--dkim-selector",
            "google",
        ]

        with mock.patch.object(MODULE, "query_dns", return_value=["ERROR: synthetic failure"]):
            with mock.patch.object(sys, "argv", argv):
                with contextlib.redirect_stdout(output):
                    exit_code = MODULE.main()

        report = output.getvalue()
        self.assertEqual(exit_code, 2)
        self.assertIn("SPF: not checked because the DNS query failed", report)
        self.assertIn("DMARC: not checked because the DNS query failed", report)
        self.assertIn(
            "DKIM selector 'google': not checked because the DNS query failed",
            report,
        )
        self.assertNotIn("SPF: not found", report)
        self.assertNotIn("DMARC: found", report)


if __name__ == "__main__":
    unittest.main()
