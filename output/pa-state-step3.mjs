// Supply side, venue spreads, level math, holder check.
import fs from 'node:fs';
const P = 'memory/topics/price-alert-state.json';
const st = JSON.parse(fs.readFileSync(P, 'utf8'));
const NOW = '2026-10-25T02:05:00Z';
const MARK = 0.017447263;

st.supply_side_02z = {
  observed_at: NOW,
  head_block: 53052250,
  escrow_deus: 29150566.777697522,
  escrow_24h_delta_deus: 41905.103034,
  escrow_24h_delta_pct: 0.144,
  five_pct_line_deus: 1457528.34,
  pressure_ratio: 0.0288,
  escrow_burns_1h: 0,
  escrow_note: 'Escrow balance BYTE-IDENTICAL to the prior two runs (29,150,566.777697522) - zero escrow events in the hour. The 24h window has now ROLLED: the 5,000 burn of 10-24 08:16Z aged out, leaving the three stakes (10,000 + 10,905.103034 + 36,000 = 56,905.103034) minus nothing = +41,905.103034 measured and reconciled to the wei. Seventh consecutive run with the 24h window closing exactly. Unstake pressure 0.029x the 5%/day line.',
  pending_unstake: {
    wallet: '0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63',
    xdeus_nft_id: 1396,
    status: 'NOT YET BURNED - eighth consecutive run',
    verified: 'balanceOf(xDEUS) = 1, tokenOfOwnerByIndex(owner, 0) = 1396 at blk 53052250'
  },
  xdeus_total_supply: 1728,
  read: 'No unstake pressure of any kind. The pending #1396 trigger has now been armed and unfired for eight consecutive runs (~2 days). The 5-day cooldown means if the operator ever intends to use the $0.041 exit they must start now - but nothing in the escrow says anyone is.'
};

st.venue_spread = {
  observed_at: NOW,
  deepest_pool_mark: MARK,
  usdc_v3_median: 0.01734,
  usdc_v3_venues: { '0x58dBa34e': 0.01734, '0x1B2f3f5C': 0.01734, '0x75bc1495': 0.01745 },
  uniswap_v4: 0.01743,
  dexscreener_deepest: 0.01735,
  premium_pct: 0.62,
  note: 'The deepest pool now sits at a small PREMIUM to the USDC venues rather than the persistent DISCOUNT that fed the arb flow yesterday. Combined with the sweep bidding across four USDC venues AND the deepest pool, the venues have converged - which is what removes the arb bid (TELL 20 corollary).'
};

st.level_math = {
  method: 'constant-product x*y=k on deepest-pool reserves at blk 53052250, zero fees, no other flow. D_new = D_cur*sqrt(r_cur/r_tgt), r = VIRTUAL per DEUS.',
  observed_at: NOW,
  reserves: { virtual: 525651.4765648125, deus: 18944498.344048623, mark_usd: MARK, virtual_usd: 0.6288 },
  to_0_012: { action: 'net SELL', deus_needed: 3889576, usd_needed: 67808, pct_of_pool_deus: 20.5, mult_of_101k_dump: 38.2 },
  to_0_025: { action: 'net BUY', deus_needed: 3124588, usd_needed: 54472, pct_of_pool_deus: 16.5 },
  to_0_032: { action: 'net BUY', deus_needed: 4961541, usd_needed: 86496, pct_of_pool_deus: 26.2 },
  to_0_041: {
    action: 'net BUY', deus_needed: 6591224, usd_needed: 114907, pct_of_pool_deus: 34.8,
    note: 'Still ~240x the deepest pool 24h volume. $0.041 remains reachable only by supply WITHDRAWAL, not by buying - unchanged rationale for the 5-day unstake lead time.'
  }
};

st.holder_check = {
  observed_at: NOW,
  note: 'Prior run confirmed all four large holders BYTE-IDENTICAL over 1h: 0x7f6aba75 335,249.499443 / 0x6a45ca8b 70,034.140337 / 0xf0a04b07 250,000.125225 / 0x9d1c316f 284,371.457830 = 939,655 total vs 638,668 a day earlier (+300,987 absorbed by four hands). This run ADDS A FIFTH: 0x4e3ae00e8323558fa5cac04b152238924aa31b60 holds 8,070,712.23 DEUS (0.92% of supply) and is the funding source for this hour\'s seller. That address has declined from 8,621,345.61 at -30d and 8,127,671.11 at -24h - a slow, controlled distribution of ~50k/day. THE FOUR-FIRM "accumulation" STORY IS NOT THE WHOLE BOOK: total supply is barely shrinking and one 8M holder is feeding every small sell clip.'
};

fs.writeFileSync(P, JSON.stringify(st, null, 2) + '\n');
console.log('STATE_WRITTEN step3');
