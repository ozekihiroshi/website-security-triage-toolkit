# AWS EC2 System Mail Delivery via Google Workspace SMTP Relay

## Summary

This case study documents the recovery of system and application alert email delivery from a legacy AWS EC2 server using Google Workspace SMTP relay.

The server was an old production-related EC2 instance that still needed to send system notifications and application alerts during a transition period. Direct outbound SMTP delivery was not reliable because of AWS mail restrictions and legacy Postfix configuration. The goal was to send local system mail, including `root` notifications and application alerts, through Google Workspace SMTP relay over port 587, while avoiding exposure of the server as an inbound SMTP server.

## Environment

* Server: Legacy AWS EC2 instance
* Mail service: Postfix
* Relay service: Google Workspace SMTP relay
* Relay host: `smtp-relay.gmail.com`
* Relay port: `587`
* TLS: enabled
* Server identity used for SMTP HELO: `smtp-out.example.com`
* System notification recipient: `admin@example.com`

> Note: Real domain names, IP addresses, and mailbox names should be replaced with placeholders when publishing this case study.

## Initial Problem

The legacy EC2 server needed to send system and application alert emails, but mail delivery was unreliable.

Symptoms included:

* Application and system alert emails were not reaching the administrator.
* The server had an old Postfix configuration using a legacy mail hostname.
* Mail was being sent using local Unix users such as `root`.
* Google Workspace SMTP relay rejected some messages depending on the envelope sender and HELO domain.
* System mail to `root` was not initially redirected to the intended administrator mailbox.
* The server was also exposed to external SMTP authentication attempts on inbound SMTP-related ports.

## Goal

The goal was to configure the server so that:

* Local system mail can be generated normally.
* `root` mail is redirected to the administrator.
* Application alert emails can be sent from the legacy server.
* Outbound mail is relayed through Google Workspace SMTP relay.
* The server does not act as a public inbound SMTP server.
* Inbound SMTP ports are closed at the AWS Security Group level.

## Final Architecture

```text
Local system mail / application alert
        |
        v
Postfix on legacy EC2
        |
        | root alias / sender rewrite
        v
Google Workspace SMTP relay
smtp-relay.gmail.com:587
        |
        v
admin@example.com
```

The server only sends outbound mail. It does not need to receive mail from the internet.

## DNS / Hostname Decision

A dedicated hostname was used for the sending server identity:

```text
smtp-out.example.com
```

This is preferable to using a generic `mail.example.com` hostname if that name is already used by another server.

Recommended naming pattern:

```text
smtp-out.example.com
```

or:

```text
ec2-mail-relay.example.com
```

The hostname is used for Postfix identity and SMTP HELO.

## Google Workspace SMTP Relay

Google Workspace SMTP relay was used instead of direct SMTP delivery.

Postfix relay target:

```text
smtp-relay.gmail.com:587
```

Google Workspace SMTP relay settings must allow the public IP address of the EC2 instance.

Important points:

* The EC2 public IP must be registered in Google Workspace SMTP relay settings.
* The sender domain must belong to the Google Workspace domain.
* The server should use a valid domain identity in HELO and envelope sender.
* Port 587 must be reachable outbound from the EC2 instance.

## Postfix Configuration

Key Postfix settings:

```conf
myhostname = smtp-out.example.com
mydomain = example.com
myorigin = $myhostname

mydestination = $myhostname, localhost.$mydomain, localhost

relayhost = [smtp-relay.gmail.com]:587
smtp_use_tls = yes
smtp_tls_security_level = encrypt
smtp_tls_CAfile = /etc/ssl/certs/ca-certificates.crt

smtp_helo_name = smtp-out.example.com

alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases

sender_canonical_maps = hash:/etc/postfix/sender_canonical
```

The important change was:

```conf
myorigin = $myhostname
```

This allows mail addressed to `root` to be handled locally first as:

```text
root@smtp-out.example.com
```

Since `smtp-out.example.com` is included in `mydestination`, Postfix can process the local alias before relaying mail externally.

Avoid adding the main Google Workspace domain to `mydestination`:

```conf
# Do not do this unless the server is actually responsible for receiving the domain's mail
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain
```

Adding the main domain can cause the server to treat the whole mail domain as local, which is not appropriate when Google Workspace handles inbound mail.

## Root Mail Alias

System mail often goes to `root`. To forward those messages to the administrator, configure `/etc/aliases`:

```conf
root: admin@example.com
```

Then rebuild the aliases database:

```bash
newaliases
systemctl reload postfix
```

Expected behavior:

```text
root
→ root@smtp-out.example.com
→ local alias
→ admin@example.com
→ Google Workspace SMTP relay
```

## Sender Rewriting

Local system messages may originate from users such as:

* `root`
* `ubuntu`
* `www-data`
* `apache`

To normalize the envelope sender, configure sender canonical rewriting.

Example `/etc/postfix/sender_canonical`:

```text
root@smtp-out.example.com alert@example.com
ubuntu@smtp-out.example.com alert@example.com
www-data@smtp-out.example.com alert@example.com
apache@smtp-out.example.com alert@example.com

root@example.com alert@example.com
ubuntu@example.com alert@example.com
www-data@example.com alert@example.com
apache@example.com alert@example.com
```

Build the database:

```bash
postmap /etc/postfix/sender_canonical
```

Confirm the database exists:

