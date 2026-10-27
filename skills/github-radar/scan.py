#!/usr/bin/env python3
"""github-radar 扫描器（静态文件 —— 模型只调用，不重写）。

用法:
    python3 skills/github-radar/scan.py "days:30"
    python3 skills/github-radar/scan.py "days:60 probe"      # 额外跑专名簇反查

var token（空格分隔，可组合）:
    dry-run   跳过 notify、不写 seen、**不覆盖 out.json**（改写 out.dry.json）
    days:N    扫描窗口，默认 30
    min:N     star 地板，默认 0
    chk:N     核验门槛（仅在幸存数超 CHK_CAP 时启用），默认 5
    probe     强制跑专名簇反查（否则按 memory/ghradar-probe-last.txt 戳，≥7 天自动跑）
    --full    打全文审计到 stdout（默认只打 digest；全文永远落 audit.log）

probe 窗口固定 PROBE_WIN=60 天，**不跟 run 窗口**（它问的是「名字在不在积累」）。

产物（文件名固定，别改成 scan14.py / audit14.log）:
    output/ghradar/out.json       全部幸存者（非 dry-run）
    output/ghradar/out.dry.json   全部幸存者（dry-run；空数组不许覆盖上一轮真快照）
    output/ghradar/audit.log      审计全文（同时按 digest/full 打到 stdout）
    output/ghradar/report.md      通知正文（中文）
    output/ghradar/clusters.json  probe 时**必定重写**（空也写，好区分"没跑"和"跑了没货"）
    output/ghradar/dropped.json   **全量**丢弃名单（carrier / short_desc）+ carrier 存活对照
    memory/github-seen.json       非 dry-run 才写
    memory/github-candidates.md   非 dry-run 才追加
    memory/ghradar-probe-last.txt probe 成功且非 dry-run 才写戳

开跑前会清理 output/ghradar/：只保留上面这几个名字（`keep*` 前缀除外）。
"""
import json, os, re, subprocess, sys, threading, time
import urllib.error, urllib.parse, urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

VERSION = "gh-v3"        # 一版一投的版本锚点；印在审计首行

OUTD = "output/ghradar"
OUT, OUT_DRY = OUTD + "/out.json", OUTD + "/out.dry.json"
AUD, REPORT = OUTD + "/audit.log", OUTD + "/report.md"
CLUSTERS = OUTD + "/clusters.json"
DROPPED = OUTD + "/dropped.json"
SEEN = "memory/github-seen.json"
CARDS = "memory/github-candidates.md"
FARMS = "memory/github-farms.txt"
PROBE_STAMP = "memory/ghradar-probe-last.txt"

# output/ghradar/ 里只允许这些名字；其余每次开跑前删掉。`keep*` 前缀可跨轮保留。
KEEP = {"out.json", "out.dry.json", "audit.log", "report.md", "clusters.json",
        "dropped.json"}

CHK_CAP = 2000         # 幸存数 <= 这个值 → 全量核验，一个不漏
PER_TERM_CAP = 40      # 只在超上限时才启用（超上限时按词保底）
REPORT_COMMITS = 5
NOTIFY_TOP = 30
# 分页口径：subdivide-to-one-page。GitHub search 深翻页在 1000 条处封顶，所以
# 「整窗不拆 + 翻到 10 页」在长窗下必然截断（长窗比短窗更瞎）。改成：子窗只取一页，
# 子窗自身 total 仍超一页就对半再分 —— 覆盖率跟结果总数走，不再撞 1000 天花板。
WIN_TARGET = 100       # 每个子窗只取一页（= GitHub search 单页硬上限）→ 子窗容量 = 100
WIN_MAX = 200          # 单个词最多在飞多少个子窗（= 搜索调用上限，防超长窗打爆）
WIN_MAX_DEPTH = 7      # 子窗二分深度上限（防退化窗空转）
WIN_MIN_SPLIT = 3      # 整窗探针失败时的保守初始子窗数
SITE_SUFFIX = (".github.io", "-page", "-site", "-website", "-homepage", "-showcase",
               "-docs", "-web", "_web")
# `-web`/`_web` 是第十九轮补的：`brain-labbb/RFW_A_web` 的 desc 自述
# "RFW-A project website"，后缀却不在名单里被当报告级放行。这条是**无条件丢**，
# 所以另开 WEB_SUFFIX 计量，看会不会过杀真代码仓；过杀就退回 EXCL（desc 侧）那条窄路。
WEB_SUFFIX = ("-web", "_web")
SCAFFOLD_MIN = 3
SEARCH_MIN_GAP = 2.1   # search 限速 30/min
VERIFY_WORKERS = 6     # 核验并发（core quota 5000/h，但并发太高会触发二级限流）
VERIFY_BUDGET = 900    # 核验墙钟预算（秒）；超预算的标 unverified
PROBE_WORKERS = 6      # probe / carrier 热仓核验并发（原来是逐个串行）
PROBE_BUDGET = 240     # probe / carrier 并发阶段墙钟预算（秒）
CARRIER_PROBE_CAP = 150  # carrier 误杀抽核上限（owner 去重后）
PROBE_MAXTOK = 28      # probe: 最多反查多少个 token
PROBE_MAX_TOTAL = 600  # probe: 反查 total 超过这个 → 判为通用词，不是专名
PROBE_WIN = 60         # probe 窗口（天）。**独立于 run 窗口** —— 7 天窗下真簇与撞名
                       # 都在噪声底下面；名字在不在积累是周/月尺度的事。
PROBE_EVERY = 7        # probe 到期天数（戳判；跑挂不写戳 → 次日自愈）
# probe 历史种子池大小。**必须 ≈ hist 配额**，否则只有最近几条能当种子：
# 第十五轮实测 candidates 已 335 行 / 321 仓，只取最近 200 条 → 实际只有最近 24 条进池。
PROBE_HIST_POOL = 24
# probe 种子配额。顺序 = 优先级：报告级 → 幸存 → 历史报告级 → 本轮丢弃堆。
# 历史那一档是必须的：像 SuperMimic 这种簇，仓的 desc 不含任何词表词，连 raw 都进不去，
# 所以它既不在幸存、也不在丢弃堆 —— 只看本轮种子的 probe 永远抓不到它。
PROBE_QUOTA = (("rep", 12), ("out", 12), ("hist", 24), ("drop", 24))

