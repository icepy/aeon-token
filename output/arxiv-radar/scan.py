import json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NAMES_FILE = "memory/universe-names.txt"
NAMES_MODE = os.environ.get("NAMES") == "1"

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

CARRIER = ["deployed", "deployment", "mainnet", "testnet", "protocol",
           "production", "open-source", "released", "blockchain", "network",
           "token", "incentive", "marketplace", "validator", "miner"]
EXCL = ["survey", "tutorial"]
STOP = set("""a an the on of in for with from and or to at by as is are was were
towards toward via using based scalable efficient large language model models
learning deep neural network networks system systems new novel study analysis
empirical measurement framework approach method methods data theory practice
case real world beyond not all end how what why when where which that this""".split())

DAYS = int(os.environ.get("DAYS") or 7)
DRY = os.environ.get("DRY") == "1"
SEEN = "memory/arxiv-seen.json"
API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}

now = datetime.now(timezone.utc)
win = "[%s TO %s]" % ((now - timedelta(days=DAYS)).strftime("%Y%m%d%H%M"),
                      now.strftime("%Y%m%d%H%M"))

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
        if not isinstance(seen, dict):
            raise ValueError("not a dict")
    except Exception as ex:
        print("! seen load failed (%s): treating as empty" % ex, file=sys.stderr)
        seen = {}

def guess_name(title, summ, known):
    for n in known:
        if re.search(r"\b" + re.escape(n) + r"\b", title + " " + summ, re.I):
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

for term in TERMS:
    if term.startswith(("cat:", "ti:", "abs:", "all:")):
        q = term
    elif NAMES_MODE:
        q = 'ti:"%s" AND (cat:cs.CR OR cat:cs.CE OR cat:cs.GT OR cat:cs.DC OR cat:q-fin.CP OR cat:q-fin.GN)' % term
    else:
        q = 'ti:"%s"' % term

    p = {"search_query": "(%s) AND submittedDate:%s" % (q, win),
         "start": 0, "max_results": 100,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    url = API + "?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            root = ET.fromstring(r.read())
    except Exception as ex:
        print("! %s: %s" % (term, ex), file=sys.stderr)
        drop["fail"] += 1
        time.sleep(3)
        continue

    n_term = 0
    for e in root.findall("a:entry", NS):
        raw += 1
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        blob = (title + " " + summ).lower()
        pub = e.find("a:published", NS).text[:10]
        cats = [c.get("term") for c in e.findall("a:category", NS)]
        auths = [a.find("a:name", NS).text for a in e.findall("a:author", NS)]
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
            continue
        if not any(c in blob for c in CARRIER):
            drop["carrier"] += 1
            continue
        rec = {"term": term, "terms": [term], "name": guess_name(title, summ, known),
               "title": title, "published": pub,
               "link": "https://arxiv.org/abs/" + aid,
               "carrier": next(c for c in CARRIER if c in blob),
               "cats": cats, "authors": auths[:3], "n_authors": len(auths),
               "summary": summ[:400]}
        out.append(rec)
        hit_ids[aid] = rec
        n_term += 1
    per_term[term] = n_term
    time.sleep(3)

out.sort(key=lambda c: c["published"], reverse=True)
print("扫 %d 词 | 原始 %d | 幸存 %d | 丢弃 seen=%d excl=%d carrier=%d fail=%d"
      % (len(TERMS), raw, len(out), drop["seen"], drop["excl"], drop["carrier"], drop["fail"]),
      file=sys.stderr)
print("窗口内最新收录日期: %s  ← 比今天早 3 天以上即索引滞后，不是零命中" % (newest or "(无)"),
      file=sys.stderr)
print("词表命中: " + " · ".join("%s=%d" % (k, v) for k, v in
      sorted(per_term.items(), key=lambda x: -x[1]) if v), file=sys.stderr)
print("零命中: " + " · ".join(k for k, v in per_term.items() if not v), file=sys.stderr)
print("", file=sys.stderr)
for c in out:
    print("  %s [%s] %s" % (c["published"], "+".join(c["terms"]), c["title"][:95]), file=sys.stderr)

if not DRY and out:
    merged = dict(list(seen.items()) + list((k, now.strftime("%Y-%m-%d")) for k in hit_ids))
    json.dump(dict(list(merged.items())[-2000:]),
              open(SEEN, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

print(json.dumps(out, ensure_ascii=False, indent=1))
