#!/usr/bin/env python3
"""Append this run's log block to today's log file."""
import io

LOG = "memory/logs/2026-10-24.md"
BLOCK = "output/log_block.md"

with open(LOG, "r", encoding="utf-8") as f:
    existing = f.read()

with open(BLOCK, "r", encoding="utf-8") as f:
    block = f.read()

if "\n### price-alert\n- **Skill**: price-alert\n- **Token**: DEUS" in existing and "claim-and-dump" in existing.split("### price-alert")[-1]:
    print("already present, skipping")
else:
    tail = "" if existing.endswith("\n") else "\n"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(tail + block)
    print("appended %d bytes" % len(block))
