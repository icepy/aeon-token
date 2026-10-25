#!/usr/bin/env python3
"""github-radar 扫描。export DRY DAYS MIN 之后直接跑。
脚本自己写 output/ghradar/ 下的文件 —— shell 重定向会被权限层拦。"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"
OUT  = os.path.join(OUTD, "out.json")
AUD  = os.path.join(OUTD, "audit.log")
SEEN  = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"

DRY  = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN  = int(os.environ.get("MIN") or 0)

# ── 词表：AI/机器人侧是主战场，加密侧是顺带。`#` 开头是注释 ──
TERMS = [t.strip() for t in """
# ── AI / 机器人（主战场，与 DEUS / XMAQUINA 叙事同轨）──
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
# ── 加密（顺带；实证很薄，但别删）──
verifiable inference
proof of useful work
data availability
restaking
intent-based
maximal extractable value
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

# 脏词必须配 carrier：这些短语在 GitHub 上已经不是加密术语了
# （实证噪声率 88–92%：data availability 误中论文「数据可用性声明」/SQL 助手，
#  intent-based 误中 PyTorch 意图识别 chatbot）。必须与本行词同现才算命中。
CARRIER_BY_TERM = {
    "data availability": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                          "rollup", "celestia", "modular", "da layer", "zk-", "zk"],
    "intent-based": ["blockchain", "crypto", "ethereum", "onchain", "web3",
                     "solver", "swap", "defi", "amm", "wallet"],
}

# 只判 description。readme 太长，全字段匹配会误杀正经项目。
EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

now = datetime.now(timezone.utc)
# 3 个子窗口：单窗口被 per_page 截断，切窗能显著抬高覆盖率
NWIN = 3
step = DAYS / NWIN
WINS = [f"{(now - timedelta(days=step * (i + 1))):%Y-%m-%d}"
        f"..{(now - timedelta(days=step * i)):%Y-%m-%d}" for i in range(NWIN)]

# gh api 的 query 必须整段塞进 path（用 -f 传会被拒 → 静默退回未认证 → 403）
GH = True
def gh_get(path):
    global GH
    if GH:
        try:
            r = subprocess.run(["gh", "api", path], capture_output=True,
                               text=True, timeout=45)
            if r.returncode == 0 and r.stdout.strip():
                return json.loads(r.stdout), "gh"
            print("  ! gh api 失败 rc=%s: %s" % (r.returncode, r.stderr.strip()[:140]),
                  file=sys.stderr)
            GH = False
        except Exception as ex:
            print("  ! gh 不可用: %s" % ex, file=sys.stderr); GH = False
    req = urllib.request.Request("https://api.github.com/" + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "aeon-github-radar"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp), "anon"

def search(q, page=1, per=100):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": str(per), "page": str(page)})
    return gh_get("search/repositories?" + qs)

def commits_30d(rid):
    """判真伪只看这个。空仓返 409 → None。"""
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    try:
        d, _ = gh_get("repos/%s/commits?%s" % (rid, qs))
        return len(d) if isinstance(d, list) else None
    except Exception:
        return None

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0,
        "carrier": 0, "fail": 0}
hit, qfail = {}, []
cov, per_term = {}, {}

for term in TERMS:
    total, got, failed = 0, 0, False
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        try:
            res, src = search(q)
        except Exception as ex:
            print("! %s @%s: %s" % (term, w, ex), file=sys.stderr)
            drop["fail"] += 1; failed = True; time.sleep(7); continue
        total += res.get("total_count", 0)
        items = res.get("items", [])
        got += len(items)
        for it in items:
            raw += 1
            rid = it["full_name"]
            if rid in seen:
                drop["seen"] += 1; continue
            if rid in hit:
                hit[rid]["terms"].append(term); drop["seen"] += 1; continue
            if it.get("archived"):
                drop["archived"] += 1; continue
            desc = (it.get("description") or "").strip()
            if len(desc) < 25:
                drop["short_desc"] += 1; continue
            if any(x in desc.lower() for x in EXCL):
                drop["excl"] += 1; continue
            need = CARRIER_BY_TERM.get(term)
            if need and not any(c in desc.lower() for c in need):
                drop["carrier"] += 1; continue
            out.append({"term": term, "terms": [term], "repo": rid,
                        "owner": (it.get("owner") or {}).get("login", ""),
                        "url": it["html_url"],
                        "stars": it.get("stargazers_count", 0),
                        "created": (it.get("created_at") or "")[:10],
                        "topics": it.get("topics", [])[:6],
                        "desc": " ".join(desc.split())[:140]})
            hit[rid] = out[-1]
        time.sleep(2 if src == "gh" else 7)
    if failed and not got:
        qfail.append(term)
    per_term[term] = len([c for c in out if c["term"] == term])
    if total:
        cov[term] = round(100.0 * got / total, 1)

# 真伪核验：按创建时间倒序取前 25，查 30 天提交数
out.sort(key=lambda c: c["created"], reverse=True)
for c in out[:25]:
    n = commits_30d(c["repo"])
    c["commits_30d"] = n
    if n == 0:
        c["stale"] = True          # 已停更
    if n is None:
        c["maybe_empty"] = True    # 空仓（size=0 / 409）

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["farm"] = owner_n[c["owner"]]

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

L = []
L.append("扫 %d 词 × %d 窗 | 原始 %d | 幸存 %d | 丢弃 seen=%d excl=%d "
         "archived=%d short_desc=%d carrier=%d fail=%d"
         % (len(TERMS), NWIN, raw, len(out), drop["seen"], drop["excl"],
            drop["archived"], drop["short_desc"], drop["carrier"], drop["fail"]))
L.append("词表原始命中: " + " · ".join(
    "%s=%d" % (k, v) for k, v in sorted(per_term.items(), key=lambda x: -x[1])))
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % (k, v) for k, v in low.items()))
if qfail:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(qfail))
zero = [k for k, v in per_term.items() if v == 0 and k not in qfail]
if zero:
    L.append("⚠️ 真零命中（查询成功但无结果）: " + " · ".join(zero))
farms = {o: n for o, n in owner_n.items() if n >= 3}
if farms:
    L.append("⚠️ 疑似仓库农场: " + " · ".join("%s=%d" % kv for kv in farms.items()))
stale = [c["repo"] for c in out[:25] if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交（star 在骗人）: " + " · ".join(stale))
empty = [c["repo"] for c in out[:25] if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（只有 description）: " + " · ".join(empty))
for c in out[:25]:
    L.append("  %s [%s] %s ★%d commits30d=%s%s"
             % (c["created"], c["term"], c["repo"], c["stars"],
                c.get("commits_30d"), " FARM" if c.get("farm") else ""))
open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

if not DRY and hit:
    stamp = now.strftime("%Y-%m-%d")
    merged = {k: stamp for k in hit}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-3000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar\n" % stamp)
        for c in out:
            f.write("- [%s](%s) ★%d · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"], c["term"],
                       c["desc"][:100]))
