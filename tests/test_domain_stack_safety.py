import importlib.util
import pathlib
import sys
import unittest


SCRIPT_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_domain_stack.py"
)
SPEC = importlib.util.spec_from_file_location("check_domain_stack_safety", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DomainStackSafetyTests(unittest.TestCase):
    def test_dns_errors_are_not_summarized_as_missing_records(self):
        error = MODULE.CheckResult("DNS", "error", notes=["synthetic failure"])
        apex = {"A": error, "AAAA": error, "CNAME": error}
        www = {"A": error, "AAAA": error, "CNAME": error}
        mail = {
            "MX": error,
            "SPF": error,
            "DMARC": error,
            "DKIM": MODULE.CheckResult("DKIM", "manual_check"),
        }

        notes = MODULE.analyze_safety(apex, www, mail, [])
        report = " ".join(notes)

        self.assertIn("MX was not checked", report)
        self.assertIn("Apex web-routing records were not checked", report)
        self.assertIn("www web-routing records were not checked", report)
        self.assertNotIn("No MX records were found", report)
        self.assertNotIn("No common web-routing record", report)


if __name__ == "__main__":
    unittest.main()
