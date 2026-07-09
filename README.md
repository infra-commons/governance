# Governance Scaffolding

Reusable, parameterised governance repository for small committees and organisations.
Covers the full meeting cadence: agenda generation, minute capture, action-item tracking, and AGM administration.

All org-specific values live in a single config file (`org.yml`). The same templates and scripts serve any org without editing template bodies. This repo ships only `org.example.yml` (placeholders); your real `org.yml` is **gitignored** so committee names, meeting links, and recipient addresses are never committed.

## Instantiating for a new org

1. **Clone or fork** this repository.
2. **Copy the example config:** `cp org.example.yml org.yml`.
3. **Edit `org.yml`** — the only file that should contain org-specific values (it is gitignored; keep your real values here, not in `org.example.yml`):

   | Field | Description |
   |---|---|
   | `org.name` | Full legal name of the organisation |
   | `org.short_name` | Abbreviation used in headings and filenames |
   | `committee.members` | List of `{name, role}` objects; `role` values drive the AGM election section |
   | `committee.quorum` | Minimum attendees for a valid meeting |
   | `committee.minutes_prepared_by` | Name of the secretary / minute-taker |
   | `meetings.cadence` | Human-readable description (e.g. "first Tuesday of the month") |
   | `meetings.time_display` | Display time string (e.g. "8:00pm") |
   | `meetings.timezone` / `timezone_display` | IANA timezone ID and short label |
   | `meetings.platform` / `link` | Meeting platform and join URL |
   | `meetings.default_sections` | Agenda sections with `name`, `duration_min`, `presenter` |
   | `agm.month` | Month number (1–12) when the AGM is typically held |
   | `agm.month_name` | Display name of that month |
   | `agm.notice_days` | Minimum notice period required by your constitution |
   | `agm.milestones` | AGM prep milestones for `scripts/agm-timeline.py` (`id`, `offset_days`, `title`, `owner_role`) |
   | `wallet` | Multisig treasury config: `scheme`, `check_cadence`, `holders` (roles, not names) — omit if no crypto treasury |
   | `newsletter` | Newsletter cadence and section lists for the member/external editions |
   | `email.method` | `manual` \| `mailerlite` \| `smtp` — see [ADR: Email Routing](docs/adr-001-email-routing.md) |
   | `email.distribution_list` | List of recipient email addresses for meeting distribution |

4. **Install dependencies** (Python 3.9+):

   ```bash
   pip install pyyaml jinja2
   ```

5. Add your constitution to `governance/constitution-placeholder.md` and update `governance/committee.md.j2` if you need a different committee register layout.

## Running the meeting cadence

### 1 — Generate a meeting agenda

```bash
python3 scripts/generate.py --template agenda --date 2026-07-07
# Written: meetings/2026-07-07/agenda.md

# Include the previous meeting date for the minutes-confirmation line:
python3 scripts/generate.py --template agenda --date 2026-07-07 --previous-date 2026-06-03
```

Distribute `meetings/YYYY-MM-DD/agenda.md` to committee members before the meeting.

### 2 — Initialise the minutes document

```bash
python3 scripts/generate.py --template minutes --date 2026-07-07
# Written: meetings/2026-07-07/minutes.md
```

Open `meetings/2026-07-07/minutes.md` during the meeting and fill in attendance, discussion notes, resolutions, and the `## New Actions` table.

### 3 — Update the actions register after the meeting

Once the minutes are complete, append new action items to the running register:

```bash
python3 scripts/update-actions.py --minutes meetings/2026-07-07/minutes.md
# Added 3 action(s) to meetings/actions-register.md
```

The script reads the `## New Actions` table in the minutes file and appends each row with an auto-incrementing number, today's date, and status `New`. Review and update statuses in `meetings/actions-register.md` each meeting.

### 4 — Distribute the minutes

See [ADR: Email Routing](docs/adr-001-email-routing.md) for the recommended approach.

For **manual** distribution (the default): export `meetings/YYYY-MM-DD/minutes.md` to PDF (or copy the markdown) and send to the committee distribution list.

## AGM administration

### Generate an AGM reminder notice

Send this to the distribution list at least `agm.notice_days` days before the AGM:

```bash
python3 scripts/generate.py --template agm-reminder --date 2026-10-21
# Written: meetings/2026-10-21/agm-reminder.md
```

### Generate the AGM agenda

```bash
python3 scripts/generate.py --template agm-agenda --date 2026-11-04
# Written: meetings/2026-11-04/agm-agenda.md
```

The AGM agenda election section lists only committee roles other than `Member` (Chair, Treasurer, Secretary, etc.) because general member positions are typically open to nomination at the meeting.

### Generate the AGM prep timeline

As soon as an AGM date is proposed, generate the full preparation timeline
from `agm.milestones` — a dated checklist, an importable calendar, and
(optionally) reminder-schedule entries:

