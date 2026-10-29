#!/usr/bin/env bash
# 轮询直到 CF 边缘对象换新（last-modified 变化），然后跑 scan.py。
# 目的：避免在过期边缘快照上出报告、把当晚晚些登记的项目漏到下一轮。
set -u
cd /home/runner/work/aeon-token/aeon-token || exit 1
OLD="Wed, 28 Oct 2026 23:02:27 GMT"
for i in $(seq 1 20); do
  LM=$(curl -sI "https://api.llama.fi/protocols" | tr -d '\r' | awk 'tolower($1)=="last-modified:"{$1="";sub(/^ /,"");print}')
  CS=$(curl -sI "https://api.llama.fi/protocols" | tr -d '\r' | awk 'tolower($1)=="cf-cache-status:"{print $2}')
  printf 'poll=%d last-modified=%s cf=%s\n' "$i" "${LM:-none}" "${CS:-none}"
  if [ "${LM:-}" != "$OLD" ] && [ -n "${LM:-}" ]; then
    printf 'TURNOVER detected after %d polls\n' "$i"
    python3 skills/defillama-radar/scan.py "" 2>&1 | tail -14
    exit 0
  fi
  sleep 60
done
printf 'NO_TURNOVER after 20 polls\n'
exit 1
