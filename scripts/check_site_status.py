#!/usr/bin/env python3
"""
check_site_status.py

Lightweight public website status checker.

This script performs basic non-invasive checks:
- HTTP/HTTPS reachability
- Status code
- Redirect chain
- Final URL
- Page title
- Basic HTTPS check

It does not perform vulnerability scanning, brute force testing,
exploit attempts, or aggressive crawling.
"""

import argparse
import re
import ssl
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self):
        title = " ".join(part.strip() for part in self.title_parts if part.strip())
        return re.sub(r"\s+", " ", title).strip()


class TrackingRedirectHandler(HTTPRedirectHandler):
    def __init__(self):
        super().__init__()
        self.redirects = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.redirects.append((code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def normalize_url(value):
    if not value.startswith(("http://", "https://")):
        return "https://" + value
    return value


def fetch_url(url, timeout):
    redirect_handler = TrackingRedirectHandler()
    ssl_context = ssl.create_default_context()

    opener = build_opener(
        redirect_handler,
        HTTPSHandler(context=ssl_context),
    )

    request = Request(
        url,
        headers={
            "User-Agent": "WebsiteSecurityTriageToolkit/1.0 (+basic-status-check)"
        },
        method="GET",
    )

    try:
        response = opener.open(request, timeout=timeout)
        body = response.read(1024 * 256)
        final_url = response.geturl()
        status_code = response.getcode()
        headers = dict(response.headers.items())
        return {
            "ok": True,
            "status_code": status_code,
            "final_url": final_url,
            "headers": headers,
            "body": body,
            "redirects": redirect_handler.redirects,
            "error": None,
        }
    except HTTPError as exc:
        body = exc.read(1024 * 64)
        return {
            "ok": False,
            "status_code": exc.code,
            "final_url": exc.geturl(),
            "headers": dict(exc.headers.items()) if exc.headers else {},
            "body": body,
            "redirects": redirect_handler.redirects,
            "error": f"HTTP error: {exc.code} {exc.reason}",
        }
    except URLError as exc:
        return {
            "ok": False,
            "status_code": None,
            "final_url": None,
            "headers": {},
            "body": b"",
            "redirects": redirect_handler.redirects,
            "error": f"URL error: {exc.reason}",
        }
    except Exception as exc:
        return {
            "ok": False,
            "status_code": None,
            "final_url": None,
            "headers": {},
            "body": b"",
            "redirects": redirect_handler.redirects,
            "error": f"Unexpected error: {exc}",
        }


def extract_title(body):
    try:
        text = body.decode("utf-8", errors="replace")
    except Exception:
        return ""

    parser = TitleParser()
    parser.feed(text)
    return parser.title


def same_domain(original_url, final_url):
    if not original_url or not final_url:
        return None

    original_host = urlparse(original_url).hostname or ""
    final_host = urlparse(final_url).hostname or ""

    original_host = original_host.lower().removeprefix("www.")
    final_host = final_host.lower().removeprefix("www.")

    return original_host == final_host


def print_report(url, result):
    print("# Website Status Check")
    print()
    print(f"Input URL: {url}")

    parsed = urlparse(url)
    print(f"Input scheme: {parsed.scheme or 'N/A'}")
    print(f"Input host: {parsed.hostname or 'N/A'}")
    print()

    print("## Result")
    print(f"Reachable: {'yes' if result['ok'] else 'no'}")
    print(f"Status code: {result['status_code'] if result['status_code'] else 'N/A'}")
    print(f"Final URL: {result['final_url'] or 'N/A'}")

    if result["final_url"]:
        final_scheme = urlparse(result["final_url"]).scheme
        print(f"Final scheme: {final_scheme}")
        print(f"Final uses HTTPS: {'yes' if final_scheme == 'https' else 'no'}")

    domain_match = same_domain(url, result["final_url"])
    if domain_match is not None:
        print(f"Final domain matches input domain: {'yes' if domain_match else 'no'}")

    title = extract_title(result["body"])
    print(f"Page title: {title if title else 'N/A'}")

    server = result["headers"].get("Server", "")
    if server:
        print(f"Server header: {server}")

    content_type = result["headers"].get("Content-Type", "")
    if content_type:
        print(f"Content-Type: {content_type}")

    if result["error"]:
        print(f"Error: {result['error']}")

    print()
    print("## Redirect Chain")
    if result["redirects"]:
        for index, (code, redirect_url) in enumerate(result["redirects"], start=1):
            print(f"{index}. {code} -> {redirect_url}")
    else:
        print("No redirects observed.")

    print()
    print("## Notes")
    print("- This is a basic public website status check.")
    print("- It does not confirm whether a site is fully clean or secure.")
    print("- If suspicious redirects are intermittent, test from multiple devices, browsers, and locations.")


def main():
    parser = argparse.ArgumentParser(
        description="Basic website status and redirect checker."
    )
    parser.add_argument("url", help="Website URL or domain to check.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds. Default: 10.",
    )

    args = parser.parse_args()
    url = normalize_url(args.url)

    result = fetch_url(url, args.timeout)
    print_report(url, result)

    if not result["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
