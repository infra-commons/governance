#!/usr/bin/env python3
"""Validate a reminders schedule file against the schema in docs/reminders.md.

Usage:
    python3 scripts/validate-reminders.py [--file reminders.yml]

Exits non-zero with one line per problem found.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

ORDINALS = {"first", "second", "third", "fourth", "last"}
WEEKDAYS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}
AUDIENCES = {"committee", "key-holders"}


def validate_rule(rule: str) -> str:
    """Return an error message, or '' if the rule is valid."""
    if not isinstance(rule, str) or ":" not in rule:
        return f"rule must be '<kind>:<spec>', got {rule!r}"
    kind, spec = rule.split(":", 1)
    if kind in ("monthly", "quarterly"):
        parts = spec.split("-")
        if len(parts) != 2 or parts[0] not in ORDINALS or parts[1] not in WEEKDAYS:
            return f"{kind} spec must be '<ordinal>-<weekday>', got {spec!r}"
    elif kind == "annual":
        if not re.fullmatch(r"\d{2}-\d{2}", spec):
            return f"annual spec must be 'MM-DD', got {spec!r}"
        month, day = int(spec[:2]), int(spec[3:])
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return f"annual spec out of range: {spec!r}"
    elif kind == "date":
        try:
            datetime.strptime(spec, "%Y-%m-%d")
        except ValueError:
            return f"date spec must be YYYY-MM-DD, got {spec!r}"
    else:
        return f"unknown rule kind {kind!r}"
    return ""


def validate(doc: dict) -> list:
    errors = []
    reminders = (doc or {}).get("reminders")
    if not isinstance(reminders, list) or not reminders:
        return ["top-level 'reminders' must be a non-empty list"]

    seen_ids = set()
    for i, r in enumerate(reminders):
        where = f"reminders[{i}]"
        if not isinstance(r, dict):
            errors.append(f"{where}: entry must be a mapping")
            continue
        rid = r.get("id")
        where = f"reminders[{i}] ({rid})" if rid else where

        for field in ("id", "rule", "subject", "body_template", "audience"):
            if not r.get(field):
                errors.append(f"{where}: missing required field {field!r}")
        if rid:
            if rid in seen_ids:
                errors.append(f"{where}: duplicate id")
            seen_ids.add(rid)

        if r.get("rule"):
            err = validate_rule(r["rule"])
            if err:
                errors.append(f"{where}: {err}")
            kind = str(r["rule"]).split(":", 1)[0]
            if kind == "quarterly":
                months = r.get("months")
                if (
                    not isinstance(months, list)
                    or not months
                    or not all(isinstance(m, int) and 1 <= m <= 12 for m in months)
                ):
                    errors.append(
                        f"{where}: quarterly rules need 'months', a list of ints 1-12"
                    )
            elif "months" in r:
                errors.append(f"{where}: 'months' only applies to quarterly rules")

        if "offset_days" in r and not isinstance(r["offset_days"], int):
            errors.append(f"{where}: offset_days must be an integer")
        if r.get("audience") and r["audience"] not in AUDIENCES:
            errors.append(
                f"{where}: audience must be one of {sorted(AUDIENCES)}, "
                f"got {r['audience']!r}"
            )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="reminders.yml", help="Schedule file path")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    path = Path(args.file) if Path(args.file).is_absolute() else repo_root / args.file
    if not path.exists():
        sys.exit(f"Error: {path} not found")

    with path.open() as f:
        doc = yaml.safe_load(f)

    errors = validate(doc)
    if errors:
        for e in errors:
            print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {path} — {len(doc['reminders'])} reminder(s) valid")


if __name__ == "__main__":
    main()
