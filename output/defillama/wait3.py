#!/usr/bin/env python3
"""等 CF 边缘对象过期后跑一轮。最多 12 分钟。换新即跑 scan.py 并打印。
退出码 0 = 已跑 scan；2 = 始终 HIT。
"""
import subprocess
import sys
import time
import urllib.request

OLD = "Wed, 28 Oct 2026 23:02:27 GMT"
API = "https://api.llama.fi/protocols"
DEADLINE = time.time() + 660


def head():
    req = urllib.request.Request(API, method="HEAD",
                                 headers={"User-Agent": "defillama-radar/poll"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.headers.get("last-modified"), r.headers.get("cf-cache-status"), r.headers.get("age")
    except Exception as ex:
        return "err:%s" % str(ex)[:30], "err", "-"


n = 0
while time.time() < DEADLINE:
    n += 1
    lm, cs, age = head()
    print("poll=%d lm=%s cf=%s age=%s" % (n, lm, cs, age), flush=True)
    if lm and lm != OLD and not lm.startswith("err"):
        print("TURNOVER", flush=True)
        r = subprocess.run([sys.executable, "skills/defillama-radar/scan.py", ""],
                           capture_output=True, text=True)
        print(r.stdout, flush=True)
        sys.exit(0)
    time.sleep(40)
print("NO_TURNOVER tries=%d" % n, flush=True)
sys.exit(2)
