const V = 526810.442689199, D = 18902821.05361343, VUSD = 0.6226;
const r_cur = V / D;
const mark = r_cur * VUSD;
const targets = { '0.012': 'SELL', '0.025': 'BUY', '0.032': 'BUY', '0.041': 'BUY' };
const out = { mark: +mark.toFixed(8), ratio: r_cur, virtual_usd: VUSD, reserves: { virtual: V, deus: D } };
for (const [t, action] of Object.entries(targets)) {
  const target = Number(t);
  const r_t = target / VUSD;              // required VIRTUAL per DEUS
  const k = Math.sqrt(r_cur / r_t);       // D_target = D * k
  const dNeeded = Math.abs(D * k - D);
  out['to_' + t] = {
    action,
    deus_needed: Math.round(dNeeded),
    usd_needed: Math.round(dNeeded * mark),
    mult_of_101k_dump: +(dNeeded / 101983.48).toFixed(2),
  };
}
console.log(JSON.stringify(out, null, 2));
