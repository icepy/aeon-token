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

**本通道的真实产出在 AI / 机器人侧**（2026-10-25 首轮实证：加密侧 60 天实质为空，机器人侧有成型的活跃信号）。加密词只是顺带。

词表是**手抄 arxiv 那张当基准、再按平台改**的，不是自动同步的。两个平台词汇习惯不同：arxiv 写 `embodied data`，GitHub 写 `sim2real`。

## 铁律

- **star 地板是反向的。** 新建仓库必然 ★0–2，**按 star 过滤 = 按「是否已被别人发现」过滤**，而本 skill 的全部价值就在提前量。默认 `min:0`；star 只用来排序和标记，不用来筛选。
- **只匹配 `in:name,description`，不要 readme。** readme 是长文档，加进来等于把词表降级成模糊搜索（实证：`data availability` 136 → 1，全是误中）。
- **仓库名 ≠ 代币名。** 只报仓库，别猜 ticker。
- **缩写必然脏，用全称。** `MEV` / `ZK` / `DA` 在代码库里全是模板名和变量名。
- **`template` / `demo` / `sniper` 这类词出现在 description 里，多半是练手仓库或机器人农场**，不是项目。
- **一个 owner 在本轮命中 ≥3 个仓库 = 仓库农场**（实证：`nirholas` 60 天建了 100 个仓库，主题横跨 3D avatar / x402 / Hyperliquid）。标记，不采信为主信号。
- **报「零命中」必须说清是查询失败还是真零。** 查询写错（参数形式、限速 403）会静默产出 0，**长得和「真没人写」一模一样**。两者要分别断言。
- **零命中不等于废词。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star。

## Config

读：
- 下面 `TERMS` 里的方向词
- `memory/github-seen.json` — 已见仓库（跨 run 去重）

写：
- `memory/github-seen.json` — 由脚本更新（`dry-run` 不写）
- `memory/github-candidates.md` — 追加候选，一行一个
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

> 必须 `export` 单独一行。`DRY=1 python3 ...` 前缀形式会被权限层拒，导致"dry-run 其实没 dry"。

### 2. 扫描

```bash
export DRY=$DRY DAYS=$DAYS MIN=$MIN
python3 - <<'PY' > /tmp/ghradar.json 2>/tmp/ghradar.log
import json, os, subprocess, sys, time, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

SEEN  = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"

DRY  = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN  = int(os.environ.get("MIN") or 0)

# ── 词表：AI/机器人侧是主战场（实证有真信号），加密侧是顺带 ──
# `#` 开头是注释。改词只改这一段。
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

# 只判 description。readme 太长，全字段匹配会误杀正经项目。
EXCL = ["awesome", "tutorial", "course", "survey", "cheatsheet", "roadmap",
        "interview", "homework", "assignment", "lecture", "book",
        # GitHub 特有的脏：模板仓库和交易机器人农场
        "template", "boilerplate", "starter", "example", "demo", "playground",
        "sniper", "sandwich", "airdrop", "faucet", "scaffold"]

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

since = (datetime.now(timezone.utc) - timedelta(days=DAYS)).strftime("%Y-%m-%d")

# gh api 的 query 必须整段塞进 path，用 -f 传会被拒
# （`accepts 1 arg(s), received 4` → 静默退回未认证 → 10/min 撞 403）
GH = True
def gh_search(q):
    """返回 (items, source)。source 决定退避：gh=2s，anon=7s。"""
    global GH
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "50"})
    if GH:
        try:
            r = subprocess.run(["gh", "api", f"search/repositories?{qs}"],
                               capture_output=True, text=True, timeout=45)
            if r.returncode == 0 and r.stdout.strip():
                return json.loads(r.stdout).get("items", []), "gh"
            print(f"  ! gh api 失败 rc={r.returncode}: {r.stderr.strip()[:140]}",
                  file=sys.stderr)
            GH = False
        except Exception as ex:
            print(f"  ! gh 不可用: {ex}", file=sys.stderr); GH = False
    url = "https://api.github.com/search/repositories?" + qs
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "aeon-github-radar"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp).get("items", []), "anon"

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "floor": 0, "fail": 0}
hit, raw_term, qfail = {}, {}, []

for term in TERMS:
    # 只判 name+description；stars 只排序不过滤（默认 MIN=0）
    q = (f'"{term}" in:name,description '
         f'created:>{since} fork:false stars:>={MIN}')
    try:
        items, src = gh_search(q)
    except Exception as ex:
        print(f"! {term}: {ex}", file=sys.stderr)
        drop["fail"] += 1; qfail.append(term); time.sleep(7); continue
    raw_term[term] = len(items)
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
        if len(desc) < 25:            # 一句话都写不满的，多半是练手仓库
            drop["floor"] += 1; continue
        if any(x in desc.lower() for x in EXCL):
            drop["excl"] += 1; continue
        rec = {"term": term, "terms": [term], "repo": rid,
               "owner": (it.get("owner") or {}).get("login", ""),
               "url": it["html_url"], "stars": it.get("stargazers_count", 0),
               "created": (it.get("created_at") or "")[:10],
               "topics": it.get("topics", [])[:6],
               "desc": " ".join(desc.split())[:140]}
        out.append(rec); hit[rid] = rec
    time.sleep(2 if src == "gh" else 7)

# 仓库农场标记：一个 owner 本轮 ≥3 个命中 → 标记，不丢
owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["farm"] = owner_n[c["owner"]]

out.sort(key=lambda c: c["created"], reverse=True)
print(f"扫 {len(TERMS)} 词 | 原始 {raw} | 幸存 {len(out)} | "
      f"丢弃 seen={drop['seen']} excl={drop['excl']} "
      f"archived={drop['archived']} floor={drop['floor']} fail={drop['fail']}",
      file=sys.stderr)
print("词表原始命中: " + " · ".join(
      f"{k}={v}" for k, v in sorted(raw_term.items(), key=lambda x: -x[1])),
      file=sys.stderr)
if qfail:
    print(f"⚠️ 查询失败（不是零命中）: {' · '.join(qfail)}", file=sys.stderr)
zero = [k for k, v in raw_term.items() if v == 0 and k not in qfail]
if zero:
    print(f"⚠️ 真零命中（查询成功但无结果）: {' · '.join(zero)}", file=sys.stderr)
farms = {o: n for o, n in owner_n.items() if n >= 3}
if farms:
    print("⚠️ 疑似仓库农场（owner=命中数）: " +
          " · ".join(f"{o}={n}" for o, n in farms.items()), file=sys.stderr)
for c in out[:25]:
    print(f"  {c['created']} [{c['term']}] {c['repo']} ★{c['stars']}", file=sys.stderr)

if not DRY and hit:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    merged = {k: now for k in hit}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-3000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write(f"\n## {now} · github-radar\n")
        for c in out:
            f.write(f"- [{c['repo']}]({c['url']}) ★{c['stars']} · "
                    f"`{c['term']}` · {c['desc'][:100]}\n")
print(json.dumps(out, ensure_ascii=False, indent=1))
PY
cat /tmp/ghradar.log
```

### 3. 输出

- 幸存者写进 `memory/logs/${today}.md` 的 `### github-radar` 一节
- **日志里必须分开写：查询失败 N 个词 / 真零命中 N 个词** —— 不能把查询失败讲成市场结论
- 有幸存者才发通知（`dry-run` 不发）
- 只给仓库 + 一句话 + 链接 + star，按方向词分组，不做判断