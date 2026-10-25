// Scan deepest pool Swap logs for the last hour + discriminative control
const RPC = 'https://base.gateway.tenderly.co';
const DEEP = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';
const TOPIC = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b';
const BAD = '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75c'; // 1 char wrong
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
async function logs(from, to, topic) {
  const out = [];
  for (let a = from; a <= to; a += 900) {
    const b = Math.min(a + 899, to);
    const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getLogs', params: [{ address: DEEP, fromBlock: hex(a), toBlock: hex(b), topics: topic ? [topic] : undefined }] });
    if (j.error) return { error: j.error.message, upto: a };
    out.push(...j.result);
    await new Promise((s) => setTimeout(s, 250));
  }
  return { logs: out };
}
(async () => {
  const last = await logs(H1, HEAD, TOPIC);
  console.log('WINDOW_1H', JSON.stringify({ n: last.logs ? last.logs.length : null, error: last.error }));
  // control: full family scan on same window (no topic filter) -> histogram
  const all = await logs(H1, HEAD, null);
  if (all.logs) {
    const h = {};
    for (const l of all.logs) h[l.topics[0]] = (h[l.topics[0]] || 0) + 1;
    console.log('TOPIC_HISTOGRAM_1H', JSON.stringify(h));
  } else console.log('HIST_ERR', all.error);
  // discriminative test on a known-active wider window
  const wide = await logs(H1 - 7200, HEAD, TOPIC);
  const wideBad = await logs(H1 - 7200, HEAD, BAD);
  console.log('DISCRIM', JSON.stringify({ real: wide.logs ? wide.logs.length : wide.error, wrong1char: wideBad.logs ? wideBad.logs.length : wideBad.error }));
  // find last swap before now
  if (wide.logs && wide.logs.length) {
    const bs = wide.logs.map((l) => Number(BigInt(l.blockNumber))).sort((a, b) => a - b);
    console.log('SWAP_BLOCKS_RANGE', bs[0], bs[bs.length - 1], 'count', bs.length);
    // gaps
    const gaps = [];
    for (let i = 1; i < bs.length; i++) if (bs[i] - bs[i - 1] > 5) gaps.push([bs[i - 1], bs[i], bs[i] - bs[i - 1]]);
    console.log('GAPS', JSON.stringify(gaps));
    // per-block detail for swaps in the last 3h window
    const rows = [];
    for (const l of wide.logs) {
      const bn = Number(BigInt(l.blockNumber));
      if (bn < H1 - 7200) continue;
      rows.push({ bn, tx: l.transactionHash, data: l.data });
    }
    console.log('RAW_N', rows.length);
    const fs = await import('node:fs');
    fs.writeFileSync('output/price-alert/swaps-recent.json', JSON.stringify(wide.logs, null, 1));
  }
  // block timestamps for the boundary blocks
  for (const n of [H1 - 7200, H1, HEAD]) {
    const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getBlockByNumber', params: [hex(n), false] });
    console.log('BLK', n, j.result ? Number(BigInt(j.result.timestamp)) : 'ERR');
  }
})();
