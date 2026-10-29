#!/usr/bin/env python3
"""narrative-brief — 读 Grok `crypto-narrative-brief-3day` 写入的 narratives.md。

有新内容才推。空文件、只有日期、整份哈希已经推过，都不发。

用法:
    python3 skills/narrative-brief/check.py
    python3 skills/narrative-brief/check.py dry-run
    python3 skills/narrative-brief/check.py --commit-sent
    python3 skills/narrative-brief/check.py --self-test

var token（空格分隔）:
    dry-run   不发 notify、不写 seen、不覆盖 report.md（正文改写 report.dry.md）

产物（文件名固定）:
    output/narrative-brief/report.md       非 dry-run 且有新内容才写
    output/narrative-brief/report.dry.md   dry-run 的正文
    output/narrative-brief/pending.json    notify 没发出去时的待确认哈希
    memory/narrative-brief-seen.json       已推过的整份哈希。dry-run 不写

模型只调用，不重写。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

SOURCE = "crypto-narrative-brief-3day"
BLOB = "https://github.com/icepy/aeon-token/blob/main/memory/topics/narratives.md"
RAW = "https://raw.githubusercontent.com/icepy/aeon-token/main/memory/topics/narratives.md"
LOCAL_REL = "memory/topics/narratives.md"
SEEN_REL = "memory/narrative-brief-seen.json"
OUT_DIR = "output/narrative-brief"
REPORT_REL = OUT_DIR + "/report.md"
DRY_REL = OUT_DIR + "/report.dry.md"
PENDING_REL = OUT_DIR + "/pending.json"

DATE_RE = re.compile(r"^(?:\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})$")
ITEM_RE = re.compile(r"^(\d+)\.\s*标签：(.*)$")
SECTION_RE = re.compile(r"^【[^】]+】$")
SHA_RE = re.compile(r"\bsha256[:=]\s*([0-9a-f]{64})\b", re.I)
SH = timezone(timedelta(hours=8))


def now_utc():
    return datetime.now(timezone.utc)


def sh_label(dt):
    return dt.astimezone(SH).strftime("%Y-%m-%d %H:%M") + " Asia/Shanghai"


def repo_of(script_file):
    # skills/narrative-brief/check.py → repo root
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(script_file))))


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def norm_newlines(text):
    return text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")


def split_briefs(text):
    """按独占一行的日期切开。没有日期就把全文当一份。空正文丢掉。"""
    lines = [ln.rstrip() for ln in norm_newlines(text).split("\n")]
    briefs = []
    date = None
    buf = []
    seen_date = False

    def flush():
        body = "\n".join(buf).strip()
        if not body:
            return
        briefs.append({"date": date, "body": body})

    for line in lines:
        cand = line.strip()
        if cand.startswith("## "):
            cand = cand[3:].strip()
        if DATE_RE.fullmatch(cand):
            if seen_date or any(x.strip() for x in buf):
                flush()
            date = cand
            buf = []
            seen_date = True
            continue
        buf.append(line)
    if seen_date or any(x.strip() for x in buf):
        flush()
    return briefs


def norm_label(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def dedupe_body(body):
    """同一节里重复的「标签」只留先出现的一条。跨节不并。
    去掉编号后全文相同的条目，整份里只留一条。
    """
    lines = body.split("\n")
    out = []
    seen_labels = set()
    seen_blocks = set()
    dropped = 0
    n = 0
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if SECTION_RE.fullmatch(stripped):
            seen_labels = set()
            n = 0
            out.append(lines[i])
            i += 1
            continue
        m = ITEM_RE.match(stripped)
        if not m:
            out.append(lines[i])
            i += 1
            continue
        j = i + 1
        while j < len(lines):
            s = lines[j].strip()
            if ITEM_RE.match(s) or SECTION_RE.fullmatch(s):
                break
            j += 1
        label = norm_label(m.group(2))
        block_lines = [stripped] + [lines[k].rstrip() for k in range(i + 1, j)]
        block_key = re.sub(r"^\d+\.\s*", "", "\n".join(block_lines).strip())
        block_key = re.sub(r"\s+", " ", block_key)
        if (label and label in seen_labels) or block_key in seen_blocks:
            dropped += 1
        else:
            if label:
                seen_labels.add(label)
            seen_blocks.add(block_key)
            n += 1
            rebuilt = ["%d. 标签：%s" % (n, m.group(2).strip())]
            rebuilt.extend(lines[i + 1:j])
            out.extend(rebuilt)
        i = j
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out).strip())
    return text, dropped


def canonical(date, body):
    lines = [ln.rstrip() for ln in body.split("\n")]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines).strip())
    blob = (date or "undated") + "\n" + text + "\n"
    return blob, hashlib.sha256(blob.encode("utf-8")).hexdigest()


def load_seen(path):
    if not os.path.isfile(path):
        return []
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = doc.get("seen") if isinstance(doc, dict) else None
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("sha256"), str):
            out.append(row)
    return out


def shas_from_logs(root, days=3):
    """只认『推送: yes』那一节里的 sha。dry-run / 未推过的不算。"""
    found = set()
    today = now_utc().date()
    for delta in range(days):
        day = today - timedelta(days=delta)
        path = os.path.join(root, "memory", "logs", day.isoformat() + ".md")
        if not os.path.isfile(path):
            continue
        text = read_text(path)
        for chunk in re.split(r"(?m)^### ", text):
            head, _, body = chunk.partition("\n")
            if head.strip() != "narrative-brief":
                continue
            if not re.search(r"推送:\s*yes\b", body):
                continue
            found.update(SHA_RE.findall(body))
    return found


def append_log(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    block = "\n### narrative-brief\n" + "".join("- %s\n" % r for r in rows)
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)


def fetch_remote(url, timeout=25):
    fd, tmp = tempfile.mkstemp(prefix="narrative-brief-")
    os.close(fd)
    try:
        try:
            proc = subprocess.run(
                ["curl", "-sS", "-L", "--max-time", str(timeout), "-o", tmp, "-w", "%{http_code}", url],
                capture_output=True, text=True,
            )
        except OSError as exc:
            return {"http": "000", "body": "", "reason": "curl-missing", "err": str(exc)}
        code = (proc.stdout or "").strip()
        code = code[-3:] if len(code) >= 3 else (code or "000")
        if proc.returncode == 28:
            return {"http": code, "body": "", "reason": "timeout", "err": (proc.stderr or "").strip()}
        try:
            body = read_text(tmp)
        except OSError:
            body = ""
        if proc.returncode != 0 and code in ("", "000"):
            return {"http": "000", "body": "", "reason": "curl-%s" % proc.returncode, "err": (proc.stderr or "").strip()}
        if code != "200":
            return {"http": code, "body": "", "reason": "http-%s" % code, "err": (proc.stderr or "").strip()}
        if not body.strip():
            return {"http": code, "body": "", "reason": "empty", "err": ""}
        head = body.lstrip().lower()
        if head.startswith("<!doctype") or head.startswith("<html"):
            return {"http": code, "body": "", "reason": "html", "err": ""}
        return {"http": code, "body": body, "reason": "ok", "err": ""}
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def render(items):
    parts = []
    for b in items:
        head = [
            "**叙事简报** · %s" % (b["date"] or "未标日期"),
            "来源：Grok 自动化 `crypto-narrative-brief-3day`",
            "原文：%s" % BLOB,
        ]
        if b["dropped"]:
            head.append("去重：去掉 %d 条重复标签（同一节里只留先出现的一条）。" % b["dropped"])
        head.append("")
        head.append(b["body"])
        parts.append("\n".join(head))
    return "\n\n---\n\n".join(parts) + "\n"


def parse_args(argv):
    opt = {
        "dry": False,
        "commit_sent": False,
        "self_test": False,
        "root": None,
        "file": None,
        "ignored": [],
    }
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "dry-run":
            opt["dry"] = True
        elif a == "--commit-sent":
            opt["commit_sent"] = True
        elif a == "--self-test":
            opt["self_test"] = True
        elif a == "--root" and i + 1 < len(argv):
            i += 1
            opt["root"] = argv[i]
        elif a.startswith("--root="):
            opt["root"] = a.split("=", 1)[1]
        elif a == "--file" and i + 1 < len(argv):
            i += 1
            opt["file"] = argv[i]
        elif a.startswith("--file="):
            opt["file"] = a.split("=", 1)[1]
        elif a:
            opt["ignored"].append(a)
        i += 1
    return opt


def log_path(root):
    return os.path.join(root, "memory", "logs", now_utc().strftime("%Y-%m-%d") + ".md")


def save_seen(path, rows):
    dump_json(path, {
        "source": SOURCE,
        "file": BLOB,
        "seen": rows[-40:],
    })


def commit_sent(root, log_to):
    pending = os.path.join(root, PENDING_REL)
    if not os.path.isfile(pending):
        print("commit-sent: nothing pending")
        return 0
    try:
        doc = json.load(open(pending, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print("commit-sent: pending 读不了")
        return 0
    rows = doc.get("briefs") if isinstance(doc, dict) else None
    if not isinstance(rows, list) or not rows:
        print("commit-sent: nothing pending")
        return 0
    seen_path = os.path.join(root, SEEN_REL)
    seen = load_seen(seen_path)
    have = {r["sha256"] for r in seen}
    added = []
    stamp = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    for row in rows:
        sha = row.get("sha256") if isinstance(row, dict) else None
        if not sha or sha in have:
            continue
        seen.append({"sha256": sha, "date": row.get("date") or "", "notified_at": stamp})
        have.add(sha)
        added.append(sha)
    if added:
        save_seen(seen_path, seen)
    os.remove(pending)
    if log_to:
        append_log(log_to, [
            "结果: COMMIT_SENT",
            "来源: %s" % SOURCE,
            "sha256: %s" % ",".join(added) if added else "sha256: (none)",
            "推送: yes" if added else "推送: no",
            "时间: %s" % sh_label(now_utc()),
        ])
    print("commit-sent: %d" % len(added))
    for sha in added:
        print("sha256: %s" % sha)
    return 0


def prepare(text):
    prepared = []
    for brief in split_briefs(text):
        body, dropped = dedupe_body(brief["body"])
        if not body.strip():
            continue
        _blob, sha = canonical(brief["date"], body)
        prepared.append({
            "date": brief["date"],
            "body": body,
            "dropped": dropped,
            "sha256": sha,
        })
    return prepared


def run(argv):
    opt = parse_args(argv)
    if opt["self_test"]:
        return self_test()
    root = opt["root"] or os.getcwd()
    seen_path = os.path.join(root, SEEN_REL)
    local_path = os.path.join(root, LOCAL_REL)
    report_path = os.path.join(root, REPORT_REL)
    dry_path = os.path.join(root, DRY_REL)
    pending_path = os.path.join(root, PENDING_REL)
    log_to = log_path(root)
    notify_bin = os.environ.get("NARRATIVE_BRIEF_NOTIFY", "./notify")

    if opt["commit_sent"]:
        return commit_sent(root, log_to)

    if opt["file"]:
        if not os.path.isfile(opt["file"]):
            print("narratives http=- bytes=0 source=file reason=missing")
            print("结果: FETCH_FAIL")
            append_log(log_to, [
                "结果: FETCH_FAIL",
                "来源: %s" % SOURCE,
                "读取: file missing",
                "推送: no",
                "时间: %s" % sh_label(now_utc()),
            ])
            return 0
        text = read_text(opt["file"])
        print("narratives http=- bytes=%d source=file reason=ok" % len(text.encode("utf-8")))
        fetch_note = "file"
    else:
        got = fetch_remote(RAW)
        print("narratives http=%s bytes=%d source=remote reason=%s" % (
            got["http"], len(got["body"].encode("utf-8")), got["reason"]))
        if got["reason"] == "ok":
            text = got["body"]
            fetch_note = "remote http=%s" % got["http"]
            if os.path.isfile(local_path):
                local = read_text(local_path)
                if norm_newlines(local).strip() != norm_newlines(text).strip():
                    print("本地副本与 GitHub 不一致，以 GitHub 为准")
        elif os.path.isfile(local_path):
            text = read_text(local_path)
            fetch_note = "local fallback (%s)" % got["reason"]
            print("narratives fallback=local bytes=%d reason=%s" % (len(text.encode("utf-8")), got["reason"]))
        else:
            print("结果: FETCH_FAIL")
            append_log(log_to, [
                "结果: FETCH_FAIL",
                "来源: %s" % SOURCE,
                "原文: %s" % BLOB,
                "读取: none http=%s reason=%s" % (got["http"], got["reason"]),
                "推送: no",
                "时间: %s" % sh_label(now_utc()),
            ])
            return 0

    if opt["ignored"]:
        print("忽略: %s" % " ".join(opt["ignored"]))

    prepared = prepare(text)
    seen_rows = load_seen(seen_path)
    seen_shas = {r["sha256"] for r in seen_rows} | shas_from_logs(root)
    fresh = []
    skipped = []
    emitted = set()
    for item in prepared:
        if item["sha256"] in seen_shas or item["sha256"] in emitted:
            skipped.append(item)
            continue
        emitted.add(item["sha256"])
        fresh.append(item)

    print("节: %d" % len(prepared))
    print("新: %d" % len(fresh))
    print("已推过: %d" % len(skipped))
    for item in skipped:
        print("已推过: %s sha256: %s" % (item["date"] or "未标日期", item["sha256"]))

    if len(prepared) > 4:
        print("日期节 %d > 4：Grok 没删最旧的一节。本 skill 不改 narratives.md。" % len(prepared))

    if not prepared:
        print("结果: EMPTY")
        print("notify: 跳过（空）")
        append_log(log_to, [
            "结果: EMPTY",
            "来源: %s" % SOURCE,
            "原文: %s" % BLOB,
            "读取: %s" % fetch_note,
            "推送: no",
            "时间: %s" % sh_label(now_utc()),
        ])
        return 0

    if not fresh:
        print("结果: UNCHANGED")
        print("notify: 跳过（已推过）")
        append_log(log_to, [
            "结果: UNCHANGED",
            "来源: %s" % SOURCE,
            "原文: %s" % BLOB,
            "读取: %s" % fetch_note,
            "sha256: %s" % ",".join(i["sha256"] for i in skipped),
            "推送: no",
            "时间: %s" % sh_label(now_utc()),
        ])
        return 0

    body = render(fresh)
    dropped = sum(i["dropped"] for i in fresh)
    target = dry_path if opt["dry"] else report_path
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(body)
    print("结果: %s" % ("DRY" if opt["dry"] else "NEW"))
    print("去重: %d" % dropped)
    for item in fresh:
        print("日期: %s" % (item["date"] or "未标日期"))
        print("sha256: %s" % item["sha256"])
    print("--- 正文 ---")
    sys.stdout.write(body)

    rows = [
        "结果: %s" % ("DRY" if opt["dry"] else "NEW"),
        "来源: %s" % SOURCE,
        "原文: %s" % BLOB,
        "读取: %s" % fetch_note,
        "日期: %s" % ",".join(i["date"] or "未标日期" for i in fresh),
        "sha256: %s" % ",".join(i["sha256"] for i in fresh),
        "去重: 去掉 %d 条重复标签" % dropped,
        "时间: %s" % sh_label(now_utc()),
    ]

    if opt["dry"]:
        rows.append("推送: no")
        append_log(log_to, rows)
        print("notify: 跳过（dry-run）")
        return 0

    dump_json(pending_path, {"briefs": [{"sha256": i["sha256"], "date": i["date"] or ""} for i in fresh]})
    if not os.path.isfile(notify_bin):
        rows.append("推送: no")
        rows.append("原因: notify 不在")
        append_log(log_to, rows)
        print("notify: **未发**")
        print("补发: ./notify -f %s" % REPORT_REL)
        print("补发后: python3 skills/narrative-brief/check.py --commit-sent")
        return 0

    proc = subprocess.run([notify_bin, "-f", target], capture_output=True, text=True)
    note = (proc.stdout or proc.stderr or "ok").strip().replace("\n", " ")[:200]
    if proc.returncode != 0:
        rows.append("推送: no")
        rows.append("原因: notify exit %s" % proc.returncode)
        append_log(log_to, rows)
        print("notify: 失败 exit=%s %s" % (proc.returncode, note))
        print("补发: ./notify -f %s" % REPORT_REL)
        print("补发后: python3 skills/narrative-brief/check.py --commit-sent")
        return 0

    seen_rows.extend({
        "sha256": i["sha256"],
        "date": i["date"] or "",
        "notified_at": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
    } for i in fresh)
    save_seen(seen_path, seen_rows)
    try:
        os.remove(pending_path)
    except OSError:
        pass
    rows.append("推送: yes")
    append_log(log_to, rows)
    print("notify: 已发送 %s" % note)
    return 0


def self_test():
    fails = []

    def check(name, cond, detail=""):
        if cond:
            print("PASS %s" % name)
        else:
            fails.append(name)
            print("FAIL %s %s" % (name, detail))

    sample = """26/10/2026

