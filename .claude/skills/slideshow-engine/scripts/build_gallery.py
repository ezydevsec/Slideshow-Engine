#!/usr/bin/env python3
"""Build a local HTML gallery of outlier slideshows so the user can pick formats.

Usage:
  python3 build_gallery.py <raw.json> <out.html>

raw.json is a list of objects with: url, account, views, outlier, posted, caption,
sound, slides (list of image URLs), and optionally likes, comments, shares, saves, niche.

The page has a checkbox per card and an "Export selected" button that downloads
selected.json (the chosen entries) for the breakdown step.
"""
import html
import json
import sys


def fmt(n):
    n = n or 0
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}K" if n >= 1e3 else str(n)


def card(i, p):
    slides = "".join(
        f'<img loading="lazy" src="{html.escape(u)}" alt="slide {j + 1}">' for j, u in enumerate(p.get("slides", [])[:12])
    )
    stats = " · ".join(
        f"{k} {fmt(p.get(k))}" for k in ("views", "likes", "comments", "shares", "saves") if p.get(k) is not None
    )
    return f"""
<article class="card" data-i="{i}">
  <header>
    <label><input type="checkbox" data-i="{i}"> select</label>
    <a href="{html.escape(p.get('url', ''))}" target="_blank" rel="noopener">@{html.escape(p.get('account', ''))}</a>
    <span class="tag">{html.escape(p.get('niche', ''))}</span>
    <span class="outlier">{p.get('outlier', 0):.1f}x</span>
  </header>
  <div class="slides">{slides}</div>
  <p class="stats">{stats} · {html.escape(p.get('posted', ''))} · {len(p.get('slides', []))} slides</p>
  <p class="cap">{html.escape(p.get('caption', ''))}</p>
  <p class="sound">{html.escape(p.get('sound', ''))}</p>
</article>"""


def main():
    raw, out = sys.argv[1], sys.argv[2]
    with open(raw) as f:
        posts = sorted(json.load(f), key=lambda p: p.get("outlier", 0), reverse=True)
    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Outlier slideshows</title>
<style>
body{{font:14px -apple-system,system-ui,sans-serif;margin:16px;background:#fafafa;color:#111}}
.bar{{position:sticky;top:0;background:#fafafa;padding:8px 0;display:flex;gap:12px;align-items:center}}
button{{font:inherit;padding:8px 14px;border-radius:8px;border:0;background:#111;color:#fff;cursor:pointer}}
.card{{background:#fff;border:1px solid #e5e5e5;border-radius:12px;padding:12px;margin:12px 0}}
.card.on{{outline:3px solid #d97757}}
header{{display:flex;gap:12px;align-items:center}}
.outlier{{margin-left:auto;font-weight:700;color:#d97757}}
.tag{{color:#888}}
.slides{{display:flex;gap:6px;overflow-x:auto;padding:8px 0}}
.slides img{{height:260px;border-radius:6px}}
.stats,.sound{{color:#666;margin:4px 0}}
</style></head><body>
<div class="bar"><strong>{len(posts)} slideshows</strong><span id="n">0 selected</span>
<button id="export">Export selected</button></div>
{''.join(card(i, p) for i, p in enumerate(posts))}
<script>
const posts = {json.dumps(posts)};
const picked = new Set();
document.querySelectorAll('input[type=checkbox]').forEach(cb => cb.addEventListener('change', () => {{
  const i = +cb.dataset.i;
  cb.checked ? picked.add(i) : picked.delete(i);
  cb.closest('.card').classList.toggle('on', cb.checked);
  document.getElementById('n').textContent = picked.size + ' selected';
}}));
document.getElementById('export').onclick = () => {{
  const data = [...picked].map(i => posts[i]);
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}}));
  a.download = 'selected.json';
  a.click();
}};
</script></body></html>"""
    with open(out, "w") as f:
        f.write(page)
    print(f"gallery -> {out} ({len(posts)} slideshows)")


if __name__ == "__main__":
    main()
