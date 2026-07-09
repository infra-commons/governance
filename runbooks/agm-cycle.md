# Runbook: AGM Cycle

Cadence: annual, in `org.yml agm.month`. Owner: Chair + Secretary + Treasurer
per milestone. Notice period: `agm.notice_days` (check your constitution).

## 1. Generate the timeline (as soon as a date is proposed — T-90 or earlier)

```bash
python3 scripts/agm-timeline.py --agm-date YYYY-MM-DD --ics --emit-reminders
```

- `timeline.md` — dated checklist with owners; track completion in it.
- `timeline.ics` — import into the committee calendar.
- `reminders.agm.yml` — append to `reminders.yml` if you run an automated
  reminder scheduler (see `docs/reminders.md`).

Regenerate all three if the AGM date changes.

## 2. Work the milestones

The default milestone set (edit in `org.yml agm.milestones`):

| T± | Milestone | Owner |
|---|---|---|
| T-90 | Confirm date, venue/platform, returning officer | Chair |
| T-60 | Call for officer reports, open nominations | Secretary |
| T-45 | Draft annual financial statements | Treasurer |
| T-notice | **Formal notice + agenda to all members** (constitutional deadline) | Secretary |
| T-7 | Circulate papers: reports, financials, nominations | Secretary |
| T-0 | Hold the AGM | Chair |
| T+7 | Draft and circulate AGM minutes | Secretary |
| T+30 | File annual return + financials with the registrar | Treasurer |

Generate the formal notice and AGM agenda:

```bash
python3 scripts/generate.py --template agm-reminder --date <notice-date>
python3 scripts/generate.py --template agm-agenda --date <agm-date>
```

## Verification (dry-run)

- `python3 scripts/agm-timeline.py --agm-date 2099-11-02 --stdout --config org.example.yml`
  renders the full milestone table with correct arithmetic (formal-notice row
  lands exactly `notice_days` before the AGM).
- Import the `.ics` into a personal calendar before sharing it with the
  committee.
