#!/usr/bin/env python3
"""Per-day submission counts to distinguish index lag from genuinely-zero submissions."""
import re, time, urllib.request

CATS = ["cs.CR", "cs.RO", "cs.LG", "q-fin.CP"]
DAYS = ["20261021", "20261022", "20261023", "20261024", "20261025"]
API = "https://export.arxiv.org/api/query"

for c in CATS:
    row = []
    for d in DAYS:
        q = f"cat:{c} AND submittedDate:[{d}0000 TO {d}2359]"
        url = f"{API}?search_query={urllib.parse.quote(q)}&max_results=1" if False else \
              f"{API}?search_query={q.replace(' ', '+').replace('[', '%5B').replace(']', '%5D').replace(':', '%3A')}&max_results=1"
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                body = r.read().decode("utf-8", "replace")
            m = re.search(r"<opensearch:totalResults[^>]*>(\d+)<", body)
            row.append(f"{d[-4:]}={m.group(1) if m else 'ERR'}")
        except Exception as ex:
            row.append(f"{d[-4:]}=ERR({type(ex).__name__})")
        time.sleep(3)
    print(f"{c:10s} " + "  ".join(row))
