#!/usr/bin/env python3
"""农场黑名单生效验证 + 总覆盖率。"""
import json

out = json.load(open("output/ghradar/out.json", encoding="utf-8"))
keys = []
for l in open("memory/github-farms.txt", encoding="utf-8"):
    k = l.split("#")[0].strip().lower()
    if k:
        keys.append(k)
print("黑名单解析出 %d 个 key: %s" % (len(keys), keys))
print("（回归测试：旧实现会解析出带注释尾巴的垃圾 key，匹配 0 个 owner）")

res = [c for c in out if c["owner"].lower() in keys]
print("\n幸存集里黑名单 owner 残留: %d 个 %s"
      % (len(res), [c["repo"] for c in res]))

# 这三个是上轮判定的农场，本轮应被丢弃
for o in ("maxamin", "nirholas", "OpenMakerProjects"):
    print("  %-20s %s" % (o, "✅ 已丢弃" if o in keys and
          not any(c["owner"].lower() == o for c in out) else "❌ 仍在"))

# 总覆盖率
tot = 0
for t in set():
    pass
print("\n幸存 %d · 核验 %d · 报告级 %d"
      % (len(out), len([c for c in out if c.get("commits_30d") is not None]),
         len([c for c in out if (c.get("commits_30d") or 0) >= 5])))
print("stale %d · 空仓 %d · 未验 %d"
      % (len([c for c in out if c.get("stale")]),
         len([c for c in out if c.get("maybe_empty")]),
         len([c for c in out if c.get("unverified")])))