# 根目录里有这些 = 真代码仓（用来否掉"页形态"）
CODE_SKELETON = {"src", "tests", "test", "pyproject.toml", "package.json",
                 "cargo.toml", "contracts", "crates", "app", "lib", "makefile",
                 "setup.py", "requirements.txt", "cmake", "go.mod", "build.gradle"}
# 反查时不该当专名的通用 token；也用来算簇内主题词（都要排除）
STOPWORDS = set("""world model models data robot robots learning sim sim2real agent
agents lab labs ai repo code page site github io project paper papers reproduce
reproduction experiments experiment baseline baselines implementation demo
official release training framework system systems control policy
python pytorch jax deep neural research tool tools llm main new real
simulation simulator dataset datasets benchmark benchmarks""".split())
# 主题词要额外排除的「胶水词」：虚词 + 到哪都有的通用名词。
# 与 STOPWORDS 分开：STOPWORDS 管「能不能当 probe token」，GLUE 只管「能不能当主题证据」。
# 第十六轮实证：3 个 cohesive 簇全假，其中 2 个的"主题词"就是 with / content ——
# 连接词被当成主题证据，而 senku 的 need 恰好 = 11，with 恰好 = 11，刚好踩线通过。
GLUE = set("""with without using use used uses based from into onto via your their
our its this that these those there here when where how what which all any some
more most other others same different very just also then than only such each both
can may will would could should has have had does did not own way ways thing things
part parts set sets get gets got make makes made take takes give gives need needs
know see look find work works working start starting end ending time times day days
week weeks month months year years version test tests testing note notes readme doc
docs git pip install setup run runs running build builds building create created
update updated add added fix fixed change changed support supports supported include
includes including feature features module modules package packages library
libraries script scripts app apps web api server client config configuration env
environment dev development prod production master branch commit commits license
author summary description overview intro introduction guide example examples
sample samples simple complex advanced basic quick fast slow high low large small
big tiny mini micro nano super ultra multi cross self auto semi non pre post sub
over under out up down off full first second third last next final file files code
project projects content""".split())
# 主题词还必须落在「我们这条线」的语义里 —— 簇再自洽，主题不是我们的题也不是信号。
# 反例（第十六轮）：uniview 主题词 hikvision/dahua 是海康大华 NVR，pouw 主题词 content。
# 注意 world / model / data / sim2real 仍在 STOPWORDS 里（通常就等于 token 本身），
# 所以这里列的是"允许作为主题词"的语义域，不是"允许作为 token"。
THEME_LEXICON = set("""embodied robot robotics manipulation manipulator teleop
teleoperation teleoperate sim2real sim-to-real egocentric action actions policy
policies vla vision language jepa world worlds model models data dataset datasets
benchmark benchmarks eval evaluation imitation navigation driving control planning
planner latent representation generative diffusion transformer rl reinforcement
inference verifiable proof useful work availability restaking intent intent-based
blockchain crypto onchain web3 solver swap defi amm wallet layer zk rollup
ethereum modular""".split())

# ── 词表：`#` 开头是注释 ──────────────────────────────────────────
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
# vla → 全称：实测双赢（污染 22%→1.4%，且 138/205 是旧口径从没抓到的新仓）
vision language action
# jepa 保留缩写：换全称损失 94.6%；且这一簇 ★0 与 commits 反相关，必须按 commits 读
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

NEG_BY_TERM = {
    "jepa": ["jepang", "jepara", "jepan"],
    "vla": ["vlan", "vlad", "vladimir", "vladislav", "vladoss"],
}

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

# ── var ───────────────────────────────────────────────────────────
var = sys.argv[1] if len(sys.argv) > 1 else ""
DRY, DAYS, MIN, CHK, PROBE, FULL, UNKNOWN = False, 30, 0, 5, False, False, []
for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok == "probe":
        PROBE = True
    elif tok == "--full":
        FULL = True
    elif tok.startswith("days:"):
        DAYS = int(tok.split(":", 1)[1] or 30)
    elif tok.startswith("min:"):
        MIN = int(tok.split(":", 1)[1] or 0)
    elif tok.startswith("chk:"):
        CHK = int(tok.split(":", 1)[1] or 5)
    else:
        UNKNOWN.append(tok)

T0 = time.time()
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
TODAY = now.strftime("%Y-%m-%d")
FMT = "%Y-%m-%dT%H:%M:%S+00:00"          # `created:` 收 ISO8601，秒粒度
FULLWIN = "%s..%s" % ((now - timedelta(days=DAYS)).strftime(FMT), now.strftime(FMT))
PROBE_FULLWIN = "%s..%s" % ((now - timedelta(days=PROBE_WIN)).strftime(FMT),
                            now.strftime(FMT))

def subwindows(n, days):
    """把 [now-days, now] 等分 n 个不重叠子窗（秒粒度）。只是二分的起点。"""
    span = timedelta(days=days)
    return ["%s..%s" % ((now - span * ((i + 1) / n)).strftime(FMT),
                        (now - span * (i / n)).strftime(FMT))
            for i in range(n)]

def split_window(w):
    """把 "lo..hi" 对半切；切不动（已到秒下限）返回 None。"""
    lo_s, hi_s = w.split("..")
    lo = datetime.strptime(lo_s, FMT); hi = datetime.strptime(hi_s, FMT)
    mid = (lo + (hi - lo) / 2).strftime(FMT)
    if mid in (lo_s, hi_s):
        return None
    return [lo_s + ".." + mid, mid + ".." + hi_s]

def round_no():
    """轮次号：按 candidates.md 里的分节数 + 1。dry-run 不追加，所以是预估。"""
    if not os.path.exists(CARDS):
        return 1
    try:
        txt = open(CARDS, encoding="utf-8").read()
    except Exception:
        return 1
    return len(re.findall(r"^## .*github-radar", txt, re.M)) + 1

def probe_due():
    """(是否该跑 probe, 原因)。显式 `probe` 无视戳；戳缺失/坏/≥PROBE_EVERY 天 → 跑。
    跑挂不写戳 → 次日自愈。dry-run 不写戳，所以会连着跑。"""
    if PROBE:
        return True, "显式"
    try:
        last = datetime.strptime(
            open(PROBE_STAMP, encoding="utf-8").read().strip()[:10], "%Y-%m-%d").date()
    except Exception:
        return True, "无戳/戳坏"
    age = (now.date() - last).days
    return (age >= PROBE_EVERY), ("戳 %d 天" % age)

