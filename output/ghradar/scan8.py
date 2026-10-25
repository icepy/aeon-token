#!/usr/bin/env python3
"""github-radar 第八轮扫描 (2026-10-25).

对照 SKILL.md 参考实现，本轮带上 memory 里已定的修法：
  - 409（真空仓）不再拉垮认证态（缺陷 5 修法）
  - per_term==0 四分类：查询失败 / 真零 / 全已见(饱和) / 有新增（缺陷 14）
  - pages 规则只认「名字像页 + 体量小」，不用 language 豁免（缺陷 16）
  - 全量核验（缺陷 13）：core 配额与 search 独立池
"""
import json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"
OUT = OUTD + "/out8.json"
AUD = OUTD + "/audit8.log"
SEEN = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

DRY = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN = int(os.environ.get("MIN") or 0)
CHK = int(os.environ.get("CHK") or 5)
CHK_CAP = 2000
PER_TERM_CAP = 25
REPORT_COMMITS = 5
NOTIFY_TOP = 30
MAXPAGE = 3          # 第七轮已把旧词的第 2 页吃干；新全称词总量小，3 页足够覆盖

# 词表：vla / jepa 换成全称（第七轮污染 22.0% / 14.5%，memory 记为「下一次必改项」）
TERMS = [
    "embodied data",
    "robot manipulation",
    "robot dataset",
    "teleoperation",
    "sim2real",
    "sim-to-real",
    "world model",
    "world action model",
    "vision language action",
    "joint embedding predictive",
    "egocentric",
    "robotics data engine",
    "verifiable inference",
    "proof of useful work",
    "data availability",
    "restaking",
    "intent-based",
    "maximal extractable value",
]

# 全称仍可能撞同形：action 名词、jepa 家族名等。这里只保留真正的外溢。
NEG_BY_TERM = {
    "joint embedding predictive": ["jepang", "jepara", "jepan"],
}

# 脏词 carrier：须与本行词同现才算命中（判据是 carrier 之后的精度）
CARRIER_BY_TERM = {
    "world model": ["embodied", "robot", "vla", "manipulation", "sim2real",
                    "sim-to-real", "teleop", "egocentric", "action", "policy",
                    "rlbench", "lerobot"],
    "data availability": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                          "rollup", "celestia", "modular", "da layer", "zk"],
    "intent-based": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                     "solver", "swap", "defi", "amm", "wallet"],
    "embodied data": ["robot", "manipulation", "vla", "teleop", "sim2real",
                      "dataset", "embodied", "egocentric"],
}

EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]

farms = set()
if os.path.exists(FARMS):
    for l in open(FARMS, encoding="utf-8"):
        k = l.split("#")[0].strip().lower()
        if k:
            farms.add(k)

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

now = datetime.now(timezone.utc)
NWIN = 3
step = DAYS / NWIN
WINS = ["%s..%s" % ((now - timedelta(days=step * (i + 1))).strftime("%Y-%m-%d"),
                    (now - timedelta(days=step * i)).strftime("%Y-%m-%d"))
        for i in range(NWIN)]

GH = True
gh_lost = [False]


def gh_get(path):
    """返回 (data, err)。err=None 成功；'HTTP 409' 区分真空仓与限速。"""
    global GH
    last = ""
    if GH:
        for i in range(3):
            try:
                r = subprocess.run(["gh", "api", path], capture_output=True,
                                   text=True, timeout=45)
                if r.returncode == 0 and r.stdout.strip():
                    return json.loads(r.stdout), None
                last = r.stderr.strip()
                # 409 = 真空仓，属正常结果，绝不能当成认证失效
                if "409" in last or "empty" in last.lower():
                    return None, "HTTP 409"
                if ("rate limit" in last.lower() or "429" in last
                        or "403" in last or "secondary" in last.lower()):
                    time.sleep(5 * (i + 1))
                    continue
                break
            except Exception as ex:
                last = str(ex)
                time.sleep(3)
        print("  ! gh api 放弃: %s" % last[:140], file=sys.stderr)
        GH = False
        gh_lost[0] = True
    for i in range(2):
        try:
            req = urllib.request.Request("https://api.github.com/" + path, headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "aeon-github-radar"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.load(resp), None
        except urllib.error.HTTPError as he:
            last = "HTTP %s" % he.code
            if he.code in (403, 429):
                time.sleep(8 * (i + 1))
                continue
            return None, last
        except Exception as ex:
            last = str(ex)
            time.sleep(3)
    return None, last


def search(q, page=1):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100", "page": str(page)})
    return gh_get("search/repositories?" + qs)


def commits_since(rid, days):
    """返回 (n, status)：ok / empty（真空仓 409）/ unverified（限速等）。"""
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    n = len(data) if isinstance(data, list) else None
    return n, "ok"


# 主体分文件写（单次 Write 载荷过大时拆开），这里按同进程执行
exec(open(OUTD + "/scan8_body.py", encoding="utf-8").read())
