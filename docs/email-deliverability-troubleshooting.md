# Email Deliverability Troubleshooting

This document describes a practical first-response workflow for troubleshooting domain-based email delivery problems on cPanel, Bluehost, shared hosting, and small business web hosting environments.

The goal is to identify whether the issue is caused by DNS records, mailbox configuration, SMTP settings, authentication records, hosting limits, or provider-side restrictions.

## Typical Symptoms

Common client reports include:

- Email cannot be sent
- Email cannot be received
- Messages go to spam
- Contact form emails are not delivered
- Webmail works, but Outlook / Gmail / Apple Mail does not
- Domain email stopped working after DNS or hosting changes
- cPanel Email Deliverability shows warnings
- SPF, DKIM, or DMARC records are missing or invalid

## Initial Questions for the Client

Before changing any settings, collect the following information:

1. What is the domain name?
2. Is the issue with sending, receiving, or both?
3. Is the email hosted on cPanel / Bluehost, Google Workspace, Microsoft 365, Titan Email, Zoho, or another provider?
4. Who manages DNS for the domain?
   - Bluehost
   - Cloudflare
   - Namecheap
   - GoDaddy
   - name.com
   - other registrar / DNS provider
5. Which email address is affected?
6. Does webmail work?
7. Does the issue affect all recipients or only some domains?
8. Are there bounce-back messages? If yes, request the full bounce text.
9. Were there any recent changes?
   - DNS changes
   - hosting migration
   - website migration
   - nameserver change
   - mail provider change
   - SSL change
10. Are contact form emails also affected?

## Troubleshooting Workflow

### 1. Confirm DNS Authority

First identify where DNS is actually managed.

Check:

```bash
dig NS example.com
```

The active nameservers determine where MX, SPF, DKIM, and DMARC records must be edited.

A common failure pattern is that the user edits DNS records in Bluehost or cPanel, but the domain is actually using Cloudflare, Namecheap, or another external DNS provider.

### 2. Check MX Records

MX records determine where inbound mail is delivered.

```bash
dig MX example.com
```

Confirm that MX records match the intended mail provider.

Examples:

- cPanel local mail: usually the domain or mail server hostname
- Google Workspace: Google MX records
- Microsoft 365: Microsoft / Outlook protection MX record
- Titan Email: `mx1.titan.email` and `mx2.titan.email`
- Zoho Mail: Zoho MX records

Problems to look for:

- No MX record
- MX points to an old provider
- Mixed records from multiple providers
- Incorrect priority
- DNS changes made at the wrong DNS host

### 3. Check SPF Record

SPF is published as a TXT record at the root domain.

```bash
dig TXT example.com
```

Look for a record starting with:

```text
v=spf1
```

Problems to look for:

- No SPF record
- More than one SPF record
- Missing include for the active mail provider
- Syntax errors
- Too many DNS lookups
- Old provider remains in SPF
- Hard fail `-all` used before confirming all senders

Only one SPF record should exist per domain. Multiple SPF TXT records commonly cause authentication failure.

### 4. Check DMARC Record

DMARC is published as TXT at `_dmarc.example.com`.

```bash
dig TXT _dmarc.example.com
```

A basic monitoring policy may look like:

```text
v=DMARC1; p=none; rua=mailto:postmaster@example.com
```

Problems to look for:

- No DMARC record
- Invalid syntax
- Too strict policy before SPF/DKIM are working
- Reporting address not controlled by the domain owner

For first-response troubleshooting, `p=none` is often safer while diagnosing. Stronger policies such as `quarantine` or `reject` should be used only after SPF and DKIM alignment are confirmed.

### 5. Check DKIM

DKIM selector names vary by provider.

Common selectors include:

- `default`
- `selector1`
- `selector2`
- `google`
- `k1`
- provider-specific selectors

Example:

```bash
dig TXT default._domainkey.example.com
```

Problems to look for:

- Missing DKIM record
- DKIM record published at the wrong DNS provider
- Incorrect selector
- cPanel DKIM record not copied to external DNS
- Broken TXT formatting

In cPanel environments, check **Email Deliverability** for the recommended DKIM record.

### 6. Check cPanel Email Deliverability

In cPanel, review:

