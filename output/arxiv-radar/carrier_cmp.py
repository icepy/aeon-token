"""Compare the skill's current carrier list against a domain-aware one.

Diagnostic only -- does not write memory/arxiv-seen.json.
"""
import json, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"

now = datetime.now(timezone.utc)
DAYS = 90
win = "[%s TO %s]" % ((now - timedelta(days=DAYS)).strftime("%Y%m%d%H%M"),
                      now.strftime("%Y%m%d%H%M"))

OLD = ["deployed", "deployment", "mainnet", "testnet", "protocol",
       "production", "open-source", "released", "blockchain", "network",
       "token", "incentive", "marketplace", "validator", "miner"]

CHAIN = OLD + ["smart contract", "ledger", "defi", "on-chain", "exchange",
               "liquidity", "arbitrage", "gas fee", "eip-"]
ROBOT = ["robotic", "robot", "manipulation", "teleoperation", "simulation",
         "simulator", "dataset", "datasets", "real-world", "embodied",
         "sensor", "egocentric", "demonstration", "vla", "benchmark"]
ZK = ["proof", "protocol", "implementation", "deployed", "circuit", "compiler",
      "library", "backend", "snark", "stark", "evm", "blockchain", "prover"]

TERMS = [
    ("proof-of-useful-work", CHAIN), ("verifiable inference", ZK),
    ("light client", CHAIN), ("proof of training", ZK),
    ("proof of learning", ZK), ("verifiable training", ZK),
    ("auditable training", ZK), ("data availability sampling", CHAIN),
    ("restaking", CHAIN), ("automated market maker", CHAIN),
    ("consensus protocol", CHAIN), ("cat:cs.CR AND ti:\"MEV\"", CHAIN),
    ("liquid staking", CHAIN), ("embodied data", ROBOT),
    ("robot manipulation data", ROBOT), ("robot data", ROBOT),
    ("embodied AI", ROBOT), ("zero-knowledge", ZK),
    ("ti:\"EIP-1559\"", CHAIN), ("ti:\"Robinhood Chain\"", CHAIN),
]
EXCL = ["survey", "tutorial"]

t_raw = t_old = t_new = 0
rows = []
for term, car in TERMS:
    q = term if term.startswith(("cat:", "ti:", "abs:", "all:")) else 'ti:"%s"' % term
    p = {"search_query": "(%s) AND submittedDate:%s" % (q, win),
         "start": 0, "max_results": 100,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    try:
        url = API + "?" + urllib.parse.urlencode(p)
        root = ET.fromstring(urllib.request.urlopen(url, timeout=25).read())
    except Exception as ex:
        print("! %s: %s" % (term, ex))
        time.sleep(3)
        continue
    entries = root.findall("a:entry", NS)
    old = new = 0
    for e in entries:
        ti = " ".join(e.find("a:title", NS).text.split())
        blob = (ti + " " + " ".join(e.find("a:summary", NS).text.split())).lower()
        if any(x in ti.lower() for x in EXCL):
            continue
        if any(c in blob for c in OLD):
            old += 1
        if any(c in blob for c in car):
            new += 1
    t_raw += len(entries)
    t_old += old
    t_new += new
    rows.append((term, len(entries), old, new))
    time.sleep(3)

print("%-28s %5s %5s %5s %s" % ("term", "raw", "old", "new", "delta"))
for term, r, o, n in rows:
    print("%-28s %5s %5s %5s %s" % (term[:28], r, o, n,
                                    ("+%d" % (n - o)) if n != o else ""))
print()
print("TOTAL raw=%d | current carrier survives=%d | domain-aware survives=%d (+%d)"
      % (t_raw, t_old, t_new, t_new - t_old))
