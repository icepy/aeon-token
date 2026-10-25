// Identify 0x4e3ae00e (8.07M DEUS EOA) and its funding of 0x96949fd5.
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
const A = '0x4e3ae00e8323558fa5cac04b152238924aa31b60';
const head = dec(await rpc('eth_blockNumber', []));

const code = await rpc('eth_getCode', [A, 'latest']);
const nonce = await rpc('eth_getTransactionCount', [A, 'latest']);
const eth = await rpc('eth_getBalance', [A, 'latest']);
console.log('FUNDER', A);
console.log('  code', code === '0x' ? 'EOA' : 'CODE(' + (code.length - 2) / 2 + 'B) ' + code.slice(0, 20));
console.log('  nonce', dec(nonce), 'ETH', Number(BigInt(eth)) / 1e18);

for (const [tag, b] of [['-1y', head - 15768000], ['-90d', head - 3888000], ['-30d', head - 1296000], ['-7d', head - 302400], ['-24h', head - 43200], ['-1h', head - 1800], ['now', head]]) {
  const r = await rpc('eth_call', [{ to: DEUS, data: '0x70a08231' + pad(A) }, hex(b)]);
  console.log('  ', tag, (Number(BigInt(r)) / 1e18).toFixed(4));
}

// outgoing DEUS from funder in the last 2h
const TR = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const fromT = '0x' + pad(A);
for (let s = head - 3600; s <= head; s += 900) {
  const e = Math.min(s + 899, head);
  const r = await rpc('eth_getLogs', [{ address: DEUS, topics: [TR, fromT], fromBlock: hex(s), toBlock: hex(e) }]);
  if (Array.isArray(r)) for (const l of r) {
    const v = Number(BigInt(l.data)) / 1e18;
    if (v < 1) continue;
    console.log('  OUT', v.toFixed(4), '->', '0x' + l.topics[2].slice(26), 'blk', dec(l.blockNumber), l.transactionHash.slice(0, 14));
  }
  await new Promise((x) => setTimeout(x, 110));
}
