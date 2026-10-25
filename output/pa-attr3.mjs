// Who funded 0x96949fd5's rising balance while it sold 8,699 DEUS into the pool?
const RPCS = ['https://base.gateway.tenderly.co', 'https://mainnet.base.org'];
let ep = 0;
const pad = (a) => a.replace(/^0x/, '').toLowerCase().padStart(64, '0');
async function rpc(method, params) {
  for (let i = 0; i < 5; i++) {
    try {
      const r = await fetch(RPCS[ep], {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
      });
      const j = await r.json().catch(() => ({}));
      if (j.result !== undefined) return j.result;
    } catch (e) {}
    ep = (ep + 1) % RPCS.length;
    await new Promise((s) => setTimeout(s, 800 * 2 ** i));
  }
  return null;
}
const hex = (n) => '0x' + n.toString(16);
const dec = (h) => (h ? Number(BigInt(h)) : NaN);
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const W = '0x96949fd549d0da5ca279662264085a93138bdb17';
const head = dec(await rpc('eth_blockNumber', []));
const TR = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const toT = '0x' + pad(W);

console.log('Incoming DEUS to', W, 'since blk 53050000');
let tot = 0;
for (let s = 53050000; s <= head; s += 900) {
  const e = Math.min(s + 899, head);
  const r = await rpc('eth_getLogs', [{ address: DEUS, topics: [TR, null, toT], fromBlock: hex(s), toBlock: hex(e) }]);
  if (Array.isArray(r)) for (const l of r) {
    const v = Number(BigInt(l.data)) / 1e18;
    if (v < 1) continue;
    tot += v;
    console.log('  IN', v.toFixed(4), 'from', '0x' + l.topics[1].slice(26), 'blk', dec(l.blockNumber), l.transactionHash.slice(0, 14));
  }
  await new Promise((x) => setTimeout(x, 110));
}
console.log('total in', tot.toFixed(4));

// 24h balance trajectory
for (const [tag, b] of [['-30d', head - 1296000], ['-7d', head - 302400], ['-24h', head - 43200], ['-6h', head - 10800], ['-1h', head - 1800], ['now', head]]) {
  const r = await rpc('eth_call', [{ to: DEUS, data: '0x70a08231' + pad(W) }, hex(b)]);
  console.log(tag, (Number(BigInt(r)) / 1e18).toFixed(4));
}
