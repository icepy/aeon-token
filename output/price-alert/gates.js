// Final gate math. All inputs are on-chain reads + the VIRTUAL/USD reference band.
const ratio_now = 0.027869408549920902;      // blk 53041380 (20:01:47Z)
const ratio_1h = 0.027883145675288927;       // blk 53039580 (19:01:47Z)
const ratio_24h = 0.027514725530409536;      // blk 52998180 (2026-10-23T20:01:47Z)
const virtual_now = 0.6226;                  // median of 3 deepest live VIRTUAL/WETH pools (0.6226/0.6227/0.6214)
const virtual_24h_ago = 0.6226 / (1 - 0.0448); // implied from DexScreener h24 -4.48% on deepest live pool
const virtual_1h_ago = 0.6226 / (1 - 0.0015);  // implied from h1 -0.15%

const mark_now = ratio_now * virtual_now;
const mark_1h = ratio_1h * virtual_1h_ago;
const mark_24h = ratio_24h * virtual_24h_ago;

const pct = (a, b) => +(((a / b) - 1) * 100).toFixed(3);
const usdc = [0.01720375177219008, 0.017180625783704998, 0.017163279611217008];

const out = {
  mark_now: +mark_now.toFixed(8),
  mark_1h_ago: +mark_1h.toFixed(8),
  mark_24h_ago: +mark_24h.toFixed(8),
  h1_pct: pct(mark_now, mark_1h),
  h24_pct: pct(mark_now, mark_24h),
  ratio_change_1h_pct: pct(ratio_now, ratio_1h),
  ratio_change_24h_pct: pct(ratio_now, ratio_24h),
  usdc_venues: usdc,
  usdc_median: usdc.slice().sort((a, b) => a - b)[1],
  dexscreener: 0.01724,
  premium_vs_usdc_median_pct: +(((mark_now / usdc.slice().sort((a, b) => a - b)[1]) - 1) * 100).toFixed(3),
  ath: 0.06876,
  ath_distance_pct: pct(mark_now, 0.06876),
};
const targets = [0.012, 0.025, 0.032, 0.041];
out.gates = targets.map((t) => ({
  target: t,
  side: mark_now < t ? 'above' : 'below',
  crossed: (mark_now < t ? mark_now >= t : mark_now <= t),
  distance_pct: +(((t / mark_now) - 1) * 100).toFixed(2),
}));
console.log(JSON.stringify(out, null, 2));
