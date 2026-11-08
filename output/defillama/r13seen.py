import json
import urllib.request
import datetime

seen = json.load(open("memory/defillama-seen.json", encoding="utf-8"))
print("seen keys", len(seen))
for k in ["<5471>", "5471"]:
    print(repr(k), "in seen:", k in seen, seen.get(k))
req = urllib.request.Request("https://api.llama.fi/protocols?_cb=ot13",
                             headers={"User-Agent": "defillama-radar/dl-v1"})
raw = json.load(urllib.request.urlopen(req, timeout=60))
for p in raw:
    if str(p.get("id")) in ("<5471>", "5471"):
        la = p.get("listedAt")
        print(p.get("id"), p.get("name"), "category", p.get("category"),
              "tvl", p.get("tvl"), "parent", p.get("parentProtocol"),
              "listedAt", la,
              datetime.datetime.fromtimestamp(la, datetime.timezone.utc).isoformat() if la else None)
        print("  chains", p.get("chains"), "slug", p.get("slug"))
# today's new ids in seen with their notified state
for i in ["9354", "9355", "9356", "9357", "9358", "9359", "9360", "9361", "9362"]:
    print(i, seen.get(i))
