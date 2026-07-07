# Runbook: Newsletter Cycle

Cadence: `org.yml newsletter.cadence` (quarterly), two editions per cycle:
one for members, one for external stakeholders. Owner: Chair or a designated
editor.

## Steps

1. On the drafting deadline (automate via the `newsletter-deadline` entry in
   `reminders.example.yml`), generate both drafts:
   ```bash
   python3 scripts/generate.py --template newsletter-member --date YYYY-MM-DD
   python3 scripts/generate.py --template newsletter-external --date YYYY-MM-DD
   ```
2. Draft content into the section placeholders (sections are configured in
   `org.yml newsletter.member_sections` / `external_sections`).
3. Circulate drafts to the committee for review/comment; incorporate edits.
4. Send via your org's email mechanism. The `{{unsubscribe_url}}` token in
   the footer must be substituted **per recipient** at send time.
5. Archive the sent edition with the org's governance documents.

## Rules

- Recipient lists are PII: they live in your encrypted contact store, never
  in this repo or the drafts.
- External and member editions have different audiences AND different
  consent bases — never merge the lists for a send.
- Honour unsubscribes before every send (suppression list check).

## Verification (dry-run)

- `python3 scripts/generate.py --template newsletter-member --date 2099-01-05 --stdout --config org.example.yml`
  renders all configured sections and the literal `{{unsubscribe_url}}` token.
- Before a real send, deliver the rendered edition to a single test address
  and click the substituted unsubscribe link end-to-end.
