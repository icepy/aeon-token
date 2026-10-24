---
name: arxiv-radar
description: 扫 arXiv 新预印本，按话题词过滤，把命中的项目名推给我。只做发现，不做判断。
metadata:
  title: arXiv Radar
  category: crypto
  var: ""
  tags:
    - crypto
    - discovery
  capabilities:
    - external_api
    - sends_notifications
---

> **${var}** — 可选，空格分隔，可组合。`dry-run` 跳过 notify；`days:N` 换窗口（默认 7）；`names` 切到"机制/名字反查"模式（词表改读 `memory/universe-names.txt`）。

发现层的第一条通道。**词表在下面 `TERMS` 里，改词只改那一段。**

## 为什么用 arXiv

它是唯一"项目起源 + 有中心索引"的交叉点：论文先于主网、先于上市、先于叙事。PEARL 那篇 2026-06-03 的论文如果被扫到，提前量是 4 个月。

**但记住：arXiv 索引的是「机制」，不是「项目」。** 项目名（XMAQUINA）多半全期零命中；普通英文词（NOTE）会被英文用法污染。所以词表要写**持仓依赖的机制**，不是持仓的名字。

## 铁律

- **只用 `ti:`。** arXiv 的 `abs:` 是松散匹配（`abs:"MEV"` 会命中兆电子伏特）。绕不开时用 `cat:` 约束整条查询。
- **写长短语，不写单词。** 单词必然撞别的学科（MEV / SNARK / liquidation 都是这么死的）。多词**必须带引号**：`ti:foo bar` 会被解析成 `ti:foo AND bar`，后面的词掉成全字段搜索。
- **不做判断，不复述内容。** 只给名字 + 一句话 + 链接。
- **零命中不等于废词。** 可能是太前沿，也可能是没人写进标题——留观察，别删。

## Config

读：
- `memory/arxiv-seen.json` — 已见 arxiv id（跨 run 去重；key 不带版本后缀）
- `memory/MEMORY.md` — "Tracked Token" 与 Active Topics，用来标相关性
- `names` 模式额外读：`memory/universe-names.txt`

写：
- `memory/arxiv-seen.json` — 由脚本更新（`dry-run` 不写）
- `memory/logs/${today}.md` — 每次运行一条
- 通知：只在有幸存者时发

## Steps

### 1. 解析 var

按空格拆 `${var}`，逐个 token 判定，然后**用 `export` 单独一行导出**：

```bash
DRY=""; DAYS=7; NAMES=""
# token == dry-run  → DRY=1
# token == names    → NAMES=1
# token 形如 days:N → DAYS=N
export DRY DAYS NAMES
```

> 必须用 `export` 单独一行。`DRY=1 python3 ...` 这种前缀形式会被权限层拒，导致"dry-run 其实没 dry"。

### 2. 扫描

```bash
export DRY=$DRY DAYS=$DAYS NAMES=$NAMES
python3 - <<'PY' > /tmp/radar.json 2>/tmp/radar.log
import json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

NAMES_FILE = "memory/universe-names.txt"
NAMES_MODE = os.environ.get("NAMES") == "1"

# ── 词表：`#` 开头是注释。写「持仓依赖的机制」，不是持仓的名字 ──────
TERMS = [t.strip() for t in """
proof-of-useful-work
verifiable inference
light client
proof of training
proof of learning
verifiable training
auditable training
data availability sampling
restaking
automated market maker
consensus protocol
cat:cs.CR AND ti:"MEV"
liquid staking
embodied data
robot manipulation data
robot data
embodied AI
zero-knowledge
# ── 持仓依赖的机制（持仓是 NOTE / DEUS / PEARL）──
ti:"EIP-1559"
ti:"Robinhood Chain"
""".strip().split("\n") if t.strip() and not t.strip().startswith("#")]

# names 模式：拿机制/链名反查（词表整个换掉）
if NAMES_MODE:
    TERMS = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

# 已知名字表，用来给命中打一个 name 标签
known = []
if os.path.exists(NAMES_FILE):
    known = [l.strip() for l in open(NAMES_FILE, encoding="utf-8")
             if l.strip() and not l.startswith("#")]

CARRIER = ["deployed", "deployment", "mainnet", "testnet", "protocol",
           "production", "open-source", "released", "blockchain", "network",
           "token", "incentive", "marketplace", "validator", "miner"]
