import json
import urllib.request

WANT = set(["9354", "9355", "9356", "9357", "9358", "9359", "9360", "9361", "9362"])
FIELDS = ["name", "category", "parentProtocol", "chains", "tvl", "listedAt",
          "slug", "url", "misrepresentedTokens", "wrongLiquidity"]


def get(u):
    r = urllib.request.urlopen(urllib.request.Request(
        u, headers={"User-Agent": "defillama-radar/dl-v1"}), timeout=60)
    return r, json.load(r)


r1, a = get("https://api.llama.fi/protocols")
r2, b = get("https://api.llama.fi/protocols?_cb=fd13")
print("HIT", r1.headers.get("etag"), r1.headers.get("last-modified"), r1.headers.get("age"), len(a))
print("MISS", r2.headers.get("etag"), r2.headers.get("last-modified"), len(b))
da = {str(p.get("id")): p for p in a if isinstance(p, dict)}
db = {str(p.get("id")): p for p in b if isinstance(p, dict)}
print("id sets equal", set(da) == set(db))
for i in sorted(WANT):
    diffs = [f for f in FIELDS if da[i].get(f) != db[i].get(f)]
    print(i, da[i].get("name"), "field_diffs=", diffs if diffs else "none")
empty = sum(1 for p in a if isinstance(p, dict) and not (p.get("chains") or []))
print("empty_chains", empty, "/", len(a), "=", round(100.0 * empty / len(a), 2), "%")
