---
name: github-radar
description: 按方向词扫 GitHub 新建仓库，看「有没有人在写代码」。与 arxiv-radar 平行，只做发现，不做判断。
metadata:
  title: GitHub Radar
  category: crypto
  var: ""
  tags:
    - crypto
    - discovery
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（默认 30）；`min:N` 换 star 地板（**默认 0**）；`chk:N` 换核验门槛（默认 5）。

发现层第二条通道。**与 `arxiv-radar` 平行，不是它的下游。**

## 它测什么

**「有没有人在写代码」。**

| 成熟度 | 通道 | 提前量 |
|---|---|---|
| 有人在研究 | `arxiv-radar` | ~4 个月 |
| 有人在写代码 | **本 skill** | ~1–2 个月 |
| 有人在发币 | `gecko-radar`（未建） | 0 |

**同一个词在几条通道上依次点亮 —— 那个次序才是信号。**

**实证（2026-10-25）**：`SkillWeaver` 在 arxiv 是 09-28，GitHub 仓 10-08 —— **论文 → 代码滞后 10 天**。这是本 skill 存在的第一份证据。

**本通道的真实产出在 AI / 机器人侧**，加密侧顺带。

## 铁律

- **star 地板是反向的。** 新建仓库必然 ★0–2，按 star 过滤 = 按「是否已被别人发现」过滤。默认 `min:0`。
- **star 测「发布时的传播」，commits 测「现在还有人在写」。判真伪只看 commits。** 实证：`Zero-WAM` ★439 / 30d 0 提交（连续两轮，已死）· `buaacyw/code-world-model` ★543 / 0 提交 · `PrismWAM` ★48 / 10 提交（活着）。
- **核验对象不能按创建时间取前 N。** 长窗口下创建最新的一批全是 ★0 噪声，核验会空转。必须**按 star 分桶**（见 step 2）。
- **description 越像论文，越要查 commits。** 空仓（`size=0`，commits 409）写得比真仓还像样。
- **只匹配 `in:name,description`，不要 readme。**
- **脏词必须配 carrier。** 但**噪声率要在 carrier 之后算** —— `data availability` 原始 96.2% 噪声，过 carrier 后只剩 5 条，carrier 是在干活的。
- **覆盖率必须报。** `total_count` 与实取条数之比 <50% 的词，**绝对数字不可引用**（实测 `vla` 7.9% / `world model` 21.4% / `jepa` 44.3%）。总覆盖率 32.1% 已到顶，再切窗无用。
- **缩写必然脏，用全称。**
- **`template` / `demo` / `sniper` 出现在 description 里 = 练手仓库或机器人农场。**
- **一个 owner 本轮命中 ≥3 个仓 = 仓库农场**；`memory/github-farms.txt` 里的是永久黑名单。
- **报「零命中」必须分开写：查询失败 / 真零命中。**
- **零命中不等于废词。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star + 30 天提交数。

## Config

读：
- 下面 `TERMS` 里的方向词
- `memory/github-seen.json` — 已见仓库（跨 run 去重）
- `memory/github-farms.txt` — 农场 owner 黑名单，一行一个（`#` 注释）

写：
- `memory/github-seen.json` — **全部幸存者**（`dry-run` 不写）
- `memory/github-candidates.md` — **只写报告级**，一行一个
- `output/ghradar/` — `out.json` · `audit.log`
- `memory/logs/${today}.md` — 每次运行一条
- 通知：只在报告级 > 0 时发

## Steps

### 1. 解析 var

```bash
DRY=""; DAYS=30; MIN=0; CHK=5
# token == dry-run  → DRY=1
# token 形如 days:N → DAYS=N
# token 形如 min:N  → MIN=N
# token 形如 chk:N  → CHK=N
export DRY DAYS MIN CHK
```

> 必须 `export` 单独一行。

### 2. 扫描

**把下面整段写到 `output/ghradar/scan.py`（用 Write 工具，不要 heredoc —— heredoc 里 f-string 的花括号带引号会被权限层拒）**，然后：

```bash
export DRY=$DRY DAYS=$DAYS MIN=$MIN CHK=$CHK
mkdir -p output/ghradar
python3 output/ghradar/scan.py
cat output/ghradar/audit.log
```

```python
#!/usr/bin/env python3
"""github-radar 扫描。脚本自己写 output/ghradar/ —— shell 重定向会被权限层拦。"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"; OUT = OUTD + "/out.json"; AUD = OUTD + "/audit.log"
SEEN  = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

DRY  = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN  = int(os.environ.get("MIN") or 0)
CHK  = int(os.environ.get("CHK") or 5)   # 核验门槛：★>=CHK 全部核验
CHK_CAP = 250                            # 核验总上限，防跑飞
REPORT_COMMITS = 5                       # 报告级：30 天提交数下限

# ── 词表。`#` 开头是注释。改词只改这一段 ──
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