# ── 清理：output/ghradar/ 只留固定产物 ──
# 前 13 轮在这儿攒了 150 个一次性旁路脚本和中间 json。靠代码强制清，
# 不靠模型记得删。想跨轮保留就给文件名加 `keep` 前缀。
cleaned = []
if os.path.isdir(OUTD):
    for nm in sorted(os.listdir(OUTD)):
        if nm in KEEP or nm.startswith("keep"):
            continue
        if os.path.isfile(os.path.join(OUTD, nm)):
            try:
                os.remove(os.path.join(OUTD, nm)); cleaned.append(nm)
            except OSError:
                pass

GH_LOCK = threading.Lock()
GH_COOLDOWN = 60           # gh 掉线后的冷却秒数；到期自动重试，不再整轮放弃
GH_DOWN_UNTIL = [0.0]
gh_lost = [False]
GH_LOST_N = [0]            # 掉线次数
GH_LAST_ERR = [""]         # 末次原因（进审计，以前只打 stderr）
GH_UNAUTH = [0]            # 冷却期间走未认证通道的调用次数

def gh_alive():
    return time.time() >= GH_DOWN_UNTIL[0]

def gh_down(reason):
    with GH_LOCK:
        GH_DOWN_UNTIL[0] = time.time() + GH_COOLDOWN
        GH_LOST_N[0] += 1
        GH_LAST_ERR[0] = reason[:160]
        if not gh_lost[0]:
            print("  ! gh api 放弃: %s" % reason[:140], file=sys.stderr)
            gh_lost[0] = True

def gh_get(path):
    """先走 gh api（认证）；失败则冷却 GH_COOLDOWN 秒后自动回来。
    429（限速）与 409（真空仓）必须分开 —— 409 不是认证失败，不该打掉认证态。
    404（不存在）同理。"""
    last = ""
    if gh_alive():
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
        # 404 / 409 是"这条记录的问题"，不是"认证坏了"
        if not any(x in last for x in ("404", "Not Found", "409",
                                       "empty repository", "Git Repository is empty")):
            gh_down(last)
    if gh_lost[0]:
        GH_UNAUTH[0] += 1
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

SEARCH_N = [0]             # 搜索调用计数（进审计，便于发现子窗爆炸）
_last_search = [0.0]
def search(q, page=1):
    gap = SEARCH_MIN_GAP - (time.time() - _last_search[0])
    if gap > 0:
        time.sleep(gap)
    _last_search[0] = time.time()
    SEARCH_N[0] += 1
    qs = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                 "per_page": str(WIN_TARGET), "page": str(page)})
    return gh_get("search/repositories?" + qs)

