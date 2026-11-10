import json, os, glob, zipfile, sys
# usage: pack.py plan.json  — plan: [{"set": "...", "zip": "06-queue/zips-DATE/name.zip", "post_on": "YYYY-MM-DD", "sound": "...optional full sound line..."}]
plan = json.load(open(sys.argv[1])); rows = []
SB = "search the name in TikTok's Add sound; pick the version by the listed artist."
for p in plan:
    d = f"04-sets/{p['set']}"; sf = next(f for f in ("edu.json", "native.json", "meme.json", "video.json") if os.path.exists(f"{d}/{f}"))
    sp = json.load(open(f"{d}/{sf}")); sp["status"] = f"approved (founder); post on {p['post_on']}"
    json.dump(sp, open(f"{d}/{sf}", "w"), indent=2, ensure_ascii=False)
    acct = sp["account"]; plat = "(TikTok)" if acct == "@ezyxbt" else "(TikTok, + Instagram once the IG account exists)"
    if sp.get("format","").startswith("oneliner"):
        cap = "none. Leave it empty (founder, 2026-11-05)."
    else:
        cap = sp.get("caption", "") + (" " + " ".join(sp["hashtags"]) if sp.get("hashtags") else "")
    if sf == "video.json":
        files = [f"{d}/{sp['out']}"]; up = f"`{sp['out']}` (1080×1920)"
    else:
        files = sorted(glob.glob(f"{d}/final/preview/slide-*.jpg")); size = "1080×1920" if sp.get("canvas") == "1080x1920" else "1080×1350"
        up = f"`slide-01.jpg`" + (f" … `slide-{len(files):02d}.jpg`" if len(files) > 1 else "") + f" ({size})"
    s = sp.get("sound", {})
    snd = p.get("sound") or f"**{str(s.get('primary')).replace('**','')}**. Backup: **{str(s.get('backup')).replace('**','')}**. ({SB})"
    ai = "**TURN ON**" if sp.get("ai_images") or (sf == "video.json" and sp.get("ai_images") is not False) else ("OFF (" + sp["ai_note"].split(":")[0] + ")" if sp.get("ai_note") else "OFF (real photos and real app screens, nothing generated)")
    tests = []
    if sp.get("length_test"): tests.append(f"slide-length test: **{sp['length_test']}** ({len(files)} slides)")
    if sp.get("new_format_test"): tests.append("**new-format test**" + (f": {sp['new_format_test']}" if isinstance(sp['new_format_test'], str) else f" ({sp.get('format','')})"))
    md = f"""# Posting pack: {p['set']}

**Status: approved. Post manually on {p['post_on']}.** Format: {sp.get('format','').split(' (')[0]}. Space posts on the same account about 3–4 hours apart.

- **Account:** {acct} {plat}
- **Upload:** {up}
- **Caption:** {cap}
- **Sound:** {snd}
- **AI-generated content label:** {ai}
- **Before posting:** no download link (prelaunch).
""" + (f"- **Post at:** {p['post_time']} (UK time; target UK/US).\n" if p.get("post_time") else "") + (f"- **Test:** {'; '.join(tests)}. Note the result at Sunday's review.\n" if tests else "")
    open(f"{d}/posting.md", "w").write(md)
    os.makedirs(os.path.dirname(p["zip"]), exist_ok=True)
    with zipfile.ZipFile(p["zip"], "w", zipfile.ZIP_DEFLATED) as z:
        for f in files: z.write(f, os.path.basename(f))
        z.write(f"{d}/posting.md", "posting.md")
    rows.append(f"{p['set']},{acct},approved,{__import__("datetime").date.today()},{sp.get('format','').split(' (')[0]}; post on {p['post_on']}; manual posting")
existing = open("06-queue/queue.csv").read()
new = [r for r in rows if r.split(",")[0] not in existing]
open("06-queue/queue.csv", "a").write("".join(r + "\n" for r in new)); print("packed", len(plan), "queue rows added", len(new))
