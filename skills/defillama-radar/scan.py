#!/usr/bin/env python3
"""defillama-radar 扫描器。dl-v1

第二层（名字）通道：扫 DefiLlama 上白名单链新出现的协议，只出名字与地板字段。
不做方向映射、不做判断、不写候选卡。

用法:
    python3 skills/defillama-radar/scan.py "dry-run"
    python3 skills/defillama-radar/scan.py "send"
    python3 skills/defillama-radar/scan.py "mark-sent"

var token（空格分隔）:
    dry-run   跳过通知；不写 memory/；改读/写 seen.dry.json 与 out.dry.json
    send      发送 output/defillama/report.md，成功后把 out.json 里的 id 标成已通知
    mark-sent 只标记、不发送（手动发过之后用）

notified 四态: null=待报 / "YYYY-MM-DD"=已报 / "filtered"=首次就没过过滤 / "baseline"=基线轮
可报集合 = notified is None。失败必须能与「零可报」区分。

seen 文件存在但读不出来 ≠ 首次运行：前者是损坏。损坏时先备份原文件、审计打 ⚠️、
STATUS 走 DEGRADED，然后按基线轮重灌 —— 不许静默当首次跑。
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

VERSION = "dl-v1"
OUTD = "output/defillama"
OUT = OUTD + "/out.json"
OUTDRY = OUTD + "/out.dry.json"
AUD = OUTD + "/audit.log"
REPORT = OUTD + "/report.md"
SEENDRY = OUTD + "/seen.dry.json"
SEEN = "memory/defillama-seen.json"
SEENBAK = "memory/defillama-seen.broken.json"
NAMES = "memory/defillama-names.txt"
API = "https://api.llama.fi/protocols"

ATTEMPTS = 3
TIMEOUT = 45
NOTIFY_TOP = 30
SEEN_CAP = 12000
CHAIN_MIN_HITS = 3
EXCL_CATEGORY = {"CEX", "Chain", "Interface"}

# 链白名单（人维护）。拼写以 /protocols 为准，不是 /v2/chains 的显示名。
# 两组孪生：BSC↔Binance（chainId 56）、OP Mainnet↔Optimism。两条都收，防命名漂移。
# 加链后必须删 memory/defillama-seen.json 重做基线，否则该链已有协议一条都不会报。
CHAINS = ["Ethereum", "Base", "Solana", "Arbitrum", "Ink",
          "Binance", "BSC", "Optimism", "OP Mainnet",
          "Hyperliquid L1", "Robinhood Chain"]
CHAIN_TWINS = {"BSC": "Binance", "Binance": "BSC",
               "OP Mainnet": "Optimism", "Optimism": "OP Mainnet"}
TWIN_PAIRS = [("BSC", "Binance"), ("OP Mainnet", "Optimism")]   # 每对只判一次

var = sys.argv[1] if len(sys.argv) > 1 else ""
DRY = MARK = SENDNOW = False
UNKNOWN = []
for tok in var.split():
    if tok == "dry-run":
        DRY = True
    elif tok == "mark-sent":
        MARK = True
    elif tok == "send":
        SENDNOW = True
    elif tok:
        UNKNOWN.append(tok)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
T0 = time.time()


def load_seen(path):
    """返回 (dict, err)。err 非空 = 文件在、但读不出来（损坏），与「文件不存在」区分。"""
    if not os.path.exists(path):
        return {}, ""
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as ex:
        return {}, (str(ex)[:60] or "解析失败")
    if not isinstance(d, dict):
        return {}, "顶层不是对象"
    return d, ""


def save_seen(d, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def load_names():
    if not os.path.exists(NAMES):
        return []
    return [l.strip() for l in open(NAMES, encoding="utf-8")
            if l.strip() and not l.startswith("#")]


def fetch():
    """返回 (payload, err)。payload 为 None 即失败 —— 失败必须能与零可报区分。"""
    last = ""
    for i in range(ATTEMPTS):
        try:
            req = urllib.request.Request(
                API, headers={"User-Agent": "defillama-radar/%s" % VERSION})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = json.loads(r.read().decode("utf-8"))
                if isinstance(data, list):
                    return data, ""
                return None, "返回不是数组"
        except urllib.error.HTTPError as he:
            last = "HTTP %s" % he.code
            if he.code not in (429, 500, 502, 503, 504):
                return None, last
            wait = min(10 * (i + 1), 25)
        except Exception as ex:
            last = str(ex)[:90]
            wait = min(5 * (i + 1), 20)
        if i < ATTEMPTS - 1:
            print("  ↻ 重试 %d/%d（%s，等 %ds）" % (i + 1, ATTEMPTS, last, wait),
                  file=sys.stderr, flush=True)
            time.sleep(wait)
    return None, last


def out_ids():
    if not os.path.exists(OUT):
        return []
    try:
        rows = json.load(open(OUT, encoding="utf-8"))
    except Exception:
        return []
    return [str(c.get("id")) for c in rows if isinstance(c, dict)]


def mark_ids(ids):
    """只把 notified 仍为 null 的改成今天。返回改了几条。"""
    seen, _ = load_seen(SEEN)
    n = 0
    for i in ids:
        rec = seen.get(i)
        if isinstance(rec, dict) and rec.get("notified") is None:
            rec["notified"] = TODAY
            n += 1
    save_seen(seen, SEEN)
    return n


def mark_sent():
    if DRY:
        print("mark-sent 在 dry-run 下不可用（memory/ 未写）")
        sys.exit(1)
    ids = out_ids()
    if not ids:
        print("没有 %s 或为空，先跑一次正式轮" % OUT)
        sys.exit(1)
    print("mark-sent: 标记 %d 条为已通知（%s）" % (mark_ids(ids), TODAY))
    sys.exit(0)


def send():
    """发 report.md，成功才标记 —— 发送与标记是同一个动作，不靠人记。"""
    if DRY:
        print("send 在 dry-run 下不可用（memory/ 未写）")
        sys.exit(1)
    if not os.path.exists(REPORT):
        print("没有 %s —— 先跑一次正式轮，并把中文稿写进去" % REPORT)
        sys.exit(1)
    if not os.path.exists("./notify"):
        print("notify: ./notify 不存在，未发 —— 未标记，下轮自动重报")
        sys.exit(1)
    r = subprocess.run(["./notify", "-f", REPORT], capture_output=True, text=True)
    if r.returncode != 0:
        print("notify: 发送失败（%s）—— 未标记，下轮自动重报"
              % (r.stderr or r.stdout or "").strip()[:160])
        sys.exit(1)
    print("send: 已发送 · 标记 %d 条" % mark_ids(out_ids()))
    sys.exit(0)


if MARK:
    mark_sent()
if SENDNOW:
    send()

# ── seen ──────────────────────────────────────────────────────────
SEEN_SRC = SEENDRY if (DRY and os.path.exists(SEENDRY)) else SEEN
seen, SEEN_ERR = load_seen(SEEN_SRC)
BASELINE = len(seen) == 0
SEEN_BROKEN = bool(SEEN_ERR)
BAKED = False
if SEEN_BROKEN and not DRY:
    try:
        os.replace(SEEN, SEENBAK)          # 留证据，再让本轮重灌覆盖
        BAKED = True
    except Exception:
        pass
known = load_names()

drop = {"noid": 0, "seen": 0, "parent": 0, "category": 0, "chain": 0}
chain_hits = {c: 0 for c in CHAINS}
out = []
new_ids = {}
retry = 0

os.makedirs(OUTD, exist_ok=True)


def rec_of(p, pid, hit):
    name = p.get("name") or ""
    return {
        "id": pid,
        "name": name,
        "slug": p.get("slug"),
        "chains": hit,
        "tvl": p.get("tvl"),
        "category": p.get("category"),
        "listedAt": p.get("listedAt"),
        "url": p.get("url"),
        "description": " ".join((p.get("description") or "").split())[:110],
        "misrepresentedTokens": p.get("misrepresentedTokens"),
        "wrongLiquidity": p.get("wrongLiquidity"),
        "in_names": any(k.lower() in name.lower() or name.lower() in k.lower()
                        for k in known),
    }


payload, err = fetch()

if payload is None:
    L = ["defillama-radar %s · 拉取失败 · var=%r" % (VERSION, var),
         "原因: %s" % err,
         "丢弃 无id=0 · seen=0 · parent=0 · category=0 · 链白名单=0 · 拉取失败=1",
         "全量 0 · 新增 id 0（可报 0 / 过滤标记 0）· 重报（上轮未通知）0 · 本次通知 跳过（失败）",
         "判据: DefiLlama 侧降级，不是白名单的问题，别据此改词或改链。"]
    if SEEN_BROKEN:
        L.append("   ⚠️ 同时 seen 解析失败（%s），本轮未重灌 —— 下次成功跑会被当基线轮" % SEEN_ERR)
    open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    print("STATUS: DEFILLAMA_RADAR_DEGRADED · 原始 0 · 可报 0 · 总耗时 %.0fs"
          % (time.time() - T0))
    sys.exit(0)

# ── 遍历 ──────────────────────────────────────────────────────────
for p in payload:
    if not isinstance(p, dict):
        drop["noid"] += 1
        continue
    pid = str(p.get("id") or "")
    chains_all = p.get("chains") or []
    if not isinstance(chains_all, list):
        chains_all = []
    for ch in chains_all:
        if ch in chain_hits:
            chain_hits[ch] += 1
    if not pid:
        drop["noid"] += 1
        continue

    hit = [c for c in chains_all if c in CHAINS]
    rec_seen = seen.get(pid)
    if isinstance(rec_seen, dict):
        drop["seen"] += 1
        if rec_seen.get("notified") is not None:
            continue                      # 已报 / filtered / baseline，永不重报
        # 上轮没通知成的重报候选，仍要过过滤
        if p.get("parentProtocol"):
            drop["parent"] += 1
            continue
        if p.get("category") in EXCL_CATEGORY:
            drop["category"] += 1
            continue
        if not hit:
            drop["chain"] += 1
            continue
        retry += 1
        out.append(rec_of(p, pid, hit))
        continue

    if p.get("parentProtocol"):
        drop["parent"] += 1
        new_ids[pid] = "filtered"
        continue
    if p.get("category") in EXCL_CATEGORY:
        drop["category"] += 1
        new_ids[pid] = "filtered"
        continue
    if not hit:
        drop["chain"] += 1
        new_ids[pid] = "filtered"
        continue
    new_ids[pid] = None
    out.append(rec_of(p, pid, hit))

# ── 审计 ──────────────────────────────────────────────────────────
new_ok = sum(1 for v in new_ids.values() if v is None)
new_filtered = len(new_ids) - new_ok
sent = "跳过（%s）" % ("dry-run" if DRY else ("基线轮" if BASELINE else "零可报"))

L = ["defillama-radar %s · var=%r" % (VERSION, var),
     "丢弃 无id=%d · seen=%d · parent=%d · category=%d · 链白名单=%d · 拉取失败=0"
     % (drop["noid"], drop["seen"], drop["parent"], drop["category"], drop["chain"]),
     "全量 %d · 新增 id %d（可报 %d / 过滤标记 %d）· 重报（上轮未通知）%d · 本次通知 %s"
     % (len(payload), len(new_ids), new_ok, new_filtered, retry, sent),
     "基线轮=%s" % BASELINE,
     "链命中: " + " · ".join("%s=%d" % (c, chain_hits[c]) for c in CHAINS),
     "单侧读数: 加密侧 %d / AI 侧 0（本源只有加密，别把高命中读成词表变准）"
     % len(out)]

if SEEN_BROKEN:
    if not DRY:
        if BAKED:
            recovery = "已备份到 %s 并重灌" % SEENBAK
            tail = " —— 上轮及更早的 notified 记录已丢"
        else:
            recovery = "备份失败，原文件仍在 %s 未动" % SEEN
            tail = " —— 本轮写入即覆盖，上轮及更早的 notified 记录已丢"
    elif SEEN_SRC == SEEN:
        recovery = "dry-run 未备份，坏的是正式 seen，本轮没写盘"
        tail = " —— 正式 seen 还在盘上但已读不出，下次非 dry-run 会被备份后重灌"
    else:
        recovery = "dry-run 未备份，坏的只是 dry 快照，正式 seen 未受影响"
        tail = ""
    L.append("   ⚠️ seen 解析失败（%s）· %s%s"
             % (SEEN_ERR, recovery, tail))

low = [c for c in CHAINS if chain_hits[c] < CHAIN_MIN_HITS and c not in CHAIN_TWINS]
if low:
    L.append("   ⚠️ 链名可能拼错或已改名: " + " · ".join(low))
for a, b in TWIN_PAIRS:
    if chain_hits.get(a, 0) == 0 and chain_hits.get(b, 0) == 0:
        L.append("   ⚠️ 整组 0 命中，疑似已改名: %s / %s" % (a, b))
if UNKNOWN:
    L.append("未识别 token: " + " ".join(UNKNOWN))
if BASELINE:
    L.append("基线轮：%d 条入 seen，不出报告。" % len(payload))

for c in out[:25]:
    L.append("  %s · %s · tvl=%s · %s · %s%s"
             % (c["name"], "/".join(c["chains"]), c["tvl"], c["category"],
                c["listedAt"] or "-", ("  ★清单内" if c["in_names"] else "")))

if not out and not BASELINE:
    L.append("ℹ️ 本轮可报 0 = 结构性（无新增 / 全部被过滤 / 已通知过），不是故障。")

open(AUD, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))

# ── 落盘 ──────────────────────────────────────────────────────────
merged = dict(seen)
if BASELINE:
    for p in payload:
        pid = str(p.get("id") or "") if isinstance(p, dict) else ""
        if pid:
            merged[pid] = {"first": TODAY, "notified": "baseline"}
else:
    for pid, st in new_ids.items():
        merged[pid] = {"first": TODAY, "notified": st}

ordered = {}
for pid in new_ids:
    if pid in merged:
        ordered[pid] = merged[pid]
for k, v in merged.items():
    if k not in ordered:
        ordered[k] = v
ordered = dict(list(ordered.items())[:SEEN_CAP])

if DRY:
    json.dump(out, open(OUTDRY, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    save_seen(ordered, SEENDRY)
    L2 = "快照: %s（dry-run 不覆盖 out.json，也不写 memory/）" % OUTDRY
else:
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    save_seen(ordered, SEEN)
    L2 = "seen 写入 %d 条（新增 %d）" % (len(ordered), len(new_ids))

# ── 机械版报告（模型随后覆写为中文）──────────────────────────────
if out and not DRY and not BASELINE:
    R = ["**defillama-radar** · 可报 %d" % len(out), ""]
    for c in out[:NOTIFY_TOP]:
        R.append("- %s · %s · TVL $%.0f · %s · %s"
                 % (c["name"], "/".join(c["chains"]), (c["tvl"] or 0),
                    c["category"] or "-", c["url"] or "-"))
    open(REPORT, "w", encoding="utf-8").write("\n".join(R) + "\n")

if DRY or BASELINE or not out:
    print("notify: 跳过（%s）" % ("dry-run" if DRY else
                                ("基线轮" if BASELINE else "零可报")))
else:
    print("notify: **未发** —— 把 %s 覆写成中文（协议信息中文、其余英文），然后：" % REPORT)
    print("        python3 skills/defillama-radar/scan.py \"send\"")

print("%s · 全量 %d · 可报 %d · 总耗时 %.0fs"
      % (L2, len(payload), len(out), time.time() - T0))
print("STATUS: DEFILLAMA_RADAR_%s · 原始 %d · 可报 %d%s"
      % ("DEGRADED" if SEEN_BROKEN else "OK", len(payload), len(out),
         " · 原因=seen 损坏重灌" if SEEN_BROKEN else ""))