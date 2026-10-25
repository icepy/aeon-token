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

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（默认 30）；`min:N` 换 star 地板（默认 3）。

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

词表是**手抄 arxiv 那张当基准、再按平台改**的，不是自动同步的。两个平台词汇习惯不同：arxiv 写 `embodied data`，GitHub 写 `sim2real`。

## 铁律

- **仓库名 ≠ 代币名。** 只报仓库，别猜 ticker。要 ticker 得再查 GeckoTerminal。
- **star 是滞后指标。** 按 `created_at` 看，不按 star 排 —— 一个 3 star 的新仓库信息量大于一个 300 star 的老仓库。
- **缩写必然脏，用全称。** `MEV` / `ZK` / `DA` 在代码库里全是模板名和变量名。arxiv 那条「写长短语」在这里等价成立。
- **`template` / `demo` / `sniper` 这类词出现在 description 里，多半是练手仓库或机器人农场**，不是项目。
- **EXCL 只判 description。** readme 太长，全字段匹配会误杀正经项目。
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
DRY=""; DAYS=30; MIN=3
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
from datetime import datetime, timedelta, timezone

SEEN  = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"

DRY  = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN  = int(os.environ.get("MIN") or 3)

# ── 词表：从 arxiv-radar 那张抄基准，再按平台改成工程写法 ──
# `#` 开头是注释。改词只改这一段。
TERMS = [t.strip() for t in """
embodied data
robot manipulation
robot dataset
teleoperation
sim2real
world model
vla
verifiable inference
proof of useful work
data availability
restaking
intent-based
# 缩写必然脏：MEV / ZK / DA 在 GitHub 上全是模板和变量名，一律用全称
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

def gh_search(q):
    """优先 gh api（已认证，搜索限速 30/min）；退回未认证 urllib（10/min）。"""
    try:
        r = subprocess.run(
            ["gh", "api", "-X", "GET", "search/repositories",
             "-f", f"q={q}", "-f", "sort", "stars", "-f", "order", "desc",
             "-f", "per_page", "50"],
            capture_output=True, text=True, timeout=45)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout).get("items", [])
        print(f"  gh api rc={r.returncode} {r.stderr.strip()[:120]}", file=sys.stderr)
    except Exception as ex:
        print(f"  gh api 不可用: {ex}", file=sys.stderr)
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "sort": "stars", "order": "desc", "per_page": 50})
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "aeon-github-radar"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp).get("items", [])

# 先探一次认证：limit=30 正常，limit=10 说明退回未认证（要放慢退避）
try:
    r = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.search"],
                       capture_output=True, text=True, timeout=20)
    print("gh 认证探测: " + (r.stdout.strip() or r.stderr.strip()[:120]),
          file=sys.stderr)
except Exception as ex:
    print(f"gh 认证探测失败: {ex}", file=sys.stderr)

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "floor": 0, "fail": 0}
hit, raw_term = {}, {}

for term in TERMS:
    q = (f'"{term}" in:name,description,readme '
         f'created:>{since} fork:false stars:>={MIN}')
    try:
        items = gh_search(q)
    except Exception as ex:
        print(f"! {term}: {ex}", file=sys.stderr)
        drop["fail"] += 1; time.sleep(3); continue
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
        if len(desc) < 15:            # 一句话都写不满的，多半是练手仓库
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
    time.sleep(2)

# 按创建时间倒序：新仓库的信息量大于高 star
out.sort(key=lambda c: c["created"], reverse=True)
print(f"扫 {len(TERMS)} 词 | 原始 {raw} | 幸存 {len(out)} | "
      f"丢弃 seen={drop['seen']} excl={drop['excl']} "
      f"archived={drop['archived']} floor={drop['floor']} fail={drop['fail']}",
      file=sys.stderr)
print("词表原始命中: " + " · ".join(
      f"{k}={v}" for k, v in sorted(raw_term.items(), key=lambda x: -x[1])),
      file=sys.stderr)
wide = [k for k, v in raw_term.items() if v >= 50]
if wide:
    print(f"⚠️ 以下词可能太宽（返回满 50 条，只是 star 前 50）：{' · '.join(wide)}",
          file=sys.stderr)
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
- 有幸存者才发通知（`dry-run` 不发）
- 只给仓库 + 一句话 + 链接 + star，按方向词分组，不做判断