#!/usr/bin/env python3
"""Cross-account duplicate check (founder, 2026-11-15: never post the same slideshow on two accounts).

  python3 dup_check.py [--days 21] [set_dir ...]   # no args: checks every set from the last N days

Flags any pair of sets on DIFFERENT accounts within N days that share the same renderer/template AND
a similar caption or similar slide titles (difflib ratio >= 0.6). Exit code 1 if anything is flagged.
"""
import json, os, re, sys, glob, difflib, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SPECS = ("edu.json", "native.json", "comic.json", "meme.json", "pixel.json", "stick.json", "video.json")
args = sys.argv[1:]; days = 21
if "--days" in args: i = args.index("--days"); days = int(args[i + 1]); del args[i:i + 2]

def load(d):
    for f in SPECS:
        p = os.path.join(d, f)
        if os.path.exists(p):
            j = json.load(open(p)); acct = j.get("account", "")
            titles = " ".join(str(s.get("title") or s.get("lines") or s.get("caption") or s.get("hook") or "") for s in j.get("slides", []))
            norm = lambda t: re.sub(r"[^a-z ]", " ", t.lower())
            return dict(set=os.path.basename(d), acct=acct, tpl=f, cap=norm(j.get("caption", "")), titles=norm(titles))

today = datetime.date.today(); cutoff = (today - datetime.timedelta(days=days)).isoformat()
allsets = [load(d) for d in sorted(glob.glob(os.path.join(ROOT, "04-sets", "20*"))) if os.path.basename(d)[:10] >= cutoff]
allsets = [s for s in allsets if s and s["acct"]]
targets = [load(os.path.abspath(a)) for a in args] if args else allsets
flag = 0; seen = set()
for a in targets:
    for b in allsets:
        if a["set"] == b["set"] or a["acct"] == b["acct"] or a["tpl"] != b["tpl"]: continue
        key = tuple(sorted((a["set"], b["set"])))
        if key in seen: continue
        seen.add(key)
        rc = difflib.SequenceMatcher(None, a["cap"], b["cap"]).ratio() if a["cap"] and b["cap"] else 0
        rt = difflib.SequenceMatcher(None, a["titles"], b["titles"]).ratio() if a["titles"] and b["titles"] else 0
        if max(rc, rt) >= 0.6:
            flag += 1; print(f"DUPLICATE? {a['acct']} {a['set']}  <->  {b['acct']} {b['set']}  (caption {rc:.2f}, slides {rt:.2f}, {a['tpl']})")
print(f"{flag} cross-account duplicates flagged" if flag else "no cross-account duplicates")
sys.exit(1 if flag else 0)
