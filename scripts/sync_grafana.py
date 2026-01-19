#!/usr/bin/env python3
"""
Sync Grafana provisioning files (dashboards + provisioning) to the server.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], dry_run: bool) -> None:
    if dry_run:
        print("+", " ".join(cmd))
        return
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Grafana provisioning files to server.")
    parser.add_argument("--host", default="192.168.12.221", help="SSH host or IP")
    parser.add_argument("--user", default="jose", help="SSH user")
    parser.add_argument(
        "--dest",
        default="/home/jose/grafana_lmi/grafana_lmi",
        help="Destination directory on server",
    )
    parser.add_argument("--dashboards", action="store_true", help="Sync dashboards only")
    parser.add_argument("--provisioning", action="store_true", help="Sync provisioning only")
    parser.add_argument("--restart", action="store_true", help="Restart Grafana after sync")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    dashboards_dir = base_dir / "dashboards"
    provisioning_dir = base_dir / "provisioning"

    if not dashboards_dir.is_dir() or not provisioning_dir.is_dir():
        print(f"Expected dashboards/provisioning under: {base_dir}", file=sys.stderr)
        return 1

    sync_dashboards = args.dashboards or not args.provisioning
    sync_provisioning = args.provisioning or not args.dashboards

    try:
        if sync_dashboards:
            _run(
                [
                    "scp",
                    "-r",
                    str(dashboards_dir),
                    f"{args.user}@{args.host}:{args.dest}/",
                ],
                args.dry_run,
            )
        if sync_provisioning:
            _run(
                [
                    "scp",
                    "-r",
                    str(provisioning_dir),
                    f"{args.user}@{args.host}:{args.dest}/",
                ],
                args.dry_run,
            )
        if args.restart:
            _run(
                ["ssh", f"{args.user}@{args.host}", "docker", "restart", "grafana"],
                args.dry_run,
            )
    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {exc}", file=sys.stderr)
        return exc.returncode or 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
