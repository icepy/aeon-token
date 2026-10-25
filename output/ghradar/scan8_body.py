

out, raw = [], 0
drop = {"seen": 0, "excl": 0, "archived": 0, "short_desc": 0, "carrier": 0,
        "neg": 0, "pages": 0, "farm": 0, "fail": 0}
hit, qfail, cov = {}, [], {}
raw_term, new_term = {}, {}
page_dropped, neg_dropped = [], []
total_by_term = {}

for term in TERMS:
    total, got, failed = 0, 0, False
    raw_term[term] = 0
    new_term[term] = 0
    neg = NEG_BY_TERM.get(term, [])
    for w in WINS:
        q = '"%s" in:name,description created:%s fork:false stars:>=%d' % (
            term, w, MIN)
        for page in range(1, MAXPAGE + 1):
            res, err = search(q, page)
            if res is None:
                print("! %s @%s p%d: %s" % (term, w, page, err), file=sys.stderr)
                drop["fail"] += 1
                failed = True
                time.sleep(8)
                break
            if page == 1:
                total += res.get("total_count", 0)
            items = res.get("items", [])
            got += len(items)
            raw_term[term] += len(items)
            for it in items:
                raw += 1
                rid = it["full_name"]
                owner = (it.get("owner") or {}).get("login", "")
                short = rid.split("/")[-1]
                if rid in seen:
                    drop["seen"] += 1
                    continue
                if rid in hit:
                    hit[rid]["terms"].append(term)
                    drop["seen"] += 1
                    continue
                if it.get("archived"):
                    drop["archived"] += 1
                    continue
                lowall = (rid + " " + (it.get("description") or "")).lower()
                if neg and any(x in lowall for x in neg):
                    drop["neg"] += 1
                    neg_dropped.append(rid)
                    continue
                size_kb = it.get("size", 0)
                # 项目页/列表页：名字像页 **且** 体量小（不看 language，静态站常标 HTML/JS）
                if ((short.endswith(".github.io")
                     or short.lower() == owner.lower()) and size_kb < 300):
                    drop["pages"] += 1
                    page_dropped.append((rid, size_kb))
                    continue
                desc = (it.get("description") or "").strip()
                if len(desc) < 25:
                    drop["short_desc"] += 1
                    continue
                if any(x in desc.lower() for x in EXCL):
                    drop["excl"] += 1
                    continue
                need = CARRIER_BY_TERM.get(term)
                if need and not any(c in desc.lower() for c in need):
                    drop["carrier"] += 1
                    continue
                if owner.lower() in farms:
                    drop["farm"] += 1
                    continue
                out.append({"term": term, "terms": [term], "repo": rid,
                            "owner": owner, "url": it["html_url"],
                            "stars": it.get("stargazers_count", 0),
                            "created": (it.get("created_at") or "")[:10],
                            "pushed": (it.get("pushed_at") or "")[:10],
                            "topics": it.get("topics", [])[:6],
                            "size_kb": size_kb,
                            "language": it.get("language"),
                            "desc": " ".join(desc.split())[:140]})
                hit[rid] = out[-1]
                new_term[term] += 1
            time.sleep(3 if GH else 8)
            if len(items) < 100:
                break
    if failed and not got:
        qfail.append(term)
    total_by_term[term] = total
    if total:
        cov[term] = round(100.0 * got / total, 1)

# ── 核验：全量（core 配额 5,000/h，与 search 独立池）──
pick = {}
# 全量核验：幸存集 (178) 远小于 core 配额 5,000/h，按 star 分桶会饿死低星簇（lessons #8）
for c in out:
    pick[c["repo"]] = c
todo = list(pick.values())[:CHK_CAP]

for c in todo:
    n30, st = commits_since(c["repo"], 30)
    if st == "empty":
        c["maybe_empty"] = True
        continue
    if st != "ok":
        c["unverified"] = True
        continue
    c["commits_30d"] = n30
    if n30 >= 100:
        c["commits_30d_ge"] = True
    if n30 == 0:
        c["stale"] = True
        continue
    n7, st7 = commits_since(c["repo"], 7)
    if st7 == "ok":
        c["commits_7d"] = n7
        if n7 >= 100:
            c["commits_7d_ge"] = True
        if n7 == 0:
            c["burst_only"] = True
    if not c.get("language"):
        c["no_lang"] = True

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
json.dump({"terms": TERMS, "total_by_term": total_by_term, "cov": cov,
           "raw_term": raw_term, "new_term": new_term, "wins": WINS,
           "days": DAYS, "maxpage": MAXPAGE},
          open(OUTD + "/terms8.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)


def fmt(c):
    return "%s ★%d 30d=%s%s 7d=%s" % (
        c["repo"], c["stars"],
        "≥100" if c.get("commits_30d_ge") else c.get("commits_30d"),
        " [爆完即停]" if c.get("burst_only") else "",
        "≥100" if c.get("commits_7d_ge") else c.get("commits_7d", "-"))


failed_t = list(qfail)
truly_zero = [t for t in TERMS if t not in qfail and raw_term.get(t, 0) == 0]
saturated = [t for t in TERMS if raw_term.get(t, 0) > 0 and new_term.get(t, 0) == 0]
with_new = [t for t in TERMS if new_term.get(t, 0) > 0]

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
        "%s(raw=%d/total=%d)" % (t, raw_term[t], total_by_term.get(t, 0))
        for t in saturated))
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
                       "≥100" if c.get("commits_7d_ge") else c["commits_7d", "-"],
                       " [爆完即停]" if c.get("burst_only") else "",
                       c["term"], c["desc"][:100]))
