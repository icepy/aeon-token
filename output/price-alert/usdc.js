const RPC = 'https://base.gateway.tenderly.co';
const head = 53041380;
const POOLS = {
  '0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b': 'USDC/DEUS',
  '0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642': 'USDC/DEUS',
  '0x75bc14950Ab093cBd1f80BbbDf458596939180A3': 'USDC/DEUS',
  '0x7df2d59c764b290a2629e09b42773703fd1e575338f834b5ec28529299421edc': 'v4 ?',
};
async function post(body) {
  const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return r.json();
}
const Q192 = 2n ** 192n;
(async () => {
  for (const p of Object.keys(POOLS)) {
    const s = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: p, data: '0x3850c7bd' }, '0x' + head.toString(16)] });
    if (!s.result) { console.log(p, 'slot0 ERR', JSON.stringify(s.error)); continue; }
    const sq = BigInt('0x' + s.result.slice(2, 66));
    const t0 = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: p, data: '0x0dfe1681' }, '0x' + head.toString(16)] });
    const t1 = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: p, data: '0xd21220a7' }, '0x' + head.toString(16)] });
    // raw price token1/token0 = sq^2/2^192
    const raw = Number(sq * sq * 1000000n / Q192) / 1e6; // approx via scaled int math
    // token0=USDC 6dp, token1=DEUS 18dp => human DEUS per USDC = raw * 10^6/10^18
    const deusPerUsdc = raw * 1e6 / 1e18;
    const usdPerDeus = 1 / deusPerUsdc;
    console.log(JSON.stringify({
      pool: p, label: POOLS[p],
      token0: '0x' + t0.result.slice(-40), token1: '0x' + t1.result.slice(-40),
      sqrtPriceX96: sq.toString(), raw_ratio: raw,
      deus_per_usdc: deusPerUsdc, usd_per_deus: usdPerDeus,
    }));
  }
})();
