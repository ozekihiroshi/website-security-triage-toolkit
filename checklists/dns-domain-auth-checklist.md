# DNS and Domain Authentication Checklist

This checklist is for reviewing DNS, domain configuration, and basic email authentication records.

It is useful when a client reports domain authentication problems, email delivery issues, website routing problems, SSL errors, or possible domain misconfiguration.

## 1. Domain Ownership and Registrar

- [ ] Confirm the domain name.
- [ ] Confirm the domain registrar.
- [ ] Confirm the client has access to the registrar account.
- [ ] Confirm domain expiration date.
- [ ] Confirm registrar lock status if relevant.
- [ ] Confirm whether recent registrar changes were made.
- [ ] Confirm whether domain ownership verification is required.
- [ ] Confirm whether the domain is close to expiration.

## 2. Nameservers

- [ ] Identify current nameservers.
- [ ] Confirm nameservers match the expected DNS provider.
- [ ] Check whether nameservers were recently changed.
- [ ] Confirm whether DNS is managed at the registrar, hosting provider, CDN, or third-party DNS provider.
- [ ] Confirm whether multiple DNS dashboards may exist.
- [ ] Confirm whether the client knows which DNS dashboard is authoritative.

## 3. Website DNS Records

- [ ] Check A record for root domain.
- [ ] Check A record for `www` if applicable.
- [ ] Check AAAA records if IPv6 is used.
- [ ] Check CNAME records.
- [ ] Confirm root and www versions point to expected infrastructure.
- [ ] Confirm there are no unexpected web-related records.
- [ ] Confirm whether CDN or proxy service is used.
- [ ] Confirm whether old hosting records remain.
- [ ] Confirm whether DNS records match the current hosting provider instructions.

## 4. Mail DNS Records

- [ ] Check MX records.
- [ ] Confirm MX records match the expected email provider.
- [ ] Check whether old MX records remain.
- [ ] Confirm mail subdomains if used.
- [ ] Confirm whether third-party sending platforms are used.
- [ ] Confirm whether email service recently changed.

## 5. SPF

- [ ] Check whether an SPF record exists.
- [ ] Confirm there is only one SPF record.
- [ ] Confirm SPF includes the expected email provider.
- [ ] Confirm SPF includes approved third-party senders.
- [ ] Check for overly broad mechanisms such as `+all`.
- [ ] Check whether SPF ends with an appropriate policy such as `~all` or `-all`.
- [ ] Check whether SPF lookup count may be too high.
- [ ] Document any uncertainty about authorized senders.

## 6. DKIM

- [ ] Confirm the email provider.
- [ ] Confirm DKIM selector from the provider.
- [ ] Check whether DKIM TXT or CNAME record exists.
- [ ] Confirm DKIM record matches provider instructions.
- [ ] Confirm whether multiple DKIM selectors are in use.
- [ ] Document if DKIM cannot be checked because selector is unknown.
- [ ] Ask client or email provider for DKIM setup instructions if needed.
- [ ] Avoid guessing DKIM selector values without provider confirmation.

## 7. DMARC

- [ ] Check whether `_dmarc` record exists.
- [ ] Confirm DMARC policy.
- [ ] Record whether policy is `none`, `quarantine`, or `reject`.
- [ ] Check whether aggregate reporting address is configured.
- [ ] Check whether alignment requirements are specified.
- [ ] Confirm whether the current DMARC policy matches the client’s readiness.
- [ ] Avoid moving directly to strict enforcement without confirming SPF/DKIM alignment.
- [ ] Recommend monitoring mode first if the client has not validated all legitimate senders.

## 8. SSL and Domain Validation

- [ ] Confirm whether SSL certificate is valid.
- [ ] Confirm whether certificate covers root domain.
- [ ] Confirm whether certificate covers `www`.
- [ ] Confirm whether certificate is issued by expected provider.
- [ ] Confirm whether DNS validation records are required.
- [ ] Confirm whether certificate renewal is failing.
- [ ] Confirm whether CDN SSL settings are involved.
- [ ] Confirm whether HTTP to HTTPS redirect is configured correctly.

## 9. Third-Party Services

- [ ] Identify CDN or WAF provider.
- [ ] Identify email marketing provider.
- [ ] Identify transactional email provider.
- [ ] Identify website hosting provider.
- [ ] Identify domain verification records for external services.
- [ ] Confirm whether any old verification records should be removed.
- [ ] Avoid deleting records without confirming active services.
- [ ] Document all third-party services that rely on DNS records.

## 10. Common Findings

Record any of the following:

- [ ] Missing SPF record.
- [ ] Multiple SPF records.
- [ ] Missing DMARC record.
- [ ] DMARC policy set to monitoring only.
- [ ] Unknown DKIM selector.
- [ ] Missing or incorrect DKIM record.
- [ ] MX records pointing to old provider.
- [ ] DNS records pointing to old hosting.
- [ ] Nameservers not matching expected provider.
- [ ] SSL certificate mismatch.
- [ ] Expired domain or certificate.
- [ ] Unclear DNS ownership.
- [ ] Unknown third-party verification records.

## 11. Recommended Next Actions

- [ ] Ask client to confirm current email provider.
- [ ] Ask client to confirm authorized email senders.
- [ ] Ask client to confirm DNS management location.
- [ ] Correct SPF record after confirming senders.
- [ ] Add or correct DKIM record using provider instructions.
- [ ] Add or adjust DMARC record.
- [ ] Remove obsolete DNS records only after confirmation.
- [ ] Recheck DNS propagation after changes.
- [ ] Document all changes made.
- [ ] Provide a written summary of findings and recommended next steps.
