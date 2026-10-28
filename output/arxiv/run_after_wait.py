import subprocess, sys, time

time.sleep(240)  # 静默冷却，不再探测，避免继续消耗 arXiv 限流额度

r = subprocess.run([sys.executable, "skills/arxiv-radar/scan.py", ""],
                   cwd="/home/runner/work/aeon-token/aeon-token",
                   capture_output=True, text=True)
sys.stdout.write(r.stdout)
sys.stdout.write("\n--- STDERR ---\n")
sys.stdout.write(r.stderr)
print("\nexit=%d" % r.returncode)
