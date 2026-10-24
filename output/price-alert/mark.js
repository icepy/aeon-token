const RPC = 'https://base.gateway.tenderly.co';
const DEEP = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';
const USDC_POOLS = [
  '0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b',
  '0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642',
  '0x75bc14950Ab093cBd1f80BbbDf458596939180A3',
];
const head = 53041380, dayAgo = 52998180;

async function post(body) {
  const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return r.json();
}
async function reserves(pool, blk) {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: pool, data: '0x0902f1ac' }, '0x' + blk.toString(16)] });
  if (!j.result) return { err: JSON.stringify(j.error) };
  const h = j.result.slice(2);
  return {
    r0: Number(BigInt('0x' + h.slice(0, 64))) / 1e18,
    r1: Number(BigInt('0x' + h.slice(64, 128))) / 1e18,
  };
}
// Uniswap V3 slot0 -> sqrtPriceX96 is word0
async function slot0(pool, blk) {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: pool, data: '0x3850c7bd' }, '0x' + blk.toString(16)] });
  if (!j.result) return { err: JSON.stringify(j.error) };
  const h = j.result.slice(2);
  return { sqrtPriceX96: BigInt('0x' + h.slice(0, 64)) };
}
(async () => {
  const out = {};
  // deepest pool now + 24h ago
  const now = await reserves(DEEP, head);
  const ago = await reserves(DEEP, dayAgo);
  out.deepest = { now, ago, ratio_now: now.r0 / now.r1, ratio_24h_ago: ago.r0 / ago.r1 };
  out.deepest.h24_ratio_pct = +(((out.deepest.ratio_now / out.deepest.ratio_24h_ago) - 1) * 100).toFixed(3);
  out.deepest.deus_reserve_change = +(now.r1 - ago.r1).toFixed(4);

  // VIRTUAL/USD reference: use the deepest VIRTUAL/WETH pool that is LIVE (per lesson: freshness over depth)
  const vpools = [
    '0x792f465e0434fB1028EA3BfeB05240CB839C4e04',
    '0x9c087Eb773291e50CF6c6a90ef0F4500e349B903',
    '0xE31c372a7Af875b3B5E0F3713B17ef51556da667',
  ];
  out.virtual_ref = [];
  for (const p of vpools) {
    const s = await slot0(p, head);
    const t0 = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: p, data: '0x0dfe1681' }, '0x' + head.toString(16)] });
    out.virtual_ref.push({ pool: p, sqrt: s.sqrtPriceX96 ? s.sqrtPriceX96.toString() : s.err, token0: t0.result });
  }
  console.log(JSON.stringify(out, null, 2));
})();
