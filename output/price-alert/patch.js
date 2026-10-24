const fs = require('fs');
const P = 'memory/topics/price-alert-state.json';
const s = JSON.parse(fs.readFileSync(P, 'utf8'));
const mark = 0.01741034;
const dist = { '0.012': -31.08, '0.025': 43.59, '0.032': 83.8, '0.041': 135.49 };
for (const k of Object.keys(s.targets)) {
  s.targets[k].last_checked_price = mark;
  s.targets[k].last_checked_at = '2026-10-24T20:01:47Z';
  s.targets[k].distance_pct = dist[k];
}
// hour activity block
s.deepest_pool_activity = {
  window: 'blk 53039581 -> 53041380 (19:01:47Z .. 20:01:47Z)',
  swap_events: 4,
  family: 'Solidly (Aerodrome classic) - Swap topic0 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b (full 64-hex)',
  buy_tx_count: 0,
  buy_deus_out: 0.0,
  sell_tx_count: 4,
  sell_deus_in: 4704.0186,
  net_deus_into_pool: 4704.0186,
  largest_sell_deus: 2200.0,
  control_note: 'Filter discriminative: right topic0 over the last 14 blocks returned 4 logs, one-char-wrong topic0 returned 0. Decoder reconciled to reserves: 4,704.0186 DEUS in minus 1% Aerodrome fee = 4,656.98, matching the measured reserve delta exactly.',
  observed_at: '2026-10-24T20:01:47Z',
  read: 'ALL FOUR SELLS ARE ARB, NOT DISTRIBUTION. DEUS legs traced: 780.24 from USDC V3 0x58dBa34e, 842.54 from USDC V3 0x1B2f3f5C, 881.24 from 0x58dBa34e, 2,200.00 from 0xeb7c90d3 (router; the 0x6abea499 leg that was a BUY-side sink on prior runs). Only 4,704 DEUS/hour is being arb-ed against a +1.34% premium, so the tape is extremely thin - this is an absence of directional flow on BOTH sides, not a selloff and not a bid.',
};
s.level_math = {
  method: 'constant-product x*y=k on deepest-pool reserves at blk 53041380, zero fees, no other flow. Solved in RATIO space (target/VIRTUAL_price) so the VIRTUAL leg need not be held constant: D_needed = D*(sqrt(r_cur/r_target)-1).',
  observed_at: '2026-10-24T20:01:47Z',
  reserves: { virtual: 526810.442689199, deus: 18902821.05361343, mark_usd: 0.01741034, virtual_usd: 0.62471163 },
  to_0_012: { action: 'net SELL', deus_needed: 3865954, usd_needed: 67308, mult_of_101k_dump: 37.91 },
  to_0_025: { action: 'net BUY', deus_needed: 3128151, usd_needed: 54462 },
  to_0_032: { action: 'net BUY', deus_needed: 4959851, usd_needed: 86353 },
  to_0_041: { action: 'net BUY', deus_needed: 6584873, usd_needed: 114645, note: 'Still ~238x the deepest pool 24h volume. $0.041 only reachable by supply WITHDRAWAL from the book - unchanged, and the whole reason for the 5-day unstake lead time.' },
};
s.holder_check = {
  observed_at: '2026-10-24T20:01:47Z',
  note: 'All addresses taken from memory, not hand-typed (false-zero form 5). 0x7f6aba7563cb5d31980d440337d3d1a6e3db58f3 = 335,249.499443 (unchanged). 0x6a45ca8bb30f396f40721e105e0aa6cabf326657 = 70,034.140337 (unchanged). 0xf0a04b079dcf7b9d92682123ba2e2180109cb650 = 250,000.125225 (unchanged, no further trim). 0x9d1c316f1f307894c80e7d2963454e6342c8e0a9 = 284,371.457830 (unchanged, no distribution leg). 0xbb0f7533 DEUS = 0.000000 and STILL holds xDEUS #1396 (tokenOfOwnerByIndex(0)=1396) - trigger NOT fired, third consecutive run.',
  pending_unstake: { wallet: '0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63', xdeus_nft_id: 1396, status: 'NOT YET BURNED - re-verified at latest' },
};
fs.writeFileSync(P, JSON.stringify(s, null, 2) + '\n');
console.log('written');
