#!/usr/bin/env python3
"""defillama-radar 第 16 轮审计（2026-11-11）。只读，不改任何产物。"""
import json, sys, time, urllib.request
from datetime import datetime, timezone
from collections import Counter

API = "https://api.llama.fi/protocols"
CHAINS = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink",
          "Binance", "BSC", "Optimism", "OP Mainnet",
          "Hyperliquid L1", "Robinhood Chain"]
EXCL = {"CEX", "Chain", "Interface"}
TODAY = "2026-11-11"


def get(url, extra=None):
    h = {"User-Agent": "defillama-radar/dlv1-audit"}
    if extra:
        h.update(extra)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


def iso(ts):
    if ts is None:
        return "null"
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


print("=== 1. 常规取数 ===")
hit, hh = get(API)
print("条数 %d" % len(hit))
for k in ("etag", "last-modified", "age", "cf-cache-status", "cache-control"):
    print("  %s: %s" % (k, hh.get(k)))
time.sleep(2)
print("=== 2. 源站取数（?_cb= + no-cache）===")
miss, mh = get(API + "?_cb=%d" % int(time.time()),
               {"Cache-Control": "no-cache", "Pragma": "no-cache"})
print("条数 %d" % len(miss))
for k in ("etag", "last-modified", "age", "cf-cache-status", "cache-control"):
    print("  %s: %s" % (k, mh.get(k)))

hid = {str(p.get("id")): p for p in hit if isinstance(p, dict) and p.get("id")}
mid = {str(p.get("id")): p for p in miss if isinstance(p, dict) and p.get("id")}
print("only_hit=%d only_miss=%d 交集=%d" % (len(set(hid) - set(mid)),
                                            len(set(mid) - set(hid)),
                                            len(set(hid) & set(mid))))
if set(hid) - set(mid):
    print("  only_hit(前10):", sorted(set(hid) - set(mid))[:10])
if set(mid) - set(hid):
    print("  only_miss(前10):", sorted(set(mid) - set(hid))[:10])

print("=== 3. seen 反向差集 ===")
seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))
print("seen 条数 %d" % len(seen))
only_seen = sorted(set(seen) - set(hid))
only_raw = sorted(set(hid) - set(seen))
print("only_seen=%r only_raw=%r" % (only_seen, only_raw))
for i in only_seen:
    print("   seen-only %s: %r" % (i, seen[i]))

print("=== 4. 本轮新增 id（seen.first == %s）===" % TODAY)
new = [k for k, v in seen.items() if isinstance(v, dict) and v.get("first") == TODAY]
print("新增 %d 条" % len(new))
rows = []
for i in new:
    p = hid.get(i) or mid.get(i) or {}
    chains_all = p.get("chains") or []
    hit_ch = [c for c in chains_all if c in CHAINS]
    st = seen[i].get("notified")
    rows.append((i, p, hit_ch, st))

for i, p, hit_ch, st in sorted(rows, key=lambda r: int(r[0]) if r[0].isdigit() else -1):
    print("\n-- id=%s  notified=%r" % (i, st))
    print("   name=%r slug=%r" % (p.get("name"), p.get("slug")))
    print("   category=%r  parent=%r" % (p.get("category"), p.get("parentProtocol")))
    print("   chains=%r  hit=%r" % (p.get("chains"), hit_ch))
    print("   tvl=%r  chainTvls=%r" % (p.get("tvl"), p.get("chainTvls")))
    print("   listedAt=%r (%s)  url=%r" % (p.get("listedAt"), iso(p.get("listedAt")), p.get("url")))
    print("   misrepresentedTokens=%r wrongLiquidity=%r" % (p.get("misrepresentedTokens"), p.get("wrongLiquidity")))
    print("   address=%r  audits=%r  twitter=%r" % (p.get("address"), p.get("audits"), p.get("twitter")))
    print("   desc=%s" % " ".join((p.get("description") or "").split())[:260])
    # 桶归属复算 + 真边际
    b_parent = bool(p.get("parentProtocol"))
    b_excl = p.get("category") in EXCL
    b_empty = not (p.get("chains") or [])
    b_off = (not b_empty) and not hit_ch
    print("   桶: parent=%s category=%s 空链=%s 链不在白名单=%s" % (b_parent, b_excl, b_empty, b_off))
    if b_parent:
        print("   去 parent 后: category 挡=%s 空链挡=%s 链挡=%s -> 真边际=%s"
              % (b_excl, b_empty, b_off, not (b_excl or b_empty or b_off)))
    if b_excl:
        print("   去 category 后: 空链挡=%s 链挡=%s" % (b_empty, b_off))

