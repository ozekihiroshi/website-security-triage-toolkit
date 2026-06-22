# Domain, Website, and Email Connection Findings Report

**Client / organization:**  
**Domain:**  
**Date:**  
**Prepared by:**  

## 1. Request and scope

Describe the reported issue and the agreed scope.

- Website issue:
- Domain / DNS issue:
- Email issue:
- Requested outcome:
- Out-of-scope items:

## 2. Environment identified

| Area | Current provider / status | Notes |
|---|---|---|
| Domain registrar |  |  |
| DNS provider |  |  |
| Website provider |  |  |
| Email provider |  |  |
| Canonical website address |  |  |

## 3. Findings before changes

### Website routing

- Apex domain (`example.com`):
- `www` subdomain:
- HTTP / HTTPS behavior:
- TLS certificate:
- Redirect behavior:

### Email routing and authentication

- MX:
- SPF:
- DKIM:
- DMARC:
- Sending test:
- Receiving test:
- Deliverability observations:

## 4. Changes made

| Date/time | Change | Reason | Result |
|---|---|---|---|
|  |  |  |  |

## 5. Validation performed

- [ ] DNS records rechecked after changes
- [ ] Apex domain tested over HTTPS
- [ ] `www` tested over HTTPS
- [ ] Redirect behavior verified
- [ ] TLS certificate verified
- [ ] Outbound email test completed
- [ ] Inbound email test completed
- [ ] Spam / junk placement checked
- [ ] Final DNS configuration recorded

## 6. Current status

**Website:**  
**Domain / DNS:**  
**Business email:**  
**Overall status:**  

## 7. Remaining actions or risks

- 
- 
- 

## 8. Handover notes

- DNS changes should be recorded before future edits.
- Website-related DNS changes should not remove existing MX records unless the email provider is intentionally changing.
- Retain a copy of the current DNS zone and this report.
- Contact the relevant provider if account-level access, billing, or provider-side verification remains unresolved.

## Appendix: diagnostic output

Attach or paste the output from:

```bash
python3 scripts/check_domain_stack.py example.com --json domain-stack-report.json
```
