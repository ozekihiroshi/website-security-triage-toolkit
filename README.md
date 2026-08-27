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

## Where to Run It

Normally run the Python scripts from your own workstation, WSL, or Linux environment. They query public website, DNS, TLS, and email records; they do not require SSH, WordPress Admin, or target-server filesystem access. Running them on the target server is optional, and the result then reflects that server's network and DNS viewpoint.

The scripts are read-only and do not change DNS, email, TLS, or website configuration. The checklists and templates support the manual investigation and reporting around those checks.

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

Install the declared DNS dependency in a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Requirements and Failure Semantics

- Python 3.8 or later.
- `check_site_status.py` uses the Python standard library.
- `check_domain_auth.py` needs `dnspython` or the system `dig` command.
- `check_email_dns.py` and `check_domain_stack.py` require `dnspython`.

A missing DNS dependency means the DNS result is **not checked**. It must not be reported as a record being present or absent.

`check_domain_auth.py`, `check_email_dns.py`, and `check_domain_stack.py` return a non-zero execution status when one or more DNS queries fail. A failed query is reported as `not checked` or `error`, never as a confirmed missing record. A completed query that finds no record remains a normal diagnostic result.

The toolkit does not install dependencies automatically.

## Verification

After installing `requirements.txt`, run all regression tests:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

The tests use mocked DNS answers and failures. They do not query or modify a real DNS zone. Actual public DNS checks remain read-only and should be recorded separately from unit-test results.

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
