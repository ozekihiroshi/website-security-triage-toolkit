# Website Security Triage Toolkit

A practical toolkit for initial website compromise triage, DNS/domain authentication review, and post-recovery validation.

## Purpose

This toolkit helps structure the first-response assessment for small business websites where the root cause of a website, DNS, SSL, email authentication, or CMS security issue is not yet clear.

## What This Toolkit Checks

- Website availability and HTTP status
- HTTPS and redirect behavior
- DNS records
- SPF / DMARC / DKIM selector checks
- CMS / WordPress indicators
- Basic post-recovery validation
- Documentation of findings and next steps

## What This Toolkit Does Not Claim

This toolkit does not claim to provide full forensic investigation, legal/compliance-level incident response, or guaranteed malware removal.

## Included Files

- Initial triage checklist
- DNS/domain authentication checklist
- Post-recovery validation checklist
- Client initial questions template
- Findings report template
- Lightweight Python scripts

## Example Use Cases

- Hacked or suspicious website
- Unexpected redirects
- SSL or DNS issues
- Domain authentication issues
- Email authentication review
- WordPress/CMS recovery validation

```
python scripts/check_site_status.py https://example.com
python scripts/check_domain_auth.py example.com
python scripts/check_domain_auth.py example.com --dkim-selector google
```