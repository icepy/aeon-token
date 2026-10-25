// Merge this run's findings into price-alert-state.json, atomically, with .bak.
import fs from 'node:fs';

const P = 'memory/topics/price-alert-state.json';
const st = JSON.parse(fs.readFileSync(P, 'utf8'));
fs.writeFileSync(P + '.bak', JSON.stringify(st, null, 2) + '\n');

const NOW = '2026-10-25T02:05:00Z';
const MARK = 0.017447263;
const RATIO = 0.0277469198;
const RATIO_PREV = 523886.9302269761 / 19008306.855478093;

st.contract = '0x940A319B75861014A220D9c6c144d108552B089B';
st.chain = 'base';
st.last_run_at = NOW;

// ATH untouched — price is 294% below the true ATH.
st.ath.last_verdict = 'UNCHANGED';

// Targets: no cross, refresh distance bookkeeping.
const dist = {};
for (const t of Object.keys(st.targets)) {
  const tv = Number(t);
  st.targets[t].last_checked_price = MARK;
  st.targets[t].last_checked_at = NOW;
  st.targets[t].distance_pct = Number(((tv / MARK - 1) * 100).toFixed(2));
  dist[t] = st.targets[t].distance_pct;
}

st.last_price = {
  price_usd: MARK,
  h1_pct: 0.4448,
  h24_pct: -2.0982,
  pool: 'aerodrome classic (Solidly) DEUS/VIRTUAL - deepest, liq $657,448',
  pool_address: '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa',
  liquidity_usd: 657448.42,
  pool_url: 'https://dexscreener.com/base/0x3e97c5ec8c73e7d566aca606472141a9b9a8c1fa',
  observed_at: NOW,
  head_block: 53052250,
  head_ts: '2026-10-25T02:04:07Z',
  h1_source: 'ON-CHAIN exact-3600s. blk 53050450 (01:04:07Z) -> 53052250 (02:04:07Z). Pool ratio (VIRTUAL/DEUS) 0.027560947 -> 0.027746920 = +0.6748%. Quote leg VIRTUAL/USD ~-0.23% (deepest live VIRTUAL/WETH 0x792f465e). Net USD mark +0.44%.',
  h1_note: 'SIX swaps this hour in the deepest pool after the fully-dead 00:00-01:00Z hour. 1 buy (76,803.10 DEUS out of pool) vs 5 sells (13,125.84 DEUS in). Net DEUS LEFT the pool 63,677.26 in the hour - the first net-buy hour in the recorded series. Reserves timestamp moved 23:52:37Z -> 01:41:33Z, so the tape is genuinely live again, not frozen.',
  mark_source: 'Deepest-pool reserves at blk 53052250: VIRTUAL 525,651.4765648125 / DEUS 18,944,498.344048623 (token0=VIRTUAL 0x0b3e3284 18dp, token1=DEUS 0x940A319B 18dp). ratio 0.0277469198 x VIRTUAL/USD $0.6288 (mean of 0x7CB770D0 USDC $0.6287 and 0x529d2863 USDC $0.6289) = $0.0174473. Cross-check via deepest VIRTUAL/WETH 0x792f465e at $0.6283 gives $0.0174334 - the two agree to 0.08%.',
  mark_note: 'DexScreener prints $0.01735 on the deepest pair and $0.01734-$0.01745 across the four DEUS/USDC venues; the on-chain reserve mark $0.0174473 sits at the TOP of that cluster, so the deepest pool is at a small PREMIUM after being at a discount. Premium over the USDC V3 median ($0.01734) is +0.62%.',
  gate_distances_pct: dist,
  ath_distance_pct: 294.42,
  h24_note: 'h24 -2.10%, block-pinned to exactly 86400s (blk 53009138 2026-10-24T02:07:03Z -> 53052250). Decomposition: DEUS/VIRTUAL ratio +0.3018% AND VIRTUAL/USD -2.40% (median h24 of five deepest live VIRTUAL/WETH+USDC pools). The quote leg did essentially all of the damage, same as the prior four runs. Over 24h DEUS LEFT the deepest pool -28,566.26 net (18,973,064.60 -> 18,944,498.34) - i.e. the pool TIGHTENED, consistent with net accumulation.'
};
st.last_price.gate_distances_pct = dist;

st.gate_results = {
  observed_at: NOW,
  ath: { verdict: 'UNCHANGED', prior: 0.06876, current: MARK, distance_pct: 294.42 },
  sharp_move: {
    verdict: 'QUIET',
    h1_pct: 0.4448,
    threshold_pct: 20,
    note: 'On-chain exact-3600s +0.44% USD (+0.67% ratio, -0.23% quote leg). DexScreener h1 on the deepest pair reads +1.38% - a different window, both far from +/-20%.'
  },
  targets: { '0.012': 'NO_CROSS', '0.025': 'NO_CROSS', '0.032': 'NO_CROSS', '0.041': 'NO_CROSS' },
  run_verdict: 'OK',
  notifications_sent: 0
};

fs.writeFileSync(P, JSON.stringify(st, null, 2) + '\n');
console.log('STATE_WRITTEN', P);
console.log('targets', JSON.stringify(dist));