【加密线】

1. 标签：甲叙事
账号：@a
打分：热度1

2. 标签：甲叙事
账号：@b
打分：热度9

3. 标签：乙叙事
账号：@c

【美股线】

1. 标签：甲叙事
账号：@d

1. 变化 —— 全部为新。

2. 反身性 —— 故事自己在推价格。
"""
    briefs = split_briefs(sample)
    check("split one date", len(briefs) == 1 and briefs[0]["date"] == "26/10/2026", str(briefs))
    body, dropped = dedupe_body(briefs[0]["body"])
    check("drop same-section label", dropped == 1, "dropped=%s" % dropped)
    check("keep same label in another section", body.count("标签：甲叙事") == 2, body)
    check("keep closing notes", "变化" in body and "反身性" in body, body)
    check("renumber second section", "\n1. 标签：甲叙事\n账号：@d" in "\n" + body, body)
    body2, dropped2 = dedupe_body(body)
    check("dedupe idempotent", dropped2 == 0 and body2 == body, "dropped2=%s" % dropped2)

    check("date only is empty", split_briefs("26/10/2026\n") == [])
    check("blank is empty", split_briefs("  \n") == [])

    hdr = "## 2026-10-29\n\n29/10/2026\n\n【加密线】\n\n1. 标签：甲\n"
    hb = split_briefs(hdr)
    check("## header merges with date line", len(hb) == 1 and hb[0]["date"] == "29/10/2026", str(hb))
    check("## header not in body", "##" not in hb[0]["body"], hb[0]["body"])
    check("## header only is empty", split_briefs("## 2026-10-29\n\n") == [])

    two = "26/10/2026\n\n【加密线】\n\n1. 标签：旧\n\n29/10/2026\n\n【加密线】\n\n1. 标签：新\n"
    parts = split_briefs(two)
    check("two dates", [p["date"] for p in parts] == ["26/10/2026", "29/10/2026"], str(parts))
    _b, h1 = canonical("26/10/2026", "甲\n")
    _b, h2 = canonical("26/10/2026", "甲  \n\n\n")
    check("whitespace stable hash", h1 == h2)

    real = os.path.join(repo_of(__file__), LOCAL_REL)
    if os.path.isfile(real):
        prepared = prepare(read_text(real))
        check("real file parses", len(prepared) >= 1, str(len(prepared)))
        again = prepare((prepared[0]["date"] or "undated") + "\n" + prepared[0]["body"] + "\n") if prepared else []
        # re-parse from original is enough: second dedupe drops 0
        if prepared:
            _body, d2 = dedupe_body(prepared[0]["body"])
            check("real file dedupe stable", d2 == 0)
            check("real file keeps 比特币", "比特币" in prepared[0]["body"])
    else:
        print("SKIP real file")

    root = tempfile.mkdtemp(prefix="narrative-brief-test-")
    note_log = os.path.join(root, "notify.log")
    fake = os.path.join(root, "notify")
    with open(fake, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\necho \"$@\" >> \"%s\"\nexit 0\n" % note_log)
    os.chmod(fake, 0o755)
    os.environ["NARRATIVE_BRIEF_NOTIFY"] = fake
    src = os.path.join(root, "in.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write(sample)

    rc = run(["--root", root, "--file", src])
    check("first run rc", rc == 0)
    seen = load_seen(os.path.join(root, SEEN_REL))
    check("first run marks seen", len(seen) == 1, str(seen))
    check("first run notified", os.path.isfile(note_log) and "report.md" in read_text(note_log))
    report = read_text(os.path.join(root, REPORT_REL))
    check("report names source", "crypto-narrative-brief-3day" in report and BLOB in report, report[:200])
    check("report dropped a dup", "去掉 1 条" in report, report[:300])
    log1 = read_text(log_path(root))
    check("log pushed yes", "推送: yes" in log1 and "### narrative-brief" in log1, log1)

    open(note_log, "w").close()
    rc = run(["--root", root, "--file", src])
    check("second run unchanged", rc == 0)
    # stdout isn't captured; seen length stays 1 and notify log stays empty
    check("second run no second notify", read_text(note_log).strip() == "")
    check("seen still one", len(load_seen(os.path.join(root, SEEN_REL))) == 1)

    # dry-run on a new file must not mark seen or touch report.md
    src2 = os.path.join(root, "in2.md")
    with open(src2, "w", encoding="utf-8") as f:
        f.write("27/10/2026\n\n【加密线】\n\n1. 标签：另一条\n")
    before = read_text(os.path.join(root, REPORT_REL))
    run(["--root", root, "--file", src2, "dry-run"])
    check("dry-run keeps report.md", read_text(os.path.join(root, REPORT_REL)) == before)
    check("dry-run writes dry report", os.path.isfile(os.path.join(root, DRY_REL)))
    check("dry-run does not mark seen", len(load_seen(os.path.join(root, SEEN_REL))) == 1)
    check("dry-run log is not a push", "推送: yes" not in read_text(log_path(root)).split("### narrative-brief")[-1])

    # notify missing: pending, not seen, then commit-sent records it
    os.environ["NARRATIVE_BRIEF_NOTIFY"] = os.path.join(root, "no-such-notify")
    run(["--root", root, "--file", src2])
    check("missing notify leaves pending", os.path.isfile(os.path.join(root, PENDING_REL)))
    check("missing notify does not mark seen", len(load_seen(os.path.join(root, SEEN_REL))) == 1)
    run(["--root", root, "--commit-sent"])
    check("commit-sent marks seen", len(load_seen(os.path.join(root, SEEN_REL))) == 2)
    check("commit-sent clears pending", not os.path.isfile(os.path.join(root, PENDING_REL)))

    # only the new date goes out once the old hash is seen
    os.environ["NARRATIVE_BRIEF_NOTIFY"] = fake
    open(note_log, "w").close()
    both = os.path.join(root, "both.md")
    with open(both, "w", encoding="utf-8") as f:
        f.write(sample + "\n29/10/2026\n\n【加密线】\n\n1. 标签：只此一条新的\n")
    run(["--root", root, "--file", both])
    sent = read_text(os.path.join(root, REPORT_REL))
    check("only unseen date is sent", "只此一条新的" in sent and "甲叙事" not in sent, sent[:400])

    if fails:
        print("SELF_TEST_FAIL %d" % len(fails))
        return 1
    print("SELF_TEST_OK")
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