```bash
ls -l /etc/postfix/sender_canonical /etc/postfix/sender_canonical.db
```

Reload Postfix:

```bash
postfix check
systemctl reload postfix
```

## Testing

### Test root alias

```bash
/usr/sbin/sendmail -v root <<'EOF'
Subject: root alias test

This is a root alias test.
EOF
```

Expected log pattern:

```text
to=<admin@example.com>, orig_to=<root>, relay=smtp-relay.gmail.com, status=sent
```

### Test direct administrator delivery

```bash
/usr/sbin/sendmail -v admin@example.com <<'EOF'
From: alert@example.com
To: admin@example.com
Subject: direct relay test

This is a direct test via Google Workspace SMTP relay.
EOF
```

Expected log pattern:

```text
from=<alert@example.com>
to=<admin@example.com>
relay=smtp-relay.gmail.com
status=sent
```

## Troubleshooting Notes

### Relay denied due to wrong sender domain

Example problem:

```text
550-5.7.0 Mail relay denied
Invalid credentials for relay for one of the domains
```

Cause:

* The envelope sender or HELO domain did not match an allowed Google Workspace domain.
* The message used a legacy domain or local sender such as `root@legacy-domain.example`.

Fix:

* Set `myhostname` and `smtp_helo_name` to a hostname under the Workspace domain.
* Use `sender_canonical_maps` to rewrite local senders to a valid Workspace sender address.
* Confirm the EC2 public IP is allowed in Google Workspace SMTP relay settings.

### Alias not applied

Symptom:

```text
to=<root@example.com>, orig_to=<root>
```

instead of:

```text
to=<admin@example.com>, orig_to=<root>
```

Cause:

* `root` was expanded to `root@example.com` before being treated as a local recipient.
* `myorigin = $mydomain` caused local mail to be interpreted under the main mail domain.

Fix:

```conf
myorigin = $myhostname
mydestination = $myhostname, localhost.$mydomain, localhost
```

Then:

```bash
newaliases
postfix check
systemctl reload postfix
```

### sender_canonical database missing

Symptom:

```text
open database /etc/postfix/sender_canonical.db: No such file or directory
sender_canonical_maps map lookup problem
```

Cause:

* `sender_canonical_maps = hash:/etc/postfix/sender_canonical` was configured, but the `.db` file had not been generated.

Fix:

```bash
postmap /etc/postfix/sender_canonical
systemctl reload postfix
```

### Mail sent but not visible in inbox

If Postfix logs show:

```text
status=sent
250 2.0.0 OK
```

then Postfix successfully handed the message to Google Workspace SMTP relay.

If the message is not visible in the inbox:

* Check spam.
* Search all mail.
* Search by sender.
* Check Google Admin Email Log Search.
* Check Gmail filters or routing rules.

For test messages, short subjects such as `test` and minimal body content may increase the chance of spam classification.

## Security Group Hardening

The EC2 server only needs to send mail outbound to Google Workspace SMTP relay.

It does not need to accept inbound SMTP connections.

Inbound SMTP-related ports should be closed unless explicitly required:

```text
TCP 25   SMTP
TCP 465  SMTPS
TCP 587  Submission
```

Required outbound:

```text
TCP 587  to smtp-relay.gmail.com
```

After closing inbound SMTP ports, monitor the mail log:

```bash
tail -f /var/log/mail.log
```

External SMTP authentication attempts such as the following should stop after the Security Group change:

```text
postfix/smtps/smtpd
postfix/submission/smtpd
SASL LOGIN authentication failed
```

## Final Result

The final working flow:

```text
System alert / cron / root mail
→ local Postfix
→ /etc/aliases root forwarding
→ sender canonical rewrite
→ Google Workspace SMTP relay on port 587
→ administrator mailbox
```

Confirmed behavior:

```text
orig_to=<root>
to=<admin@example.com>
relay=smtp-relay.gmail.com
status=sent
```

The server was also hardened by closing inbound SMTP ports at the AWS Security Group level.

## Lessons Learned

* For system mail on a relay-only server, keep local delivery and outbound relay responsibilities separate.
* Do not make the server responsible for the main mail domain unless it actually receives mail for that domain.
* Use `myorigin = $myhostname` to keep local system mail local before alias expansion.
* Use `/etc/aliases` for local recipient forwarding.
* Use `sender_canonical_maps` for envelope sender normalization.
* Google Workspace SMTP relay requires both IP authorization and valid sender domain alignment.
* `status=sent` in Postfix means the message was accepted by the relay, but final inbox placement still depends on Google/Gmail filtering.
* Close inbound SMTP ports if the server only sends mail.

## Reusable Checklist

```text
1. Confirm EC2 public IP
2. Register EC2 public IP in Google Workspace SMTP relay settings
3. Create or choose sending hostname
4. Configure DNS A record for sending hostname
5. Configure Postfix relayhost to smtp-relay.gmail.com:587
6. Set myhostname, myorigin, mydestination, smtp_helo_name
7. Configure /etc/aliases for root forwarding
8. Run newaliases
9. Configure sender_canonical_maps
10. Run postmap for sender_canonical
11. Run postfix check
12. Reload Postfix
13. Send root alias test
14. Confirm mail.log shows relay=smtp-relay.gmail.com and status=sent
15. Confirm mailbox receives the message
16. Close inbound SMTP ports 25/465/587
17. Monitor logs for remaining SMTP authentication attempts
```