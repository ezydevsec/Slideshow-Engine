#!/usr/bin/env python3
"""Join posting manifests, post performance, and daily revenue into one weekly table.

Usage:
  python3 results_join.py [--project .] [--days 7]

Reads:
  06-queue/*-manifest.csv         set_id,post_id,account,account_id,platform,format,trend,hook_id,messaging_angle,queued_at,status
  07-results/performance.csv      date,account,platform,post_id,post_url,set_id,messaging_angle,views,profile_visits,likes,comments,shares,saves,app_questions,attributable_purchases
  07-results/revenue.csv          date,installs,trials,revenue

Writes:
  07-results/weekly-YYYY-MM-DD.csv, one row per account and set

Reporting is kept separate per account. A metric with no recorded values stays
blank instead of showing 0, so "not measured" is never read as "zero".

est_installs spreads each day's installs across that day's posts by view share.
That's a rough estimate for comparing sets, not true attribution. Use
attributable_purchases where the platform or store can actually measure it.
"""
import argparse
import csv
import datetime as dt
import glob
import os
from collections import defaultdict

METRICS = ("views", "profile_visits", "likes", "comments", "shares", "saves", "app_questions", "attributable_purchases")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def total(values):
    vals = [v for v in values if v is not None]
    return int(sum(vals)) if vals else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    ap.add_argument("--days", type=int, default=7)
    a = ap.parse_args()
    p = a.project
    since = (dt.date.today() - dt.timedelta(days=a.days)).isoformat()

    meta = {}
    for path in glob.glob(os.path.join(p, "06-queue", "*-manifest.csv")):
        for r in read(path):
            meta.setdefault(r["set_id"], r)

    perf = [r for r in read(os.path.join(p, "07-results", "performance.csv")) if r.get("date", "") >= since]
    revenue = {r["date"]: r for r in read(os.path.join(p, "07-results", "revenue.csv"))}

    day_views = defaultdict(float)
    for r in perf:
        day_views[r["date"]] += num(r.get("views")) or 0

    groups = defaultdict(list)
    for r in perf:
        groups[(r.get("account", ""), r["set_id"])].append(r)

    out = os.path.join(p, "07-results", f"weekly-{dt.date.today().isoformat()}.csv")
    cols = ["account", "set_id", "messaging_angle", "format", "trend", "hook_id", "posts", *METRICS,
            "views_per_post", "est_installs", "best_post_views", "best_post_id", "best_post_url"]
    rows = []
    for (account, set_id), posts in groups.items():
        m = meta.get(set_id, {})
        row = {"account": account, "set_id": set_id, "posts": len(posts),
               "messaging_angle": next((r["messaging_angle"] for r in posts if r.get("messaging_angle")), m.get("messaging_angle", "")),
               "format": m.get("format", ""), "trend": m.get("trend", ""), "hook_id": m.get("hook_id", "")}
        for k in METRICS:
            row[k] = total(num(r.get(k)) for r in posts)
        row["views_per_post"] = int(row["views"] / len(posts)) if row["views"] != "" else ""
        est = []
        for r in posts:
            rev, v = revenue.get(r["date"]), num(r.get("views"))
            if rev and v is not None and day_views[r["date"]] and num(rev.get("installs")) is not None:
                est.append(v / day_views[r["date"]] * num(rev.get("installs")))
        row["est_installs"] = round(sum(est), 1) if est else ""
        best = max(posts, key=lambda r: num(r.get("views")) or 0)
        row["best_post_views"] = total([num(best.get("views"))])
        row["best_post_id"], row["best_post_url"] = best.get("post_id", ""), best.get("post_url", "")
        rows.append(row)
    rows.sort(key=lambda r: (r["account"], -(r["views"] or 0)))
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} account/set rows -> {out}")


if __name__ == "__main__":
    main()
