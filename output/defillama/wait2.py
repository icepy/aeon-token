#!/usr/bin/env python3
"""前台等待 CF 边缘对象换新（last-modified 变化），最多 ~8.5 分钟。
换新即跑 scan.py。退出码 0 = 已跑；2 = 未换新（继续用已取到的数据）。
"""
import subprocess
import sys
import time
import urllib.request

OLD = "Wed, 28 Oct 2026 23:02:27 GMT"
API = "https://api.llama.fi/protocols"
DEADLINE = time.time() + 510


def head():
    req = urllib.request.Request(API, method="HEAD",
                                 headers={"User-Agent": "defillama-radar/poll"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.headers.get("last-modified"), r.headers.get("cf-cache-status")
    except Exception as ex:
        return "err:%s" % str(ex)[:30], "err"


tries = 0
while time.time() < DEADLINE:
    tries += 1
    lm, cs = head()
    print("poll=%d lm=%s cf=%s" % (tries, lm, cs), flush=True)
    if lm and lm != OLD and not lm.startswith("err"):
        print("TURNOVER", flush=True)
        r = subprocess.run([sys.executable, "skills/defillama-radar/scan.py", ""],
                           capture_output=True, text=True)
        print(r.stdout, flush=True)
        if r.stderr.strip():
            print("STDERR:" + r.stderr[-500:], flush=True)
        sys.exit(0)
    time.sleep(45)
print("NO_TURNOVER tries=%d" % tries, flush=True)
sys.exit(2)
