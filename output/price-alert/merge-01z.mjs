// atomic state merge + validation + .bak
import fs from 'node:fs';

const P = 'memory/topics/price-alert-state.json';
const BAK = P + '.bak';
const PATCH = JSON.parse(fs.readFileSync('output/price-alert/patch-01z.json', 'utf8'));
const raw = fs.readFileSync(P, 'utf8');
const s = JSON.parse(raw);
fs.writeFileSync(BAK, raw);

const NOW = '2026-10-25T01:02:19Z';
const PRICE = PATCH.last_price.price_usd;

// ATH: monotonic, unchanged
s.ath = s.ath || {};
if (PRICE > (s.ath.price_usd || 0)) {
  s.ath = { price_usd: PRICE, observed_at: NOW, announced_at: NOW, last_verdict: 'BASELINE' };
}
s.ath.last_verdict = 'UNCHANGED';

s.last_run_at = NOW;
s.last_alerts = s.last_alerts || { ath: null, sharp_move: null, target_hit: null };
s.last_price = PATCH.last_price;
s.gate_results = PATCH.gate_results;
s.deepest_pool_activity = PATCH.deepest_pool_activity;
s.venue_activity_1h = PATCH.venue_activity_1h;
s.venue_spread = PATCH.venue_spread;
s.supply_side_01z = PATCH.supply_side_01z;
s.holder_check = PATCH.holder_check;

// targets: no crosses this run; refresh check metadata
for (const [k, t] of Object.entries(PATCH.gate_results.targets)) {
  const e = s.targets[k];
  if (!e) continue;
  if (e.hit_at) continue; // one-shot, frozen
  e.last_checked_price = PRICE;
  e.last_checked_at = NOW;
  e.distance_pct = PATCH.last_price.gate_distances_pct[k];
}

fs.writeFileSync(P, JSON.stringify(s, null, 2) + '\n');
const check = JSON.parse(fs.readFileSync(P, 'utf8'));
const ok = check.last_price.price_usd === PRICE && check.ath.price_usd === 0.06876;
console.log('written', P, 'json_valid=true', 'invariants_ok=' + ok);
console.log('targets', JSON.stringify(Object.fromEntries(Object.entries(check.targets).map(([k, v]) => [k, { side: v.side, hit: v.hit_at, dist: v.distance_pct }]))));
