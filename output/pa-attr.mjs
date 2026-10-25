// Attribute the 76,803 DEUS deepest-pool BUY at blk 53051313 and the 5 uniform sells.
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
const POOL = '0x3E97c5EC8c73e7d566aCA606472141a9b9a8C1Fa';

const TXS = [
  ['BUY  76,803', '0x53d72487d63c99679737551639f2f6b55c866a9ee7c672bdac76a9576460cd90'],
  ['SELL  2,949', '0x67c81dce976ab037b3fb901ce5e4b530d1a48f8e990f33086df909ca010c2f9e'],
  ['SELL  1,478', '0x0e5b4fcc7e0f4f15f7c23f00ac97fe871dc461706505e51d18c682951045c0b2'],
  ['SELL  2,900', '0xdb8e8673d6984c4ec0933ebecac70449b42b3e98fd50e9b1740bd2caf07d8c32'],
  ['SELL  2,900', '0x6f5175699dee3fa9a2a34b9508ac617d730d9c0797e43450ce4e1fbb873c04a6'],
  ['SELL  2,900', '0x85ed207a2f28ccf60eb195b3df1e16b8ff398ef3a7e554810e41a914eca421cd'],
];

const head = dec(await rpc('eth_blockNumber', []));
const TR = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';

async function bal(who, blk) {
  const r = await rpc('eth_call', [{ to: DEUS, data: '0x70a08231' + pad(who) }, hex(blk)]);
  return r ? Number(BigInt(r)) / 1e18 : NaN;
}

for (const [label, tx] of TXS) {
  const r = await rpc('eth_getTransactionByHash', [tx]);
  const rc = await rpc('eth_getTransactionReceipt', [tx]);
  if (!r || !rc) { console.log(label, 'ERR'); continue; }
  const blk = dec(rc.blockNumber);
  const from = r.from;
  console.log('\n===', label, 'blk', blk, 'ts', new Date(dec(rc.blockTimestamp || '0x0') * 1000).toISOString());
  console.log('  tx.from', from, 'to', r.to);
  const code = await rpc('eth_getCode', [from, 'latest']);
  const nonce = await rpc('eth_getTransactionCount', [from, 'latest']);
  console.log('  kind', code === '0x' ? 'EOA' : (code.startsWith('0xef0100') ? 'EIP-7702 ' + code.slice(0, 50) : 'CONTRACT'));
  console.log('  nonce', dec(nonce));

  // DEUS transfers in the tx
  const tr = await rpc('eth_getLogs', [{ address: DEUS, topics: [TR], fromBlock: hex(blk), toBlock: hex(blk) }]);
  const mine = (tr || []).filter(l => l.transactionHash === tx);
  for (const l of mine) {
    const val = Number(BigInt(l.data)) / 1e18;
    if (val < 0.0001) continue;
    const a = '0x' + l.topics[1].slice(26);
    const b = '0x' + l.topics[2].slice(26);
    console.log('   DEUS', val.toFixed(4), a.slice(0, 10), '->', b.slice(0, 10));
  }
  // endpoint balance held?
  const bNow = await bal(from, head);
  const bPre = await bal(from, blk - 1);
  console.log('  from DEUS balance pre', bPre.toFixed(4), 'now', bNow.toFixed(4));
  await new Promise(s => setTimeout(s, 120));
}
