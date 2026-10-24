#!/usr/bin/env python3
"""Join posting manifests, post performance, and daily revenue into one weekly table.

Usage:
  python3 results_join.py [--project .] [--days 7]

Reads:
  06-queue/*-manifest.csv         set_id,post_id,account_id,platform,format,trend,hook_id,queued_at,status
  07-results/performance.csv      date,set_id,account_id,platform,post_url,views,likes,comments,shares,saves,app_questions
  07-results/revenue.csv          date,installs,trials,revenue

Writes:
  07-results/weekly-YYYY-MM-DD.csv, one row per set

Installs are spread across each day's posts by view share. That's a rough
estimate for comparing sets, not true attribution.
"""
import argparse
import csv
import datetime as dt
import glob
import os
from collections import defaultdict


def num(v):
    try:
        return float(v or 0)
    except ValueError:
        return 0.0


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


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
        day_views[r["date"]] += num(r["views"])

    sets = defaultdict(lambda: defaultdict(float))
    accounts = defaultdict(set)
    best = {}
    for r in perf:
        s, v = r["set_id"], num(r["views"])
        for k in ("views", "likes", "comments", "shares", "saves", "app_questions"):
            sets[s][k] += num(r.get(k))
        sets[s]["posts"] += 1
        accounts[s].add(r["account_id"])
        rev = revenue.get(r["date"])
        if rev and day_views[r["date"]]:
            share = v / day_views[r["date"]]
            sets[s]["est_installs"] += share * num(rev.get("installs"))
            sets[s]["est_trials"] += share * num(rev.get("trials"))
        if v > best.get(s, (0, ""))[0]:
            best[s] = (v, r.get("post_url", ""))

    out = os.path.join(p, "07-results", f"weekly-{dt.date.today().isoformat()}.csv")
    cols = ["set_id", "format", "trend", "hook_id", "posts", "accounts", "views", "views_per_post",
            "saves", "shares", "comments", "app_questions", "est_installs", "est_trials", "best_post_views", "best_post_url"]
    rows = []
    for s, t in sets.items():
        m = meta.get(s, {})
        rows.append({
            "set_id": s, "format": m.get("format", ""), "trend": m.get("trend", ""), "hook_id": m.get("hook_id", ""),
            "posts": int(t["posts"]), "accounts": len(accounts[s]), "views": int(t["views"]),
            "views_per_post": int(t["views"] / t["posts"]) if t["posts"] else 0,
            "saves": int(t["saves"]), "shares": int(t["shares"]), "comments": int(t["comments"]),
            "app_questions": int(t["app_questions"]),
            "est_installs": round(t["est_installs"], 1), "est_trials": round(t["est_trials"], 1),
            "best_post_views": int(best.get(s, (0, ""))[0]), "best_post_url": best.get(s, (0, ""))[1],
        })
    rows.sort(key=lambda r: r["views"], reverse=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} sets -> {out}")


if __name__ == "__main__":
    main()
