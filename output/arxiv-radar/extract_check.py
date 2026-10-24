"""Extract the python heredoc from skills/arxiv-radar/SKILL.md and syntax-check it."""
import re, sys

src = open("skills/arxiv-radar/SKILL.md", encoding="utf-8").read()
m = re.search(r"python3 - <<'PY'.*?\n(.*?)\nPY\n", src, re.S)
if not m:
    print("could not find heredoc")
    sys.exit(1)
code = m.group(1)
open("output/arxiv-radar/extracted_scan.py", "w", encoding="utf-8").write(code)
try:
    compile(code, "extracted_scan.py", "exec")
    print("SYNTAX OK — %d lines" % code.count("\n"))
except SyntaxError as ex:
    print("SYNTAX ERROR: %s (line %s)" % (ex.msg, ex.lineno))
    sys.exit(1)
# static checks
for need in ["CARRIER_BY_TERM", "carrier = CARRIER_BY_TERM.get", "hit_ids", "per_term"]:
    print(("OK   " if need in code else "MISS ") + need)
print("still writes seen in loop:", "seen[aid] = now" in code)
