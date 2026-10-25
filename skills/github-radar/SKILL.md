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

- **`per_term == 0` 必须分四类，不能只报「真零」。** 有 seen 基线后，**饱和词会全部读成 0** —— 实证 12 个词被误标真零，逐词单查全部非空（`data availability` 60 天 total 126）。四类：查询失败 / 真零 / **全已见（饱和）** / 有新增。**「饱和」和「查不到」是完全不同的处置：前者留着，后者才谈删词。**
- **采样必须按「簇」保证覆盖，不能只按 star 分桶。** 实证：加密侧 35 仓里 34 个 ★0–2，连续六轮被误判为「空」。**核验宁可全量**（core 配额 5,000/h，与 search 独立池，1,231 仓 119 秒）。
- **缩写必然脏 —— 所以词表里不要放缩写。** 实证：`vla` 撞 VLAN/Vlad（污染 22%），`jepa` 撞 jepang/Jepara（14.5%）。带缩写就必须配 `NEG_BY_TERM`。
- **star 地板是反向的。** 默认 `min:0`。
- **star 测「发布时的传播」，commits 测「现在还有人在写」。判真伪只看 commits。**
- **30 天提交高 ≠ 现在在写。** 必须同时看近 7 天 —— 实证全量核验下 **222/402（55.2%）爆完即停**。
- **高提交数 ≠ 代码仓。** `dehype` 30d=100 是论文排行站、`diamond-cs2-v2` 100/100 是课程项目、`yifanliu-ai.github.io` 是个人主页。**必须看根目录形态 / language 字段。**
- **`commits=100` 是 `per_page` 上限，不是真值** —— 必须标成 `≥100`。
- **限速要重试，不能放弃。** **429（限速）和 409（真空仓）必须分开。gh 掉线必须在审计里显形。**
- **description 越像论文，越要查 commits。**
- **只匹配 `in:name,description`，不要 readme。**
- **脏词必须配 carrier**（`world model` 已严重外溢）。判据是 carrier **之后**的精度。
- **覆盖率必须报。** <50% 的词绝对数不可引用。
- **`template` / `demo` / `sniper` = 练手仓库或农场。**
- **项目页/列表页要「名字像页 + 体量小」两个条件同时成立才丢。** 别用 language 豁免 —— 静态站常被标 HTML/JS，会反向泄露。
- **每条丢弃规则都要能被审计。**
- **农场只认黑名单。** 「owner 有 3 个仓」只是**候选**。
- **根目录有 `AGENTS.md` / `CLAUDE.md` / `.clinerules` = 单人 + agent 一次性搭完**，不是长期工程团队。
- **报「零命中」必须分开写：查询失败 / 真零 / 全已见 / 未核验。**
- **不做判断。** 只给仓库 + 一句话 + 链接 + star + 30 天 / 7 天提交数。

## Config

读：
- `TERMS` 里的方向词
- `memory/github-seen.json` · `memory/github-farms.txt`（**黑名单，行内可带 `#` 注释**）

写：
- `memory/github-seen.json` — 全部幸存者（`dry-run` 不写）
- `memory/github-candidates.md` — 只写报告级
- `output/ghradar/` — `out.json` · `audit.log`
- `memory/logs/${today}.md` — 每次一条
- 通知：只在报告级 > 0 时发，**最多 `NOTIFY_TOP` 条**

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
CHK_CAP = 2000         # 核验上限（≈全量；core 配额独立于 search，很快）
PER_TERM_CAP = 25      # 超上限时每词保底，防低星簇失明
REPORT_COMMITS = 5
NOTIFY_TOP = 30
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

# 缩写词的子串污染：命中词撞到完全无关的同形串 → 直接否掉。
# 铁律「缩写必然脏」，所以词表里带缩写就必须在这里兜。
NEG_BY_TERM = {
    "vla": ["vlan", "vlad", "vladimir", "vladislav", "vladoss"],
    "jepa": ["jepang", "jepara", "jepan"],
}

