# Domain, Website, and Business Email Connection Checklist

Use this checklist when a client is connecting a domain to a new website provider, changing DNS, or troubleshooting business email.

This procedure is designed to reduce the risk of accidentally interrupting email while changing website-related DNS records.

## Scope and safety boundary

- Confirm the exact goal: website connection, email repair, domain transfer, or a combination.
- Identify who owns the domain registrar account and who controls DNS.
- Confirm the client can approve DNS changes and recover account access.
- Do not delete or replace existing records until their purpose is understood.
- Do not treat DNS propagation delay as a configuration failure without checking the expected TTL and provider requirements.

## 1. Record the starting state

Before making changes, capture:

- Domain registrar and DNS provider
- Nameservers
- Existing A, AAAA, CNAME, MX, and TXT records
- Existing redirects and website provider
- Current email provider
- Screenshots or an exported DNS zone, where available
- Date, time, editor, and stated purpose of any planned change

Suggested command:

```bash
python3 scripts/check_domain_stack.py example.com --json before-change.json
```

## 2. Identify the email service

Determine which service currently handles business email:

- Google Workspace
- Microsoft 365
- GoDaddy Professional Email
- cPanel or hosting email
- Another provider

Confirm:

- MX records
- SPF TXT record
- DKIM selector and record
- DMARC record
- Whether the domain is expected to receive email at all

**Important:** Website connection changes normally affect A, AAAA, CNAME, or provider-verification TXT records. They should not require deletion of MX records.

## 3. Confirm the website provider requirements

Obtain the provider's exact connection instructions before editing DNS.

Record:

- Required host or name, such as `@` or `www`
- Required record type: A, AAAA, CNAME, TXT, or verification record
- Exact target value
- Whether the provider requires a redirect between apex and `www`
- Whether the domain must be verified before SSL is issued
- Expected propagation period

Do not rely on generic instructions from a different provider.

## 4. Plan the smallest safe change

- Keep email-related records unchanged unless email itself is being repaired.
- Change only the records required for the website connection.
- Avoid duplicate or conflicting records for the same host and record type.
- For an existing live website, confirm whether a maintenance window or rollback plan is needed.
- Preserve a copy of the original record values.

## 5. Apply and verify the change

After the DNS change:

1. Check the DNS zone in the provider dashboard.
2. Run the domain-stack check again.
3. Test the apex domain over HTTP and HTTPS.
4. Test `www` over HTTPS.
5. Confirm redirects behave as intended.
6. Confirm the TLS certificate is valid.
7. Send a test email from the business address to an external mailbox.
8. Reply from an external mailbox to the business address.
9. Check spam or junk folders and relevant mail logs, where available.

Suggested command:

```bash
python3 scripts/check_domain_stack.py example.com --dkim-selector YOUR_SELECTOR --json after-change.json
```

## 6. Distinguish propagation from configuration errors

Possible signs of DNS propagation:

- The DNS dashboard shows the intended record, but public resolvers still show the old value.
- The website provider indicates that verification is pending.
- Results differ by network or resolver.
- The relevant TTL has not yet elapsed.

Possible signs of a configuration error:

- The record type, host, or target differs from the provider's documented requirement.
- An old conflicting A, AAAA, or CNAME record remains.
- The site works on one hostname but not the other without an intentional redirect.
- MX records changed unexpectedly or mail delivery fails after the change.
- TLS issuance remains unsuccessful after the expected verification period.

## 7. Record the final state and handover

Document:

- Final DNS records changed
- Records intentionally left unchanged
- Website provider and selected canonical hostname
- Email provider and authentication status
- Tests performed and outcomes
- Remaining limitations or pending propagation
- A rollback reference, including original record values

Use `templates/domain-connection-findings-report.md` for a client-facing summary.
