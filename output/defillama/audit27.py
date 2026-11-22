#!/usr/bin/env python3
"""第 27 轮审计：只读。取源站缓存穿透份，拆桶 + 结构读数。"""
import json
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone

CH = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink", "Binance", "BSC",
      "Optimism", "OP Mainnet", "Hyperliquid L1", "Robinhood Chain"]
EXCL = {"CEX", "Chain", "Interface"}
API = "https://api.llama.fi/protocols"
WANT = ["9486", "9487", "9488"]


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


bus, hb = get(API, {"User-Agent": "defillama-radar/audit27"})
time.sleep(1)
cb, hc = get(API + "?_cb=%d" % int(time.time()),
             {"User-Agent": "defillama-radar/audit27",
              "Cache-Control": "no-cache", "Pragma": "no-cache"})

print("== CF ==")
for tag, n, h in (("bus", len(bus), hb), ("cb", len(cb), hc)):
    print("%s n=%d lm=%s cf=%s age=%s etag=%s"
          % (tag, n, h.get("last-modified"), h.get("cf-cache-status"),
             h.get("age"), (h.get("etag") or "")[:26]))

byid_b = {str(p.get("id")): p for p in bus if isinstance(p, dict)}
byid_c = {str(p.get("id")): p for p in cb if isinstance(p, dict)}
sb, sc = set(byid_b), set(byid_c)
print("only_bus=%s only_cb=%s equal=%s" % (sorted(sb - sc), sorted(sc - sb), sb == sc))
diff_tvl = [k for k in sb & sc if byid_b[k].get("tvl") != byid_c[k].get("tvl")]
print("tvl 逐条差异 %d 条" % len(diff_tvl))
diff_parent = [k for k in sb & sc
               if bool(byid_b[k].get("parentProtocol")) != bool(byid_c[k].get("parentProtocol"))]
print("parent 逐条翻转 %d 条 %s" % (len(diff_parent), diff_parent[:8]))

seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))

print("\n== 新增 3 条逐条 ==")
for i in WANT:
    p = byid_c.get(i) or byid_b.get(i) or {}
    ch_all = p.get("chains") or []
    hit = [c for c in ch_all if c in CH]
    ct = p.get("chainTvls") or {}
    ct_small = {k: v for k, v in ct.items()
                if not any(k.endswith(s) for s in ("-borrowed", "-staking", "-pool2"))}
    print("%s | %s | cat=%s | chains=%s | hit=%s" %
          (i, p.get("name"), p.get("category"), ch_all, hit))
    print("     tvl=%s | chainTvls=%s | parent=%s | mod=%s | listedAt=%s"
          % (p.get("tvl"), ct_small, p.get("parentProtocol"),
             p.get("module"), p.get("listedAt")))
    print("     url=%s | misrep=%s wrongLiq=%s" %
          (p.get("url"), p.get("misrepresentedTokens"), p.get("wrongLiquidity")))
    print("     desc=%s" % " ".join((p.get("description") or "").split())[:200])

print("\n== 桶拆（去第一个命中桶后是否仍被挡）==")
pm = 0
pcount = sum(1 for i in WANT if (byid_c.get(i) or {}).get("parentProtocol"))
for i in WANT:
    p = byid_c.get(i) or {}
    ch_all = p.get("chains") or []
    hit = [c for c in ch_all if c in CH]
    hp, hc_, hch = bool(p.get("parentProtocol")), p.get("category") in EXCL, not hit
    rest = []
    if hp:
        rest.append("parent")
    if hc_:
        rest.append("EXCL")
    if hch:
        rest.append("空链/链外")
    only = "—"
    if hp and not hc_ and not hch:
        only = "**parent 唯一**"
        pm += 1
    elif hc_ and not hp and not hch:
        only = "**EXCL 唯一**"
    elif hch and not hp and not hc_:
        only = "**空链唯一**"
    print("%s %s → 桶: %s | %s" % (i, p.get("name"), rest, only))
print("parent 真边际: %d / %d" % (pm, pcount))

print("\n== id 连续性 ==")
num = sorted(int(k) for k in sc if k.isdigit())
print("max_id=%d | 数字 id %d 条 | 非数字 %s" %
      (max(num), len(num), sorted(k for k in sc if not k.isdigit())))
print("窗口 9475-9495:", [x for x in num if 9475 <= x <= 9495])
gaps = [x for x in range(9000, max(num)) if x not in set(num)]
print("≥9000 缺口(%d): %s" % (len(gaps), gaps[-12:]))

print("\n== 差集方向 ==")
only_raw = sorted(sc - set(seen))
only_seen = sorted(set(seen) - sc)
print("only_raw=%s（共 %d）" % (only_raw, len(only_raw)))
print("only_seen=%s" % only_seen)

print("\n== listedAt 跨度 / 同秒簇 ==")
las = []
for i in WANT:
    p = byid_c.get(i) or {}
    la = p.get("listedAt")
    if la:
        las.append(la)
        print("  %s %s → %s" % (i, p.get("name"),
                                datetime.fromtimestamp(la, timezone.utc).isoformat()))
if las:
    print("  跨度 %.2f h | 相邻间隔 %s" %
          ((max(las) - min(las)) / 3600.0,
           [int(b - a) for a, b in zip(sorted(las), sorted(las)[1:])]))
c = Counter(p.get("listedAt") for p in cb if isinstance(p, dict) and p.get("listedAt"))
big = {k: v for k, v in c.items() if v >= 3}
print("同秒 ≥3 簇 %d 组" % len(big))

print("\n== 结构读数 ==")
n = len(cb)
empty = [p for p in cb if isinstance(p, dict) and not (p.get("chains") or []) and p.get("id")]
print("chains=[] %d/%d = %.2f%%" % (len(empty), n, 100.0 * len(empty) / n))
print("  其中 tvl 非空: %d | 带 parent: %d | module=dummy: %d"
      % (sum(1 for p in empty if p.get("tvl")),
         sum(1 for p in empty if p.get("parentProtocol")),
         sum(1 for p in empty if p.get("module") == "dummy.js")))
print("listedAt 缺失 %d | tvl=None %d"
      % (sum(1 for p in cb if isinstance(p, dict) and not p.get("listedAt")),
         sum(1 for p in cb if isinstance(p, dict) and p.get("tvl") is None)))
tot = sum(p.get("tvl") or 0 for p in cb if isinstance(p, dict))
print("全量 TVL $%.2fB" % (tot / 1e9))
now = time.time()
d7 = sum(1 for p in cb if isinstance(p, dict) and p.get("listedAt")
         and now - p["listedAt"] <= 7 * 86400)
d30 = sum(1 for p in cb if isinstance(p, dict) and p.get("listedAt")
          and now - p["listedAt"] <= 30 * 86400)
print("近 7d 登记 %d | 近 30d %d" % (d7, d30))
print("UTC 整日 listedAt %d 条" %
      sum(1 for p in cb if isinstance(p, dict) and p.get("listedAt")
          and p["listedAt"] % 86400 == 0))

print("\n== 链命中 vs 白名单 ==")
hits = {c: 0 for c in CH}
for p in cb:
    if isinstance(p, dict):
        for ch in (p.get("chains") or []):
            if ch in hits:
                hits[ch] += 1
print(hits)

print("\n== category 分布（新增 3 条）==")
print(Counter((byid_c.get(i) or {}).get("category") for i in WANT))
