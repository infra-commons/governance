# ADR-001: Email / distribution routing for governance documents

**Status:** Accepted  
**Date:** 2026-06-29

## Context

The governance scaffolding generates meeting agendas, minutes, and AGM notices as Markdown files. These documents need to reach committee members. Three routing options exist:

1. **Manual** — the operator exports/copies the rendered document and sends it through their existing email client.
2. **MailerLite** — use the MailerLite API (an email marketing platform commonly used for newsletters) to send the document to a stored subscriber list.
3. **SMTP** — send directly via an SMTP relay, either self-hosted or a transactional service (SendGrid, Postmark, etc.), using env vars `SMTP_HOST` / `SMTP_USER` / `SMTP_PASS`.

## Decision

**Default: manual. Long-term (when automation is worth the overhead): SMTP via a shared-infra mailer helper. MailerLite is not recommended for governance distribution.**

## Rationale

### Why manual is correct as the default

- Governance committees are small and stable (typically 5–10 named members). There is no list-management problem to solve.
- Meeting frequency is low (monthly at most). The overhead of one manual send per meeting is negligible.
- Manual mode requires zero credentials, zero infrastructure, and zero ongoing maintenance — exactly right for scaffolding that must be low-friction to instantiate.
- The current `email.method: manual` default in `org.yml` reflects this recommendation.

### Why MailerLite is not the right fit

MailerLite is a marketing email platform designed for subscriber lists, campaign analytics, and unsubscribe management. Governance minutes distribution has none of those requirements:
- Recipients are a fixed, consenting committee (no unsubscribe management needed).
- Minutes are formal records, not campaigns — they should not go through a marketing tool.
- MailerLite pricing is per-subscriber and per-send; at committee scale this is wasteful.
- Using the same MailerLite account / API key for governance and marketing complicates credential scope and billing.

### Why SMTP is the right long-term path (but not now)

When the committee wants to automate distribution (e.g. auto-send minutes on merge/approval), SMTP is the correct mechanism:
- A transactional SMTP relay (Postmark, SendGrid free tier, or a self-hosted relay) is purpose-built for exactly this kind of low-volume, high-reliability sending.
- A shared-infrastructure org is the natural home for a reusable SMTP helper workflow or script — this avoids each governance repo carrying its own SMTP credentials.
- No such helper exists today. The work to build it is out of scope for this scaffolding card and should be a separate shared-infra plan.

## Implementation guide (when SMTP is ready)

Set `email.method: smtp` in `org.yml` and configure the following env vars in your CI or local environment:

```
SMTP_HOST=smtp.postmarkapp.com   # or your relay
SMTP_PORT=587
SMTP_USER=<api-token>
SMTP_PASS=<api-token>
SMTP_FROM=governance@yourorg.org
```

Populate `email.distribution_list` in `org.yml` with recipient addresses. A send script reading these env vars and the rendered Markdown output can be added to `scripts/send.py` as a follow-on.

## Consequences

- All governance repos instantiated from this scaffolding default to `email.method: manual` until they opt in.
- The `email.distribution_list` field in `org.yml` is populated now so it is available when an automated sender is wired up — no config change needed at that point.
- A future shared-infra SMTP helper plan should reference this ADR as the upstream decision that deferred sending integration.
