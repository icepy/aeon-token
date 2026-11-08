import json
import urllib.request
from collections import Counter
import datetime

req = urllib.request.Request("https://api.llama.fi/protocols?_cb=id13",
                             headers={"User-Agent": "defillama-radar/dl-v1"})
raw = json.load(urllib.request.urlopen(req, timeout=60))
byid = {str(p.get("id")): p for p in raw if isinstance(p, dict)}
weird = [k for k in byid if not k.isdigit()]
print("non-numeric ids:", [(k, byid[k].get("name"), byid[k].get("chains"), byid[k].get("category")) for k in weird])
ids = sorted(int(k) for k in byid if k.isdigit())
print("numeric max", ids[-1], "count", len(ids))
print("window 9340-9375:", [x for x in ids if 9340 <= x <= 9375])
c = Counter(p.get("listedAt") for p in raw if isinstance(p, dict) and p.get("listedAt"))
big = {k: v for k, v in c.items() if v >= 3}
print("same-second clusters >=3 (last 6):")
for k, v in sorted(big.items())[-6:]:
    print("  ", datetime.datetime.fromtimestamp(k, datetime.timezone.utc).isoformat(), "n=", v)
