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
    / "check_domain_stack.py"
)
SPEC = importlib.util.spec_from_file_location("check_domain_stack", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DomainStackTests(unittest.TestCase):
    def test_txt_error_is_preserved(self):
        error_result = MODULE.CheckResult(
            "TXT",
            "error",
            notes=["DNS lookup timed out."],
        )
        with mock.patch.object(MODULE, "resolve_records", return_value=error_result):
            result = MODULE.get_txt_result(mock.sentinel.resolver, "example.com")

        self.assertEqual(result.status, "error")
        self.assertIn("timed out", result.notes[0])

    def test_dmarc_failure_is_not_reported_as_absent(self):
        error_result = MODULE.CheckResult(
            "TXT",
            "error",
            notes=["DNS lookup timed out."],
        )
        with mock.patch.object(MODULE, "get_txt_result", return_value=error_result):
            result = MODULE.check_dmarc(mock.sentinel.resolver, "example.com")

        self.assertEqual(result.status, "error")
        self.assertIn("not checked", result.notes[0])
        self.assertNotIn("No DMARC policy", " ".join(result.notes))

    def test_main_returns_two_when_dns_queries_fail(self):
        dns_error = MODULE.CheckResult(
            "DNS",
            "error",
            notes=["synthetic DNS failure"],
        )
        http_ok = MODULE.HttpResult(
            "https://example.com",
            "ok",
            http_status=200,
            final_url="https://example.com",
        )
        argv = ["check_domain_stack.py", "example.com"]
        output = io.StringIO()

        with mock.patch.object(MODULE, "make_resolver", return_value=mock.sentinel.resolver):
            with mock.patch.object(MODULE, "resolve_records", return_value=dns_error):
                with mock.patch.object(MODULE, "http_request", return_value=http_ok):
                    with mock.patch.object(MODULE, "get_certificate_note", return_value=MODULE.CheckResult("TLS", "ok")):
                        with mock.patch.object(sys, "argv", argv):
                            with contextlib.redirect_stdout(output):
                                exit_code = MODULE.main()

        self.assertEqual(exit_code, 2)
        self.assertIn("SPF was not checked", output.getvalue())
        self.assertNotIn("No SPF record was detected", output.getvalue())


if __name__ == "__main__":
    unittest.main()
