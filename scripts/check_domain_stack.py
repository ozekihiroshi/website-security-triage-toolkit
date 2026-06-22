#!/usr/bin/env python3
"""
Check a domain's website, DNS, and email-routing configuration.

Examples:
  python3 scripts/check_domain_stack.py example.com
  python3 scripts/check_domain_stack.py example.com --dkim-selector google
  python3 scripts/check_domain_stack.py example.com --json report.json

Optional dependency:
  pip install dnspython

The script is read-only. It does not change DNS, website, or email settings.
"""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from http.client import HTTPConnection, HTTPSConnection
from typing import Any, Iterable, Optional
from urllib.parse import urljoin, urlparse

try:
    import dns.exception
    import dns.resolver
except ImportError:
    print(
        "Missing dependency: dnspython\n"
        "Install it with: python3 -m pip install dnspython",
        file=sys.stderr,
    )
    raise SystemExit(2)


USER_AGENT = "domain-stack-check/1.0"
DEFAULT_TIMEOUT = 12


@dataclass
class CheckResult:
    name: str
    status: str
    records: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class HttpResult:
    url: str
    status: str
    http_status: Optional[int] = None
    final_url: Optional[str] = None
    redirect_chain: list[str] = field(default_factory=list)
    server: Optional[str] = None
    error: Optional[str] = None


