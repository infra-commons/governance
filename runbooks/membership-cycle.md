# Runbook: Membership Cycle

Cadence: continuous (signups) + annual per member (renewals). Owner:
Treasurer (payments, receipts) + Secretary (register).

## Principles

- The member register (names, emails, membership status) is PII: it lives in
  an encrypted store (e.g. a field-encrypted database), never in a git repo —
  public or private — and never at rest in shared drives.
- Every payment gets a receipt; every membership has an explicit expiry.

## Signup

1. Applicant submits name + email + payment via the org's signup mechanism.
2. On payment confirmation: record the member (encrypted store), membership
   status `active`, expiry = start + 12 months.
3. Send a receipt (amount, date, method, org details) and a welcome note.

## Renewal

1. At expiry −30 and −7 days, and on the day: send a renewal reminder with a
   payment link (automatable via the reminder scheduler pattern in
   `docs/reminders.md`).
2. On payment: extend expiry by 12 months from the previous expiry (not the
   payment date), send a receipt.
3. No payment by expiry + grace period: mark `lapsed`; lapsed members leave
   the member-newsletter audience but may be retained (with consent) on the
   external list.

## Reporting

- Treasurer reports member count and subscription revenue at each committee
  meeting (numbers only — no member PII in minutes).
- The AGM financial statements reconcile subscription revenue against the
  payments log.

## Verification (dry-run)

- Walk one fake member through signup → receipt → renewal reminder →
  renewal → lapse using a test email address, with real sends rerouted to a
  test recipient.
- Verify at-rest encryption by inspecting the raw store: PII columns must be
  ciphertext.
