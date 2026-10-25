// decode recent swaps + timestamp of silence start + USDC venue control
const RPC = 'https://base.gateway.tenderly.co';
const DEEP = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';
const VENUES = {
  '0x58dBa34e6ee6eb76Ef71A6ca0f18871CAE817D3b': 'aerodrome V3 USDC',
  '0x1B2f3f5C1B6037101FDD3EC14649E0d3F98fA642': 'aero V3 USDC',
  '0x75bc14950Ab093cBd1f80BbbDf458596939180A3': 'aerodrome V3 USDC',
};
const V3SYNC = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67';
const SOLIDLY = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b';
const HEAD = 53050396, H1 = 53048596;

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
const hex = (n) => '0x' + n.toString(16);
const ts = async (n) => { const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getBlockByNumber', params: [hex(n), false] }); return j.result ? Number(BigInt(j.result.timestamp)) : null; };
async function logs(addr, from, to, topics) {
  const out = [];
  for (let a = from; a <= to; a += 900) {
    const b = Math.min(a + 899, to);
    const p = { address: addr, fromBlock: hex(a), toBlock: hex(b) };
    if (topics) p.topics = topics;
    const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getLogs', params: [p] });
    if (j.error) return { error: j.error.message, upto: a };
    out.push(...j.result);
    await new Promise((s) => setTimeout(s, 250));
  }
  return { logs: out };
}
// Solidly Swap(int256,uint256,uint256,...) data words; topics 3
// Aerodrome classic: Swap(address indexed sender, address indexed to, uint256 amount0In, uint256 amount1In, uint256 amount0Out, uint256 amount1Out)
const bi = (h) => BigInt('0x' + h);
(async () => {
  const raw = JSON.parse((await import('node:fs')).readFileSync('output/price-alert/swaps-recent.json', 'utf8'));
  const out = [];
  for (const l of raw) {
    const bn = Number(BigInt(l.blockNumber));
    const w = l.data.slice(2).match(/.{64}/g).map((x) => BigInt('0x' + x));
    // token0=VIRTUAL, token1=DEUS ; a0In,a1In,a0Out,a1Out
    const [a0In, a1In, a0Out, a1Out] = w;
    const deusIn = Number(a1In) / 1e18, deusOut = Number(a1Out) / 1e18;
    out.push({ bn, t: await ts(bn), in: +deusIn.toFixed(4), out: +deusOut.toFixed(4), side: deusIn > 0 ? 'SELL' : 'BUY', tx: l.transactionHash, topics: l.topics.length });
  }
  out.sort((a, b) => a.bn - b.bn);
  console.log('DECODED_N', out.length);
  for (const r of out) console.log(JSON.stringify({ bn: r.bn, ts: new Date(r.t * 1000).toISOString(), side: r.side, deus: r.side === 'SELL' ? r.in : r.out, tx: r.tx.slice(0, 12) }));
  const lastS = out[out.length - 1];
  console.log('LAST_SWAP', lastS.bn, new Date(lastS.t * 1000).toISOString(), 'silence_min', ((Date.now() / 1000 - lastS.t) / 60).toFixed(1));

  // USDC venue control: are they trading this hour?
  for (const [addr, name] of Object.entries(VENUES)) {
    const r = await logs(addr, H1, HEAD, [V3SYNC]);
    console.log('VENUE', name, addr.slice(0, 10), r.error ? 'ERR:' + r.error : 'swaps_1h=' + r.logs.length);
  }
})();