def normalize_domain(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("https://", "").replace("http://", "")
    value = value.split("/", 1)[0]
    value = value.split(":", 1)[0]
    return value.rstrip(".")


def make_resolver(timeout: int) -> dns.resolver.Resolver:
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout
    return resolver


def resolve_records(
    resolver: dns.resolver.Resolver, domain: str, record_type: str
) -> CheckResult:
    try:
        answers = resolver.resolve(domain, record_type)
        records = sorted(str(answer).rstrip(".") for answer in answers)
        return CheckResult(record_type, "ok", records)
    except dns.resolver.NXDOMAIN:
        return CheckResult(record_type, "not_found", notes=["Domain does not exist (NXDOMAIN)."])
    except dns.resolver.NoAnswer:
        return CheckResult(record_type, "not_found", notes=[f"No {record_type} record found."])
    except dns.resolver.NoNameservers as exc:
        return CheckResult(record_type, "error", notes=[f"Nameserver error: {exc}"])
    except dns.exception.Timeout:
        return CheckResult(record_type, "error", notes=["DNS lookup timed out."])
    except Exception as exc:  # pragma: no cover - defensive CLI behavior
        return CheckResult(record_type, "error", notes=[f"DNS lookup failed: {exc}"])


def get_txt_values(
    resolver: dns.resolver.Resolver, domain: str
) -> list[str]:
    result = resolve_records(resolver, domain, "TXT")
    if result.status != "ok":
        return []
    values: list[str] = []
    for record in result.records:
        # dnspython renders quoted chunks. Keep the content readable.
        values.append(record.replace('" "', "").strip('"'))
    return values


def find_prefixed_txt(
    values: Iterable[str], prefixes: tuple[str, ...]
) -> list[str]:
    return [value for value in values if value.lower().startswith(prefixes)]


def check_dmarc(resolver: dns.resolver.Resolver, domain: str) -> CheckResult:
    values = get_txt_values(resolver, f"_dmarc.{domain}")
    matches = find_prefixed_txt(values, ("v=dmarc1",))
    if matches:
        return CheckResult("DMARC", "ok", matches)
    return CheckResult(
        "DMARC",
        "warning",
        notes=["No DMARC policy record found at _dmarc."],
    )


def check_dkim(
    resolver: dns.resolver.Resolver, domain: str, selector: Optional[str]
) -> CheckResult:
    if not selector:
        return CheckResult(
            "DKIM",
            "manual_check",
            notes=[
                "A DKIM selector is required for DNS verification.",
                "Run again with --dkim-selector SELECTOR after confirming the selector from the email provider.",
            ],
        )

    host = f"{selector}._domainkey.{domain}"
    values = get_txt_values(resolver, host)
    matches = find_prefixed_txt(values, ("v=dkim1", "k=rsa", "k=ed25519"))
    if matches:
        return CheckResult("DKIM", "ok", matches, [f"Selector checked: {selector}"])
    return CheckResult(
        "DKIM",
        "warning",
        notes=[f"No DKIM TXT record found for selector '{selector}' at {host}."],
    )


def http_request(url: str, timeout: int, max_redirects: int = 5) -> HttpResult:
    current_url = url
    chain: list[str] = []

    for _ in range(max_redirects + 1):
        parsed = urlparse(current_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return HttpResult(url, "error", error=f"Invalid URL: {current_url}")

        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        try:
            connection_cls = HTTPSConnection if parsed.scheme == "https" else HTTPConnection
            connection = connection_cls(parsed.netloc, timeout=timeout)
            connection.request("HEAD", path, headers={"User-Agent": USER_AGENT})
            response = connection.getresponse()

            # Some servers reject HEAD; retry once with GET.
            if response.status in {405, 501}:
                connection.close()
                connection = connection_cls(parsed.netloc, timeout=timeout)
                connection.request("GET", path, headers={"User-Agent": USER_AGENT})
                response = connection.getresponse()

            status = response.status
            server = response.getheader("Server")
            location = response.getheader("Location")
            connection.close()

            if status in {301, 302, 303, 307, 308} and location:
                next_url = urljoin(current_url, location)
                chain.append(f"{status} {current_url} -> {next_url}")
                current_url = next_url
                continue

            result_status = "ok" if 200 <= status < 400 else "warning"
            return HttpResult(
                url=url,
                status=result_status,
                http_status=status,
                final_url=current_url,
                redirect_chain=chain,
                server=server,
            )
        except Exception as exc:
            return HttpResult(url, "error", redirect_chain=chain, error=str(exc))

    return HttpResult(url, "warning", final_url=current_url, redirect_chain=chain,
                      error=f"Stopped after {max_redirects} redirects.")


def get_certificate_note(domain: str, timeout: int) -> CheckResult:
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                cert = secure_sock.getpeercert()
                not_after = cert.get("notAfter", "unknown")
                subject = ", ".join("=".join(item) for group in cert.get("subject", []) for item in group)
                return CheckResult(
                    "TLS certificate",
                    "ok",
                    records=[f"Subject: {subject or 'not provided'}", f"Expires: {not_after}"],
                )
    except Exception as exc:
        return CheckResult("TLS certificate", "warning", notes=[f"Could not validate HTTPS certificate: {exc}"])


def analyze_safety(
    apex: dict[str, CheckResult],
    www: dict[str, CheckResult],
    mail: dict[str, CheckResult],
    http_results: list[HttpResult],
) -> list[str]:
    notes: list[str] = []

    if mail["MX"].status == "ok":
        notes.append(
            "Existing MX records detected. Do not replace or delete MX records when connecting a website to a new provider."
        )
    else:
        notes.append(
            "No MX records were found. Confirm whether this domain is expected to receive email before changing DNS."
        )

    if mail["SPF"].status != "ok":
        notes.append("No SPF record was detected. Confirm the email provider and publishing requirements before adding one.")
    if mail["DMARC"].status != "ok":
        notes.append("No DMARC policy was detected. Add it only after confirming SPF and DKIM alignment.")
    if all(item.status == "error" for item in http_results):
        notes.append("Website checks failed. Confirm DNS propagation, hosting status, firewall rules, and the expected web host.")
    if apex["A"].status != "ok" and apex["AAAA"].status != "ok" and apex["CNAME"].status != "ok":
        notes.append("No common web-routing record was detected at the apex domain. Verify the provider's required A, ALIAS/ANAME, or CNAME-equivalent record.")
    if www["A"].status != "ok" and www["AAAA"].status != "ok" and www["CNAME"].status != "ok":
        notes.append("No common web-routing record was detected for www. Confirm whether www should redirect or point to a separate host.")

    notes.append(
        "DNS propagation can take time. Compare the provider's exact required records with the current DNS zone before making further changes."
    )
    return notes


def format_record_block(result: CheckResult) -> list[str]:
    lines = [f"## {result.name} [{result.status}]"]
    if result.records:
        lines.append("Records:")
        lines.extend(f"  - {record}" for record in result.records)
    if result.notes:
        lines.append("Notes:")
        lines.extend(f"  - {note}" for note in result.notes)
    lines.append("")
    return lines


def build_report(
    domain: str,
    apex: dict[str, CheckResult],
    www: dict[str, CheckResult],
    mail: dict[str, CheckResult],
    http_results: list[HttpResult],
    tls: CheckResult,
    safety_notes: list[str],
) -> str:
    lines = [
        f"# Domain Stack Check Report: {domain}",
        "",
        f"Generated (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "This is a read-only diagnostic report. Review DNS changes carefully before applying them.",
        "",
        "# Website routing — apex domain",
        "",
    ]
    for key in ("NS", "A", "AAAA", "CNAME"):
        lines.extend(format_record_block(apex[key]))

    lines.extend(["# Website routing — www subdomain", ""])
    for key in ("A", "AAAA", "CNAME"):
        lines.extend(format_record_block(www[key]))

    lines.extend(["# Email routing and authentication", ""])
    for key in ("MX", "SPF", "DMARC", "DKIM"):
        lines.extend(format_record_block(mail[key]))

    lines.extend(["# HTTP and HTTPS checks", ""])
    for result in http_results:
        label = result.url
        lines.append(f"## {label} [{result.status}]")
        if result.http_status is not None:
            lines.append(f"HTTP status: {result.http_status}")
        if result.final_url:
            lines.append(f"Final URL: {result.final_url}")
        if result.server:
            lines.append(f"Server header: {result.server}")
        if result.redirect_chain:
            lines.append("Redirects:")
            lines.extend(f"  - {item}" for item in result.redirect_chain)
        if result.error:
            lines.append(f"Notes:\n  - {result.error}")
        lines.append("")

    lines.extend(format_record_block(tls))
    lines.extend(["# Safety notes", ""])
    lines.extend(f"- {note}" for note in safety_notes)
    lines.append("")
    lines.extend(
        [
            "# Manual checks still required",
            "",
            "- Confirm the intended website provider's exact A, CNAME, or TXT verification values.",
            "- Confirm which service currently receives business email (for example Google Workspace, Microsoft 365, or a hosting email service).",
            "- Send and receive a real test message after DNS changes, including a message to an external mailbox.",
            "- Verify the final DNS zone in the DNS provider dashboard and record the change date, editor, and purpose.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only website, DNS, and email-routing diagnostic."
    )
    parser.add_argument("domain", help="Domain name, such as example.com")
    parser.add_argument(
        "--dkim-selector",
        help="Optional DKIM selector to verify, such as google or selector1",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"DNS and HTTP timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        help="Optional JSON output path. The human-readable report is still printed.",
    )
    args = parser.parse_args()

    domain = normalize_domain(args.domain)
    if not domain or "." not in domain:
        parser.error("Provide a valid domain name, such as example.com")

    resolver = make_resolver(args.timeout)

    apex = {
        record_type: resolve_records(resolver, domain, record_type)
        for record_type in ("NS", "A", "AAAA", "CNAME")
    }
    www_domain = f"www.{domain}"
    www = {
        record_type: resolve_records(resolver, www_domain, record_type)
        for record_type in ("A", "AAAA", "CNAME")
    }

    txt_values = get_txt_values(resolver, domain)
    spf_values = find_prefixed_txt(txt_values, ("v=spf1",))
    spf = CheckResult("SPF", "ok", spf_values) if spf_values else CheckResult(
        "SPF", "warning", notes=["No SPF TXT record found at the apex domain."]
    )

    mail = {
        "MX": resolve_records(resolver, domain, "MX"),
        "SPF": spf,
        "DMARC": check_dmarc(resolver, domain),
        "DKIM": check_dkim(resolver, domain, args.dkim_selector),
    }

    http_results = [
        http_request(f"http://{domain}", args.timeout),
        http_request(f"https://{domain}", args.timeout),
        http_request(f"https://{www_domain}", args.timeout),
    ]
    tls = get_certificate_note(domain, args.timeout)
    safety_notes = analyze_safety(apex, www, mail, http_results)

    report = build_report(domain, apex, www, mail, http_results, tls, safety_notes)
    print(report)

    if args.json:
        payload: dict[str, Any] = {
            "domain": domain,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "apex_dns": {key: asdict(value) for key, value in apex.items()},
            "www_dns": {key: asdict(value) for key, value in www.items()},
            "email": {key: asdict(value) for key, value in mail.items()},
            "http": [asdict(value) for value in http_results],
            "tls": asdict(tls),
            "safety_notes": safety_notes,
        }
        try:
            with open(args.json, "w", encoding="utf-8") as fp:
                json.dump(payload, fp, indent=2, ensure_ascii=False)
            print(f"JSON report written to: {args.json}", file=sys.stderr)
        except OSError as exc:
            print(f"Could not write JSON output: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
