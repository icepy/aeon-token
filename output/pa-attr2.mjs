// Is the 111,385 DEUS aggregator sweep a directional buy or MM/arb pass-through?
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
const head = dec(await rpc('eth_blockNumber', []));

const WATCH = {
  'payerEOA 0xcdfd7379': '0xcdfd73794ec9d9b56c24f26dd21956dcb6e7ef82',
  'sink 0x7d683941': '0x7d6839415693801e94cdc4a7d732c9a3fdbbd1d7',
  'executor 0x92325e5a': '0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f',
  'seller 0x96949fd5': '0x96949fd549d0da5ca279662264085a93138bdb17',
};
async function bal(who, blk) {
  const r = await rpc('eth_call', [{ to: DEUS, data: '0x70a08231' + pad(who) }, hex(blk)]);
  return r ? Number(BigInt(r)) / 1e18 : NaN;
}
for (const [label, a] of Object.entries(WATCH)) {
  const code = await rpc('eth_getCode', [a, 'latest']);
  const nonce = await rpc('eth_getTransactionCount', [a, 'latest']);
  const now = await bal(a, head);
  const pre = await bal(a, 53051312 - 1);
  const b24 = await bal(a, head - 43200);
  console.log(label, '|', code === '0x' ? 'EOA' : 'CODE ' + code.slice(0, 12), '| nonce', dec(nonce),
    '| DEUS pre-sweep', pre.toFixed(4), '| now', now.toFixed(4), '| -24h', b24.toFixed(4));
}

// Where did the 111,385 DEUS go AFTER blk 53051313? DEUS transfers from executor/sink.
const TR = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
for (const [label, a] of [['sink', '0x7d6839415693801e94cdc4a7d732c9a3fdbbd1d7'], ['executor', '0x92325e5ac24ec4d8d0032cf4cb37b080f4a6374f']]) {
  const fromT = '0x' + pad(a);
  let n = 0;
  for (let s = 53051313; s <= head; s += 900) {
    const e = Math.min(s + 899, head);
    const r = await rpc('eth_getLogs', [{ address: DEUS, topics: [TR, fromT], fromBlock: hex(s), toBlock: hex(e) }]);
    if (Array.isArray(r) && r.length) {
      for (const l of r) {
        const v = Number(BigInt(l.data)) / 1e18;
        if (v < 1) continue;
        console.log(label, 'OUT', v.toFixed(4), '->', '0x' + l.topics[2].slice(26), 'blk', dec(l.blockNumber), l.transactionHash.slice(0, 12));
        n++;
      }
    }
    await new Promise((x) => setTimeout(x, 110));
  }
  console.log(label, 'outgoing transfers >1 DEUS since sweep:', n);
}