# 脏词必须配 carrier（须与本行词同现才算命中）。判据是 carrier **之后**的精度。
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

# 黑名单：剥掉行内注释（否则 "name  # 说明" 整串当 key，匹配 0 个）
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
    """返回 (data, err)。err=None 成功；'HTTP 409' 用于区分真空仓与限速。"""
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
    """返回 (n, status)：ok / empty（真空仓 409）/ unverified（限速等）。"""
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    n = len(data) if isinstance(data, list) else None
    return n, "ok"

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "neg": 0, "pages": 0, "farm": 0, "fail": 0}
hit, qfail, cov = {}, [], {}
raw_term, new_term = {}, {}      # 返回条数（含已见） / 本轮新收
page_dropped, neg_dropped = [], []

for term in TERMS:
    total, got, failed = 0, 0, False
    raw_term[term] = 0; new_term[term] = 0
    neg = NEG_BY_TERM.get(term, [])
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
            got += len(items); raw_term[term] += len(items)
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
                # 缩写子串污染：名字或描述里出现否定词 → 丢
                lowall = (rid + " " + (it.get("description") or "")).lower()
                if neg and any(x in lowall for x in neg):
                    drop["neg"] += 1; neg_dropped.append(rid); continue
                size_kb = it.get("size", 0)
                # 项目页 / 列表页：名字像页**且**体量小才算（别用 language 豁免）
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
                            "topics": it.get("topics", [])[:6],
                            "size_kb": size_kb,
                            "language": it.get("language"),
                            "desc": " ".join(desc.split())[:140]})
                hit[rid] = out[-1]; new_term[term] += 1
            time.sleep(3 if GH else 8)
            if len(items) < 100:
                break
    if failed and not got:
        qfail.append(term)
    if total:
        cov[term] = round(100.0 * got / total, 1)

# ── 核验：全量（core 配额独立于 search，很快）──
# 超上限时按词保底，防低星簇失明。
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
    if st == "empty":
        c["maybe_empty"] = True; continue
    if st != "ok":
        c["unverified"] = True; continue
    c["commits_30d"] = n30
    if n30 >= 100:
        c["commits_30d_ge"] = True      # per_page 撞顶，是下限
    if n30 == 0:
        c["stale"] = True; continue
    n7, st7 = commits_since(c["repo"], 7)
    if st7 == "ok":
        c["commits_7d"] = n7
        if n7 >= 100:
            c["commits_7d_ge"] = True
        if n7 == 0:
            c["burst_only"] = True
    if not c.get("language"):
        c["no_lang"] = True             # 疑似非代码仓（排行站 / 课程项目 / 主页）

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

def fmt(c):
    return "%s ★%d 30d=%s%s 7d=%s" % (
        c["repo"], c["stars"],
        "≥100" if c.get("commits_30d_ge") else c.get("commits_30d"),
        " [爆完即停]" if c.get("burst_only") else "",
        "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"))

# ── per_term==0 四分类：查询失败 / 真零 / 全已见（饱和） / 有新增 ──
failed_t = list(qfail)
truly_zero = [t for t in TERMS if t not in qfail and raw_term.get(t, 0) == 0]
saturated  = [t for t in TERMS if raw_term.get(t, 0) > 0 and new_term.get(t, 0) == 0]
with_new   = [t for t in TERMS if new_term.get(t, 0) > 0]

L = ["扫 %d 词 × %d 窗 × %d 页 | 原始 %d | 幸存 %d | 报告级 %d"
     % (len(TERMS), NWIN, MAXPAGE, raw, len(out), len(rep)),
     "丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d neg=%d "
     "pages=%d farm=%d fail=%d" % (drop["seen"], drop["excl"], drop["archived"],
                                   drop["short_desc"], drop["carrier"],
                                   drop["neg"], drop["pages"], drop["farm"],
                                   drop["fail"]),
     "核验 %d（上限 %d）· 黑名单载入 %d 个 owner" % (len(todo), CHK_CAP, len(farms)),
     "词表四分类 —— 查询失败 %d / 真零 %d / 全已见(饱和) %d / 有新增 %d"
     % (len(failed_t), len(truly_zero), len(saturated), len(with_new))]
