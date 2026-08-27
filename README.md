# Website Security Triage Toolkit

A practical toolkit for initial website compromise triage, DNS/domain authentication review, website and email connection checks, and post-recovery validation.

This toolkit is designed for small business websites, WordPress/CMS sites, and general hosting environments where the root cause of a website, domain, DNS, SSL, email authentication, website connection, or security issue is not yet clear.

The goal is to support a structured first-response assessment, document findings clearly, and identify practical next steps.

## Purpose

This toolkit helps organize the initial investigation of issues such as:

* Hacked or suspicious websites
* Unexpected redirects
* Website downtime or abnormal HTTP responses
* SSL / HTTPS problems
* DNS misconfiguration
* Domain connection issues when moving to a new website provider
* Business email sending, receiving, or deliverability issues
* SPF / DKIM / DMARC issues
* WordPress or CMS compromise indicators
* Post-recovery validation after cleanup or migration

## What This Toolkit Includes

* Initial website security triage checklist
* DNS and domain authentication checklist
* Domain, website, and business email connection checklist
* Post-recovery validation checklist
* Client initial questions template
* Findings report templates
* Lightweight Python scripts for website, DNS, email, and connection checks

## Email Deliverability / DNS Checks

This toolkit includes a basic email DNS troubleshooting script for small business hosting and cPanel-style environments.

It checks:

* NS records
* MX records
* SPF
* DMARC
* DKIM selectors
* Common mail hostnames such as `mail.example.com`

Example:

```bash
python3 scripts/check_email_dns.py example.com
python3 scripts/check_email_dns.py example.com --selector google
```

## Domain, Website, and Email Connection Checks

The toolkit also includes a read-only diagnostic script for cases where a domain, website provider, and business email service must work together safely.

It checks:

* Apex domain and `www` DNS routing
* NS, A, AAAA, CNAME, MX, and TXT-related records
* SPF, DMARC, and an optional DKIM selector
* HTTP, HTTPS, redirects, and TLS certificate status
* Existing MX records that should be preserved during website connection work
* Common risks when changing DNS for a new website provider

Example:

```bash
python3 scripts/check_domain_stack.py example.com
python3 scripts/check_domain_stack.py example.com --dkim-selector google
python3 scripts/check_domain_stack.py example.com --json domain-stack-report.json
```

The script requires `dnspython`:

```bash
python3 -m pip install dnspython
```

## Requirements and Failure Semantics

- Python 3.8 or later.
- `check_site_status.py` uses the Python standard library.
- `check_domain_auth.py` needs `dnspython` or the system `dig` command.
- `check_email_dns.py` and `check_domain_stack.py` require `dnspython`.

A missing DNS dependency means the DNS result is **not checked**. It must not be reported as a record being present or absent.

`check_domain_auth.py` returns exit 2 when a DNS query cannot run or returns an execution error. It returns exit 0 only when its DNS queries complete without an `ERROR:` result.

The toolkit does not install dependencies automatically.

## Verification

Run the standard-library regression test:

```bash
python -m unittest tests/test_check_domain_auth.py
```

The test uses mocked DNS errors and does not query or modify a real DNS zone.

## Suggested Workflow

1. Confirm the client’s reported symptoms and intended outcome.
2. Review website availability, SSL, redirects, and HTTP status.
3. Record the current DNS zone before making changes.
4. Check DNS, domain, website routing, and email authentication records.
5. Identify the current website provider and email provider.
6. Preserve MX and email authentication records unless email settings are intentionally changing.
7. Review CMS or WordPress indicators if applicable.
8. Confirm access, backups, and recent changes.
9. Document findings and recommended next steps.
10. Perform remediation only within the confirmed scope.
11. Validate website access, TLS, email sending, and email receiving after changes.

## What This Toolkit Does Not Claim

This toolkit does not claim to provide full forensic investigation, legal/compliance-level incident response, guaranteed malware removal, or guaranteed DNS/email remediation.

It is intended for structured assessment, practical first-response review, documentation, and basic validation.

## Included Files

### Checklists

* [Initial Triage Checklist](checklists/initial-triage-checklist.md)
* [DNS / Domain Authentication Checklist](checklists/dns-domain-auth-checklist.md)
* [Domain, Website, and Business Email Connection Checklist](docs/domain-email-website-connection-checklist.md)
* [Post-Recovery Validation Checklist](checklists/post-recovery-validation-checklist.md)

### Templates

* [Client Initial Questions](templates/client-initial-questions.md)
* [Findings Report Template](templates/findings-report-template.md)
* [Domain Connection Findings Report](templates/domain-connection-findings-report.md)

### Scripts

* `scripts/check_site_status.py`
* `scripts/check_domain_auth.py`
* `scripts/check_email_dns.py`
* `scripts/check_domain_stack.py`

### Examples and Case Studies

* [Sample Findings Report](examples/sample-findings-report.md)
* [AWS EC2 System Mail Delivery via Google Workspace SMTP Relay](docs/case-studies/aws-ec2-system-mail-google-workspace-smtp-relay.md)

## Example Script Usage

```bash
python3 scripts/check_site_status.py https://example.com

python3 scripts/check_domain_auth.py example.com
python3 scripts/check_domain_auth.py example.com --dkim-selector google

python3 scripts/check_email_dns.py example.com
python3 scripts/check_email_dns.py example.com --selector google

python3 scripts/check_domain_stack.py example.com
python3 scripts/check_domain_stack.py example.com --dkim-selector google
```