print("\n=== 5. 两份快照对新增 15 条的字段比对 ===")
FIELDS = ["name", "category", "chains", "tvl", "parentProtocol", "listedAt",
          "url", "misrepresentedTokens", "wrongLiquidity", "slug", "description"]
for i, p, _, _ in rows:
    a, b = hid.get(i), mid.get(i)
    if a is None or b is None:
        print("  %s 只在一份快照里: hit=%s miss=%s" % (i, a is not None, b is not None))
        continue
    d = [f for f in FIELDS if a.get(f) != b.get(f)]
    print("  %s %s: %s" % (i, p.get("name"), "零字段差异" if not d else "差异字段=%r" % d))
    for f in d:
        print("      %s: hit=%r miss=%r" % (f, a.get(f), b.get(f)))

print("\n=== 6. id 连续性 ===")
nums = sorted(int(k) for k in set(hid) if k.isdigit())
print("数字 id %d 条 · min=%d max=%d" % (len(nums), nums[0], nums[-1]))
gaps = [(nums[j], nums[j + 1]) for j in range(len(nums) - 1) if nums[j + 1] - nums[j] > 1]
print("缺口数 %d" % len(gaps))
print("  最近 12 个缺口:", gaps[-12:] if gaps else "无")
nonnum = sorted(k for k in set(hid) if not k.isdigit())
print("非数字 id: %r" % nonnum)

print("\n=== 7. listedAt 跨度 / 同秒批量 ===")
lats = [(i, p.get("listedAt")) for i, p, _, _ in rows if p.get("listedAt")]
lats.sort(key=lambda x: x[1])
print("有 listedAt 的新增 %d 条" % len(lats))
if lats:
    print("  最早 %s (%s) id=%s" % (iso(lats[0][1]), lats[0][1], lats[0][0]))
    print("  最晚 %s (%s) id=%s" % (iso(lats[-1][1]), lats[-1][1], lats[-1][0]))
    span = (lats[-1][1] - lats[0][1]) / 3600.0
    print("  跨度 %.2fh" % span)
    gs = [(lats[j + 1][1] - lats[j][1], lats[j][0], lats[j + 1][0]) for j in range(len(lats) - 1)]
    if gs:
        gs.sort()
        print("  最小间隔 %ds (%s -> %s)" % gs[0])
cnt_all = Counter(p.get("listedAt") for p in hid.values()
                  if isinstance(p, dict) and p.get("listedAt"))
clusters = sorted([(t, n) for t, n in cnt_all.items() if n >= 3])
print("全量同秒>=3 条簇 %d 组；最近 5 组:" % len(clusters))
for t, n in clusters[-5:]:
    print("   %s (%s) n=%d" % (iso(t), t, n))
newlats = Counter(p.get("listedAt") for _, p, _, _ in rows if p.get("listedAt"))
print("新增内同秒>=3: %r" % [(iso(t), n) for t, n in newlats.items() if n >= 3])

print("\n=== 8. 全量空 chains 占比 ===")
empty = sum(1 for p in hid.values() if isinstance(p, dict) and not (p.get("chains") or []))
print("%d / %d = %.2f%%" % (empty, len(hid), 100.0 * empty / len(hid)))

print("\n=== 9. 链命中复算 ===")
ch = Counter()
for p in hid.values():
    if isinstance(p, dict):
        for c in (p.get("chains") or []):
            if c in CHAINS:
                ch[c] += 1
print(" · ".join("%s=%d" % (c, ch.get(c, 0)) for c in CHAINS))

print("\n=== 10. 过滤器总览（按新增 15 条）===")
print("parent 桶 %d · category 桶 %d · 空链 %d · 链不在白名单 %d"
      % (sum(1 for _, p, _, _ in rows if p.get("parentProtocol")),
         sum(1 for _, p, _, _ in rows if p.get("category") in EXCL),
         sum(1 for _, p, _, _ in rows if not (p.get("chains") or [])),
         sum(1 for _, p, _, _ in rows if (p.get("chains") or []) and not [c for c in p["chains"] if c in CHAINS])))
