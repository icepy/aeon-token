#!/usr/bin/env python3
"""arxiv-radar scanner. argv: DAYS dry|live [names]  -- faithful to skills/arxiv-radar/SKILL.md"""
import json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

DAYS_ARG = sys.argv[1] if len(sys.argv) > 1 else "7"
MODE_ARG = sys.argv[2] if len(sys.argv) > 2 else "live"
NAMES_MODE = len(sys.argv) > 3 and sys.argv[3] == "names"

NAMES_FILE = "memory/universe-names.txt"

TERMS = [t.strip() for t in """
proof-of-useful-work
verifiable inference
light client
proof of training
proof of learning
verifiable training
auditable training
data availability sampling
restaking
automated market maker
consensus protocol
cat:cs.CR AND ti:"MEV"
liquid staking
embodied data
robot manipulation data
robot data
embodied AI
zero-knowledge
# ── 持仓依赖的机制（持仓是 NOTE / DEUS / PEARL）──
ti:"EIP-1559"
ti:"Robinhood Chain"
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

if NAMES_MODE:
    TERMS = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

known = []
if os.path.exists(NAMES_FILE):
    known = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

CARRIER_BASE = ["deployed", "deployment", "mainnet", "testnet", "protocol",
                "production", "open-source", "released", "blockchain", "network",
                "token", "incentive", "marketplace", "validator", "miner"]
CARRIER_ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
                 "simulator", "dataset", "datasets", "real-world", "embodied",
                 "sensor", "egocentric", "demonstration", "vla"]
CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher"]

CARRIER_BY_TERM = {
    "embodied data": CARRIER_ROBOT,
    "robot manipulation data": CARRIER_ROBOT,
    "robot data": CARRIER_ROBOT,
    "embodied AI": CARRIER_ROBOT,
    "automated market maker": CARRIER_BASE + CARRIER_MARKET,
    'cat:cs.CR AND ti:"MEV"': CARRIER_BASE + CARRIER_MARKET,
}
EXCL = ["survey", "tutorial"]
STOP = set("""a an the on of in for with from and or to at by as is are was were
towards toward via using based scalable efficient large language model models
learning deep neural network networks system systems new novel study analysis
empirical measurement framework approach method methods data theory practice
case real world beyond not all end how what why when where which that this""".split())

DAYS = int(DAYS_ARG)
DRY = MODE_ARG == "dry"
SEEN = "memory/arxiv-seen.json"
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}

now = datetime.now(timezone.utc)
win = f"[{(now - timedelta(days=DAYS)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

def guess_name(title, summ, known):
    for n in known:
        if re.search(rf"\b{re.escape(n)}\b", title + " " + summ, re.I):
            return n
    m = re.search(r"\b([A-Z][A-Za-z0-9\-]{2,})(?:'s|’s)\b", title + " " + summ)
    if m:
        return m.group(1)
    for w in re.findall(r"\b[A-Z][A-Za-z0-9\-]{2,}\b", title):
        if w.lower() not in STOP:
            return w
    return ""

out, raw, newest = [], 0, ""
drop = {"seen": 0, "excl": 0, "carrier": 0, "fail": 0}
hit_ids = {}
per_term = {}
raw_term = {}
excluded = []

for term in TERMS:
    carrier = CARRIER_BY_TERM.get(term, CARRIER_BASE)
    if term.startswith(("cat:", "ti:", "abs:", "all:")):
        q = term
    elif NAMES_MODE:
        q = (f'ti:"{term}" AND (cat:cs.CR OR cat:cs.CE OR cat:cs.GT OR cat:cs.DC '
             'OR cat:q-fin.CP OR cat:q-fin.GN)')
    else:
        q = f'ti:"{term}"'

    p = {"search_query": f"({q}) AND submittedDate:{win}",
         "start": 0, "max_results": 100,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    url = API + "?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            root = ET.fromstring(r.read())
    except Exception as ex:
        print(f"! {term}: {ex}", file=sys.stderr)
        drop["fail"] += 1
        time.sleep(3)
        continue

    for e in root.findall("a:entry", NS):
        raw += 1
        raw_term[term] = raw_term.get(term, 0) + 1
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        blob = (title + " " + summ).lower()
        pub = e.find("a:published", NS).text[:10]
        if pub > newest:
            newest = pub
        if aid in seen:
            drop["seen"] += 1
            continue
        if aid in hit_ids:
            hit_ids[aid]["terms"].append(term)
            drop["seen"] += 1
            continue
        if any(x in title.lower() for x in EXCL):
            drop["excl"] += 1
            excluded.append({"id": aid, "term": term, "title": title, "why": "excl"})
            continue
        if not any(c in blob for c in carrier):
            drop["carrier"] += 1
            excluded.append({"id": aid, "term": term, "title": title, "why": "carrier"})
            continue
        rec = {"term": term, "terms": [term], "name": guess_name(title, summ, known),
               "title": title, "published": pub, "link": f"https://arxiv.org/abs/{aid}",
               "carrier": next(c for c in carrier if c in blob)}
        out.append(rec)
        hit_ids[aid] = rec
        per_term[term] = per_term.get(term, 0) + 1
    time.sleep(3)

out.sort(key=lambda c: c["published"], reverse=True)
print(f"扫 {len(TERMS)} 词 | 窗口 {DAYS}d | 原始 {raw} | 幸存 {len(out)} | "
      f"丢弃 seen={drop['seen']} excl={drop['excl']} "
      f"carrier={drop['carrier']} fail={drop['fail']}", file=sys.stderr)
print(f"窗口内最新收录日期: {newest or '(无)'}", file=sys.stderr)
print("词表原始/新收: " + " · ".join(
      f"{k}={v}/{per_term.get(k, 0)}" for k, v in
      sorted(raw_term.items(), key=lambda x: -x[1])), file=sys.stderr)
print(f"零命中词 ({len([t for t in TERMS if t not in raw_term])}): " + " · ".join(
      t for t in TERMS if t not in raw_term), file=sys.stderr)
for c in out[:25]:
    print(f"  {c['published']} [{'+'.join(c['terms'])}] {c['title'][:85]}", file=sys.stderr)
for x in excluded:
    print(f"  DROP[{x['why']}] {x['id']} ({x['term']}) {x['title'][:70]}", file=sys.stderr)

if not DRY and hit_ids:
    merged = {k: now.strftime("%Y-%m-%d") for k in hit_ids}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-2000:]),
              open(SEEN, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
print(json.dumps({"survivors": out, "excluded": excluded, "drop": drop,
                  "raw": raw, "newest": newest, "terms": len(TERMS),
                  "zero_terms": [t for t in TERMS if t not in raw_term],
                  "raw_term": raw_term},
                 ensure_ascii=False, indent=1))
