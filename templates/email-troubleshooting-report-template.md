# Email Troubleshooting Report

## 1. Client / Domain

- Client:
- Domain:
- Date:
- Technician:
- Hosting provider:
- DNS provider:
- Mail provider:
- Affected email address(es):

## 2. Reported Problem

Client reported:

- [ ] Cannot send email
- [ ] Cannot receive email
- [ ] Emails go to spam
- [ ] Contact form emails not delivered
- [ ] Mail client issue
- [ ] Webmail issue
- [ ] Other:

Details:

```text
Describe the symptoms here.
```

## 3. Recent Changes

- [ ] Hosting migration
- [ ] DNS / nameserver change
- [ ] Mail provider change
- [ ] Website migration
- [ ] SSL change
- [ ] Password change
- [ ] No known recent changes

Notes:

```text
Add details here.
```

## 4. DNS Authority Check

Command:

```bash
dig NS example.com
```

Findings:

```text
Active nameservers:
-
-
```

Conclusion:

```text
DNS is managed at:
```

## 5. MX Record Check

Command:

```bash
dig MX example.com
```

Current MX records:

```text
Paste MX results here.
```

Expected MX records:

```text
Paste expected provider MX records here.
```

Assessment:

- [ ] Correct
- [ ] Incorrect
- [ ] Missing
- [ ] Mixed old/new providers
- [ ] Needs provider confirmation

Notes:

```text
Add findings here.
```

## 6. SPF Record Check

Command:

```bash
dig TXT example.com
```

Current SPF:

```text
Paste SPF result here.
```

Assessment:

- [ ] Present
- [ ] Missing
- [ ] Multiple SPF records found
- [ ] Missing active mail provider
- [ ] Syntax issue suspected
- [ ] Too many DNS lookups suspected

Recommended SPF:

```text
Add recommendation here.
```

## 7. DKIM Check

Selector(s) checked:

- default
- selector1
- selector2
- other:

Command examples:

```bash
dig TXT default._domainkey.example.com
dig TXT selector1._domainkey.example.com
```

Findings:

```text
Paste DKIM findings here.
```

Assessment:

- [ ] DKIM present
- [ ] DKIM missing
- [ ] Selector unknown
- [ ] cPanel recommended record not published
- [ ] External DNS needs update

## 8. DMARC Check

Command:

```bash
dig TXT _dmarc.example.com
```

Current DMARC:

```text
Paste DMARC result here.
```

Assessment:

- [ ] Present
- [ ] Missing
- [ ] Invalid syntax suspected
- [ ] Policy too strict for current state
- [ ] Reporting address issue

Recommended DMARC:

```text
Add recommendation here.
```

## 9. cPanel / Hosting Checks

Reviewed:

- [ ] Email Deliverability
- [ ] Email Accounts
- [ ] Email Routing
- [ ] Track Delivery
- [ ] Forwarders
- [ ] Default Address
- [ ] Spam Filters
- [ ] Mailbox quota
- [ ] Disk usage
- [ ] Webmail access
- [ ] SMTP/IMAP settings

Findings:

```text
Add cPanel findings here.
```

Email Routing:

- [ ] Local Mail Exchanger
- [ ] Remote Mail Exchanger
- [ ] Automatically Detect Configuration
- [ ] Not checked / not available

Assessment:

```text
Add assessment here.
```

## 10. Sending Test

Test method:

- [ ] Webmail
- [ ] SMTP client
- [ ] WordPress SMTP plugin
- [ ] External test recipient
- [ ] Other:

Result:

```text
Add result here.
```

Errors / bounce messages:

```text
Paste errors here.
```

## 11. Receiving Test

Test method:

- [ ] External sender to domain mailbox
- [ ] Same-domain sender
- [ ] Webmail
- [ ] Mail client
- [ ] Other:

Result:

```text
Add result here.
```

Errors / bounce messages:

```text
Paste errors here.
```

## 12. Changes Made

DNS changes:

```text
List exact records changed.
```

cPanel changes:

```text
List exact cPanel changes.
```

Mailbox / SMTP changes:

```text
List exact mailbox or SMTP changes.
```

Other changes:

```text
List other changes.
```

## 13. Final Status

- [ ] Resolved
- [ ] Partially resolved
- [ ] Pending DNS propagation
- [ ] Requires hosting provider support
- [ ] Requires mail provider support
- [ ] Requires client confirmation

Summary:

```text
Write a concise final status here.
```

## 14. Remaining Risks / Limitations

```text
Examples:
- DNS propagation may take time.
- Inbox placement cannot be guaranteed.
- Shared hosting mail reputation may require provider support.
- Further testing is needed after DNS propagation.
```

## 15. Recommended Next Steps

1.
2.
3.

## 16. Support Escalation Notes

If escalation to the hosting provider is required, send the following:

```text
Domain:
Affected email:
Problem:
Tests performed:
DNS findings:
Bounce message:
Time of failed test:
Requested provider action:
```
