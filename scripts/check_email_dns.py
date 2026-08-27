#!/usr/bin/env python3
"""
check_email_dns.py

DNS-based email deliverability checker for small business domains.

Checks:
- NS records
- MX records
- SPF record
- DMARC record
- DKIM record for one or more selectors
- Basic warnings for common misconfigurations

This script is intended for first-response troubleshooting.
It does not send email and does not guarantee inbox placement.

Requirements:
    pip install dnspython

Usage:
    python3 scripts/check_email_dns.py example.com
    python3 scripts/check_email_dns.py example.com --selector default
    python3 scripts/check_email_dns.py example.com --selector default --selector selector1
    python3 scripts/check_email_dns.py example.com --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

try:
    import dns.resolver
    import dns.exception
except ImportError:
    print("Error: dnspython is required. Install it with: pip install dnspython", file=sys.stderr)
    sys.exit(2)


DEFAULT_SELECTORS = ["default", "selector1", "selector2", "google", "k1"]


@dataclass
class CheckResult:
    name: str
    status: str
    records: List[str]
    warnings: List[str]
    notes: List[str]


def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0]
    domain = domain.strip(".")
    if not domain or "." not in domain:
        raise ValueError("Please provide a valid domain, for example: example.com")
    return domain


def query_records(name: str, record_type: str, timeout: float = 5.0) -> List[str]:
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    resolver.timeout = timeout

    try:
        answers = resolver.resolve(name, record_type)
    except dns.resolver.NXDOMAIN:
        return []
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NoNameservers as exc:
        return [f"ERROR: nameserver failure: {exc}"]
    except dns.exception.Timeout:
        return ["ERROR: DNS query timed out"]
    except Exception as exc:
        return [f"ERROR: DNS query failed: {exc}"]

    records = []
    for answer in answers:
        if record_type.upper() == "TXT":
            # dnspython TXT strings may be split; join them.
            try:
                txt = b"".join(answer.strings).decode("utf-8", errors="replace")
                records.append(txt)
            except AttributeError:
                records.append(str(answer).strip('"'))
        else:
            records.append(str(answer).rstrip("."))
    return records


def query_failed(records: List[str]) -> bool:
    return any(record.startswith("ERROR:") for record in records)


def check_ns(domain: str) -> CheckResult:
    records = query_records(domain, "NS")
    warnings = []
    notes = []

    if query_failed(records):
        warnings.append("NS was not checked because the DNS query failed.")
        status = "error"
    elif not records:
        warnings.append("No NS records found. DNS authority could not be confirmed.")
        status = "warning"
    else:
        status = "ok"
        notes.append("These nameservers indicate where DNS is currently managed.")

    return CheckResult("NS", status, records, warnings, notes)


def check_mx(domain: str) -> CheckResult:
    records = query_records(domain, "MX")
    warnings = []
    notes = []

    if query_failed(records):
        warnings.append("MX was not checked because the DNS query failed.")
        status = "error"
    elif not records:
        warnings.append("No MX records found. Incoming email may not be delivered.")
        status = "warning"
    else:
        status = "ok"
        notes.append("MX records determine where inbound mail is delivered.")

        lower = " ".join(records).lower()
        providers = {
            "google": ["aspmx.l.google.com", "googlemail.com"],
            "microsoft": ["mail.protection.outlook.com"],
            "titan": ["mx1.titan.email", "mx2.titan.email"],
            "zoho": ["zoho.com", "zohomail"],
        }
        detected = [provider for provider, needles in providers.items() if any(n in lower for n in needles)]
        if len(detected) > 1:
            warnings.append(f"MX records appear to reference multiple providers: {', '.join(detected)}. Confirm intended mail provider.")

    return CheckResult("MX", status, records, warnings, notes)


def extract_spf_records(txt_records: List[str]) -> List[str]:
    return [r for r in txt_records if r.lower().startswith("v=spf1")]


def check_spf(domain: str) -> CheckResult:
    txt_records = query_records(domain, "TXT")
    spf_records = extract_spf_records(txt_records)
    warnings = []
    notes = []

    if query_failed(txt_records):
        warnings.append("SPF was not checked because the DNS query failed.")
        notes.extend(txt_records)
        return CheckResult("SPF", "error", [], warnings, notes)

    if not spf_records:
        warnings.append("No SPF record found. Outbound mail authentication may fail.")
        status = "warning"
    elif len(spf_records) > 1:
        warnings.append("Multiple SPF records found. A domain should publish only one SPF record.")
        status = "warning"
    else:
        status = "ok"
        spf = spf_records[0]
        notes.append("SPF record found.")

        mechanism_pattern = r"(?:^|\s)[+?~-]?(?:include:|ip4:|ip6:|a(?=\s|$|:|/)|mx(?=\s|$|:|/))"
        if not re.search(mechanism_pattern, spf, flags=re.IGNORECASE):
            warnings.append("SPF record has no obvious sending source mechanism such as include, ip4, ip6, a, or mx.")

        if "-all" in spf:
            notes.append("SPF uses hard fail (-all). This can be appropriate, but confirm all legitimate senders are included.")
        elif "~all" in spf:
            notes.append("SPF uses soft fail (~all), commonly used during normal operation or transition.")
        elif "?all" in spf:
            warnings.append("SPF uses neutral (?all), which may be weak for authentication.")
        elif "+all" in spf:
            warnings.append("SPF uses +all, which is unsafe because it authorizes any sender.")

    return CheckResult("SPF", status, spf_records, warnings, notes)


def check_dmarc(domain: str) -> CheckResult:
    name = f"_dmarc.{domain}"
    txt_records = query_records(name, "TXT")
    dmarc_records = [r for r in txt_records if r.lower().startswith("v=dmarc1")]
    warnings = []
    notes = []

    if query_failed(txt_records):
        warnings.append("DMARC was not checked because the DNS query failed.")
        notes.extend(txt_records)
        return CheckResult("DMARC", "error", [], warnings, notes)

    if not dmarc_records:
        warnings.append("No DMARC record found.")
        status = "warning"
    elif len(dmarc_records) > 1:
        warnings.append("Multiple DMARC records found. Only one DMARC record should be published.")
        status = "warning"
    else:
        status = "ok"
        dmarc = dmarc_records[0]
        notes.append("DMARC record found.")

        if "p=none" in dmarc.lower():
            notes.append("DMARC policy is p=none. This is useful for monitoring and initial troubleshooting.")
        elif "p=quarantine" in dmarc.lower():
            notes.append("DMARC policy is p=quarantine. Confirm SPF/DKIM alignment before using this policy.")
        elif "p=reject" in dmarc.lower():
            notes.append("DMARC policy is p=reject. Confirm SPF/DKIM alignment and legitimate senders.")
        else:
            warnings.append("DMARC policy tag p= was not clearly found.")

    return CheckResult("DMARC", status, dmarc_records, warnings, notes)


def check_dkim(domain: str, selectors: List[str]) -> CheckResult:
    found_records = []
    warnings = []
    notes = []
    query_errors = []

    for selector in selectors:
        name = f"{selector}._domainkey.{domain}"
        txt_records = query_records(name, "TXT")
        if query_failed(txt_records):
            query_errors.extend(f"{selector}: {record}" for record in txt_records)
            continue
        dkim_records = [r for r in txt_records if "v=dkim1" in r.lower() or "p=" in r.lower()]
        for record in dkim_records:
            found_records.append(f"{selector}: {record}")

    if query_errors:
        status = "error"
        warnings.append("DKIM was not fully checked because one or more DNS queries failed.")
        notes.extend(query_errors)
    elif not found_records:
        status = "warning"
        warnings.append("No DKIM records found for the checked selectors. The correct selector may be different.")
        notes.append("Check cPanel Email Deliverability or the mail provider admin panel for the exact DKIM selector.")
    else:
        status = "ok"
        notes.append("DKIM record found for at least one selector.")

    return CheckResult("DKIM", status, found_records, warnings, notes)


def check_common_mail_hosts(domain: str) -> CheckResult:
    names = [
        f"mail.{domain}",
        f"webmail.{domain}",
        f"smtp.{domain}",
        f"imap.{domain}",
    ]
    records = []
    warnings = []
    notes = []
    query_errors = []

    for name in names:
        a_records = query_records(name, "A")
        cname_records = query_records(name, "CNAME")
        query_errors.extend(f"{name} A {record}" for record in a_records if record.startswith("ERROR:"))
        query_errors.extend(f"{name} CNAME {record}" for record in cname_records if record.startswith("ERROR:"))
        for r in a_records:
            if not r.startswith("ERROR:"):
                records.append(f"{name} A {r}")
        for r in cname_records:
            if not r.startswith("ERROR:"):
                records.append(f"{name} CNAME {r}")

    if query_errors:
        status = "error"
        warnings.append("Common mail hosts were not fully checked because one or more DNS queries failed.")
        notes.extend(query_errors)
    elif records:
        status = "ok"
        notes.append("Common mail-related hostnames were found.")
    else:
        status = "info"
        notes.append("No common mail hostnames found. This may be normal for external mail providers.")

    return CheckResult("Common mail hosts", status, records, warnings, notes)


def build_summary(results: List[CheckResult]) -> Dict[str, Any]:
    warning_count = sum(len(r.warnings) for r in results)
    error_count = sum(1 for r in results if r.status == "error")
    status = "error" if error_count else ("ok" if warning_count == 0 else "warning")

    return {
        "overall_status": status,
        "warning_count": warning_count,
        "error_count": error_count,
        "results": [asdict(r) for r in results],
    }


def print_human_report(domain: str, summary: Dict[str, Any]) -> None:
    print(f"# Email DNS Check Report: {domain}")
    print()
    print(f"Overall status: {summary['overall_status']}")
    print(f"Warnings: {summary['warning_count']}")
    print(f"Errors: {summary['error_count']}")
    print()

    for result in summary["results"]:
        print(f"## {result['name']} [{result['status']}]")

        if result["records"]:
            print("Records:")
            for record in result["records"]:
                print(f"  - {record}")
        else:
            print("Records: none found")

        if result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")

        if result["notes"]:
            print("Notes:")
            for note in result["notes"]:
                print(f"  - {note}")

        print()

    print("## Suggested next steps")
    print("- Confirm the active DNS provider before making changes.")
    print("- Compare MX/SPF/DKIM/DMARC records with the intended mail provider documentation.")
    print("- In cPanel, review Email Deliverability and Email Routing.")
    print("- If bounce messages exist, inspect the exact SMTP error text.")
    print("- If provider-side blocking or server reputation is suspected, escalate to the hosting provider with this report.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check DNS email deliverability records for a domain.")
    parser.add_argument("domain", help="Domain to check, for example: example.com")
    parser.add_argument(
        "--selector",
        action="append",
        dest="selectors",
        help="DKIM selector to check. Can be used multiple times.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of a human-readable report.",
    )
    args = parser.parse_args()

    try:
        domain = normalize_domain(args.domain)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    selectors = args.selectors if args.selectors else DEFAULT_SELECTORS

    results = [
        check_ns(domain),
        check_mx(domain),
        check_spf(domain),
        check_dmarc(domain),
        check_dkim(domain, selectors),
        check_common_mail_hosts(domain),
    ]

    summary = build_summary(results)

    if args.json:
        print(json.dumps({"domain": domain, **summary}, indent=2, ensure_ascii=False))
    else:
        print_human_report(domain, summary)

    return 2 if summary["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
