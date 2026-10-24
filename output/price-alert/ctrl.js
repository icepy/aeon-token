const RPC = 'https://base.gateway.tenderly.co';
const DEUS = '0x940A319B75861014A220D9c6c144d108552B089B';
const W = '0xe338adc6c0fb242ca5bb2711c7f789c24486e61d';
const head = 53041380;
const T = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const pad = (a) => '0x000000000000000000000000' + a.slice(2).toLowerCase();

async function logs(params) {
  const r = await fetch(RPC, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'eth_getLogs', params: [params] }) });
  const j = await r.json();
  if (j.error) return { error: j.error };
  return { count: j.result.length, logs: j.result };
}
(async () => {
  // A: to = W, wide window (checks the filter)
  const a = await logs({ address: DEUS, topics: [T, null, pad(W)], fromBlock: '0x' + (head - 30000).toString(16), toBlock: '0x' + head.toString(16) });
  console.log('A to=W last30k:', a.error ? 'ERR ' + JSON.stringify(a.error) : a.count);
  // B: any DEUS transfer in last 1000 blocks (control that the topic works at all)
  const b = await logs({ address: DEUS, topics: [T], fromBlock: '0x' + (head - 1000).toString(16), toBlock: '0x' + head.toString(16) });
  console.log('B any DEUS transfer last1000:', b.error ? 'ERR ' + JSON.stringify(b.error) : b.count);
  // C: wrong topic, must be 0
  const c = await logs({ address: DEUS, topics: [T.slice(0, 65) + 'c'], fromBlock: '0x' + (head - 1000).toString(16), toBlock: '0x' + head.toString(16) });
  console.log('C wrong topic:', c.error ? 'ERR ' + JSON.stringify(c.error) : c.count);
  // D: from = W
  const d = await logs({ address: DEUS, topics: [T, pad(W)], fromBlock: '0x' + (head - 30000).toString(16), toBlock: '0x' + head.toString(16) });
  console.log('D from=W last30k:', d.error ? 'ERR ' + JSON.stringify(d.error) : d.count);
  if (d.logs) for (const l of d.logs) console.log('  out', parseInt(l.blockNumber, 16), Number(BigInt(l.data)) / 1e18, 'to 0x' + l.topics[2].slice(-40));
  if (a.logs) for (const l of a.logs) console.log('  in ', parseInt(l.blockNumber, 16), Number(BigInt(l.data)) / 1e18, 'from 0x' + l.topics[1].slice(-40));
})();