- Email Deliverability
- Email Accounts
- Forwarders
- Default Address
- Email Routing
- Track Delivery
- Spam Filters
- Autoresponders
- Disk Usage
- Mailbox quota

Important cPanel setting:

- If mail is handled by the same cPanel server, Email Routing is usually **Local Mail Exchanger**.
- If mail is handled elsewhere, Email Routing is usually **Remote Mail Exchanger**.

Incorrect Email Routing can break delivery even when MX records look correct.

### 7. Check Sending Configuration

For SMTP clients, verify:

- Username is the full email address
- Password is current
- SMTP hostname is correct
- Port is correct
- SSL/TLS mode is correct
- Authentication is enabled

Common ports:

- 465: SMTP over SSL
- 587: SMTP with STARTTLS
- 993: IMAP over SSL
- 995: POP3 over SSL

If webmail works but a mail client does not, the problem is likely client configuration, password, SSL/TLS, or port settings rather than DNS.

### 8. Check Receiving Configuration

If inbound mail fails:

- Confirm MX records
- Confirm Email Routing
- Confirm mailbox exists
- Confirm mailbox quota
- Check forwarders
- Check spam/junk filtering
- Check whether the domain is using external DNS
- Check whether the provider requires specific MX records

### 9. Check Bounce Messages

Bounce-back messages often reveal the actual cause.

Look for:

- `550`
- `554`
- `Relay access denied`
- `SPF fail`
- `DKIM fail`
- `DMARC policy`
- `Mailbox full`
- `User unknown`
- `Connection timed out`
- `Blocked using`
- `Blacklisted`
- `Rate limited`

Never guess from symptoms alone if a bounce message is available.

### 10. Check Contact Form Delivery

Website contact forms commonly fail because the site sends mail as an address that does not match the domain authentication setup.

Check:

- From address domain
- Reply-To address
- SMTP plugin settings
- WordPress mail plugin logs
- Whether the website uses PHP mail or authenticated SMTP
- Whether SPF includes the web server or SMTP provider

For WordPress, authenticated SMTP is usually more reliable than PHP mail.

## Common Findings and Recommended Fixes

| Finding | Likely Cause | Recommended Action |
|---|---|---|
| No MX record | Mail provider not configured | Add correct MX records |
| MX points to old provider | Previous migration incomplete | Replace old MX records |
| Multiple SPF records | DNS misconfiguration | Merge into one SPF record |
| SPF missing provider include | Active sender not authorized | Add correct include mechanism |
| DKIM missing | DKIM not enabled or not copied to DNS | Enable DKIM and publish TXT/CNAME |
| DMARC too strict | Policy applied before SPF/DKIM alignment | Temporarily use p=none while fixing |
| Webmail works but mail client fails | Client settings issue | Fix SMTP/IMAP host, port, SSL, password |
| Receiving fails but sending works | MX or routing issue | Check MX and Email Routing |
| Sending fails to Gmail/Outlook | Authentication or reputation issue | Check SPF/DKIM/DMARC and bounce text |
| cPanel shows deliverability warnings | DNS records missing or incorrect | Apply recommended records at active DNS host |

## Safety Notes

- Do not delete existing DNS records without recording the current state.
- Take screenshots or copy current DNS records before changes.
- Confirm the active DNS provider before editing anything.
- Avoid changing nameservers unless absolutely necessary.
- Avoid setting DMARC to `reject` during initial troubleshooting.
- Do not promise inbox placement. SPF, DKIM, and DMARC improve authentication but do not guarantee delivery to inbox.
- Provider-side blocks, IP reputation, and shared hosting limits may require escalation to the hosting provider.

## Deliverables for a Client

A concise troubleshooting engagement should produce:

1. Summary of the issue
2. DNS authority confirmation
3. MX/SPF/DKIM/DMARC findings
4. cPanel / hosting findings
5. Changes made
6. Remaining risks or provider-side limitations
7. Recommended next steps
8. Evidence for hosting provider support if escalation is needed

## Example Scope Statement

This troubleshooting process covers DNS, cPanel, mailbox, SMTP, and email authentication checks. If the issue is caused by Bluehost-side restrictions, server reputation, rate limits, or shared hosting mail policy, the finding should be documented clearly for escalation to Bluehost support.
