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
    / "check_email_dns.py"
)
SPEC = importlib.util.spec_from_file_location("check_email_dns", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EmailDnsTests(unittest.TestCase):
    def test_query_failure_is_distinct_from_empty_answer(self):
        with mock.patch.object(
            MODULE.dns.resolver.Resolver,
            "resolve",
            side_effect=MODULE.dns.exception.Timeout(),
        ):
            records = MODULE.query_records("example.com", "MX")

        self.assertTrue(MODULE.query_failed(records))
        self.assertIn("timed out", records[0])

    def test_spf_qualified_ip4_is_recognized(self):
        with mock.patch.object(
            MODULE,
            "query_records",
            return_value=["v=spf1 +ip4:192.0.2.10/32 ~all"],
        ):
            result = MODULE.check_spf("example.com")

        self.assertEqual(result.status, "ok")
        self.assertFalse(
            any("no obvious sending source" in warning for warning in result.warnings)
        )
    def test_ns_failure_is_error_not_missing_record_warning(self):
        with mock.patch.object(
            MODULE,
            "query_records",
            return_value=["ERROR: synthetic DNS failure"],
        ):
            result = MODULE.check_ns("example.com")

        self.assertEqual(result.status, "error")
        self.assertIn("not checked", result.warnings[0])
        self.assertNotIn("No NS records found", result.warnings)

    def test_main_returns_two_when_queries_fail(self):
        output = io.StringIO()
        argv = ["check_email_dns.py", "example.com"]

        with mock.patch.object(
            MODULE,
            "query_records",
            return_value=["ERROR: synthetic DNS failure"],
        ):
            with mock.patch.object(sys, "argv", argv):
                with contextlib.redirect_stdout(output):
                    exit_code = MODULE.main()

        report = output.getvalue()
        self.assertEqual(exit_code, 2)
        self.assertIn("Overall status: error", report)
        self.assertIn("NS was not checked", report)
        self.assertNotIn("No MX records found", report)


if __name__ == "__main__":
    unittest.main()
