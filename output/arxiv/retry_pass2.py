#!/usr/bin/env python3
"""arxiv-radar 补扫：只重跑 pass1 查询失败的词，带重试 + 长退避。
不覆盖 pass1 产物；新增幸存者落 out-pass2.json，并补写 seen / hits。
"""
import json, os, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}totalResults"
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
MAX_RESULTS = 100

FAILED = sys.argv[2].split("|") if len(sys.argv) > 2 else []

CARRIER_BASE = ["deployed", "deployment", "mainnet", "testnet", "protocol",
                "production", "open-source", "released", "blockchain", "network",
                "token", "incentive", "marketplace", "validator", "miner"]
CARRIER_ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
                 "simulator", "dataset", "datasets", "real-world", "embodied",
                 "sensor", "egocentric", "demonstration", "vla"]
CARRIER_MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher",
                  "ledger", "ledgers", "block creator", "block builder",
                  "block proposer", "transaction ordering", "on-chain",
                  "state transition"]
CARRIER_BY_TERM = {
    "embodied data": CARRIER_ROBOT,
    "robot manipulation data": CARRIER_ROBOT,
    "robot data": CARRIER_ROBOT,
    "embodied AI": CARRIER_ROBOT,
    "automated market maker": CARRIER_BASE + CARRIER_MARKET,
    'cat:cs.CR AND ti:"MEV"': CARRIER_BASE + CARRIER_MARKET,
}
EXCL = ["survey", "tutorial"]


def q_of(term):
    if term.startswith(("cat:", "ti:", "abs:", "all:")):
        return term
    return f'ti:"{term}"'


def fetch(q, days, tries=3):
    now = datetime.now(timezone.utc)
    since = (now - timedelta(days=days)).strftime("%Y%m%d%H%M")
    p = {"search_query": f"({q}) AND submittedDate:[{since} TO {now:%Y%m%d%H%M}]",
         "start": 0, "max_results": MAX_RESULTS,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    url = API + "?" + urllib.parse.urlencode(p)
    err = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return ET.fromstring(r.read()), None
        except Exception as ex:
            err = str(ex)
            time.sleep(10 * (k + 1))
    return None, err


seen = json.load(open("memory/arxiv-seen.json", encoding="utf-8"))
HITS = "memory/arxiv-hits.tsv"

# hits.tsv 行完整性：pass1 追加时上一行无换行，可能粘连两条记录
bad = []
for i, ln in enumerate(open(HITS, encoding="utf-8")):
    f = ln.rstrip("\n").split("\t")
    if i == 0:
        continue
    if len(f) != 3 or "\t" in "".join(f[2:]) is None:
        pass
    if len(f) != 3:
        bad.append((i + 1, ln.rstrip("\n")[:110]))
print("hits.tsv 行数=%d · 字段数≠3 的行=%d" % (
    sum(1 for _ in open(HITS, encoding="utf-8")) - 1, len(bad)))
for b in bad:
    print("  ! 行%d: %s" % b)

out, stats = [], {}
for term in FAILED:
    carrier = CARRIER_BY_TERM.get(term, CARRIER_BASE)
    root, err = fetch(q_of(term), DAYS)
    if root is None:
        stats[term] = ("FAIL", err)
        print("! %-34s FAIL %s" % (term, err))
        time.sleep(5)
        continue
    n_raw = n_new = n_seen = n_car = n_excl = 0
    node = root.find(OPENSEARCH)
    tot = int(node.text) if node is not None and node.text else 0
    for e in root.findall("a:entry", NS):
        n_raw += 1
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        blob = (title + " " + summ).lower()
        pub = e.find("a:published", NS).text[:10]
        if aid in seen:
            n_seen += 1
            continue
        if any(x in title.lower() for x in EXCL):
            n_excl += 1
            continue
        if not any(c in blob for c in carrier):
            n_car += 1
            continue
        n_new += 1
        rec = {"term": term, "terms": [term], "name": "",
               "title": title, "published": pub,
               "link": f"https://arxiv.org/abs/{aid}",
               "carrier": next(c for c in carrier if c in blob)}
        out.append(rec)
        seen[aid] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats[term] = ("OK", tot, n_raw, n_seen, n_car, n_excl, n_new)
    print("%-36s total=%-5d raw=%-3d seen=%-3d carrier=%-3d excl=%-2d new=%d"
          % (term, tot, n_raw, n_seen, n_car, n_excl, n_new))
    time.sleep(8)

out.sort(key=lambda c: c["published"], reverse=True)
json.dump(out, open("output/arxiv/out-pass2.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

if out:
    with open(HITS, "a", encoding="utf-8") as f:
        f.write("\n")
        for c in out:
            f.write("%s\t%s\t%s\n" % (datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                      c["link"].split("/abs/")[-1],
                                      (c["title"])[:60].replace("\t", " ")))
    json.dump(dict(list(seen.items())[-2000:]),
              open("memory/arxiv-seen.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

print("\n补扫幸存 %d 条" % len(out))
for c in out:
    print("  %s [%s] %s" % (c["published"], c["term"], c["title"][:88]))