if failed_t:
    L.append("⚠️ 查询失败（不是零命中）: " + " · ".join(failed_t))
if truly_zero:
    L.append("⚠️ 真零命中（total=0，可考虑删词）: " + " · ".join(truly_zero))
if saturated:
    L.append("ℹ️ 全已见（饱和，**别删**）: " + " · ".join(
        "%s(raw=%d)" % (t, raw_term[t]) for t in saturated))
L.append("词表返回/新收: " + " · ".join(
    "%s=%d/%d" % (t, raw_term.get(t, 0), new_term.get(t, 0)) for t in
    sorted(TERMS, key=lambda x: -raw_term.get(x, 0))))
if gh_lost[0]:
    L.append("⚠️ gh 认证已丢失，降级未认证 —— 本轮完整性存疑")
low = {k: v for k, v in cov.items() if v < 50}
if low:
    L.append("⚠️ 覆盖率 <50%%（绝对数不可引用）: " +
             " · ".join("%s=%.1f%%" % kv for kv in low.items()))
if neg_dropped:
    L.append("ℹ️ 被 NEG 规则丢弃 %d 个（缩写同形污染）: %s"
             % (len(neg_dropped), " · ".join(neg_dropped[:12])))
if page_dropped:
    L.append("ℹ️ 被 pages 规则丢弃 %d 个（体量<300KB）: %s"
             % (len(page_dropped), " · ".join("%s(%dKB)" % p for p in page_dropped[:12])))
vt = Counter(c["term"] for c in todo)
L.append("逐词核验数: " + " · ".join("%s=%d" % (k, vt.get(k, 0)) for k in
                                     sorted(TERMS, key=lambda x: -vt.get(x, 0))))
uv = [c["repo"] for c in todo if c.get("unverified")]
if uv:
    L.append("⚠️ 未核验（限速，勿当空仓）%d: %s" % (len(uv), " · ".join(uv[:12])))
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    L.append("⚠️ 30 天零提交（star 在骗人）%d: %s" % (len(stale), " · ".join(stale[:15])))
burst = [c["repo"] for c in todo if c.get("burst_only")]
if burst:
    L.append("⚠️ 爆完即停（30d 有量 / 7d 归零）%d: %s"
             % (len(burst), " · ".join(burst[:15])))
nol = [c["repo"] for c in todo if c.get("no_lang")]
if nol:
    L.append("⚠️ 无 language 字段（疑似非代码仓）%d: %s"
             % (len(nol), " · ".join(nol[:12])))
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    L.append("⚠️ 空仓（409）: " + " · ".join(empty))
cand = {o: n for o, n in owner_n.items() if n >= 3}
if cand:
    L.append("ℹ️ 候选农场（owner≥3，需人工判）: " +
             " · ".join("%s=%d" % kv for kv in cand.items()))
for c in rep[:25]:
    L.append("  " + fmt(c))
open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

if not DRY and hit:
    stamp = now.strftime("%Y-%m-%d")
    merged = {k: stamp for k in hit}
    merged.update(seen)
    json.dump(dict(list(merged.items())[-8000:]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar（报告级 %d）\n" % (stamp, len(rep)))
        for c in rep:
            f.write("- [%s](%s) ★%d · 30d=%s 7d=%s%s · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"],
                       "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
                       "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
                       " [爆完即停]" if c.get("burst_only") else "",
                       c["term"], c["desc"][:100]))
```

### 3. 输出

- `memory/logs/${today}.md` 追加一节，**四分类必须分开写**
- 通知只发**报告级前 `NOTIFY_TOP` 条**，按 7 天提交数排序，每条给仓库 + 一句话 + 链接 + star + 30d/7d
- 报告级为 0 时不发通知