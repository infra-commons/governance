#!/usr/bin/env python3
"""Append new action items from a completed minutes file to the actions register.

The minutes file must contain a section headed:

    ## New Actions

followed by a markdown table with columns:

    | Action | Responsible |

Any data rows in that table are appended to the actions register with
auto-incrementing numbers, today's date, and status "New".

Usage:
    python3 scripts/update-actions.py --minutes meetings/2026-07-07/minutes.md
    python3 scripts/update-actions.py --minutes meetings/2026-07-07/minutes.md \\
        --register meetings/actions-register.md --date 2026-07-07
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path


def parse_new_actions(minutes_text: str) -> list[tuple[str, str]]:
    """Return [(action, responsible), ...] from the '## New Actions' table in minutes."""
    match = re.search(r"^## New Actions\s*\n", minutes_text, re.MULTILINE)
    if not match:
        return []

    section = minutes_text[match.end():]
    end = re.search(r"^##+ ", section, re.MULTILINE)
    if end:
        section = section[: end.start()]

    actions = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*[-:]+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        action, responsible = cells[0].strip(), cells[1].strip()
        if not action or action.lower() in ("action", "[action description]"):
            continue
        actions.append((action, responsible))
    return actions


def next_action_number(register_text: str) -> int:
    """Return the next action number (max existing + 1, minimum 1)."""
    numbers = re.findall(r"^\|\s*(\d+)\s*\|", register_text, re.MULTILINE)
    return max((int(n) for n in numbers), default=0) + 1


def append_actions(
    register_path: Path, new_actions: list[tuple[str, str]], created_date: str
) -> int:
    """Append new_actions to the register file; return count of rows added."""
    text = register_path.read_text() if register_path.exists() else ""
    if not text:
        text = "# Actions Register\n\n| # | Action | Responsible | Created | Status |\n|---|--------|-------------|---------|--------|\n"

    next_num = next_action_number(text)
    rows = []
    for i, (action, responsible) in enumerate(new_actions):
        num = next_num + i
        rows.append(f"| {num} | {action} | {responsible} | {created_date} | New |")

    if not rows:
        return 0

    if not text.endswith("\n"):
        text += "\n"
    text += "\n".join(rows) + "\n"
    register_path.write_text(text)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--minutes", required=True, help="Path to completed minutes markdown file"
    )
    parser.add_argument(
        "--register",
        default=None,
        help="Path to actions register (default: meetings/actions-register.md)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Date to record as Created (YYYY-MM-DD or DD/MM/YYYY; default: today)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    minutes_path = (
        Path(args.minutes)
        if Path(args.minutes).is_absolute()
        else repo_root / args.minutes
    )
    register_path = (
        Path(args.register)
        if args.register
        else repo_root / "meetings" / "actions-register.md"
    )

    if args.date:
        created_date = args.date
    else:
        created_date = date.today().strftime("%d/%m/%Y")

    if not minutes_path.exists():
        sys.exit(f"Error: minutes file not found: {minutes_path}")

    minutes_text = minutes_path.read_text()
    actions = parse_new_actions(minutes_text)

    if not actions:
        print(
            "No new actions found in minutes (looked for '## New Actions' section with a table)."
        )
        return

    register_path.parent.mkdir(parents=True, exist_ok=True)
    added = append_actions(register_path, actions, created_date)
    print(f"Added {added} action(s) to {register_path}")
    for action, responsible in actions:
        print(f"  - {action!r} -> {responsible}")


if __name__ == "__main__":
    main()
