const rNow = 0.027869408549920902, rH1 = 0.027883145675288927, rH24 = 0.027514725530409536;
const vNow = (0.62545573 + 0.62396753) / 2;
const vH1 = (0.62297054 + 0.62247334) / 2;
const vH24 = (0.65219417 + 0.65308951) / 2;
const mNow = rNow * vNow, mH1 = rH1 * vH1, mH24 = rH24 * vH24;
const pct = (a, b) => +(((a / b) - 1) * 100).toFixed(3);
const usdc = [0.01720375177219008, 0.017180625783704998, 0.017163279611217008].sort((a, b) => a - b);
const out = {
  virtual_usd: { now: +vNow.toFixed(8), h1: +vH1.toFixed(8), h24: +vH24.toFixed(8) },
  mark_now: +mNow.toFixed(8),
  mark_1h_ago: +mH1.toFixed(8),
  mark_24h_ago: +mH24.toFixed(8),
  h1_pct: pct(mNow, mH1),
  h24_pct: pct(mNow, mH24),
  ratio_1h_pct: pct(rNow, rH1),
  ratio_24h_pct: pct(rNow, rH24),
  usdc_median: +usdc[1].toFixed(8),
  usdc_range: [+usdc[0].toFixed(8), +usdc[2].toFixed(8)],
  dexscreener: 0.01724,
  band_low: +Math.min(usdc[0], mNow).toFixed(8),
  band_high: +Math.max(usdc[2], mNow).toFixed(8),
  premium_vs_usdc_median_pct: pct(mNow, usdc[1]),
  ath_distance_pct: pct(mNow, 0.06876),
};
out.gates = [0.012, 0.025, 0.032, 0.041].map((t) => ({
  target: t,
  distance_pct: +(((t / mNow) - 1) * 100).toFixed(2),
  crossed: t <= 0.012 ? mNow <= t : mNow >= t,
}));
// levels in ratio space using vNow
const V = 526810.442689199, D = 18902821.05361343;
for (const t of [0.012, 0.025, 0.032, 0.041]) {
  const rT = t / vNow;
  const k = Math.sqrt(rNow / rT);
  const dNeed = Math.abs(D * k - D);
  out['level_' + t] = { deus_needed: Math.round(dNeed), usd: Math.round(dNeed * mNow) };
}
console.log(JSON.stringify(out, null, 2));
