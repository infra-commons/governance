#!/usr/bin/env python3
"""Generate governance documents (agenda, minutes, AGM notices) from org.yml + Jinja2 templates.

Usage:
    python3 scripts/generate.py --template agenda --date 2026-07-07
    python3 scripts/generate.py --template minutes --date 2026-07-07
    python3 scripts/generate.py --template agm-agenda --date 2026-11-04
    python3 scripts/generate.py --template agm-reminder --date 2026-10-21
    python3 scripts/generate.py --template wallet-check --date 2026-07-06
    python3 scripts/generate.py --template newsletter-member --date 2026-08-03

Options:
    --config PATH        Path to org config file (default: org.yml)
    --template NAME      Template name: agenda|minutes|agm-agenda|agm-reminder|
                         wallet-check|newsletter-member|newsletter-external
    --date YYYY-MM-DD    Meeting date
    --previous-date DATE Previous meeting date (agenda/minutes confirmation item)
    --output PATH        Output file path (default: meetings/YYYY-MM-DD/{template}.md)
    --stdout             Print to stdout instead of writing a file
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def load_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return yaml.safe_load(f)


def render(template_name: str, context: dict, templates_dir: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template(f"{template_name}.md.j2")
    return tpl.render(**context)


def default_output(template_name: str, meeting_date: str, base_dir: Path) -> Path:
    return base_dir / "meetings" / meeting_date / f"{template_name}.md"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", default="org.yml", help="Path to org config YAML")
    parser.add_argument(
        "--template",
        required=True,
        choices=[
            "agenda",
            "minutes",
            "agm-agenda",
            "agm-reminder",
            "wallet-check",
            "newsletter-member",
            "newsletter-external",
        ],
        help="Template to render",
    )
    parser.add_argument("--date", required=True, help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--previous-date", help="Previous meeting date (YYYY-MM-DD)")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    config_path = (
        Path(args.config)
        if Path(args.config).is_absolute()
        else repo_root / args.config
    )
    templates_dir = repo_root / "templates"

    cfg = load_config(config_path)

    try:
        date_obj = datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        sys.exit(f"Error: --date must be YYYY-MM-DD, got {args.date!r}")

    meeting_date_display = date_obj.strftime("%-d %B %Y")

    context = {
        **cfg,
        "meeting_date": meeting_date_display,
        "meeting_date_iso": args.date,
        "meeting_type": "Committee",
        "previous_meeting_date": args.previous_date or "[previous meeting date]",
    }

    rendered = render(args.template, context, templates_dir)

    if args.stdout:
        print(rendered, end="")
        return

    out_path = (
        Path(args.output)
        if args.output
        else default_output(args.template, args.date, repo_root)
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered)
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