# 脏词必须配 carrier（须与本行词同现才算命中）。
# 判据是 carrier **之后**的精度，不是原始噪声率。
CARRIER_BY_TERM = {
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
    farms = {l.strip().lower() for l in open(FARMS, encoding="utf-8")
             if l.strip() and not l.startswith("#")}

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
def gh_get(path):
    global GH
    if GH:
        try:
            r = subprocess.run(["gh", "api", path], capture_output=True,
                               text=True, timeout=45)
            if r.returncode == 0 and r.stdout.strip():
                return json.loads(r.stdout), "gh"
            print("  ! gh api 失败 rc=%s: %s" % (r.returncode, r.stderr.strip()[:140]),
                  file=sys.stderr); GH = False
        except Exception as ex:
            print("  ! gh 不可用: %s" % ex, file=sys.stderr); GH = False
    req = urllib.request.Request("https://api.github.com/" + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "aeon-github-radar"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp), "anon"

def search(q):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100"})
    return gh_get("search/repositories?" + qs)

def commits_30d(rid):
    """判真伪只看这个。空仓 409 → None。"""
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    try:
        d, _ = gh_get("repos/%s/commits?%s" % (rid, qs))
        return len(d) if isinstance(d, list) else None
    except Exception:
        return None

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "farm": 0, "fail": 0}
hit, qfail, cov, per_term = {}, [], {}, {}

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
            owner = (it.get("owner") or {}).get("login", "")
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
            if owner.lower() in farms:
                drop["farm"] += 1; continue
            out.append({"term": term, "terms": [term], "repo": rid,
                        "owner": owner, "url": it["html_url"],
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

# ── 核验：按 star 分桶，不是按创建时间 ──
# 先全部 ★>=CHK（高信号），再补创建最新的，直到上限。
out.sort(key=lambda c: -c["stars"])
todo = [c for c in out if c["stars"] >= CHK]
if len(todo) < CHK_CAP:
    rest = sorted([c for c in out if c["stars"] < CHK],
                  key=lambda c: c["created"], reverse=True)
    todo += rest[:CHK_CAP - len(todo)]
for c in todo:
    n = commits_30d(c["repo"])
    c["commits_30d"] = n
    if n == 0:
        c["stale"] = True
    if n is None:
        c["maybe_empty"] = True

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["farm_hit"] = owner_n[c["owner"]]

# ── 报告级：核验过 + 还在写 + 不农场 + 不空仓 ──
def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= REPORT_COMMITS
            and not c.get("stale") and not c.get("maybe_empty")
            and not c.get("farm_hit"))

rep = [c for c in out if reportable(c)]
rep.sort(key=lambda c: (-c["commits_30d"], -c["stars"]))

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

L = ["扫 %d 词 × %d 窗 | 原始 %d | 幸存 %d | 报告级 %d" % (
        len(TERMS), NWIN, raw, len(out), len(rep)),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d farm=%d fail=%d"
        % (drop["seen"], drop["excl"], drop["archived"], drop["short_desc"],
           drop["carrier"], drop["farm"], drop["fail"]),
     "核验 %d 个（★>=%d 全部 + 最新补齐，上限 %d）"
        % (len(todo), CHK, CHK_CAP),
     "词表命中: " + " · ".join("%s=%d" % (k, v) for k, v in
        sorted(per_term.items(), key=lambda x: -x[1]))]
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % (k, v) for k, v in low.items()))
if qfail:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(qfail))
zero = [k for k, v in per_term.items() if v == 0 and k not in qfail]
if zero:
    L.append("⚠️ 真零命中: " + " · ".join(zero))
fh = {o: n for o, n in owner_n.items() if n >= 3}
if fh:
    L.append("⚠️ 疑似仓库农场（待入黑名单）: " + " · ".join(
        "%s=%d" % kv for kv in fh.items()))
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交（star 在骗人）: " + " · ".join(stale))
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（只有 description）: " + " · ".join(empty))
for c in rep[:25]:
    L.append("  %s [%s] %s ★%d commits30d=%d"
             % (c["created"], c["term"], c["repo"], c["stars"], c["commits_30d"]))
open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

if not DRY and hit:
    stamp = now.strftime("%Y-%m-%d")
    merged = {k: stamp for k in hit}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-5000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar（报告级 %d）\n" % (stamp, len(rep)))
        for c in rep:
            f.write("- [%s](%s) ★%d · %dd提交 · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"], c["commits_30d"],
                       c["term"], c["desc"][:100]))
```

### 3. 输出

- `memory/logs/${today}.md` 追加一节，**必须分开写**：查询失败 N 词 / 真零 N 词 / 覆盖率 <50% 的词 / 核验结果
- 通知只发**报告级**，按方向词分组，每条给：仓库 + 一句话 + 链接 + star + **30 天提交数**
- 报告级为 0 时不发通知

## 附录：农场黑名单

`memory/github-farms.txt` 现在应含（三轮复现，判成立）：

```
# 仓库农场 owner —— 命中不采信为主信号
maxamin
nirholas
OpenMakerProjects
```