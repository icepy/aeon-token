#!/usr/bin/env python3
"""Independently verify PR #10's recall claim: existing 4 robot terms vs a cs.RO data baseline."""
import json, os, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"
DAYS = int(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 30
now = datetime.now(timezone.utc)
win = f"[{(now - timedelta(days=DAYS)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"
seen = json.load(open("memory/arxiv-seen.json", encoding="utf-8")) if os.path.exists("memory/arxiv-seen.json") else {}

def fetch(q, cap=200):
    p = {"search_query": f"({q}) AND submittedDate:{win}", "start": 0,
         "max_results": cap, "sortBy": "submittedDate", "sortOrder": "descending"}
    with urllib.request.urlopen(API + "?" + urllib.parse.urlencode(p), timeout=30) as r:
        root = ET.fromstring(r.read())
    res = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        res.append((aid, title))
    return res

# baseline: robotics papers whose TITLE mentions data
base = fetch('ti:"data" AND cat:cs.RO')
time.sleep(3)
base_ids = {a for a, _ in base}
base_new = base_ids - set(seen)
print(f"基准集 ti:\"data\" AND cat:cs.RO ({DAYS}d): {len(base_ids)} 篇, 去掉 seen 后 {len(base_new)}")

OLD_TERMS = ["embodied data", "robot manipulation data", "robot data", "embodied AI"]
NEW_TERMS = ['ti:"data engine" AND cat:cs.RO', 'ti:"human data" AND cat:cs.RO',
             'ti:"egocentric" AND cat:cs.RO', 'ti:"data generation" AND cat:cs.RO']

def coverage(terms, label):
    hit = set()
    for t in terms:
        q = t if t.startswith(("ti:", "cat:", "abs:")) else f'ti:"{t}"'
        try:
            for a, _ in fetch(q):
                hit.add(a)
        except Exception as ex:
            print(f"  ! {t}: {ex}")
        time.sleep(3)
    cov = hit & base_new
    print(f"{label}: 命中基准集 {len(cov)}/{len(base_new)}")
    return cov, hit

cov_old, _ = coverage(OLD_TERMS, "现有 4 词")
cov_new, all_new = coverage(NEW_TERMS, "PR#10 新增 4 词")
print(f"两者都漏: {len(base_new - cov_old - cov_new)}")
print("PR#10 救回的基准集论文:")
for a in sorted(cov_new - cov_old):
    t = dict(base).get(a, "?")
    print(f"  {a} {t[:88]}")
