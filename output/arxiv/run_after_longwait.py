import subprocess, sys, time

# arXiv 限流是 IP 级，短冷却无效（前面 4 分钟仍 429）。
# 这次静默等 12 分钟，期间不发任何请求。
time.sleep(720)

r = subprocess.run([sys.executable, "skills/arxiv-radar/scan.py", ""],
                   cwd="/home/runner/work/aeon-token/aeon-token",
                   capture_output=True, text=True)
sys.stdout.write(r.stdout)
sys.stdout.write("\n--- STDERR ---\n")
sys.stdout.write(r.stderr)
print("\nexit=%d" % r.returncode)
