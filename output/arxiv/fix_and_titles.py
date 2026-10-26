#!/usr/bin/env python3
"""修 hits.tsv 粘连行 + 拉全量标题供打标签（不猜）。"""
import json, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HITS = "memory/arxiv-hits.tsv"
NS = {"a": "http://www.w3.org/2005/Atom"}

lines = open(HITS, encoding="utf-8").read().split("\n")
fixed, inj = [], 0
for ln in lines:
    if ln.count("\t") > 2:
        parts = ln.split("\t")
        # 粘连形态：...名字 + YYYY-MM-DD  键  名字
        for i, p in enumerate(parts):
            m = re.match(r"^(.*?)(\d{4}-\d{2}-\d{2})$", p)
            if m and i + 2 < len(parts):
                left = m.group(1).strip()
                date = m.group(2)
                key, name = parts[i + 1], "\t".join(parts[i + 2:])
                fixed.append("\t".join(parts[:i] + ([left] if left else [])))
                fixed.append("\t".join([date, key, name]))
                inj += 1
                break
        else:
            fixed.append(ln)
        continue
    fixed.append(ln)
out = "\n".join(x for x in fixed if x.strip() or x is fixed[-1])
open(HITS, "w", encoding="utf-8").write(out if out.endswith("\n") else out + "\n")
print("修复粘连行 %d 处" % inj)

# 收集全部键 + pass2 新条目的标题
keys, names = {}, {}
for i, ln in enumerate(open(HITS, encoding="utf-8")):
    if i == 0:
        continue
    f = ln.rstrip("\n").split("\t")
    if len(f) == 3 and f[1]:
        keys[f[1]] = f[0]
        names[f[1]] = f[2]
print("hits 键数 =", len(keys))

titles = {}
ids = sorted(keys)
for i in range(0, len(ids), 25):
    chunk = ids[i:i + 25]
    p = {"id_list": ",".join(chunk), "max_results": 50}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(p)
    for t in range(3):
        try:
            with urllib.request.urlopen(url, timeout=40) as r:
                root = ET.fromstring(r.read())
            break
        except Exception as ex:
            print("  retry", ex)
            time.sleep(8)
    else:
        root = None
    if root is None:
        print("chunk FAIL", chunk[:2])
        continue
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        titles[aid] = " ".join(e.find("a:title", NS).text.split())
    time.sleep(4)

print("\n键\t名字\t标题")
for k in ids:
    print("%s\t%s\t%s" % (k, names.get(k, ""), titles.get(k, "(未取到)")))
json.dump(titles, open("output/arxiv/titles.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
