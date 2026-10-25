#!/usr/bin/env python3
"""Measure what the reverted CARRIER_MARKET fix costs: PR#8 words vs current 5 words."""
import json, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "https://export.arxiv.org/api/query"
OLD = ["arbitrage", "swap", "liquidity", "order flow", "searcher"]
NEW = OLD + ["ledger", "ledgers", "block creator", "block builder",
             "block proposer", "transaction ordering", "on-chain", "state transition"]
BASE = ["deployed", "deployment", "mainnet", "testnet", "protocol",
        "production", "open-source", "released", "blockchain", "network",
        "token", "incentive", "marketplace", "validator", "miner"]
QUERIES = ['automated market maker', 'cat:cs.CR AND ti:"MEV"',
           'consensus protocol', 'restaking']
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 90

now = datetime.now(timezone.utc)
win = f"[{(now - timedelta(days=DAYS)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"
seen = json.load(open("memory/arxiv-seen.json", encoding="utf-8")) if __import__("os").path.exists("memory/arxiv-seen.json") else {}

rows = {}
for term in QUERIES:
    p = {"search_query": f'({term}) AND submittedDate:{win}', "start": 0,
         "max_results": 100, "sortBy": "submittedDate", "sortOrder": "descending"}
    try:
        with urllib.request.urlopen(API + "?" + urllib.parse.urlencode(p), timeout=20) as r:
            root = ET.fromstring(r.read())
    except Exception as ex:
        print(f"! {term}: {ex}"); time.sleep(3); continue
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        blob = (title + " " + summ).lower()
        m_old = any(c in blob for c in BASE + OLD)
        m_new = any(c in blob for c in BASE + NEW)
        if m_new and not m_old:
            rows[aid] = (aid, term, title, aid in seen)
    time.sleep(3)

print(f"窗口 {DAYS}d | 被 PR#8 carrier 救回、当前版本会丢的论文: {len(rows)}")
for aid, term, title, s in sorted(rows.values()):
    print(f"  {aid} [{'seen' if s else 'NEW'}] ({term}) {title[:88]}")
