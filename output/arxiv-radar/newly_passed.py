"""Precision check: list papers that ONLY the domain-aware carrier lets through."""
import time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"

now = datetime.now(timezone.utc)
win = "[%s TO %s]" % ((now - timedelta(days=90)).strftime("%Y%m%d%H%M"),
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

TERMS = [("proof of training", ZK), ("auditable training", ZK),
         ("cat:cs.CR AND ti:\"MEV\"", CHAIN), ("embodied data", ROBOT),
         ("robot manipulation data", ROBOT), ("robot data", ROBOT),
         ("embodied AI", ROBOT), ("zero-knowledge", ZK)]
EXCL = ["survey", "tutorial"]

seen_ids = set()
for term, car in TERMS:
    q = term if term.startswith(("cat:", "ti:")) else 'ti:"%s"' % term
    p = {"search_query": "(%s) AND submittedDate:%s" % (q, win),
         "start": 0, "max_results": 100,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root = ET.fromstring(urllib.request.urlopen(
        API + "?" + urllib.parse.urlencode(p), timeout=25).read())
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        if aid in seen_ids:
            continue
        ti = " ".join(e.find("a:title", NS).text.split())
        blob = (ti + " " + " ".join(e.find("a:summary", NS).text.split())).lower()
        if any(x in ti.lower() for x in EXCL):
            continue
        if any(c in blob for c in OLD):
            continue
        h = [c for c in car if c in blob]
        if h:
            seen_ids.add(aid)
            print("%s  %-9s | %s\n     via: %s" % (aid, term[:9], ti[:88], ",".join(h[:4])))
    time.sleep(3)
