const RPC = 'https://base.gateway.tenderly.co';
const V3 = {
  '0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b': 'aerodrome',
  '0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642': 'aero',
  '0x75bc14950Ab093cBd1f80BbbDf458596939180A3': 'aerodrome',
};
const USDC = '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913';
const DEUS = '0x940a319b75861014a220d9c6c144d108552b089b';
const Q192 = 2n ** 192n;
const HEAD = 53050396;
async function post(body) {
  for (let i = 0; i < 5; i++) {
    try {
      const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      const j = await r.json();
      if (j.error) { await new Promise((s) => setTimeout(s, 500 * 2 ** i)); continue; }
      return j;
    } catch { await new Promise((s) => setTimeout(s, 500 * 2 ** i)); }
  }
  return { error: { message: 'rpc-fail' } };
}
const call = async (to, data) => {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to, data }, '0x' + HEAD.toString(16)] });
  return j.error ? { err: j.error.message } : j.result;
};
const word = (r, i) => BigInt('0x' + r.slice(2 + i * 64, 2 + (i + 1) * 64));
(async () => {
  const marks = {};
  for (const p of Object.keys(V3)) {
    const t0 = await call(p, '0x0dfe1681'), t1 = await call(p, '0xd21220a7');
    if (!t0 || t0.err) { console.log(p, 'err', t0); continue; }
    const a0 = '0x' + t0.slice(-40), a1 = '0x' + t1.slice(-40);
    const s = await call(p, '0x3850c7bd');
    if (!s || s.err) { console.log(p, 'slot0 err'); continue; }
    const sq = word(s, 0);
    const raw = Number(sq * sq) / Number(Q192);
    // token0=USDC(6dp) token1=DEUS(18dp) -> DEUS per USDC ; invert for USD per DEUS
    let usdPerDeus;
    if (a0.toLowerCase() === USDC && a1.toLowerCase() === DEUS) {
      // raw = DEUS per USDC in raw units; human DEUS per USDC = raw * 1e6/1e18
      usdPerDeus = 1 / (raw * (1e6 / 1e18));
    } else if (a0.toLowerCase() === DEUS && a1.toLowerCase() === USDC) {
      usdPerDeus = raw * (1e18 / 1e6);
    } else { console.log(p, 'unexpected tokens', a0, a1); continue; }
    marks[p] = +usdPerDeus.toFixed(9);
    console.log(p, V3[p], 'a0', a0, 'usd/deus', marks[p]);
  }
  const vals = Object.values(marks).sort((a, b) => a - b);
  const med = vals[Math.floor(vals.length / 2)];
  const deep = 0.02756094660140625 * ((0.62992219 + 0.62892821) / 2);
  console.log('MEDIAN', med, 'DEEP', deep, 'PREMIUM_PCT', (((deep / med) - 1) * 100).toFixed(4));
})();
