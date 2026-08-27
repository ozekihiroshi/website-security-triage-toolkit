#!/usr/bin/env python3
"""
check_domain_auth.py

Lightweight DNS and domain authentication checker.

This script performs basic public DNS checks:
- NS
- A
- AAAA
- CNAME
- MX
- TXT
- SPF
- DMARC
- Optional DKIM selector

It uses dnspython if available. If dnspython is not installed,
it falls back to the system "dig" command when available.

It does not make DNS changes and does not perform aggressive scanning.
"""

import argparse
import shutil
import subprocess
import sys


try:
    import dns.resolver
    DNSPYTHON_AVAILABLE = True
except ImportError:
    DNSPYTHON_AVAILABLE = False


RECORD_TYPES = ["NS", "A", "AAAA", "CNAME", "MX", "TXT"]


def query_with_dnspython(name, record_type):
    try:
        answers = dns.resolver.resolve(name, record_type)
        return [format_answer(record_type, answer) for answer in answers]
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        return []
    except dns.resolver.NoNameservers:
        return []
    except dns.exception.Timeout:
        return ["ERROR: DNS query timed out"]
    except Exception as exc:
        return [f"ERROR: {exc}"]


def format_answer(record_type, answer):
    if record_type == "TXT":
        try:
            return "".join(part.decode("utf-8", errors="replace") for part in answer.strings)
        except Exception:
            return str(answer).strip('"')

    if record_type == "MX":
        return f"{answer.preference} {answer.exchange}".rstrip(".")

    return str(answer).rstrip(".")


def query_with_dig(name, record_type):
    if not shutil.which("dig"):
        return ["ERROR: dnspython is not installed and dig command was not found"]

    command = ["dig", "+short", name, record_type]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return ["ERROR: dig query timed out"]
    except Exception as exc:
        return [f"ERROR: {exc}"]

    if completed.returncode != 0:
        error = completed.stderr.strip()
        return [f"ERROR: {error or 'dig failed'}"]

    lines = [line.strip().strip('"') for line in completed.stdout.splitlines() if line.strip()]
    return lines


def query_dns(name, record_type):
    if DNSPYTHON_AVAILABLE:
        return query_with_dnspython(name, record_type)
    return query_with_dig(name, record_type)


def query_failed(records):
    return any(record.startswith("ERROR:") for record in records)


def find_spf(txt_records):
    return [record for record in txt_records if record.lower().startswith("v=spf1")]


def find_dmarc(domain):
    return query_dns(f"_dmarc.{domain}", "TXT")


def find_dkim(domain, selector):
    if not selector:
        return []
    return query_dns(f"{selector}._domainkey.{domain}", "TXT")


def print_records(title, records):
    print(f"## {title}")
    if records:
        for record in records:
            print(f"- {record}")
    else:
        print("- Not found")
    print()


def print_assessment(domain, txt_records, dmarc_records, dkim_records, selector):
    spf_records = find_spf(txt_records)

    print("## Basic Assessment")

    if query_failed(txt_records):
        print("- SPF: not checked because the DNS query failed")
    elif not spf_records:
        print("- SPF: not found")
    elif len(spf_records) == 1:
        print("- SPF: found")
    else:
        print("- SPF: multiple SPF records found. This should usually be corrected.")

    if query_failed(dmarc_records):
        print("- DMARC: not checked because the DNS query failed")
    elif not dmarc_records:
        print("- DMARC: not found")
    else:
        print("- DMARC: found")

    if selector:
        if query_failed(dkim_records):
            print(f"- DKIM selector '{selector}': not checked because the DNS query failed")
        elif not dkim_records:
            print(f"- DKIM selector '{selector}': not found")
        elif any("p=" in record.lower() and record.lower().strip().endswith("p=") for record in dkim_records):
            print(f"- DKIM selector '{selector}': record found, but public key appears empty")
        else:
            print(f"- DKIM selector '{selector}': found")
    else:
        print("- DKIM: not checked because no selector was provided")

    print()
    print("## Notes")
    print("- SPF should normally have only one TXT record starting with v=spf1.")
    print("- DKIM requires the selector provided by the email service.")
    print("- DMARC is checked at _dmarc.<domain>.")
    print("- DNS records should not be changed without confirming the active email, hosting, and third-party services.")
    print()


def normalize_domain(domain):
    domain = domain.strip()
    for prefix in ("http://", "https://"):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
            break
    domain = domain.split("/")[0]
    return domain.strip().lower()


def main():
    parser = argparse.ArgumentParser(
        description="Check public DNS and domain authentication records."
    )
    parser.add_argument("domain", help="Domain to check, for example example.com")
    parser.add_argument(
        "--dkim-selector",
        help="Optional DKIM selector, for example google, selector1, or default",
    )

    args = parser.parse_args()
    domain = normalize_domain(args.domain)

    print("# Domain Authentication Check")
    print()
    print(f"Domain: {domain}")
    print(f"DNS library: {'dnspython' if DNSPYTHON_AVAILABLE else 'dig fallback'}")
    print()

    results = {}
    for record_type in RECORD_TYPES:
        results[record_type] = query_dns(domain, record_type)
        print_records(record_type, results[record_type])

    dmarc_records = find_dmarc(domain)
    print_records("DMARC", dmarc_records)

    dkim_records = []
    if args.dkim_selector:
        dkim_records = find_dkim(domain, args.dkim_selector)
        print_records(f"DKIM ({args.dkim_selector})", dkim_records)

    txt_records = results.get("TXT", [])
    print_assessment(domain, txt_records, dmarc_records, dkim_records, args.dkim_selector)

    checked_record_sets = list(results.values()) + [dmarc_records]
    if args.dkim_selector:
        checked_record_sets.append(dkim_records)
    return 2 if any(query_failed(records) for records in checked_record_sets) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        sys.exit(130)
