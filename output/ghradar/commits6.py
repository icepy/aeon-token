import json, subprocess, time, urllib.parse
from datetime import datetime, timedelta, timezone
from collections import Counter

now = datetime.now(timezone.utc)
since = (now - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")

REPOS = ["samooth/zig-zkml", "opodark/hyperspace-agi-1.05", "xXGuilasXx/spark-pearl-miner",
         "Ulysse98/prism", "itzebe/intent-pay", "pastaisfine/swapsos",
         "Dhaiwat10/openinstinct-qwen", "sublimestate/swap-RFQ",
         # 机器人侧对照
         "OpenInterpretability/ekbasis", "video-db/RoboPeek"]

for rid in REPOS:
    qs = urllib.parse.urlencode({"since": since, "per_page": "100"})
    r = subprocess.run(["gh", "api", "repos/%s/commits?%s" % (rid, qs)],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print("%-40s ERR %s" % (rid, r.stderr.strip()[:60])); continue
    data = json.loads(r.stdout)
    if not isinstance(data, list):
        continue
    authors = Counter()
    msgs = []
    for c in data:
        a = c.get("author") or {}
        a2 = c.get("commit", {}).get("author", {})
        authors[a.get("login") or a2.get("name") or "?"] += 1
        msgs.append(c["commit"]["message"].split("\n")[0][:70])
    print("\n%-40s %d 提交" % (rid, len(data)))
    print("  authors:", dict(authors.most_common(3)))
    for m in msgs[:6]:
        print("   ·", m)
    time.sleep(0.4)
