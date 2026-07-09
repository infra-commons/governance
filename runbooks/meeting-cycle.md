# Runbook: Committee Meeting Cycle

Cadence: per `org.yml meetings.cadence`. Owner: Secretary (or minute-taker).

## Before the meeting (T-2 days)

1. Generate the agenda, carrying forward open items from the actions register:
   ```bash
   python3 scripts/generate.py --template agenda --date YYYY-MM-DD --previous-date YYYY-MM-DD
   ```
2. Fill in the discussion items and report topics, review open/in-progress
   rows from `meetings/actions-register.md` into the Action Updates section.
3. Distribute the agenda to the committee (PDF export + your org's
   distribution method — see `docs/adr-001-email-routing.md`).

## During the meeting

4. Initialise the minutes document and capture attendance, apologies,
   discussion, resolutions, and the `## New Actions` table:
   ```bash
   python3 scripts/generate.py --template minutes --date YYYY-MM-DD
   ```
5. Confirm quorum (`committee.quorum`) before any resolution.

## After the meeting (within 7 days)

6. Finalise the minutes (from notes or transcript).
7. Append new actions to the register:
   ```bash
   python3 scripts/update-actions.py --minutes meetings/YYYY-MM-DD/minutes.md
   ```
8. Update statuses of existing register rows discussed at the meeting.
9. Distribute draft minutes for comment; they are confirmed at the next
   meeting's "Confirmation of Previous Minutes" item.

## Verification (dry-run)

- `python3 scripts/generate.py --template agenda --date 2099-01-05 --stdout`
  renders without error against your `org.yml`.
- Run `update-actions.py` against a scratch copy of a minutes file with a
  test `## New Actions` row and diff the register before/after.
