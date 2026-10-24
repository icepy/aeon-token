"""Validate the minimal precise carrier fix: per-domain carrier, no ZK loosening.

Expected: +20 robotics (all genuine), +2 MEV, no ZK noise.
"""
import time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"

now = datetime.now(timezone.utc)
win = "[%s TO %s]" % ((now - timedelta(days=90)).strftime("%Y%m%d%H%M"),
                      now.strftime("%Y%m%d%H%M"))

BASE = ["deployed", "deployment", "mainnet", "testnet", "protocol",
        "production", "open-source", "released", "blockchain", "network",
        "token", "incentive", "marketplace", "validator", "miner"]
ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
         "simulator", "dataset", "datasets", "real-world", "embodied",
         "sensor", "egocentric", "demonstration", "vla"]
MARKET = ["arbitrage", "swap", "liquidity", "order flow", "searcher"]

TERMS = [
    ("proof-of-useful-work", BASE), ("verifiable inference", BASE),
    ("light client", BASE), ("proof of training", BASE),
    ("proof of learning", BASE), ("verifiable training", BASE),
    ("auditable training", BASE), ("data availability sampling", BASE),
    ("restaking", BASE), ("automated market maker", BASE + MARKET),
    ("consensus protocol", BASE), ("cat:cs.CR AND ti:\"MEV\"", BASE + MARKET),
    ("liquid staking", BASE), ("embodied data", ROBOT),
    ("robot manipulation data", ROBOT), ("robot data", ROBOT),
    ("embodied AI", ROBOT), ("zero-knowledge", BASE),
    ("ti:\"EIP-1559\"", BASE), ("ti:\"Robinhood Chain\"", BASE),
]
EXCL = ["survey", "tutorial"]

t_raw = t_old = t_new = 0
for term, car in TERMS:
    q = term if term.startswith(("cat:", "ti:")) else 'ti:"%s"' % term
    p = {"search_query": "(%s) AND submittedDate:%s" % (q, win),
         "start": 0, "max_results": 100,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root = ET.fromstring(urllib.request.urlopen(
        API + "?" + urllib.parse.urlencode(p), timeout=25).read())
    old = new = 0
    for e in root.findall("a:entry", NS):
        ti = " ".join(e.find("a:title", NS).text.split())
        blob = (ti + " " + " ".join(e.find("a:summary", NS).text.split())).lower()
        if any(x in ti.lower() for x in EXCL):
            continue
        old += any(c in blob for c in BASE)
        new += any(c in blob for c in car)
    t_raw += len(root.findall("a:entry", NS))
    t_old += old
    t_new += new
    if new != old:
        print("%-26s raw=%3d old=%2d new=%2d  %+d"
              % (term[:26], len(root.findall("a:entry", NS)), old, new, new - old))
    time.sleep(3)

print("\nTOTAL raw=%d | current=%d | per-domain=%d (+%d)"
      % (t_raw, t_old, t_new, t_new - t_old))
