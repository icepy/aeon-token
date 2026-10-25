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

**实证**：`SkillWeaver` 在 arxiv 是 09-28，GitHub 仓 10-08 —— **论文 → 代码滞后 10 天**。

**本通道的真实产出在 AI / 机器人侧**，加密侧顺带。

## 铁律

- **star 地板是反向的。** 新建仓库必然 ★0–2。默认 `min:0`。
- **star 测「发布时的传播」，commits 测「现在还有人在写」。判真伪只看 commits。** 实证：`Zero-WAM` ★439 五轮零提交 · `code-world-model` ★543 / 0 提交 · `PrismWAM` ★48 / 10 提交。
- **核验对象不能按创建时间取前 N**，长窗口下那批全是 ★0 噪声。按 star 分桶。
- **限速要重试，不能放弃。** 放弃会静默降级到未认证（10/min），把活仓标成空仓。**429（限速）和 409（真空仓）必须分开。**
- **description 越像论文，越要查 commits。**
- **只匹配 `in:name,description`，不要 readme。**
- **脏词必须配 carrier**（`world model` 已严重外溢，必须配具身词）。判据是 carrier **之后**的精度。
- **覆盖率必须报。** <50% 的词绝对数不可引用（`vla` 7.9% / `world model` 21.4% / `jepa` 44.3%）。总覆盖率 32.1% 已到顶。
- **缩写必然脏，用全称。**
- **`template` / `demo` / `sniper` = 练手仓库或农场。**
- **项目页/列表页要「名字像页 + 体量小」两个条件同时成立才丢。** 只看名字会误杀真代码仓（实证 4 个，含 `UniWAM` ★135）。
- **每条丢弃规则都要能被审计。** 丢掉的样本要列出来 —— 只看幸存者会得出「过滤器正常」的错误结论。
- **农场只认黑名单。** 「owner 有 3 个仓」只是**候选**，不是判决 —— 实证误杀过 `rzc156/dreamforge` ★130/21 提交、`Roboparty/P-BFM` ★95、`NEBULIS-Lab/D-JEPA` ★32/68 提交。
- **报「零命中」必须分开写：查询失败 / 真零命中 / 未核验。**
- **零命中不等于废词。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star + 30 天提交数。

## Config

读：
- `TERMS` 里的方向词
- `memory/github-seen.json` · `memory/github-farms.txt`（**黑名单，行内可带 `#` 注释**）

写：
- `memory/github-seen.json` — 全部幸存者（`dry-run` 不写）
- `memory/github-candidates.md` — 只写报告级
- `output/ghradar/` — `out.json` · `audit.log`
- `memory/logs/${today}.md` — 每次一条
- 通知：只在报告级 > 0 时发

## Steps

### 1. 解析 var

```bash
DRY=""; DAYS=30; MIN=0; CHK=5
# token == dry-run → DRY=1 | days:N → DAYS=N | min:N → MIN=N | chk:N → CHK=N
export DRY DAYS MIN CHK
```

### 2. 扫描

**写到 `output/ghradar/scan.py`（用 Write 工具，不要 heredoc）**，然后：

```bash
export DRY=$DRY DAYS=$DAYS MIN=$MIN CHK=$CHK
mkdir -p output/ghradar
python3 output/ghradar/scan.py
cat output/ghradar/audit.log
```

