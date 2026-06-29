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
├── templates/
│   ├── agenda.md.j2               ← committee meeting agenda
│   ├── minutes.md.j2              ← committee meeting minutes
│   ├── actions-register.md.j2     ← initial empty actions register
│   ├── agm-agenda.md.j2           ← AGM agenda
│   └── agm-reminder.md.j2         ← AGM notice email
├── governance/
│   ├── committee.md.j2            ← committee register (rendered from config)
│   └── constitution-placeholder.md
├── scripts/
│   ├── generate.py                ← renders templates → meetings/YYYY-MM-DD/
│   └── update-actions.py          ← appends new actions from minutes to register
├── meetings/                      ← gitignored; generated output lives here
│   ├── YYYY-MM-DD/
│   │   ├── agenda.md
│   │   └── minutes.md
│   └── actions-register.md
└── docs/
    └── adr-001-email-routing.md   ← email/SMTP/MailerLite routing decision
```

The `meetings/` directory is gitignored. If you want to version meeting documents, remove that line from `.gitignore`.

## Email / distribution

The default `email.method: manual` means no automated sending is configured. See [ADR: Email Routing](docs/adr-001-email-routing.md) for when and how to upgrade to SMTP or MailerLite.
