const RPC = 'https://base.gateway.tenderly.co';
const ESCROW = '0xA85A38796B951CE87B378538b32B3E6Ee3C4C373';
const from = Number(process.argv[2]), to = Number(process.argv[3]);

async function post(body) {
  for (let i = 0; i < 4; i++) {
    const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const j = await r.json();
    if (j.error) { await new Promise((s) => setTimeout(s, 1000 * 2 ** i)); continue; }
    return j;
  }
  throw new Error('rpc failed');
}
(async () => {
  let all = [];
  for (let a = from; a <= to; a += 1000) {
    const b = Math.min(a + 999, to);
    const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getLogs', params: [{ address: ESCROW, fromBlock: '0x' + a.toString(16), toBlock: '0x' + b.toString(16) }] });
    if (!j.result) { console.log('ERR', JSON.stringify(j.error)); continue; }
    all = all.concat(j.result);
  }
  const hist = {};
  for (const l of all) hist[l.topics[0]] = (hist[l.topics[0]] || 0) + 1;
  console.log('TOPIC0 HISTOGRAM over', from, '..', to);
  for (const [k, v] of Object.entries(hist)) console.log(' ', k, v);
  const dec = (x) => Number(BigInt('0x' + x)) / 1e18;
  for (const l of all) {
    const d = l.data.slice(2);
    const words = [];
    for (let i = 0; i < d.length; i += 64) words.push(d.slice(i, i + 64));
    console.log(JSON.stringify({
      topic0: l.topics[0].slice(0, 12),
      blk: parseInt(l.blockNumber, 16),
      tx: l.transactionHash,
      topics1: l.topics[1] ? '0x' + l.topics[1].slice(-40) : null,
      topics2: l.topics[2] || null,
      words_dec: words.map((w) => dec(w)),
      words_ints: words.map((w) => Number(BigInt('0x' + w))),
    }));
  }
})();
