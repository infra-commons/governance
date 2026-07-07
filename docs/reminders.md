# Reminder Schedule Format

A declarative schedule (`reminders.yml`, see `reminders.example.yml`) that any
scheduler can consume to email recurring governance reminders — meeting prep,
wallet health checks, newsletter deadlines, AGM milestones.

## Design

The consumer runs **one cron, once per day**, and evaluates every rule in the
org's timezone (`org.yml meetings.timezone`) in code. Encoding each reminder
as its own cron expression in UTC breaks twice a year at daylight-saving
transitions; a single daily tick plus local-date evaluation does not.

A reminder fires on a day when: `rule` resolves to that local date after
applying `offset_days`. Consumers should treat the schedule as idempotent per
(id, date) — if the same day is evaluated twice, send once.

## Schema

```yaml
reminders:
  - id: meeting-prep            # unique slug
    rule: "monthly:first-tuesday"
    months: [1, 4, 7, 10]       # quarterly rules only
    offset_days: -2             # optional, default 0; negative = earlier
    subject: "Committee meeting in 2 days"
    body_template: "meeting-prep"   # slug the consumer maps to a body
    audience: "committee"       # committee | key-holders
```

### Rule grammar

| Rule | Meaning |
|---|---|
| `monthly:<ordinal>-<weekday>` | e.g. `monthly:first-tuesday` — every month |
| `quarterly:<ordinal>-<weekday>` + `months:` | same, but only in the listed months |
| `annual:MM-DD` | fixed date each year |
| `date:YYYY-MM-DD` | one-off (used for AGM milestones) |

Ordinals: `first`–`fourth`, `last`. Weekdays: lowercase English names.

### Audiences

Recipient lists are **never stored in this file** (they are PII). The consumer
resolves `committee` and `key-holders` to real addresses from its own secret
or encrypted store.

## Generating AGM entries

```bash
python3 scripts/agm-timeline.py --agm-date 2026-11-03 --emit-reminders
```

emits `date:` entries for each AGM milestone; append them to `reminders.yml`
and remove them after the AGM (or leave them — past `date:` rules never fire
again).

## Validation

```bash
python3 scripts/validate-reminders.py --file reminders.yml
```

Checks: required fields, unique ids, rule grammar, `months` presence/range for
quarterly rules, integer `offset_days`, known audience values.
