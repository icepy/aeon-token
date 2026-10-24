import time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

CARRIER = ["deployed", "deployment", "mainnet", "testnet", "protocol",
           "production", "open-source", "released", "blockchain", "network",
           "token", "incentive", "marketplace", "validator", "miner"]
NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"

now = datetime.now(timezone.utc)
win = "[%s TO %s]" % ((now - timedelta(days=7)).strftime("%Y%m%d%H%M"),
                      now.strftime("%Y%m%d%H%M"))

TERMS = ["proof-of-useful-work", "zero-knowledge", 'ti:"EIP-1559"', "automated market maker",
         "consensus protocol", "embodied AI", "robot data", "embodied data",
         "restaking", "light client", "verifiable inference", "proof of training",
         'cat:cs.CR AND ti:"MEV"', "data availability sampling", "liquid staking",
         "auditable training", "robot manipulation data", "proof of learning",
         "verifiable training", 'ti:"Robinhood Chain"']

seenids = set()
for term in TERMS:
    q = term if term.startswith(("cat:", "ti:", "abs:", "all:")) else 'ti:"%s"' % term
    p = {"search_query": "(%s) AND submittedDate:%s" % (q, win), "start": 0,
         "max_results": 100, "sortBy": "submittedDate", "sortOrder": "descending"}
    url = API + "?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            root = ET.fromstring(r.read())
    except Exception as ex:
        print("! %s %s" % (term, ex))
        time.sleep(3)
        continue
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        if aid in seenids:
            continue
        seenids.add(aid)
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        blob = (title + " " + summ).lower()
        ok = any(c in blob for c in CARRIER)
        print("%s %-10s %s | %s" % ("KEEP" if ok else "DROP", aid, term[:30], title[:80]))
    time.sleep(3)
