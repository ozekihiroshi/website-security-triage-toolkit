# Initial Website Security Triage Checklist

This checklist is for the first-response review of a website, DNS, domain, SSL, or CMS security issue.

It is intended to help identify the likely problem area before making changes.

## 1. Scope Confirmation

- [ ] Confirm the affected domain.
- [ ] Confirm the reported symptoms.
- [ ] Confirm when the issue started.
- [ ] Confirm whether the issue is website, DNS, email, SSL, hosting, or CMS related.
- [ ] Confirm whether the client has access to hosting, domain registrar, DNS, and CMS.
- [ ] Confirm whether the site is currently live.
- [ ] Confirm whether users are seeing warnings, redirects, or errors.
- [ ] Confirm whether the client has a recent clean backup.
- [ ] Confirm whether assessment-only work is required before remediation.

## 2. Website Availability

- [ ] Check whether the website loads.
- [ ] Check HTTP status code.
- [ ] Check final destination URL.
- [ ] Check whether the website redirects unexpectedly.
- [ ] Check both HTTP and HTTPS versions.
- [ ] Check both www and non-www versions.
- [ ] Check whether the issue occurs across multiple browsers.
- [ ] Check whether the issue occurs on both desktop and mobile.
- [ ] Check whether the issue appears location-specific.

Example checks:

```bash
curl -I https://example.com
curl -I http://example.com
curl -I https://www.example.com
```

## 3. SSL and HTTPS

- [ ] Confirm HTTPS is enabled.
- [ ] Confirm HTTP redirects to HTTPS.
- [ ] Check certificate validity.
- [ ] Check certificate domain names.
- [ ] Check certificate expiration date.
- [ ] Check whether both www and non-www are covered.
- [ ] Check for mixed content if pages load incorrectly.
- [ ] Check whether SSL issue is browser-specific or global.

## 4. Redirect Behavior

- [ ] Check redirect chain.
- [ ] Confirm there are no unexpected external redirects.
- [ ] Check whether redirects differ by device, browser, user-agent, or referrer.
- [ ] Check whether search engine visitors are redirected differently.
- [ ] Check `.htaccess` if Apache is used.
- [ ] Check web server config if Nginx is used.
- [ ] Check CMS redirect plugins or settings.
- [ ] Check CDN or proxy redirect rules if applicable.

## 5. DNS and Domain

- [ ] Check nameservers.
- [ ] Check A records.
- [ ] Check AAAA records if used.
- [ ] Check CNAME records.
- [ ] Check MX records.
- [ ] Check TXT records.
- [ ] Confirm DNS points to the expected hosting provider.
- [ ] Confirm there are no unexpected DNS records.
- [ ] Confirm recent DNS changes if possible.
- [ ] Confirm domain registrar access.
- [ ] Confirm domain expiration status.
- [ ] Confirm whether DNS is managed directly or through a third-party provider.

## 6. Email Authentication

- [ ] Check SPF record.
- [ ] Check DMARC record.
- [ ] Check DKIM record if selector is known.
- [ ] Confirm email provider.
- [ ] Confirm third-party senders.
- [ ] Confirm whether the issue is website security or email deliverability.
- [ ] Confirm whether emails are going to spam.
- [ ] Confirm whether domain verification is failing.

## 7. CMS / WordPress Indicators

If the website uses WordPress or another CMS:

- [ ] Confirm CMS type.
- [ ] Confirm CMS version if accessible.
- [ ] Check admin users.
- [ ] Check recently modified plugins or themes.
- [ ] Check unknown plugins or themes.
- [ ] Check suspicious files in upload directories.
- [ ] Check suspicious PHP files in unexpected locations.
- [ ] Check `.htaccess` modifications.
- [ ] Check `wp-config.php` for unexpected changes.
- [ ] Check whether XML-RPC exposure is relevant.
- [ ] Check whether backups exist before making changes.
- [ ] Check whether plugins/themes/core can be safely updated.
- [ ] Check whether there are abandoned or unsupported plugins.

## 8. Hosting / Server Indicators

If server access is available:

- [ ] Check recent login activity.
- [ ] Check recently modified files.
- [ ] Check web server logs.
- [ ] Check suspicious cron jobs.
- [ ] Check file permissions.
- [ ] Check disk usage.
- [ ] Check running processes if applicable.
- [ ] Check whether hosting provider has quarantined files.
- [ ] Check whether malware scan results are available.
- [ ] Check whether backups are available before making changes.

## 9. Immediate Risk Notes

Record any urgent risks:

- [ ] Unknown admin users.
- [ ] Unexpected external redirects.
- [ ] Browser security warnings.
- [ ] Malicious file indicators.
- [ ] DNS pointing to unknown infrastructure.
- [ ] No available backup.
- [ ] No access to domain or hosting.
- [ ] Email authentication failure.
- [ ] Hosting provider warning.
- [ ] Search engine security warning.

## 10. Recommended Next Actions

Choose one or more:

- [ ] Proceed with website cleanup.
- [ ] Proceed with DNS correction.
- [ ] Proceed with SPF / DKIM / DMARC correction.
- [ ] Restore from known clean backup.
- [ ] Request missing access from client.
- [ ] Escalate to hosting provider.
- [ ] Escalate to domain registrar.
- [ ] Escalate to specialized incident response provider.
- [ ] Prepare written findings report.
- [ ] Perform post-recovery validation.