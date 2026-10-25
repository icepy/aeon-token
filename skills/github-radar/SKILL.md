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

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（默认 30）；`min:N` 换 star 地板（**默认 0**）。

发现层第二条通道。**与 `arxiv-radar` 平行，不是它的下游。**

## 它测什么

**「有没有人在写代码」。**

同一个方向有三条平行探针，测不同成熟度：

| 成熟度 | 通道 | 提前量 |
|---|---|---|
| 有人在研究 | `arxiv-radar` | ~4 个月 |
| 有人在写代码 | **本 skill** | ~1–2 个月 |
| 有人在发币 | `gecko-radar`（未建） | 0 |

**同一个词在几条通道上依次点亮 —— 那个次序才是信号。**

**本通道的真实产出在 AI / 机器人侧**（实证：加密侧 60 天实质为空，机器人侧有成型的活跃信号）。加密词只是顺带。

词表是**手抄 arxiv 那张当基准、再按平台改**的，不是自动同步的。

## 铁律

- **star 地板是反向的。** 新建仓库必然 ★0–2，按 star 过滤 = 按「是否已被别人发现」过滤，而本 skill 的全部价值就在提前量。默认 `min:0`。
- **star 测「发布时的传播」，commits 测「现在还有人在写」。** 判真伪只看 commits。实证：`Zero-WAM` ★439 但 30 天 0 提交（已死），`PrismWAM` ★48 但 7 天 10 提交（活着）。
- **description 越像论文，越要查 commits。** 实证两个「被 star 过滤丢掉的零星真货」其实是空仓（`size=0`，commits API 返 409）。
- **只匹配 `in:name,description`，不要 readme。** readme 是长文档，加进来等于把词表降级成模糊搜索。
- **脏词必须配 carrier。** 一个短语在 GitHub 上不再是本行术语时，要求它与一个本行词同现才算命中（见 `CARRIER_BY_TERM`）。
- **必须报覆盖率。** `total_count` 与实取条数的比例低于 50% 的词，**它的绝对数字不能引用**。`sort=stars` 天然按「已被发现程度」采样。
- **缩写必然脏，用全称。** `MEV` / `ZK` / `DA` 在代码库里全是模板名和变量名。
- **`template` / `demo` / `sniper` 出现在 description 里，多半是练手仓库或机器人农场。**
- **一个 owner 本轮命中 ≥3 个仓库 = 仓库农场**，标记，不采信为主信号。
- **报「零命中」必须分开写：查询失败 N 个词 / 真零命中 N 个词。** 查询写错会静默产出 0，长得和「真没人写」一模一样。
- **零命中不等于废词。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star + 30 天提交数。

## Config

读：
- 下面 `TERMS` 里的方向词
- `memory/github-seen.json` — 已见仓库（跨 run 去重）

写：
- `memory/github-seen.json` — 由脚本更新（`dry-run` 不写）
- `memory/github-candidates.md` — 追加候选，一行一个
- `output/ghradar/out.json` · `output/ghradar/audit.log` — 本轮快照与审计
- `memory/logs/${today}.md` — 每次运行一条
- 通知：只在有幸存者时发

## Steps

### 1. 解析 var

按空格拆 `${var}`，逐个 token 判定，然后**用 `export` 单独一行导出**：

```bash
DRY=""; DAYS=30; MIN=0
# token == dry-run  → DRY=1
# token 形如 days:N → DAYS=N
# token 形如 min:N  → MIN=N
export DRY DAYS MIN
```

> 必须 `export` 单独一行。`DRY=1 python3 ...` 前缀形式会被权限层拒。

### 2. 扫描

**把下面整段写到 `output/ghradar/scan.py`（用 Write 工具，不要用 heredoc —— heredoc 里 f-string 的花括号带引号会被权限层拒）**，然后：

```bash
export DRY=$DRY DAYS=$DAYS MIN=$MIN
mkdir -p output/ghradar
python3 output/ghradar/scan.py
cat output/ghradar/audit.log
```

```python
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
```

### 3. 输出

- 幸存者写进 `memory/logs/${today}.md` 的 `### github-radar` 一节
- **日志里必须分开写**：查询失败 N 个词 / 真零命中 N 个词 / 覆盖率 <50% 的词
- 通知按方向词分组，每条给：仓库 + 一句话 + 链接 + star + **30 天提交数**
- 有幸存者才发通知（`dry-run` 不发），不做判断