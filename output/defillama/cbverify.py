#!/usr/bin/env python3
"""cache-busted 复取，与 scan.py 那份 payload 比对 id 集合。只读，不写 memory/。"""
import json
import sys
import time
import urllib.request

API = "https://api.llama.fi/protocols"


def get(url, hdrs):
    req = urllib.request.Request(url, headers=hdrs)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


bus, hb = get(API, {"User-Agent": "defillama-radar/cb"})
time.sleep(1)
cb, hc = get(API + "?_cb=%d" % int(time.time()),
             {"User-Agent": "defillama-radar/cb",
              "Cache-Control": "no-cache", "Pragma": "no-cache"})

ids_b = {str(p.get("id")) for p in bus if isinstance(p, dict) and p.get("id")}
ids_c = {str(p.get("id")) for p in cb if isinstance(p, dict) and p.get("id")}

print("bus  n=%d lm=%s cf=%s age=%s etag=%s"
      % (len(bus), hb.get("last-modified"), hb.get("cf-cache-status"),
         hb.get("age"), (hb.get("etag") or "")[:24]))
print("cb   n=%d lm=%s cf=%s age=%s etag=%s"
      % (len(cb), hc.get("last-modified"), hc.get("cf-cache-status"),
         hc.get("age"), (hc.get("etag") or "")[:24]))
print("only_busted=%s" % sorted(ids_c - ids_b))
print("only_bus=%s" % sorted(ids_b - ids_c))
print("id_sets_equal=%s" % (ids_b == ids_c))

# 与 seen 比：源站上所有 seen 里没有的 id
seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))
new_cb = sorted(ids_c - set(seen), key=lambda x: int(x) if x.isdigit() else 0)
print("源站相对 seen 的新 id (%d): %s" % (len(new_cb), new_cb))
maxid = max(int(k) for k in seen if k.isdigit())
print("seen 历史最大 id=%d" % maxid)
for pid in new_cb:
    p = next((x for x in cb if str(x.get("id")) == pid), {})
    print("  %s · %s · chains=%s · parent=%s · tvl=%s · listedAt=%s · cat=%s · url=%s"
          % (pid, p.get("name"), p.get("chains"), bool(p.get("parentProtocol")),
             p.get("tvl"), p.get("listedAt"), p.get("category"), p.get("url")))
