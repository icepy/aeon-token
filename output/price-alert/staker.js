const RPC = 'https://base.gateway.tenderly.co';
const W = '0xe338adc6c0fb242ca5bb2711c7f789c24486e61d';
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const head = 53041380;
const TX = '0x8897062a3f6cadfa5efe8c75af1f27248838ed5fbce7bf783071c14aee62545d';

async function post(body) {
  const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return r.json();
}
const pad = (a) => '0x000000000000000000000000' + a.slice(2).toLowerCase();
const balAt = async (blk) => {
  const j = await post({ jsonrpc: '2.0', id: 1, method: 'eth_call', params: [{ to: DEUS, data: '0x70a08231' + pad(W).slice(2) }, '0x' + blk.toString(16)] });
  return j.result ? Number(BigInt(j.result)) / 1e18 : 'ERR';
};
(async () => {
  const out = {};
  const code = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getCode', params: [W, 'latest'] });
  out.code = code.result ? code.result.slice(0, 40) : 'ERR';
  const nonce = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getTransactionCount', params: [W, 'latest'] });
  out.nonce = parseInt(nonce.result, 16);
  const eth = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getBalance', params: [W, 'latest'] });
  out.eth = Number(BigInt(eth.result)) / 1e18;
  out.deus_now = await balAt(head);
  for (const [label, back] of [['-1h', 1800], ['-6h', 10800], ['-24h', 43200], ['-7d', 302400], ['-30d', 1296000]]) {
    out['deus' + label] = await balAt(head - back);
  }
  // receipt of the stake tx -> who funded, and DEUS transfers in the last 30k blocks
  const rc = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getTransactionReceipt', params: [TX] });
  out.stake_tx_from = rc.result.from;
  out.stake_tx_to = rc.result.to;
  out.stake_tx_status = rc.result.status;
  const blk = await post({ jsonrpc: '2.0', id: 1, method: 'eth_getBlockByNumber', params: [rc.result.blockNumber, false] });
  out.stake_ts = new Date(parseInt(blk.result.timestamp, 16) * 1000).toISOString();
  // incoming DEUS transfers to W in last 30k blocks (Transfer topic with to=W)
  const t = await post({
    jsonrpc: '2.0', id: 1, method: 'eth_getLogs',
    params: [{ address: DEUS, topics: ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', null, pad(W)], fromBlock: '0x' + (head - 30000).toString(16), toBlock: '0x' + head.toString(16) }],
  });
  out.incoming = (t.result || []).map((l) => ({
    blk: parseInt(l.blockNumber, 16),
    from: '0x' + l.topics[1].slice(-40),
    deus: Number(BigInt(l.data)) / 1e18,
  }));
  console.log(JSON.stringify(out, null, 2));
})();
