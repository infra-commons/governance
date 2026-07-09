#!/usr/bin/env python3
"""Generate an AGM preparation timeline from org.yml milestones.

Given the AGM date, resolves each milestone in agm.milestones to a calendar
date and emits:
  - a dated markdown checklist (default: meetings/agm-YYYY/timeline.md)
  - an iCalendar file with one all-day event per milestone (--ics)
  - a reminders YAML fragment consumable by the reminders schedule (--emit-reminders)

Usage:
    python3 scripts/agm-timeline.py --agm-date 2026-11-03
    python3 scripts/agm-timeline.py --agm-date 2026-11-03 --stdout
    python3 scripts/agm-timeline.py --agm-date 2026-11-03 --ics
    python3 scripts/agm-timeline.py --agm-date 2026-11-03 --emit-reminders

Options:
    --config PATH       Path to org config file (default: org.yml)
    --agm-date DATE     Confirmed (or provisional) AGM date, YYYY-MM-DD
    --output PATH       Markdown output path (default: meetings/agm-YYYY/timeline.md)
    --ics               Also write an .ics calendar (default: alongside the markdown)
    --ics-output PATH   Override the .ics output path
    --emit-reminders    Also write a reminders YAML fragment (alongside the markdown)
    --stdout            Print the markdown to stdout instead of writing files
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml


def load_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return yaml.safe_load(f)


def resolve_milestones(cfg: dict, agm_date: datetime) -> list:
    agm = cfg.get("agm", {})
    milestones = agm.get("milestones")
    if not milestones:
        sys.exit("Error: agm.milestones not found in config (see org.example.yml)")
    notice_days = agm.get("notice_days", 14)

    resolved = []
    for m in milestones:
        offset = m.get("offset_days")
        if offset == "notice":
            offset = -notice_days
        if not isinstance(offset, int):
            sys.exit(
                f"Error: milestone {m.get('id')!r} offset_days must be an integer "
                f'or "notice", got {m.get("offset_days")!r}'
            )
        resolved.append(
            {
                "id": m["id"],
                "date": agm_date + timedelta(days=offset),
                "offset_days": offset,
                "title": m["title"],
                "owner_role": m.get("owner_role", ""),
            }
        )
    resolved.sort(key=lambda m: m["date"])
    return resolved


def render_markdown(cfg: dict, agm_date: datetime, milestones: list) -> str:
    org = cfg["org"]
    notice_days = cfg.get("agm", {}).get("notice_days", 14)
    lines = [
        f"# {org['name']} — AGM Preparation Timeline",
        "",
        f"**AGM date:** {agm_date.strftime('%-d %B %Y')}",
        f"**Notice period:** {notice_days} days (per constitution)",
        "",
        "| Due | T± | Milestone | Owner | Done |",
        "|---|---|---|---|---|",
    ]
    for m in milestones:
        t = f"T{m['offset_days']:+d}" if m["offset_days"] else "T-0"
        lines.append(
            f"| {m['date'].strftime('%a %-d %b %Y')} | {t} | {m['title']} "
            f"| {m['owner_role']} | ☐ |"
        )
    lines += [
        "",
        "Regenerate this timeline if the AGM date changes:",
        f"`python3 scripts/agm-timeline.py --agm-date {agm_date.strftime('%Y-%m-%d')}`",
        "",
    ]
    return "\n".join(lines)


def ics_escape(text: str) -> str:
    """Escape TEXT values per RFC 5545 §3.3.11."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def ics_fold(line: str) -> str:
    """Fold content lines longer than 75 octets per RFC 5545 §3.1."""
    if len(line.encode()) <= 75:
        return line
    parts = []
    while len(line.encode()) > 75:
        # Byte-safe split point at or below 75 octets
        cut = 75
        while len(line[:cut].encode()) > 75:
            cut -= 1
        parts.append(line[:cut])
        line = " " + line[cut:]
    parts.append(line)
    return "\r\n".join(parts)


def render_ics(cfg: dict, agm_date: datetime, milestones: list) -> str:
    org = cfg["org"]
    slug = org.get("short_name", "org").lower()
    year = agm_date.year
    # Deterministic DTSTAMP (derived from the AGM date) keeps regenerated
    # files diff-stable for the same inputs.
    dtstamp = agm_date.strftime("%Y%m%dT000000Z")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//{org['name']}//agm-timeline//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    for m in milestones:
        start = m["date"].strftime("%Y%m%d")
        end = (m["date"] + timedelta(days=1)).strftime("%Y%m%d")
        summary = f"{org.get('short_name', 'AGM')} AGM: {m['title']}"
        lines += [
            "BEGIN:VEVENT",
            f"UID:agm-{year}-{m['id']}@{slug}",
            f"DTSTAMP:{dtstamp}",
            f"DTSTART;VALUE=DATE:{start}",
            f"DTEND;VALUE=DATE:{end}",
            f"SUMMARY:{ics_escape(summary)}",
            f"DESCRIPTION:{ics_escape('Owner: ' + m['owner_role'])}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(ics_fold(line) for line in lines) + "\r\n"


def render_reminders(agm_date: datetime, milestones: list) -> str:
    """Emit a reminders fragment in the schema of reminders.example.yml."""
    entries = []
    for m in milestones:
        entries.append(
            {
                "id": f"agm-{agm_date.year}-{m['id']}",
                "rule": f"date:{m['date'].strftime('%Y-%m-%d')}",
                "subject": f"AGM prep: {m['title']}",
                "body_template": "agm-milestone",
                "audience": "committee",
            }
        )
    return yaml.safe_dump({"reminders": entries}, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", default="org.yml", help="Path to org config YAML")
    parser.add_argument("--agm-date", required=True, help="AGM date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Markdown output path")
    parser.add_argument("--ics", action="store_true", help="Also write an .ics file")
    parser.add_argument("--ics-output", help="Override .ics output path")
    parser.add_argument(
        "--emit-reminders",
        action="store_true",
        help="Also write a reminders YAML fragment",
    )
    parser.add_argument("--stdout", action="store_true", help="Print to stdout")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    config_path = (
        Path(args.config)
        if Path(args.config).is_absolute()
        else repo_root / args.config
    )
    cfg = load_config(config_path)

    try:
        agm_date = datetime.strptime(args.agm_date, "%Y-%m-%d")
    except ValueError:
        sys.exit(f"Error: --agm-date must be YYYY-MM-DD, got {args.agm_date!r}")

    milestones = resolve_milestones(cfg, agm_date)
    markdown = render_markdown(cfg, agm_date, milestones)

    if args.stdout:
        print(markdown, end="")
        if args.emit_reminders:
            print("\n---\n")
            print(render_reminders(agm_date, milestones), end="")
        return

    out_path = (
        Path(args.output)
        if args.output
        else repo_root / "meetings" / f"agm-{agm_date.year}" / "timeline.md"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown)
    print(f"Written: {out_path}")

    if args.ics or args.ics_output:
        ics_path = (
            Path(args.ics_output)
            if args.ics_output
            else out_path.with_suffix(".ics")
        )
        ics_path.parent.mkdir(parents=True, exist_ok=True)
        ics_path.write_text(render_ics(cfg, agm_date, milestones))
        print(f"Written: {ics_path}")

    if args.emit_reminders:
        reminders_path = out_path.parent / "reminders.agm.yml"
        reminders_path.write_text(render_reminders(agm_date, milestones))
        print(f"Written: {reminders_path}")


if __name__ == "__main__":
    main()