```python
#!/usr/bin/env python3
"""github-radar 扫描。脚本自己写 output/ghradar/ —— shell 重定向会被权限层拦。"""
import json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

OUTD = "output/ghradar"; OUT = OUTD + "/out.json"; AUD = OUTD + "/audit.log"
SEEN = "memory/github-seen.json"; CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"

DRY  = os.environ.get("DRY") == "1"
DAYS = int(os.environ.get("DAYS") or 30)
MIN  = int(os.environ.get("MIN") or 0)
CHK  = int(os.environ.get("CHK") or 5)
CHK_CAP = 250
REPORT_COMMITS = 5

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

# 脏词必须配 carrier。判据是 carrier **之后**的精度。
# world model 已严重外溢（自驾 / GUI agent / 游戏 / 音频 / 分子），必须配具身词。
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

# 黑名单：**剥掉行内注释**（否则 "name  # 说明" 整串当 key，匹配 0 个）
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
def gh_get(path):
    """返回 (data, err)。err=None 成功；'HTTP 409' 之类用于区分真空仓与限速。"""
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
                if ("rate limit" in last.lower() or "429" in last
                        or "403" in last or "secondary" in last.lower()):
                    time.sleep(5 * (i + 1)); continue
                break
            except Exception as ex:
                last = str(ex); time.sleep(3)
        print("  ! gh api 放弃: %s" % last[:140], file=sys.stderr)
        GH = False
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

def search(q):
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": "100"})
    return gh_get("search/repositories?" + qs)

def commits_30d(rid):
    """返回 (n, status)：ok / empty（真空仓 409）/ unverified（限速等）。"""
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    return (len(data) if isinstance(data, list) else None), "ok"

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "pages": 0, "farm": 0, "fail": 0}
hit, qfail, cov, per_term = {}, [], {}, {}
page_dropped = []          # 被 pages 规则丢掉的，进审计备查

for term in TERMS:
    total, got, failed = 0, 0, False
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        res, err = search(q)
        if res is None:
            print("! %s @%s: %s" % (term, w, err), file=sys.stderr)
            drop["fail"] += 1; failed = True; time.sleep(8); continue
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
            # 项目页 / 列表页：名字像页**且**体量小才算。
            # 实证：只看名字会误杀 —— 21 个被丢的里 4 个是真代码仓
            # （UniWAM 3.3MB/c30=20、DexTacWAM 3.0MB/c30=26、
            #   两个 .github.io 站点仓 75MB / 594MB）。
            size_kb = it.get("size", 0)
            if ((short.endswith(".github.io") or short.lower() == owner.lower())
                    and size_kb < 300):
                drop["pages"] += 1
                page_dropped.append((rid, size_kb))
                continue
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
                        "size_kb": size_kb,
                        "desc": " ".join(desc.split())[:140]})
            hit[rid] = out[-1]
        time.sleep(3 if GH else 8)
    if failed and not got:
        qfail.append(term)
    per_term[term] = len([c for c in out if c["term"] == term])
    if total:
        cov[term] = round(100.0 * got / total, 1)

# 核验：★>=CHK 全部，再按创建最新补齐
out.sort(key=lambda c: -c["stars"])
todo = [c for c in out if c["stars"] >= CHK]
if len(todo) < CHK_CAP:
    todo += sorted([c for c in out if c["stars"] < CHK],
                   key=lambda c: c["created"], reverse=True)[:CHK_CAP - len(todo)]
for c in todo:
    n, st = commits_30d(c["repo"])
    if st == "ok":
        c["commits_30d"] = n
        if n == 0:
            c["stale"] = True
    elif st == "empty":
        c["maybe_empty"] = True
    else:
        c["unverified"] = True

# owner>=3 只是「候选农场」，标记不丢
owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["owner_repos"] = owner_n[c["owner"]]

def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= REPORT_COMMITS
            and not c.get("stale") and not c.get("maybe_empty"))

rep = sorted([c for c in out if reportable(c)],
             key=lambda c: (-c["commits_30d"], -c["stars"]))

os.makedirs(OUTD, exist_ok=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

L = ["扫 %d 词 × %d 窗 | 原始 %d | 幸存 %d | 报告级 %d"
     % (len(TERMS), NWIN, raw, len(out), len(rep)),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d pages=%d "
     "farm=%d fail=%d" % (drop["seen"], drop["excl"], drop["archived"],
                          drop["short_desc"], drop["carrier"], drop["pages"],
                          drop["farm"], drop["fail"]),
     "核验 %d（★>=%d 全部 + 最新补齐，上限 %d）" % (len(todo), CHK, CHK_CAP),
     "黑名单载入 %d 个 owner" % len(farms),
     "词表命中: " + " · ".join("%s=%d" % (k, v) for k, v in
                              sorted(per_term.items(), key=lambda x: -x[1]))]
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % kv for kv in low.items()))
if qfail:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(qfail))
zero = [k for k, v in per_term.items() if v == 0 and k not in qfail]
if zero:
    L.append("⚠️ 真零命中: " + " · ".join(zero))
if page_dropped:
    L.append("ℹ️ 被 pages 规则丢弃 %d 个（可审计，体量<300KB）: %s"
             % (len(page_dropped),
                " · ".join("%s(%dKB)" % p for p in page_dropped[:15])))
uv = [c["repo"] for c in todo if c.get("unverified")]
if uv:
    L.append("⚠️ 未核验（限速，勿当空仓）%d 个: %s" % (len(uv), " · ".join(uv[:15])))
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交（star 在骗人）: " + " · ".join(stale))
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（409，只有 description）: " + " · ".join(empty))
cand = {o: n for o, n in owner_n.items() if n >= 3}
if cand:
    L.append("ℹ️ 候选农场（owner≥3，需人工判，非判决）: " +
             " · ".join("%s=%d" % kv for kv in cand.items()))
for c in rep[:25]:
    L.append("  %s [%s] %s ★%d commits30d=%d size=%dKB"
             % (c["created"], c["term"], c["repo"], c["stars"],
                c["commits_30d"], c["size_kb"]))
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

- `memory/logs/${today}.md` 追加一节，**分开写**：查询失败 / 真零 / 未核验 / 覆盖率低 / 核验结果
- 通知只发**报告级**，按方向词分组，每条给仓库 + 一句话 + 链接 + star + **30 天提交数**
- 报告级为 0 时不发通知