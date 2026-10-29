#!/usr/bin/env bash
# 等 CF 边缘对象过期后重跑一轮；命中「新增 id > 0」即停。
# 最多 10 次 × 150s = 25 分钟。退出码 0 = 拿到新鲜轮；1 = 始终 HIT。
set -u
cd /home/runner/work/aeon-token/aeon-token || exit 1
for i in $(seq 1 10); do
  out=$(python3 skills/defillama-radar/scan.py "" 2>&1)
  line=$(printf '%s\n' "$out" | grep '新增 id' | head -1)
  new=$(printf '%s\n' "$line" | sed -n 's/.*新增 id \([0-9][0-9]*\).*/\1/p')
  printf 'try=%d %s\n' "$i" "$line"
  if [ -n "${new:-}" ] && [ "$new" -gt 0 ]; then
    printf 'FRESH after %d tries\n' "$i"
    exit 0
  fi
  sleep 150
done
printf 'STILL_STALE after 10 tries\n'
exit 1