def commits_since(rid, days):
    qs = urllib.parse.urlencode({
        "since": (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "per_page": "100"})
    data, err = gh_get("repos/%s/commits?%s" % (rid, qs))
    if data is None:
        return None, ("empty" if err and "409" in err else "unverified")
    return (len(data) if isinstance(data, list) else None), "ok"

def load_history(limit=PROBE_HIST_POOL):
    """从 memory/github-candidates.md 抓历轮报告级仓名，给 probe 当历史种子。
    文件是追加写的，倒过来读 = 最近优先。
    **必须「最近一半 + 其余等距」**：只取最近 N 条时，candidates 越长老仓越饿死
    （第十五轮实测：335 行 / 321 仓，只取最近 200 条 → 实际只有最近 24 条能当种子）。"""
    if not os.path.exists(CARDS):
        return []
    try:
        txt = open(CARDS, encoding="utf-8").read()
    except Exception:
        return []
    found = []
    for rid in reversed(re.findall(r"\]\(https://github\.com/([^/\s]+/[^/)\s]+)\)", txt)):
        if rid not in found:
            found.append(rid)
    if len(found) <= limit:
        return found
    half = max(1, limit // 2)
    rest = found[half:]
    stride = max(1, len(rest) // max(1, limit - half))
    return found[:half] + rest[::stride][:limit - half]

def cluster_cohesion(items, token):
    """簇内同主题度。真专名簇（一个工作被大量复现）的 desc 会反复出现同一批词；
    撞名簇各写各的。返回 (是否同主题, [(词, 出现仓数), …])。
    **`total` 小只是必要条件，簇内同主题也只是必要条件** —— 第十六轮 3 个 cohesive
    簇全假，因为"主题词"可能是 with / content 这类胶水词。所以主题词还必须落在
    THEME_LEXICON 里（由调用方判 `thematic`）。
    阈值 max(3, ceil(n/5)) 是首版，下一轮用真实分布校准。
    **已知洞（第十九轮确认）**：真簇（supermimic 61 仓）恰恰是各仓各写各的 desc，
    13 个仓共享同一个词的门槛过不去 → 被误判为异质。这是 v4 要动的点。"""
    n = len(items)
    if n < 2:
        return False, []
    cnt = Counter()
    for it in items:
        words = {w for w in re.split(r"[^a-z0-9]+",
                                     (it.get("description") or "").lower())
                 if len(w) >= 4 and not w.isdigit()
                 and w not in STOPWORDS and w not in GLUE and w != token}
        cnt.update(words)
    need = max(3, (n + 4) // 5)
    theme = [[w, c] for w, c in cnt.most_common(40) if c >= need][:8]
    return (len(theme) > 0), theme

# ── 扫描 ──────────────────────────────────────────────────────────
out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "neg": 0, "pages": 0, "pages_root": 0, "farm": 0, "fail": 0}
hit, qfail, cov = {}, [], {}
raw_term, new_term, seen_term = {}, {}, {}
page_dropped, neg_dropped, root_dropped, web_dropped = [], [], [], []
carrier_topic_only, desc_topic_only = [], []      # 两条放行路径，单独记账
capped = []                                       # 二分到顶仍超一页的叶子窗（有截断）
win_whole, win_split = 0, 0                       # 自适应窗口：单窗 / 需拆窗 的词数
SPLIT_N = [0]                                     # 二分次数
# carrier / short_desc 丢掉的仓 —— **全量**存（可审计性 + probe 的第四顺位种子）。
# 之前只累加计数，是本轮唯一两条不落仓名的丢弃规则（第十五轮判据 37）。
carrier_dropped, short_desc_dropped = [], []

for term in TERMS:
    total, got, failed = 0, 0, False
    raw_term[term] = 0; new_term[term] = 0; seen_term[term] = 0
    neg = NEG_BY_TERM.get(term, [])
    # 先探一次整窗 total 定初始子窗数。subdivide-to-one-page：每个子窗只取 page 1，
    # 于是不再撞「深翻页 1000 条封顶」—— 原来长窗（total>1000）比短窗更瞎。
    q_whole = ('"%s" in:name,description created:%s fork:false stars:>=%d'
               % (term, FULLWIN, MIN))
    whole_res, _ = search(q_whole, 1)
    if whole_res is None:
        nwin = WIN_MIN_SPLIT; win_split += 1
    else:
        nwin = max(1, min(WIN_MAX, -(-whole_res.get("total_count", 0) // WIN_TARGET)))
        if nwin == 1:
            win_whole += 1
        else:
            win_split += 1
    # 队列元素 (窗口, 深度)。初始 nwin 等分只是起点；任何子窗自身 total 仍超一页
    # 就对半再分，切到 ≤一页为止 —— 子窗日期不均匀（周中/周末、发布潮）也吃不掉覆盖率。
    if nwin == 1 and whole_res is not None:
        queue = [(FULLWIN, 0)]; reuse_root = True
    else:
        queue = [(w, 0) for w in subwindows(nwin, DAYS)]; reuse_root = False
    while queue:
        w, depth = queue.pop(0)
        if reuse_root:
            res, err = whole_res, None; reuse_root = False
        else:
            q = ('"%s" in:name,description created:%s fork:false stars:>=%d'
                 % (term, w, MIN))
            res, err = search(q, 1)
        if res is None:
            print("! %s @%s: %s" % (term, w, err), file=sys.stderr)
            drop["fail"] += 1; failed = True; continue
        t = res.get("total_count", 0)
        kids = split_window(w)
        if (t > WIN_TARGET and kids and depth < WIN_MAX_DEPTH
                and len(queue) + 2 <= WIN_MAX):
            queue.extend((k, depth + 1) for k in kids)
            SPLIT_N[0] += 1
            continue                  # 父窗丢弃，由两个子窗覆盖（免得 total 重复计）
        total += t
        if t > WIN_TARGET:
            capped.append((term, w, t))   # 到顶了还超一页 → 该叶子窗有截断
        items = res.get("items", [])
        got += len(items); raw_term[term] += len(items)
        for it in items:
            raw += 1
            rid = it["full_name"]
            owner = (it.get("owner") or {}).get("login", "")
            short = rid.split("/")[-1]
            if rid in seen:
                drop["seen"] += 1; seen_term[term] += 1; continue
            if rid in hit:
                hit[rid]["terms"].append(term)
                drop["seen"] += 1; seen_term[term] += 1; continue
            if it.get("archived"):
                drop["archived"] += 1; continue
            lang = it.get("language")
            lowall = (rid + " " + (it.get("description") or "")).lower()
            if neg and any(x in lowall for x in neg):
                drop["neg"] += 1; neg_dropped.append(rid); continue
            size_kb = it.get("size", 0)
            # 站点仓：按后缀**无条件**丢 —— 体量不是判据（304MB 静态站照样是站）
            if short.lower().endswith(SITE_SUFFIX):
                drop["pages"] += 1
                page_dropped.append((rid, size_kb))
                if short.lower().endswith(WEB_SUFFIX):
                    web_dropped.append(rid)      # 新后缀单独计量，便于判过杀
                continue
            # 同名仓：可能是真代码仓（UniWAM/UniWAM），也可能是个人主页
            if (short.lower() == owner.lower() and size_kb < 300
                    and not lang):
                drop["pages"] += 1
                page_dropped.append((rid, size_kb)); continue
            desc = (it.get("description") or "").strip()
            topics = [str(x).lower() for x in (it.get("topics") or [])]
            # carrier 用 desc ∪ topics；EXCL 仍只看 name+desc（否则会放走 awesome 列表仓）
            blob_t = (desc + " " + " ".join(topics)).lower()
            if len(desc) < 25:
                if not topics:
                    drop["short_desc"] += 1
                    short_desc_dropped.append((it.get("pushed_at") or "", rid))
                    continue
                desc_topic_only.append(rid)     # 空/短 desc 靠 topics 放行
            if any(x in lowall for x in EXCL):
                drop["excl"] += 1; continue
            need = CARRIER_BY_TERM.get(term)
            if need and not any(c in blob_t for c in need):
                drop["carrier"] += 1
                carrier_dropped.append((it.get("pushed_at") or "", rid))
                continue
            if need and not any(c in desc.lower() for c in need):
                carrier_topic_only.append(rid)  # 只靠 topics 过的 carrier
            if owner.lower() in farms:
                drop["farm"] += 1; continue
            out.append({"term": term, "terms": [term], "repo": rid,
                        "owner": owner, "url": it["html_url"],
                        "stars": it.get("stargazers_count", 0),
                        "created": (it.get("created_at") or "")[:10],
                        "topics": topics[:6],
                        "size_kb": size_kb, "language": lang,
                        "desc": " ".join(desc.split())[:140]})
            hit[rid] = out[-1]; new_term[term] += 1
    if failed and not got:
        qfail.append(term)
    if total:
        cov[term] = round(100.0 * got / total, 1)

T_SEARCH = time.time() - T0

# ── 共享脚手架：owner 黑名单抓不到 ──
byname = {}
for c in out:
    byname.setdefault(c["repo"].split("/")[-1].lower(), []).append(c)
scaffold = []
for nm, lst in byname.items():
    if len({c["owner"] for c in lst}) >= SCAFFOLD_MIN:
        pref, n = Counter(c["desc"][:80] for c in lst).most_common(1)[0]
        if n >= SCAFFOLD_MIN:
            for c in lst:
                if c["desc"][:80] == pref:
                    c["scaffold"] = True; scaffold.append(c["repo"])
out = [c for c in out if not c.get("scaffold")]

# ── pages 根目录规则（三次独立复现后固化）──
# index.html + .nojekyll 且根目录无任何代码骨架 → 页。体积不做豁免。
def is_page_repo(rid):
    data, _ = gh_get("repos/%s/contents" % rid)
    if not isinstance(data, list):
        return False
    names = {str(x.get("name", "")).lower() for x in data}
    return ("index.html" in names and ".nojekyll" in names
            and not (names & CODE_SKELETON))

if out:
    # 4 路：并发太高会把 gh 打成二级限流
    with ThreadPoolExecutor(max_workers=4) as ex:
        flags = list(ex.map(is_page_repo, [c["repo"] for c in out]))
    kept = []
    for c, isp in zip(out, flags):
        if isp:
            drop["pages_root"] += 1; root_dropped.append(c["repo"])
        else:
            kept.append(c)
    out = kept

# ── 核验：幸存数不超上限就**全量**；并发 + 墙钟预算 ──
if len(out) <= CHK_CAP:
    todo = list(out)
    verify_mode = "全量"
else:
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
    verify_mode = "抽样(超上限)"

DEADLINE = time.time() + VERIFY_BUDGET

def verify_one(c):
    if time.time() > DEADLINE:
        c["unverified"] = True; return
    n30, st = commits_since(c["repo"], 30)
    if st == "empty":
        c["maybe_empty"] = True; return
    if st != "ok":
        c["unverified"] = True; return
    c["commits_30d"] = n30
    if n30 >= 100:
        c["commits_30d_ge"] = True
    if n30 == 0:
        c["stale"] = True; return
    n7, st7 = commits_since(c["repo"], 7)
    if st7 == "ok":
        c["commits_7d"] = n7
        if n7 >= 100:
            c["commits_7d_ge"] = True
        if n7 == 0:
            c["burst_only"] = True
    if not c.get("language"):
        c["no_lang"] = True

T_V0 = time.time()
with ThreadPoolExecutor(max_workers=VERIFY_WORKERS) as ex:
    list(ex.map(verify_one, todo))
T_VERIFY = time.time() - T_V0

owner_n = Counter(c["owner"] for c in out)
for c in out:
    if owner_n[c["owner"]] >= 3:
        c["owner_repos"] = owner_n[c["owner"]]

def reportable(c):
    return (c.get("commits_30d") is not None and c["commits_30d"] >= REPORT_COMMITS
            and not c.get("stale") and not c.get("maybe_empty"))

rep = sorted([c for c in out if reportable(c)],
             key=lambda c: (-c.get("commits_7d", 0), -c["commits_30d"], -c["stars"]))

# ── carrier 误杀率（第十六轮判据：dropped.json 上线后第一次可算）──
# 口径：carrier 丢弃名单里「仓名自带词表词」的那批（= 名字上明确属于这条线却被丢的），
# owner 去重后并发核近 7 天存活，与「放行的幸存者」存活率**对照**。
# 只给两个数，不下结论 —— 放宽 carrier 必须对照（参照 `jepa`→全称 654→35）。
NAME_TOKENS = {tk for t in TERMS for tk in re.split(r"[^a-z0-9]+", t.lower())
               if len(tk) >= 4 and not tk.isdigit()}
for _ws in CARRIER_BY_TERM.values():
    NAME_TOKENS.update(_ws)
carrier_named = [rid for _, rid in sorted(carrier_dropped, reverse=True)
                 if any(tk in rid.lower() for tk in NAME_TOKENS)]
_cown, carrier_named_uniq = set(), []
for rid in carrier_named:
    ow = rid.split("/")[0].lower()
    if ow in _cown:
        continue
    _cown.add(ow); carrier_named_uniq.append(rid)
carrier_probe = carrier_named_uniq[:CARRIER_PROBE_CAP]
CARRIER_ALIVE = {}

def carrier_alive(rid):
    if time.time() > C_DEADLINE:
        return
    n7, st = commits_since(rid, 7)
    if st == "ok" and n7 is not None:
        CARRIER_ALIVE[rid] = n7

if carrier_probe:
    C_DEADLINE = time.time() + PROBE_BUDGET
    with ThreadPoolExecutor(max_workers=PROBE_WORKERS) as ex:
        list(ex.map(carrier_alive, carrier_probe))

_ctrl = [c for c in out if c.get("commits_7d") is not None]
ctrl_alive = sum(1 for c in _ctrl if c["commits_7d"] > 0)
car_alive = sum(1 for v in CARRIER_ALIVE.values() if v > 0)

os.makedirs(OUTD, exist_ok=True)
# dry-run 不覆盖 out.json —— 否则一次 0 幸存就会把上一轮的真快照写成 "[]"
SNAP = OUT_DRY if DRY else OUT
json.dump(out, open(SNAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# 全量丢弃名单，每次无条件重写（空也写）—— 让「carrier 误杀率」可直接算，不必离线重放
json.dump({"carrier": [r for _, r in carrier_dropped],
           "short_desc": [r for _, r in short_desc_dropped],
           "carrier_named_uniq": carrier_named_uniq,
           "carrier_named_alive_7d": {r: v for r, v in CARRIER_ALIVE.items() if v > 0}},
          open(DROPPED, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── probe：反查找词表漏掉的专名簇 ──
# 种子池必须是「报告级 → 幸存 → 历史报告级 → 本轮丢弃堆」四级。
# 只看本轮会在两种情况下空转：幸存 0（第十三轮）和"该抓的簇本轮恰好没有命中"（第十四轮）。
# 顺序必须是「先反查、再排序」—— 按 token 在种子里出现几次排会漏掉
# SuperMimic（它只出现 1 次，被 capstone/recall 这类通用词挤掉）。
# 专名判据（三条，缺一不可）：① 反查 total 小；② 簇内同主题（cluster_cohesion）；
# ③ 主题词落在 THEME_LEXICON 语义内（`thematic`）。只有 ① 会误报（eidolon/senku/
# physguard 全是撞名）；只有 ①② 也会误报（第十六轮 3 个 cohesive 簇全假，主题词是
# with / content / hikvision 这类胶水词或非本线专名）。
# 窗口固定 PROBE_WIN，**不跟 run 窗口** —— 名字在不在积累是周/月尺度的事。
# 阶段 1 串行反查（受 SEARCH_MIN_GAP 约束）；阶段 2 并发核热仓 commits。
RUN_PROBE, PROBE_WHY = probe_due()
drop_names = sorted(carrier_dropped + short_desc_dropped, reverse=True)
cluster_report = []
probe_stat = {"rep": 0, "out": 0, "hist": 0, "drop": 0, "tok": 0, "done": 0,
              "seeds": 0, "hot": 0, "hot_quiet": 0}
if RUN_PROBE:
    srcs = (("rep", [c["repo"] for c in rep]),
            ("out", [c["repo"] for c in out]),
            ("hist", load_history()),
            ("drop", [r for _, r in drop_names]))
    seeds = []
    for tag, lst in srcs:
        n0 = len(seeds)
        for rid in lst[:dict(PROBE_QUOTA)[tag]]:
            if rid not in seeds:
                seeds.append(rid)
        probe_stat[tag] = len(seeds) - n0
    probe_stat["seeds"] = len(seeds)
    toks = []
    for rid in seeds:
        for tk in re.split(r"[-_./]", rid.split("/")[-1].lower()):
            if (len(tk) >= 4 and tk not in STOPWORDS
                    and not tk.isdigit() and tk not in toks):
                toks.append(tk)
    probe_stat["tok"] = len(toks)
    in_out = {c["repo"] for c in out}
    pending = []
    for tk in toks[:PROBE_MAXTOK]:
        res, err = search('"%s" in:name,description created:%s fork:false'
                          % (tk, PROBE_FULLWIN))
        if res is None:
            continue
        total = res.get("total_count", 0)
        items = res.get("items", [])
        owners = {(i.get("owner") or {}).get("login", "") for i in items}
        cohesive, theme = cluster_cohesion(items, tk)
        thematic = any(w in THEME_LEXICON for w, _ in theme)
        for i in items[:8]:
            pending.append((tk, i["full_name"], i.get("stargazers_count", 0)))
        cluster_report.append({
            "token": tk, "total": total, "owners": len(owners),
            "cohesive": cohesive, "thematic": thematic, "theme": theme,
            "one_man": len(owners) <= 2 and total >= 3,
            "generic": total > PROBE_MAX_TOTAL,
            "not_in_out": sum(1 for i in items if i["full_name"] not in in_out),
            "hot": []})
        probe_stat["done"] += 1
    # 阶段 2：热仓 commits 并发核验（原来逐个串行，probe 吃掉脚本近一半墙钟）
    hot_repos = sorted({r for _, r, _ in pending})
    probe_stat["hot"] = len(hot_repos)
    HOT = {}
    P_DEADLINE = time.time() + PROBE_BUDGET

    def probe_hot(rid):
        if time.time() > P_DEADLINE:
            return
        n30, st = commits_since(rid, 30)
        if st != "ok" or not n30 or n30 < REPORT_COMMITS:
            return
        n7, st7 = commits_since(rid, 7)
        HOT[rid] = (n30, n7 if st7 == "ok" else None)

    if hot_repos:
        with ThreadPoolExecutor(max_workers=PROBE_WORKERS) as ex:
            list(ex.map(probe_hot, hot_repos))
    probe_stat["hot_quiet"] = len(hot_repos) - len(HOT)
    by_tok = {cl["token"]: cl for cl in cluster_report}
    for tk, rid, st in pending:
        cl = by_tok.get(tk)
        if cl is not None and rid in HOT:
            cl["hot"].append({"repo": rid, "stars": st,
                              "commits_30d": HOT[rid][0], "commits_7d": HOT[rid][1]})
    for cl in cluster_report:
        cl["hot"].sort(key=lambda x: (-(x["commits_7d"] or 0), -x["commits_30d"]))
        cl["hot"] = cl["hot"][:8]
    # 专名优先：非通用词 → **同主题且主题词是本线的** → 簇内活跃仓多 → owner 密度高
    cluster_report.sort(key=lambda x: (x["generic"],
                                       not (x["cohesive"] and x["thematic"]),
                                       -len(x["hot"]), -x["owners"]))
    # **无条件重写** —— 空数组也要写，否则上一轮的 clusters.json 会冒充本轮结果
    json.dump(cluster_report, open(CLUSTERS, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    # 戳只在「跑了 + 非 dry-run」时写；跑挂不写 → 次日自愈
    if not DRY:
        try:
            open(PROBE_STAMP, "w", encoding="utf-8").write(TODAY + "\n")
        except OSError:
            pass

def fmt(c):
    return "%s ★%d 30d=%s%s 7d=%s%s" % (
        c["repo"], c["stars"],
        "≥100" if c.get("commits_30d_ge") else c.get("commits_30d"),
        " [爆完即停]" if c.get("burst_only") else "",
        "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
        "" if c.get("language") else " [无语言]")

failed_t = list(qfail)
truly_zero = [t for t in TERMS if t not in qfail and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and new_term.get(t, 0) == 0]
with_new = [t for t in TERMS if new_term.get(t, 0) > 0]
sat_seen = [t for t in saturated if seen_term.get(t, 0) > 0]
sat_loss = [t for t in saturated if seen_term.get(t, 0) == 0]

# 审计分两层：L = 全文（永远落 audit.log）；D = digest（默认打 stdout）。
# `--full` 时 stdout 打 L。要补字段就补 digest，别让模型去补工具调用。
L, D = [], []
def A(line, d=False):
    L.append(line)
    if d:
        D.append(line)

A("github-radar %s · 第 %d 轮%s · 扫 %d 词 × 二分至一页（单窗 %d / 需拆窗 %d · "
  "二分 %d 次 · 搜索调用 %d）| 原始 %d | 幸存 %d | 报告级 %d | var=%r"
  % (VERSION, round_no(), "（dry-run 不递增）" if DRY else "", len(TERMS),
     win_whole, win_split, SPLIT_N[0], SEARCH_N[0], raw, len(out), len(rep), var),
  d=True)
A("全文 %s%s" % (AUD, "" if FULL else "（stdout 只打 digest；加 --full 打全文）"), d=True)
A("快照 %s%s" % (SNAP, "（dry-run 不覆盖 out.json）" if DRY else ""), d=True)
A("丢弃 seen=%d excl=%d archived=%d short_desc=%d carrier=%d neg=%d "
  "pages=%d pages_root=%d scaffold=%d farm=%d fail=%d"
  % (drop["seen"], drop["excl"], drop["archived"], drop["short_desc"],
     drop["carrier"], drop["neg"], drop["pages"], drop["pages_root"],
     len(scaffold), drop["farm"], drop["fail"]), d=True)
A("核验 %d/%d (%.1f%%) · 模式 %s · 黑名单 %d owner"
  % (len(todo), len(out), 100.0 * len(todo) / max(len(out), 1),
     verify_mode, len(farms)), d=True)
A("词表四分类 —— 查询失败 %d / 真零 %d / 全已见(饱和) %d / 有新增 %d"
  % (len(failed_t), len(truly_zero), len(saturated), len(with_new)), d=True)
A("耗时 搜索 %.0fs · 核验 %.0fs · 总 %.0fs"
  % (T_SEARCH, T_VERIFY, time.time() - T0), d=True)
if cleaned:
    A("🧹 清理 output/ghradar/ 历史文件 %d 个（只留 %s；`keep*` 前缀可跨轮保留）: %s"
      % (len(cleaned), " / ".join(sorted(KEEP)),
         " · ".join(cleaned[:12]) + (" …" if len(cleaned) > 12 else "")))
if capped:
    A("ℹ️ 子窗自身 total>%d 且已到二分上限（该叶子窗有截断）%d 个: %s"
      % (WIN_TARGET, len(capped),
         " · ".join("%s@%s(total=%d)" % c for c in capped[:8])), d=True)
if web_dropped:
    A("ℹ️ 新后缀 -web/_web 命中 %d 个（无条件丢；看会不会过杀真代码仓）: %s"
      % (len(web_dropped), " · ".join(web_dropped[:12])), d=True)
if carrier_topic_only:
    A("ℹ️ carrier 只靠 topics 放行 %d 个（desc 里没有 carrier 词）: %s"
      % (len(carrier_topic_only), " · ".join(carrier_topic_only[:12])))
if desc_topic_only:
    A("ℹ️ 空/短 desc 靠 topics 放行 %d 个: %s"
      % (len(desc_topic_only), " · ".join(desc_topic_only[:12])))
if carrier_dropped:
    A("ℹ️ 被 carrier 规则丢弃 %d 个（desc 与 topics 均无 carrier 词）"
      "—— 全量在 dropped.json，最近 20: %s"
      % (len(carrier_dropped),
         " · ".join("%s(%s)" % (r, p[:10])
                    for p, r in sorted(carrier_dropped, reverse=True)[:20])))
    A("ℹ️ carrier 误杀口径（对照，不下结论）：丢弃里仓名自带词表词 %d 个，"
      "owner 去重 %d 个，本轮核 %d 个 → 近 7 天存活 %d/%d = %s"
      % (len(carrier_named), len(carrier_named_uniq), len(CARRIER_ALIVE),
         car_alive, len(CARRIER_ALIVE),
         "%.0f%%" % (100.0 * car_alive / len(CARRIER_ALIVE))
         if CARRIER_ALIVE else "n/a"), d=True)
    A("   对照（放行的幸存者，已核 %d）：近 7 天存活 %d/%d = %s"
      % (len(_ctrl), ctrl_alive, len(_ctrl),
         "%.0f%%" % (100.0 * ctrl_alive / len(_ctrl)) if _ctrl else "n/a"), d=True)
if short_desc_dropped:
    A("ℹ️ 被 short_desc 规则丢弃 %d 个（len(desc)<25 且无 topics）"
      "—— 全量在 dropped.json，最近 20: %s"
      % (len(short_desc_dropped),
         " · ".join("%s(%s)" % (r, p[:10])
                    for p, r in sorted(short_desc_dropped, reverse=True)[:20])))
if UNKNOWN:
    A("⚠️ 未识别 var token（会被静默忽略）: " + " · ".join(UNKNOWN), d=True)
if failed_t:
    A("⚠️ 查询失败（不是零命中）: " + " · ".join(failed_t), d=True)
if truly_zero:
    A("⚠️ 真零命中（total=0，可考虑删词）: " + " · ".join(truly_zero), d=True)
if saturated:
    # 「饱和」这个标签本身是混的：new_term 只在全部过滤器跑完之后才自增，
    # 所以「被 carrier/short_desc 丢光」和「真被 seen 吸收」会落进同一类。必须拆开。
    A("ℹ️ 饱和（raw>0 且 0 新增）%d —— 其中真被 seen 吸收 %d 个（**别删**）: %s"
      % (len(saturated), len(sat_seen),
         " · ".join("%s(raw=%d seen=%d)" % (t, raw_term[t], seen_term[t])
                    for t in sat_seen)), d=True)
    if sat_loss:
        A("   └ 全是过滤损耗 %d 个（seen=0，**不是饱和**，别按饱和读）: %s"
          % (len(sat_loss), " · ".join("%s(raw=%d)" % (t, raw_term[t])
                                       for t in sat_loss)), d=True)
A("词表返回/新收/已见: " + " · ".join(
    "%s=%d/%d/%d" % (t, raw_term.get(t, 0), new_term.get(t, 0), seen_term.get(t, 0))
    for t in sorted(TERMS, key=lambda x: -raw_term.get(x, 0))), d=True)
if gh_lost[0]:
    A("⚠️ gh 认证曾掉线 %d 次（末次原因: %s）；已按 %ds 冷却自动重试，"
      "冷却期间 %d 次调用走未认证通道（配额低、数据一致）"
      % (GH_LOST_N[0], GH_LAST_ERR[0] or "(未记录)", GH_COOLDOWN, GH_UNAUTH[0]), d=True)
low = {k: v for k, v in cov.items() if v < 95}
if low:
    A("⚠️ 覆盖率 <95%%（叶子窗截断或 total_count 不准，绝对数不可引用）: " +
      " · ".join("%s=%.1f%%" % kv for kv in low.items()), d=True)
if scaffold:
    A("ℹ️ 共享脚手架（同短名跨≥%d owner 且 desc 前缀同）%d 个: %s"
      % (SCAFFOLD_MIN, len(scaffold), " · ".join(scaffold[:12])))
if neg_dropped:
    A("ℹ️ 被 NEG 规则丢弃 %d 个: %s" % (len(neg_dropped),
                                       " · ".join(neg_dropped[:12])))
if page_dropped:
    A("ℹ️ 被 pages 后缀规则丢弃 %d 个: %s"
      % (len(page_dropped), " · ".join("%s(%dKB)" % p for p in page_dropped[:12])))
if root_dropped:
    A("ℹ️ 被 pages 根目录规则丢弃 %d 个（index.html+.nojekyll 且无代码骨架）: %s"
      % (len(root_dropped), " · ".join(root_dropped[:12])))
vt = Counter(c["term"] for c in todo)
A("逐词核验数: " + " · ".join("%s=%d" % (k, vt.get(k, 0)) for k in
                              sorted(TERMS, key=lambda x: -vt.get(x, 0))))
uv = [c["repo"] for c in todo if c.get("unverified")]
if uv:
    A("⚠️ 未核验（限速或超预算，勿当空仓）%d: %s" % (len(uv), " · ".join(uv[:12])), d=True)
stale = [c["repo"] for c in todo if c.get("stale")]
if stale:
    A("⚠️ 30 天零提交（star 在骗人）%d: %s" % (len(stale), " · ".join(stale[:15])), d=True)
burst = [c["repo"] for c in todo if c.get("burst_only")]
if burst:
    A("⚠️ 爆完即停（30d 有量 / 7d 归零）%d: %s"
      % (len(burst), " · ".join(burst[:15])), d=True)
nol = [c["repo"] for c in todo if c.get("no_lang")]
if nol:
    A("⚠️ 无 language 字段（疑似非代码仓）%d: %s"
      % (len(nol), " · ".join(nol[:12])), d=True)
empty = [c["repo"] for c in todo if c.get("maybe_empty")]
if empty:
    A("⚠️ 空仓（409）: " + " · ".join(empty), d=True)
cand = {o: n for o, n in owner_n.items() if n >= 3}
if cand:
    A("ℹ️ 候选农场（owner≥3，需人工判）: " +
      " · ".join("%s=%d" % kv for kv in cand.items()))
if RUN_PROBE:
    A("ℹ️ probe 触发（%s）· 窗口 %d 天（不跟 run 窗口）· 种子 %d"
      "（报告级 %d / 幸存 %d / 历史 %d / 丢弃堆 %d）→ 候选 token %d → 已反查 %d · "
      "热仓核验 %d（未达门槛 %d）· clusters.json 已重写%s"
      % (PROBE_WHY, PROBE_WIN, probe_stat["seeds"], probe_stat["rep"],
         probe_stat["out"], probe_stat["hist"], probe_stat["drop"],
         probe_stat["tok"], probe_stat["done"], probe_stat["hot"],
         probe_stat["hot_quiet"],
         "" if DRY else " · 戳已写"), d=True)
    if not probe_stat["seeds"]:
        A("   ⚠️ 种子为 0 —— 本轮 probe 无从反查，不是「没有簇」", d=True)
    else:
        ours = [c for c in cluster_report
                if not c["generic"] and c["cohesive"] and c["thematic"]]
        near = [c for c in cluster_report
                if not c["generic"] and c["cohesive"] and not c["thematic"]]
        alias = [c for c in cluster_report if not c["generic"] and not c["cohesive"]]
        A("ℹ️ probe 反查 —— 小 total 候选（≤%d）。**同主题**=簇内 desc 有跨仓重复词"
          "**且主题词落在词表语义内**；**近似**=簇内自洽但主题词不是本线的；"
          "**异质**=各写各的（撞名嫌疑）。给证据，不下结论。" % PROBE_MAX_TOTAL, d=True)
        for cl in ours[:8]:
            A("  ✅ `%s` total=%d owners=%d%s 未在幸存者=%d 主题词=%s | %s"
              % (cl["token"], cl["total"], cl["owners"],
                 " [一人多仓]" if cl["one_man"] else "", cl["not_in_out"],
                 ",".join("%s×%d" % (w, c) for w, c in cl["theme"][:5]),
                 " · ".join("%s(%s/%s)" % (h["repo"], h["commits_30d"],
                                           h["commits_7d"]) for h in cl["hot"][:3])),
              d=True)
        if near:
            A("  ⚠️ 近似（同主题但主题词不在词表语义内，仍可能是撞名）%d 个: %s"
              % (len(near), " · ".join(
                  "`%s`(total=%d,owners=%d,主题词=%s)"
                  % (c["token"], c["total"], c["owners"],
                     ",".join(w for w, _ in c["theme"][:3])) for c in near[:8])), d=True)
        if alias:
            A("  ⚠️ 撞名嫌疑（异质，各写各的）%d 个: %s" % (len(alias),
              " · ".join("%s(total=%d,owners=%d)" % (c["token"], c["total"],
                                                     c["owners"])
                         for c in alias[:8])), d=True)
        gen = [c for c in cluster_report if c["generic"]][:5]
        if gen:
            A("  （通用词，反查噪声）: " + " · ".join(
                "%s(total=%d)" % (c["token"], c["total"]) for c in gen), d=True)
else:
    A("ℹ️ probe 跳过（%s < %d 天）—— clusters.json 未重写，是上次结果，别当本轮"
      % (PROBE_WHY, PROBE_EVERY), d=True)
for c in rep[:25]:
    A("  " + fmt(c), d=True)

open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L if FULL else D))

# ── 落盘 / 通知 ───────────────────────────────────────────────────
stamp = TODAY
if not DRY and hit:
    merged = {k: stamp for k in hit}
    merged.update(seen)
    # 保留**新**条目：merged 的顺序是「本轮新命中 → 旧 seen」，
    # 原来取 [-8000:] 保留的是尾部旧条目，超 8000 会先把新命中挤掉。
    json.dump(dict(list(merged.items())[:8000]),
              open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(CARDS, "a", encoding="utf-8") as f:
        f.write("\n## %s · github-radar（报告级 %d）\n" % (stamp, len(rep)))
        for c in rep:
            f.write("- [%s](%s) ★%d · 30天=%s · 7天=%s%s · `%s` · %s\n"
                    % (c["repo"], c["url"], c["stars"],
                       "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
                       "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
                       " [爆完即停]" if c.get("burst_only") else "",
                       c["term"], c["desc"][:100]))

if rep:
    R = ["**github-radar** · 窗口 %d 天 · 报告级 %d · 近 7 天活跃 %d"
         % (DAYS, len(rep), sum(1 for c in rep if c.get("commits_7d"))), ""]
    for c in rep[:NOTIFY_TOP]:
        R.append("- [%s](%s) ★%d · 30天=%s · 7天=%s%s · 词 `%s` · %s"
                 % (c["repo"], c["url"], c["stars"],
                    "≥100" if c.get("commits_30d_ge") else c["commits_30d"],
                    "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"),
                    " [爆完即停]" if c.get("burst_only") else "",
                    c["term"], c["desc"][:100]))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

if not DRY and rep and os.path.exists("./notify"):
    r = subprocess.run(["./notify", "-f", REPORT], capture_output=True, text=True)
    print("notify: %s" % ((r.stdout or r.stderr or "ok").strip()[:200]))
else:
    print("notify: 跳过（%s）" % ("dry-run" if DRY else "报告级 0"))
print("STATUS: GITHUB_RADAR_OK · 幸存 %d · 报告级 %d · 总耗时 %.0fs"
      % (len(out), len(rep), time.time() - T0))