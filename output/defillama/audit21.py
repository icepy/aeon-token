#!/usr/bin/env python3
"""第 12 轮 CF 校验：常规取数与 ?_cb= 源站取数比对，并导出本轮 6 条新增的完整字段。"""
import json
import sys
import urllib.request
from datetime import datetime, timezone

API = "https://api.llama.fi/protocols"
TODAY = "2026-11-07"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "defillama-radar/dl-v1"})
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read()
        h = {k.lower(): v for k, v in r.headers.items()}
        return json.loads(body.decode("utf-8")), h, len(body)


def brief(h):
    return {
        "etag": h.get("etag"),
        "last-modified": h.get("last-modified"),
        "age": h.get("age"),
        "cf-cache-status": h.get("cf-cache-status"),
    }


cb = int(datetime.now(timezone.utc).timestamp())
hit, hh, hb = get(API)
miss, mh, mb = get(API + "?_cb=%d" % cb)
print("HIT ", brief(hh), "bytes", hb, "n", len(hit))
print("MISS", brief(mh), "bytes", mb, "n", len(miss))

ih = {str(p.get("id")) for p in hit if isinstance(p, dict) and p.get("id")}
im = {str(p.get("id")) for p in miss if isinstance(p, dict) and p.get("id")}
print("only_hit ", sorted(ih - im))
print("only_miss", sorted(im - ih))

seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))
new = sorted([k for k, v in seen.items() if isinstance(v, dict) and v.get("first") == TODAY],
             key=lambda x: int(x) if x.isdigit() else 0)
print("new ids", new)

mh_by = {str(p.get("id")): p for p in miss if isinstance(p, dict)}
hh_by = {str(p.get("id")): p for p in hit if isinstance(p, dict)}
for pid in new:
    row = {}
    for tag, src in (("hit", hh_by), ("cb", mh_by)):
        p = src.get(pid)
        if not p:
            row[tag] = None
            continue
        row[tag] = {k: p.get(k) for k in
                    ("name", "slug", "chains", "category", "parentProtocol", "tvl",
                     "listedAt", "url", "address", "chainTvls", "staking", "mcap",
                     "description")}
    print("\n=== id", pid, "seen:", seen.get(pid))
    for tag in ("hit", "cb"):
        r = row[tag]
        if not r:
            print(" ", tag, "MISSING")
            continue
        r = dict(r)
        r["description"] = (r.get("description") or "")[:160]
        print(" ", tag, json.dumps(r, ensure_ascii=False))
    if row["hit"] and row["cb"]:
        diff = [k for k in row["hit"] if row["hit"][k] != row["cb"][k]]
        print("  field-diff:", diff or "none")

# listedAt 分布与同秒批量指纹
lst = sorted(int(p["listedAt"]) for p in miss
             if isinstance(p, dict) and p.get("id") in new and p.get("listedAt"))
if lst:
    print("\nlistedAt n=%d span=%.2fh" % (len(lst), (lst[-1] - lst[0]) / 3600))
    print("  from", datetime.fromtimestamp(lst[0], timezone.utc).isoformat(),
          "to", datetime.fromtimestamp(lst[-1], timezone.utc).isoformat())
    print("  min gap(s):", min((b - a) for a, b in zip(lst, lst[1:])) if len(lst) > 1 else "-")

maxid = max(int(i) for i in im if i.isdigit())
print("\nmax id in payload:", maxid)
print("max id in seen  :", max(int(k) for k in seen if k.isdigit()))
print("only_seen:", sorted({k for k in seen if k not in im and k.isdigit()},
                           key=lambda x: int(x))[:20])
print("only_raw:", sorted(im - set(seen), key=lambda x: int(x) if x.isdigit() else 0))
