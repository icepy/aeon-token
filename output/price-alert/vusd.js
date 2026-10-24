const RPC = 'https://base.gateway.tenderly.co';
// VIRTUAL/USDC V3 pools (token0/token1 resolved at runtime)
const CAND = [
  '0x7CB770D0513c30e0CB45E4899e4a2CbEEd6F9830',
  '0x529d2863a1521d0b57db028168fdE2E97120017C',
  '0xaf2baac6d043d22f9ce14439228fbbf90c108a1dc809e32ad4e7e9e13fc941ac',
];
const USDC = '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913';
const VIRTUAL = '0x0b3e328455c4059eeb9e3f84b5543f74e24e7e1b';
const blocks = { now: 53041380, h1: 53039580, h24: 52998180 };
const Q192 = 2n ** 192n;

async function post(body) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const j = await r.json();
    if (j.error) { await new Promise((s) => setTimeout(s, 600 * 2 ** i)); continue; }
    return j;
  }
  return null;
}
const call = async (to, data, blk) => {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to, data }, '0x' + blk.toString(16)] });
  return j && j.result ? j.result : null;
};
(async () => {
  for (const p of CAND) {
    const t0 = await call(p, '0x0dfe1681', blocks.now);
    const t1 = await call(p, '0xd21220a7', blocks.now);
    if (!t0 || !t1) { console.log(p, 'token probe failed'); continue; }
    const a0 = '0x' + t0.slice(-40), a1 = '0x' + t1.slice(-40);
    let base, quote, baseDp, quoteDp, invert;
    if (a0 === VIRTUAL && a1 === USDC) { base = 'VIRTUAL'; quote = 'USDC'; baseDp = 18; quoteDp = 6; invert = false; }
    else if (a0 === USDC && a1 === VIRTUAL) { base = 'VIRTUAL'; quote = 'USDC'; baseDp = 18; quoteDp = 6; invert = true; }
    else { console.log(p, 'not a VIRTUAL/USDC pool', a0, a1); continue; }
    const res = {};
    for (const [k, b] of Object.entries(blocks)) {
      const s = await call(p, '0x3850c7bd', b);
      if (!s) { res[k] = 'ERR'; continue; }
      const sq = BigInt('0x' + s.slice(2, 66));
      // raw = token1 per token0 (in smallest units ratio)
      const raw = Number(sq * sq) / Number(Q192);
      // convert to USD per VIRTUAL
      let usdPerVirtual;
      if (!invert) {
        // token1(USDC 6dp) per token0(VIRTUAL 18dp): human = raw * 10^18/10^6 per 1 VIRTUAL?
        // price human = raw * (10^baseDp / 10^quoteDp) = USDC per VIRTUAL
        usdPerVirtual = raw * (10 ** baseDp / 10 ** quoteDp);
      } else {
        // token1(VIRTUAL) per token0(USDC): human VIRTUAL per USDC
        const virtualPerUsdc = raw * (10 ** quoteDp / 10 ** baseDp);
        usdPerVirtual = 1 / virtualPerUsdc;
      }
      res[k] = +usdPerVirtual.toFixed(8);
    }
    console.log(JSON.stringify({ pool: p, invert, virtual_usd: res }));
  }
})();