# 只对 title 判，且只留这两个：benchmark 是论文自称，不该丢
EXCL = ["survey", "tutorial"]
STOP = set("""a an the on of in for with from and or to at by as is are was were
towards toward via using based scalable efficient large language model models
learning deep neural network networks system systems new novel study analysis
empirical measurement framework approach method methods data theory practice
case real world beyond not all end how what why when where which that this""".split())

DAYS = int(os.environ.get("DAYS") or 7)
DRY  = os.environ.get("DRY") == "1"
SEEN = "memory/arxiv-seen.json"
API  = "https://export.arxiv.org/api/query"
NS   = {"a": "http://www.w3.org/2005/Atom"}

now = datetime.now(timezone.utc)
win = f"[{(now - timedelta(days=DAYS)):%Y%m%d%H%M} TO {now:%Y%m%d%H%M}]"

seen = {}
if os.path.exists(SEEN):
    try:
        seen = json.load(open(SEEN, encoding="utf-8"))
    except Exception:
        seen = {}

def guess_name(title, summ, known):
    for n in known:
        if re.search(rf"\b{re.escape(n)}\b", title + " " + summ, re.I):
            return n
    m = re.search(r"\b([A-Z][A-Za-z0-9\-]{2,})(?:'s|\u2019s)\b", title + " " + summ)
    if m:
        return m.group(1)
    for w in re.findall(r"\b[A-Z][A-Za-z0-9\-]{2,}\b", title):
        if w.lower() not in STOP:
            return w
    return ""

out, raw, newest = [], 0, ""
drop = {"seen": 0, "excl": 0, "carrier": 0, "fail": 0}

for term in TERMS:
    # 已经是完整查询的直接用；否则套 ti:。names 模式额外加领域限缩。
    if term.startswith(("cat:", "ti:", "abs:", "all:")):
        q = term
    elif NAMES_MODE:
        q = (f'ti:"{term}" AND (cat:cs.CR OR cat:cs.CE OR cat:cs.GT OR cat:cs.DC '
             'OR cat:q-fin.CP OR cat:q-fin.GN)')
    else:
        q = f'ti:"{term}"'

    p = {"search_query": f"({q}) AND submittedDate:{win}",
         "start": 0, "max_results": 100,
         "sortBy": "submittedDate", "sortOrder": "descending"}
    url = API + "?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            root = ET.fromstring(r.read())
    except Exception as ex:
        print(f"! {term}: {ex}", file=sys.stderr)
        drop["fail"] += 1
        time.sleep(3)
        continue

    for e in root.findall("a:entry", NS):
        raw += 1
        # 去掉版本后缀：v2 不该被当新命中重报
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        summ = " ".join(e.find("a:summary", NS).text.split())
        blob = (title + " " + summ).lower()
        pub = e.find("a:published", NS).text[:10]
        if pub > newest:
            newest = pub
        if aid in seen:
            drop["seen"] += 1
            continue
        if any(x in title.lower() for x in EXCL):
            drop["excl"] += 1
            continue
        if not any(c in blob for c in CARRIER):
            drop["carrier"] += 1
            continue
        out.append({"term": term, "name": guess_name(title, summ, known), "title": title,
                    "published": pub, "link": f"https://arxiv.org/abs/{aid}",
                    "carrier": next(c for c in CARRIER if c in blob)})
        seen[aid] = now.strftime("%Y-%m-%d")
    time.sleep(3)

out.sort(key=lambda c: c["published"], reverse=True)
print(f"扫 {len(TERMS)} 词 | 原始 {raw} | 幸存 {len(out)} | "
      f"丢弃 seen={drop['seen']} excl={drop['excl']} "
      f"carrier={drop['carrier']} fail={drop['fail']}", file=sys.stderr)
print(f"窗口内最新收录日期: {newest or '(无)'}  ← 比今天早 3 天以上即索引滞后，不是零命中",
      file=sys.stderr)
for c in out[:25]:
    print(f"  {c['published']} [{c['term']}] {c['title'][:85]}", file=sys.stderr)

if not DRY and out:
    json.dump(dict(list(seen.items())[-2000:]),
              open(SEEN, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
PY
cat /tmp/radar.log
```

### 3. 输出

- 幸存者写进 `memory/logs/${today}.md` 的 `### arxiv-radar` 一节
- 有幸存者才发通知（`dry-run` 不发）
- 只给名字 + 一句话 + 链接，按簇分组，不做判断