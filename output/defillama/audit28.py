#!/usr/bin/env python3
"""第 33 轮（11-28）审计：CF 双取校验 + 新增 5 条逐条拆桶 + 结构读数。只读。"""
import json
import time
import urllib.request
from datetime import datetime, timezone

API = "https://api.llama.fi/protocols"
NEW = ["9524", "9525", "9526", "9527", "9528"]


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


bus, hb = get(API, {"User-Agent": "defillama-radar/audit33"})
time.sleep(1)
cb, hc = get(API + "?_cb=%d" % int(time.time()),
             {"User-Agent": "defillama-radar/audit33",
              "Cache-Control": "no-cache", "Pragma": "no-cache"})

def ids(rows):
    return {str(p.get("id")) for p in rows if isinstance(p, dict) and p.get("id")}

ib, ic = ids(bus), ids(cb)
print("bus n=%d lm=%s cf=%s age=%s etag=%s"
      % (len(bus), hb.get("last-modified"), hb.get("cf-cache-status"),
         hb.get("age"), (hb.get("etag") or "")[:24]))
print("cb  n=%d lm=%s cf=%s age=%s etag=%s"
      % (len(cb), hc.get("last-modified"), hc.get("cf-cache-status"),
         hc.get("age"), (hc.get("etag") or "")[:24]))
print("only_bus=%s only_cb=%s equal=%s" % (sorted(ib - ic), sorted(ic - ib), ib == ic))

# 逐条字段差异（只对同 id 比 key 字段）
bm = {str(p.get("id")): p for p in bus if isinstance(p, dict) and p.get("id")}
cm = {str(p.get("id")): p for p in cb if isinstance(p, dict) and p.get("id")}
diff = 0
for k in ib & ic:
    a, b = bm[k], cm[k]
    for f in ("parentProtocol", "chains", "category", "tvl"):
        if a.get(f) != b.get(f):
            diff += 1
            print("  DIFF %s %s: %r -> %r" % (k, f, a.get(f), b.get(f)))
print("字段差异条数=%d" % diff)

print("\n== 新增 5 条（来自 cb 源站快照）==")
EXCL = {"CEX", "Chain", "Interface"}
CHAINS = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
          "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"]
for pid in NEW:
    p = cm.get(pid)
    if not p:
        print("%s 不在 cb 快照" % pid)
        continue
    hit = [c for c in (p.get("chains") or []) if c in CHAINS]
    print("%s · %s" % (pid, p.get("name")))
    print("   chains=%s hit=%s parent=%s cat=%s tvl=%s listedAt=%s(%s)"
          % (p.get("chains"), hit, p.get("parentProtocol"), p.get("category"),
             p.get("tvl"), p.get("listedAt"),
             datetime.fromtimestamp(p["listedAt"], timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
             if p.get("listedAt") else "-"))
    print("   url=%s audits=%s gecko=%s mcap=%s misrep=%s wrongLiq=%s"
          % (p.get("url"), p.get("audits"), p.get("gecko_id"), p.get("mcap"),
             p.get("misrepresentedTokens"), p.get("wrongLiquidity")))
    print("   desc=%s" % " ".join((p.get("description") or "").split())[:220])
    ct = p.get("chainTvls") or {}
    if ct:
        top = sorted(((k, v) for k, v in ct.items() if isinstance(v, (int, float))),
                     key=lambda x: -x[1])[:5]
        print("   chainTvls top=%s" % [(k, round(v, 1)) for k, v in top])
    print("   address=%s" % p.get("address"))

print("\n== 结构读数 ==")
listed = [p for p in cb if isinstance(p, dict) and p.get("listedAt")]
print("全量=%d 有listedAt=%d 缺=%d" % (len(cb), len(listed), len(cb) - len(listed)))
empty = [p for p in cb if isinstance(p, dict) and not (p.get("chains") or [])]
print("空chains=%d 其中listedAt缺=%d" % (len(empty), sum(1 for p in empty if not p.get("listedAt"))))
print("tvl=None=%d 空chains且tvl=None=%d"
      % (sum(1 for p in cb if isinstance(p, dict) and p.get("tvl") is None),
         sum(1 for p in empty if p.get("tvl") is None)))

# 同秒批量
from collections import Counter
sec = Counter(p["listedAt"] for p in listed)
clusters = [(s, n) for s, n in sec.items() if n >= 3]
print("同秒≥3簇=%d" % len(clusters))
for s, n in sorted(clusters)[-3:]:
    print("   %s n=%d" % (datetime.fromtimestamp(s, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), n))

# id 结构
numids = [int(str(p.get("id"))) for p in cb if isinstance(p, dict) and str(p.get("id") or "").isdigit()]
nonnum = [str(p.get("id")) for p in cb if isinstance(p, dict) and p.get("id") is not None
          and not str(p.get("id")).isdigit()]
print("max_id=%d 数字id=%d 非数字id=%s" % (max(numids), len(numids), nonnum))
mx = max(numids)
gaps = [i for i in range(9000, mx + 1) if i not in set(numids)]
print("≥9000 缺口(%d): %s" % (len(gaps), gaps))

# 未来 listedAt
now = int(time.time())
fut = [p.get("id") for p in listed if p["listedAt"] > now]
print("未来listedAt=%d %s" % (len(fut), fut[:5]))

# 滚动秒窗
buckets = [0] * 12
for p in listed:
    age = now - p["listedAt"]
    if 0 <= age < 12 * 2592000:
        buckets[age // 2592000] += 1
print("12 桶(30d) = %s" % buckets)
print("7d=%d 30d=%d 90d=%d" % (sum(buckets[:1]), sum(buckets[:1]) + buckets[1],
                               sum(buckets[:3])))

# 新条目 vs listedAt 窗口
print("\n== 新增 5 条 listedAt 跨度 ==")
ts = sorted((cm[i]["listedAt"], i) for i in NEW if i in cm and cm[i].get("listedAt"))
if ts:
    print("最早 %s(%s) → 最晚 %s(%s) 跨度 %.2fh"
          % (datetime.fromtimestamp(ts[0][0], timezone.utc).strftime("%m-%dT%H:%M:%SZ"),
             ts[0][1],
             datetime.fromtimestamp(ts[-1][0], timezone.utc).strftime("%m-%dT%H:%M:%SZ"),
             ts[-1][1], (ts[-1][0] - ts[0][0]) / 3600.0))
    for i in range(1, len(ts)):
        print("   %s(%s) → %s(%s) 间隔 %ds"
              % (datetime.fromtimestamp(ts[i - 1][0], timezone.utc).strftime("%H:%M:%S"), ts[i - 1][1],
                 datetime.fromtimestamp(ts[i][0], timezone.utc).strftime("%H:%M:%S"), ts[i][1],
                 ts[i][0] - ts[i - 1][0]))

# 清单命中
names = [l.strip() for l in open("memory/defillama-names.txt", encoding="utf-8")
         if l.strip() and not l.startswith("#")]
print("\n清单词=%s" % names)
for p in cb:
    if not isinstance(p, dict):
        continue
    nm = (p.get("name") or "").lower()
    if any(k.lower() in nm for k in names):
        print("   清单内: %s · %s · %s · tvl=%s · first_in_seen=%s"
              % (p.get("id"), p.get("name"), p.get("category"), p.get("tvl"),
                 (json.load(open("memory/defillama-seen.json")).get(str(p.get("id"))) or {}).get("first")))
