#!/usr/bin/env python3
"""轮询 CF 边缘对象直到换新，然后跑 scan.py。单进程，避免多次 bash 往返。"""
import subprocess
import sys
import time
import urllib.request

OLD = "Wed, 28 Oct 2026 23:02:27 GMT"
API = "https://api.llama.fi/protocols"


def head():
    req = urllib.request.Request(API, method="HEAD",
                                 headers={"User-Agent": "defillama-radar/poll"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            h = r.headers
            return h.get("last-modified"), h.get("cf-cache-status")
    except Exception as ex:
        return "err:%s" % str(ex)[:40], "err"


for i in range(1, 21):
    lm, cs = head()
    print("poll=%d last-modified=%s cf=%s" % (i, lm, cs), flush=True)
    if lm and lm != OLD and not lm.startswith("err"):
        print("TURNOVER after %d polls" % i, flush=True)
        r = subprocess.run([sys.executable, "skills/defillama-radar/scan.py", ""],
                           capture_output=True, text=True)
        print(r.stdout[-2500:], flush=True)
        print(r.stderr[-800:], flush=True)
        sys.exit(0)
    time.sleep(60)
print("NO_TURNOVER after 20 polls", flush=True)
sys.exit(1)
