# Post-Recovery Validation Checklist

This checklist is used after website cleanup, restore, migration, DNS correction, SSL correction, or security hardening.

The goal is to confirm that the website is functioning correctly and that obvious symptoms of compromise or misconfiguration are no longer present.

## 1. Basic Availability

- [ ] Website loads successfully.
- [ ] Homepage returns expected content.
- [ ] Key pages load successfully.
- [ ] No unexpected downtime is observed.
- [ ] No hosting suspension page appears.
- [ ] No maintenance page appears unintentionally.
- [ ] Client confirms that the website is reachable from their location.

## 2. HTTP / HTTPS Behavior

- [ ] HTTPS version loads correctly.
- [ ] HTTP redirects to HTTPS.
- [ ] Root domain works as expected.
- [ ] www version works as expected.
- [ ] No redirect loop is present.
- [ ] No unexpected external redirect is present.
- [ ] Final URL is expected.
- [ ] SSL certificate is valid.
- [ ] SSL certificate covers expected domain names.

## 3. Browser and Security Warnings

- [ ] No browser malware warning appears.
- [ ] No SSL warning appears.
- [ ] No mixed content warning appears.
- [ ] No unsafe site warning appears.
- [ ] No antivirus or browser extension warning is reported by the client.
- [ ] If warning remains, document where it appears and what service reports it.
- [ ] If Google warnings remain, confirm whether a review request is needed.

## 4. Website Content

- [ ] Homepage content is correct.
- [ ] Header and footer appear correctly.
- [ ] Navigation works.
- [ ] Important images load.
- [ ] Important CSS and JavaScript files load.
- [ ] No suspicious injected text appears.
- [ ] No casino, pharma, spam, or unrelated keywords are visible.
- [ ] Page titles and meta descriptions appear normal.
- [ ] Important internal links work.

## 5. Forms and User Actions

- [ ] Contact form works.
- [ ] Login page works if applicable.
- [ ] Search function works if applicable.
- [ ] Newsletter or lead form works if applicable.
- [ ] Checkout or payment flow is reviewed if applicable.
- [ ] Client confirms any business-critical forms.
- [ ] Form notifications are delivered correctly if email is involved.

## 6. CMS / WordPress Validation

If the website uses WordPress or another CMS:

- [ ] Admin login works.
- [ ] Unknown admin users have been reviewed.
- [ ] Plugins are reviewed.
- [ ] Themes are reviewed.
- [ ] Unused themes or plugins are removed or disabled where appropriate.
- [ ] CMS core is updated where appropriate.
- [ ] Plugin and theme updates are applied where safe.
- [ ] File editor is disabled if appropriate.
- [ ] Backups are configured or confirmed.
- [ ] Security plugin or WAF settings are reviewed if applicable.
- [ ] XML-RPC exposure is reviewed if relevant.
- [ ] Default or weak admin usernames are reviewed.

## 7. DNS and Email Validation

- [ ] DNS records point to expected services.
- [ ] A / CNAME records are correct.
- [ ] MX records are correct.
- [ ] SPF record is present if email is used.
- [ ] DKIM is configured if selector/provider information is available.
- [ ] DMARC record is present or recommended.
- [ ] Email sending is tested where applicable.
- [ ] Domain verification records remain intact where needed.
- [ ] Old or unnecessary DNS records are documented before removal.

## 8. Search Engine and External Status

- [ ] Google Search Console status is reviewed if access is available.
- [ ] Google Safe Browsing status is reviewed if relevant.
- [ ] Hosting provider warning status is reviewed.
- [ ] CDN/WAF status is reviewed if applicable.
- [ ] Client is advised that external warning removal may take time.
- [ ] Sitemap and robots.txt are reviewed if search visibility was affected.

## 9. Access and Hardening

- [ ] Admin passwords changed where appropriate.
- [ ] Hosting password changed where appropriate.
- [ ] DNS/registrar password changed where appropriate.
- [ ] Email provider admin password reviewed where appropriate.
- [ ] Two-factor authentication recommended.
- [ ] Former developer or agency accounts reviewed.
- [ ] Unknown accounts removed or disabled.
- [ ] Backup access confirmed.
- [ ] Principle of least privilege recommended.
- [ ] Temporary access removed after completion where appropriate.

## 10. Documentation

- [ ] Summary of issue documented.
- [ ] Findings documented.
- [ ] Actions taken documented.
- [ ] Remaining risks documented.
- [ ] Client confirmations documented.
- [ ] Recommended next steps documented.
- [ ] Any limitations of the review documented.
- [ ] Any items requiring external provider support documented.

## 11. Client Confirmation

Ask the client to confirm:

- [ ] Website appears normal from their location.
- [ ] Key pages work.
- [ ] Forms work.
- [ ] Business-critical functions work.
- [ ] No known warning remains.
- [ ] Any remaining issues are documented for follow-up.
- [ ] The client understands any remaining risks or recommended next steps.
