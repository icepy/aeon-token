#!/usr/bin/env python3
"""github-radar 第七轮扫描。脚本自己写 output/ghradar/。"""
import json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"; OUT = OUTD + "/out7.json"; AUD = OUTD + "/audit7.log"
SEEN = "memory/github-seen.json"; CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

# 参数走 argv（环境变量前缀命令会被权限层拒）
_args = sys.argv[1:]
def _arg(name, default):
    for a in _args:
        if a.startswith(name + ":"):
            return a.split(":", 1)[1]
    return default

DRY  = "dry-run" in _args
DAYS = int(_arg("days", 30))
MIN  = int(_arg("min", 0))
CHK  = int(_arg("chk", 5))
CHK_CAP = 600
PER_TERM_CAP = 25
REPORT_COMMITS = 5
MAXPAGE = 2

TERMS = [t.strip() for t in """
# ── AI / 机器人（主战场）──
embodied data
robot manipulation
robot dataset
teleoperation
sim2real
sim-to-real
world model
world action model
vla
jepa
egocentric
robotics data engine
# ── 加密（顺带）──
verifiable inference
proof of useful work
data availability
restaking
intent-based
maximal extractable value
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

CARRIER_BY_TERM = {
    "world model": ["embodied", "robot", "vla", "manipulation", "sim2real",
                    "sim-to-real", "teleop", "egocentric", "action", "policy",
                    "rlbench", "lerobot"],
    "data availability": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                          "rollup", "celestia", "modular", "da layer", "zk"],
    "intent-based": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                     "solver", "swap", "defi", "amm", "wallet"],
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
    """返回 (data, err)。err=None 成功。
    409（真空仓）绝不降级认证态 —— 那是数据缺失，不是限速。"""
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
                # 409 / empty repo：数据是「空」，不是限速，直接返回，不降级
                if "409" in last or "empty" in last.lower():
                    return None, "HTTP 409"
                if ("rate limit" in last.lower() or "429" in last
                        or "403" in last or "secondary" in last.lower()):
                    time.sleep(5 * (i + 1)); continue
                break
            except Exception as ex:
                last = str(ex); time.sleep(3)
        print("  ! gh api 降级: %s" % last[:140], file=sys.stderr)
        GH = False; gh_lost[0] = True
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
                time.sleep(8 * (i + 1)); continue
            return None, last
        except Exception as ex:
            last = str(ex); time.sleep(3)
    return None, last

def search(q, page=1):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100", "page": str(page)})
    return gh_get("search/repositories?" + qs)

def commits_since(rid, days):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    return (len(data) if isinstance(data, list) else None), "ok"

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "pages": 0, "farm": 0, "fail": 0}
hit, qfail, cov, per_term = {}, [], {}, {}
page_dropped = []

for term in TERMS:
    total, got, failed = 0, 0, False
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        for page in range(1, MAXPAGE + 1):
            res, err = search(q, page)
            if res is None:
                print("! %s @%s p%d: %s" % (term, w, page, err), file=sys.stderr)
                drop["fail"] += 1; failed = True; time.sleep(8); break
            if page == 1:
                total += res.get("total_count", 0)
            items = res.get("items", [])
            got += len(items)
            for it in items:
                raw += 1
                rid = it["full_name"]
                owner = (it.get("owner") or {}).get("login", "")
                short = rid.split("/")[-1]
                if rid in seen:
                    drop["seen"] += 1; continue
                if rid in hit:
                    hit[rid]["terms"].append(term); drop["seen"] += 1; continue
                if it.get("archived"):
                    drop["archived"] += 1; continue
                size_kb = it.get("size", 0)
                lang = it.get("language")
                # 项目页 / 列表页：名字像页 **且** 体量小。两个条件，不设 language 豁免
                # —— GitHub 会把纯静态站标成 HTML/JS/CSS，用 not lang 会反向放行。
                if ((short.endswith(".github.io")
                     or short.lower() == owner.lower()) and size_kb < 300):
                    drop["pages"] += 1
                    page_dropped.append((rid, size_kb)); continue
                desc = (it.get("description") or "").strip()
                if len(desc) < 25:
                    drop["short_desc"] += 1; continue
                if any(x in desc.lower() for x in EXCL):
                    drop["excl"] += 1; continue
                need = CARRIER_BY_TERM.get(term)
                if need and not any(c in desc.lower() for c in need):
                    drop["carrier"] += 1; continue
                if owner.lower() in farms:
                    drop["farm"] += 1; continue
                out.append({"term": term, "terms": [term], "repo": rid,
                            "owner": owner, "url": it["html_url"],
                            "stars": it.get("stargazers_count", 0),
                            "created": (it.get("created_at") or "")[:10],
                            "pushed": (it.get("pushed_at") or "")[:10],
                            "lang": lang or "",
                            "topics": it.get("topics", [])[:6],
                            "size_kb": size_kb,
                            "desc": " ".join(desc.split())[:140]})
                hit[rid] = out[-1]
            time.sleep(3 if GH else 8)
            if len(items) < 100:
                break
    if failed and not got:
        qfail.append(term)
    per_term[term] = len([c for c in out if c["term"] == term])
    if total:
        cov[term] = round(100.0 * got / total, 1)

# ── 核验采样：按词分层，不是只按 star ──
pick = {}
for c in out:
    if c["stars"] >= CHK:
        pick[c["repo"]] = c
by_term = {}
for c in out:
    by_term.setdefault(c["term"], []).append(c)
for t, lst in by_term.items():
    lst.sort(key=lambda c: (-c["stars"], c["created"]))
    for c in lst[:PER_TERM_CAP]:
        pick[c["repo"]] = c
todo = list(pick.values())[:CHK_CAP]

for c in todo:
    n30, st = commits_since(c["repo"], 30)
    if st == "ok":
        c["commits_30d"] = n30
        if n30 == 0:
            c["stale"] = True
    elif st == "empty":
        c["maybe_empty"] = True
        continue
    else:
        c["unverified"] = True
        continue
    if not c.get("stale"):
        n7, st7 = commits_since(c["repo"], 7)
        if st7 == "ok":
            c["commits_7d"] = n7
            if n7 == 0:
                c["burst_only"] = True

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["owner_repos"] = owner_n[c["owner"]]

def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= REPORT_COMMITS
            and not c.get("stale") and not c.get("maybe_empty"))

rep = sorted([c for c in out if reportable(c)],
             key=lambda c: (-c.get("commits_7d", 0), -c["commits_30d"], -c["stars"]))

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

L = ["扫 %d 词 × %d 窗（每窗最多 %d 页）| 原始 %d | 幸存 %d | 报告级 %d"
     % (len(TERMS), NWIN, MAXPAGE, raw, len(out), len(rep)),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d pages=%d "
     "farm=%d fail=%d" % (drop["seen"], drop["excl"], drop["archived"],
                          drop["short_desc"], drop["carrier"], drop["pages"],
                          drop["farm"], drop["fail"]),
     "核验 %d / %d = %.1f%%（★>=%d 全部 + 每词保证 %d 个，上限 %d）"
     % (len(todo), len(out), 100.0 * len(todo) / max(len(out), 1),
        CHK, PER_TERM_CAP, CHK_CAP),
     "黑名单载入 %d 个 owner" % len(farms),
     "词表命中: " + " · ".join("%s=%d" % (k, v) for k, v in
                              sorted(per_term.items(), key=lambda x: -x[1]))]
if gh_lost[0]:
    L.append("⚠️ gh 认证已丢失，降级未认证（8s 退避）—— 检查是否限速，"
             "本轮核验完整性存疑")
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % kv for kv in low.items()))
if qfail:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(qfail))
# 🔴 per_term 只数「新幸存者」。有 seen 基线后，词的命中若全部已见 → 0。
# 「0」≠ 废词，必须和「真零命中」分开 —— 否则会把有 126 个仓的词判成空词删掉。
zero_new = [k for k, v in per_term.items() if v == 0 and k not in qfail]
if zero_new:
    L.append("ℹ️ 本轮零新增（多为 seen 饱和，≠废词，需单查 total_count 才能定）: "
             + " · ".join(zero_new))
if page_dropped:
    L.append("ℹ️ 被 pages 规则丢弃 %d 个（可审计，体量<300KB）: %s"
             % (len(page_dropped),
                " · ".join("%s(%dKB)" % p for p in page_dropped[:15])))
vt = Counter(c["term"] for c in todo)
L.append("逐词核验数: " + " · ".join("%s=%d/%d" % (k, vt.get(k, 0), v)
                                     for k, v in sorted(per_term.items(),
                                                        key=lambda x: -x[1])))
uv = [c["repo"] for c in todo if c.get("unverified")]
if uv:
    L.append("⚠️ 未核验（限速，勿当空仓）%d 个: %s" % (len(uv), " · ".join(uv[:15])))
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交（star 在骗人）: " + " · ".join(stale))
burst = [c["repo"] for c in todo if c.get("burst_only")]
if burst:
    L.append("⚠️ 30d 有量但近 7 天已停（爆完即停）%d 个: %s"
             % (len(burst), " · ".join(burst[:15])))
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（409，只有 description）: " + " · ".join(empty))
cand = {o: n for o, n in owner_n.items() if n >= 3}
if cand:
    L.append("ℹ️ 候选农场（owner≥3，需人工判，非判决）: " +
             " · ".join("%s=%d" % kv for kv in cand.items()))
for c in rep[:25]:
    L.append("  %s [%s] %s ★%d 30d=%d 7d=%d size=%dKB"
             % (c["created"], c["term"], c["repo"], c["stars"],
                c["commits_30d"], c.get("commits_7d", -1), c["size_kb"]))
open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

if not DRY and hit:
    stamp = now.strftime("%Y-%m-%d")
    merged = {k: stamp for k in hit}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-6000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar（报告级 %d）\n" % (stamp, len(rep)))
        for c in rep:
            tag = " [爆完即停]" if c.get("burst_only") else ""
            f.write("- [%s](%s) ★%d · 30d=%d 7d=%d%s · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"], c["commits_30d"],
                       c.get("commits_7d", -1), tag, c["term"],
                       c["desc"][:100]))
