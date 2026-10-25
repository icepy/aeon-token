#!/usr/bin/env python3
"""第九轮：逐词单查 60d total_count，分四类（查询失败 / 真零 / 全已见 / 有新增）。"""
import json, subprocess, sys, time

TERMS = [l.strip() for l in open("output/ghradar/terms9.txt", encoding="utf-8")
         if l.strip()]
res = {}
for t in TERMS:
    q = '"%s" in:name,description created:2026-08-26..2026-10-25 fork:false' % t
    n, err = None, ""
    for i in range(3):
        r = subprocess.run(["gh", "api", "-X", "GET", "search/repositories",
                            "-f", "q=" + q, "-f", "per_page=1"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            n = json.loads(r.stdout).get("total_count")
            break
        err = r.stderr.strip()
        if "rate limit" in err.lower() or "403" in err or "429" in err:
            time.sleep(10 * (i + 1)); continue
        break
    res[t] = {"total": n, "err": err[:120] if n is None else ""}
    print("%-32s %s %s" % (t, n if n is not None else "FAIL", err[:60]))
    time.sleep(2)
json.dump(res, open("output/ghradar/terms9.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
