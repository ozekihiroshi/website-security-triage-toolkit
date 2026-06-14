## Website Security Triage Toolkit

A practical toolkit for initial website compromise triage, DNS/domain authentication review, and post-recovery validation.

This toolkit is designed for small business websites, WordPress/CMS sites, and general hosting environments where the root cause of a website, domain, DNS, SSL, email authentication, or security issue is not yet clear.

The goal is to support a structured first-response assessment, document findings clearly, and identify practical next steps.

## Email Deliverability / DNS Checks

This toolkit also includes a basic email DNS troubleshooting script for small business hosting and cPanel-style environments.

It checks:

- NS records
- MX records
- SPF
- DMARC
- DKIM selectors
- common mail hostnames such as `mail.example.com`

Example:

```bash
python3 scripts/check_email_dns.py example.com
python3 scripts/check_email_dns.py example.com --selector google

## Purpose

This toolkit helps organize the initial investigation of issues such as:

- Hacked or suspicious websites
- Unexpected redirects
- Website downtime or abnormal HTTP responses
- SSL / HTTPS problems
- DNS misconfiguration
- SPF / DKIM / DMARC issues
- WordPress or CMS compromise indicators
- Post-recovery validation after cleanup or migration

## What This Toolkit Includes

- Initial website security triage checklist
- DNS and domain authentication checklist
- Post-recovery validation checklist
- Client initial questions template
- Findings report template
- Lightweight Python scripts for basic checks

## What This Toolkit Does Not Claim

This toolkit does not claim to provide full forensic investigation, legal/compliance-level incident response, or guaranteed malware removal.

It is intended for structured assessment, practical first-response review, documentation, and basic validation.

## Suggested Workflow

1. Confirm the client’s reported symptoms.
2. Review website availability, SSL, redirects, and HTTP status.
3. Check DNS, domain, and email authentication records.
4. Review CMS or WordPress indicators if applicable.
5. Confirm access, backups, and recent changes.
6. Document findings and recommended next steps.
7. Perform remediation only within the confirmed scope.

## Included Files

- [Initial Triage Checklist](checklists/initial-triage-checklist.md)
- [DNS / Domain Authentication Checklist](checklists/dns-domain-auth-checklist.md)
- [Post-Recovery Validation Checklist](checklists/post-recovery-validation-checklist.md)
- [Client Initial Questions](templates/client-initial-questions.md)
- [Findings Report Template](templates/findings-report-template.md)
- [Sample Findings Report](examples/sample-findings-report.md)

## Example Script Usage

```bash
python3 scripts/check_site_status.py https://example.com
python3 scripts/check_domain_auth.py example.com
python3 scripts/check_domain_auth.py example.com --dkim-selector google
```