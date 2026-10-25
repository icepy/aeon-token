#!/bin/bash
# 等待 scan.py 写出 audit.log 且有内容
for i in $(seq 1 300); do
  if [ -s output/ghradar/audit.log ]; then echo READY; exit 0; fi
  sleep 4
done
echo TIMEOUT
exit 1
