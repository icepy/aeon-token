"""Refined domain-aware carrier: ZK list WITHOUT the bare word 'proof'."""
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
ZK = ["blockchain", "smart contract", "evm", "snark", "stark", "circuit",
      "prover", "compiler", "cryptographic library", "on-chain"]

for term in ["zero-knowledge", "proof of training", "auditable training",
             "verifiable training", "verifiable inference"]:
    q = 'ti:"%s"' % term
    p = {"search_query": "(%s) AND submittedDate:%s" % (q, win),
         "start": 0, "max_results": 100,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    root = ET.fromstring(urllib.request.urlopen(
        API + "?" + urllib.parse.urlencode(p), timeout=25).read())
    old = newp = 0
    extra = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        ti = " ".join(e.find("a:title", NS).text.split())
        blob = (ti + " " + " ".join(e.find("a:summary", NS).text.split())).lower()
        if any(x in ti.lower() for x in ["survey", "tutorial"]):
            continue
        o = any(c in blob for c in OLD)
        n = any(c in blob for c in ZK)
        old += o
        newp += n
        if n and not o:
            extra.append((aid, ti[:70]))
    print("%-22s raw=%3d old=%2d zk-only=%2d" % (term, len(root.findall("a:entry", NS)), old, newp))
    for a, t in extra:
        print("      + %s %s" % (a, t))
    time.sleep(3)
