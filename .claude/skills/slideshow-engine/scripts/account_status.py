#!/usr/bin/env python3
"""Check posting-account readiness, one account at a time.

Usage:
  python3 account_status.py [--project .] [--account @handle]

Reads 06-queue/accounts.json. An account is ready when its status is active and
every field in its `required` list is set (not null, not containing "TO CONFIRM").
Missing settings block only that account. An unconfirmed bio is a warning.
"""
import argparse
import json
import os
import sys


def load(project):
    path = os.path.join(project, "06-queue", "accounts.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def field(acct, dotted):
    v = acct
    for part in dotted.split("."):
        v = v.get(part) if isinstance(v, dict) else None
    return v


def unset(v):
    return v is None or v == [] or v == {} or "TO CONFIRM" in json.dumps(v)


def check(cfg, handle):
    """Return (blockers, warnings, account) for one handle."""
    acct = next((a for a in cfg.get("accounts", []) if a.get("handle") == handle), None)
    if acct is None:
        return [f"{handle} is not in accounts.json"], [], None
    phase = cfg.get("phase", "prelaunch")
    blockers = []
    if acct.get("status") != "active":
        blockers.append(f"status is {acct.get('status')!r}, not 'active'")
    required = [r.replace("cta.prelaunch", f"cta.{phase}") for r in acct.get("required", [])]
    blockers += [f"{r} not confirmed" for r in required if unset(field(acct, r))]
    if phase == "launched" and not field(cfg, "launch.download_url"):
        blockers.append("phase is 'launched' but launch.download_url is not set")
    warnings = [] if acct.get("bio") else ["bio not confirmed"]
    return blockers, warnings, acct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    ap.add_argument("--account", default=None)
    a = ap.parse_args()
    cfg = load(a.project)
    if cfg is None:
        sys.exit("no 06-queue/accounts.json")
    handles = [a.account] if a.account else [x["handle"] for x in cfg.get("accounts", [])]
    any_blocked = False
    for h in handles:
        blockers, warnings, _ = check(cfg, h)
        any_blocked |= bool(blockers)
        print(f"{h}: {'BLOCKED' if blockers else 'ready'}")
        for b in blockers:
            print(f"  blocker: {b}")
        for w in warnings:
            print(f"  warning: {w}")
    sys.exit(1 if a.account and any_blocked else 0)


if __name__ == "__main__":
    main()