```bash
python3 scripts/agm-timeline.py --agm-date 2026-11-03 --ics --emit-reminders
# Written: meetings/agm-2026/timeline.md
# Written: meetings/agm-2026/timeline.ics
# Written: meetings/agm-2026/reminders.agm.yml
```

Regenerate if the date changes. See `runbooks/agm-cycle.md`.

## Wallet health checks

For orgs holding a crypto treasury in an N-of-M multisig (configured under
`wallet:` in `org.yml`), generate the periodic health-check record:

```bash
python3 scripts/generate.py --template wallet-check --date 2026-07-06
```

Process and escalation: `runbooks/wallet-cycle.md` and
`docs/wallet-key-hygiene.md`. Health-check records capture pass/fail only —
never key material.

## Newsletters

Two quarterly editions with config-driven sections (`newsletter.*` in
`org.yml`): one for members, one for external stakeholders.

```bash
python3 scripts/generate.py --template newsletter-member --date 2026-08-03
python3 scripts/generate.py --template newsletter-external --date 2026-08-03
```

The footer carries a literal `{{unsubscribe_url}}` token for per-recipient
substitution at send time. Process: `runbooks/newsletter-cycle.md`.

## Automated reminders

`reminders.example.yml` defines a declarative schedule (meeting prep, wallet
checks, newsletter deadlines, AGM milestones) that a daily scheduler can
consume — schema and design notes in `docs/reminders.md`. Validate with:

```bash
python3 scripts/validate-reminders.py --file reminders.example.yml
```

## Runbooks

Step-by-step operating procedures, each ending with a dry-run verification:

| Runbook | Covers |
|---|---|
| `runbooks/meeting-cycle.md` | Agenda → meeting → minutes → actions register |
| `runbooks/agm-cycle.md` | Timeline, notice, papers, filing |
| `runbooks/wallet-cycle.md` | Quarterly multisig health checks, escalation |
| `runbooks/newsletter-cycle.md` | Drafting, review, send, suppression rules |
| `runbooks/membership-cycle.md` | Signup, renewal, receipts, lapse, reporting |

## Governance admin files

| File | Purpose |
|---|---|
| `governance/committee.md.j2` | Renders the current committee register from `org.yml` |
| `governance/constitution-placeholder.md` | Replace with the org's actual constitution text |
| `org.example.yml` | Committed template; copy to `org.yml` and edit |
| `org.yml` | Single source of all org-specific values (gitignored) |

To render the current committee register:

```bash
python3 scripts/generate.py --template ../governance/committee --date $(date +%F)
```

(Or open `governance/committee.md.j2` directly — the Jinja2 syntax is readable as-is for human review.)

## Repository structure

```
├── org.example.yml                ← committed template (placeholders)
├── org.yml                        ← your org config (gitignored; cp from example)
├── reminders.example.yml          ← declarative reminder schedule (see docs/reminders.md)
├── templates/
│   ├── agenda.md.j2               ← committee meeting agenda
│   ├── minutes.md.j2              ← committee meeting minutes
│   ├── actions-register.md.j2     ← initial empty actions register
│   ├── agm-agenda.md.j2           ← AGM agenda
│   ├── agm-reminder.md.j2         ← AGM notice email
│   ├── wallet-check.md.j2         ← multisig wallet health-check record
│   ├── newsletter-member.md.j2    ← member newsletter skeleton
│   └── newsletter-external.md.j2  ← external stakeholder newsletter skeleton
├── governance/
│   ├── committee.md.j2            ← committee register (rendered from config)
│   └── constitution-placeholder.md
├── runbooks/                      ← operating procedures per governance cycle
│   ├── meeting-cycle.md
│   ├── agm-cycle.md
│   ├── wallet-cycle.md
│   ├── newsletter-cycle.md
│   └── membership-cycle.md
├── scripts/
│   ├── generate.py                ← renders templates → meetings/YYYY-MM-DD/
│   ├── update-actions.py          ← appends new actions from minutes to register
│   ├── agm-timeline.py            ← AGM prep timeline: md + .ics + reminder entries
│   └── validate-reminders.py      ← lints a reminders.yml schedule
├── meetings/                      ← gitignored; generated output lives here
│   ├── YYYY-MM-DD/
│   │   ├── agenda.md
│   │   └── minutes.md
│   ├── agm-YYYY/
│   │   └── timeline.md / .ics
│   └── actions-register.md
└── docs/
    ├── adr-001-email-routing.md   ← email/SMTP/MailerLite routing decision
    ├── reminders.md               ← reminder schedule schema + design
    └── wallet-key-hygiene.md      ← N-of-M custody policy
```

The `meetings/` directory is gitignored. If you want to version meeting documents, remove that line from `.gitignore`.

## Email / distribution

The default `email.method: manual` means no automated sending is configured. See [ADR: Email Routing](docs/adr-001-email-routing.md) for when and how to upgrade to SMTP or MailerLite.
