import json, subprocess, urllib.parse
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
since = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

REPOS = ["Ada4321/SkillWeaver", "NVIDIA/Flora", "wellkilo/embodigen",
         "vearl-verified-compute/vearl", "UniWAM/UniWAM", "dextacwam/DexTacWAM"]

def gh(p):
    r = subprocess.run(["gh", "api", p], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None, r.stderr.strip()[:100]
    return json.loads(r.stdout), None

for rid in REPOS:
    d, e = gh("repos/" + rid)
    if d is None:
        print("%-40s ERROR %s" % (rid, e)); continue
    qs = urllib.parse.urlencode({"since": since, "per_page": "100"})
    c, ce = gh("repos/%s/commits?%s" % (rid, qs))
    n = len(c) if isinstance(c, list) else ("ERR " + str(ce))
    print("%-40s ★%-5d created=%s pushed=%s 30d=%s lang=%s size=%dKB" % (
        rid, d.get("stargazers_count", 0), (d.get("created_at") or "")[:10],
        (d.get("pushed_at") or "")[:10], n, d.get("language"), d.get("size", 0)))
