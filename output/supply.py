import json, sys
sys.path.insert(0, "output")
from decimal import Decimal
from rpc import call

ESCROW = "0xA85A38796B951CE87B378538b32B3E6Ee3C4C373"
XDEUS = "0xe6d5f7439Bc236C40054e2275f765f59343D4431"
HOLDER = "0xbb0f753321e2b5fd29bd1d14b532f5b54959ae63"
DEUS = "0x940A319B75861014A220D9c6c144d108552B089B"

def bal(token, who, blk="latest"):
    b = hex(blk) if blk != "latest" else blk
    r = call("eth_call", [{"to": token,
                           "data": "0x70a08231" + "0" * 24 + who[2:].lower()}, b])
    return int(r, 16) / 1e18

blk = int(sys.argv[1])
print(json.dumps({
    "block": blk,
    "escrow_deus": bal(DEUS, ESCROW, blk),
    "holder_xdeus": bal(XDEUS, HOLDER, blk),
    "holder_deus": bal(DEUS, HOLDER, blk),
}, indent=1))
