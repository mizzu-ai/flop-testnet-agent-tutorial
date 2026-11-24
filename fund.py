"""Claim a FLOP devnet faucet grant — two lanes.

Usage:
  python3 fund.py --post    POST /fund: 25 FLOP, tier "anonymous".
                            DO THIS FIRST on a fresh address: an address
                            already funded on the agent lane keeps agent
                            rules on every lane (official faucet guide),
                            so the 25 FLOP lane is only available before
                            any agent-lane grant.
  python3 fund.py <nonce>   Agent lane: sign challenge
                            "fund|<ss58>|<nonce>" with the Sr25519 wallet
                            key and privately GET the faucet fund endpoint.
                            2 FLOP per grant, 24 h cooldown, repeat grant
                            needs on-chain spend of the previous grant.

Reads the wallet address from wallet.json (0600). The --post lane only
needs the address; the <nonce> lane also needs the mnemonic to sign.
Prints ONLY the faucet response. Never prints the mnemonic or signature.
"""
import json
import os
import subprocess
import sys

from substrateinterface import Keypair

OUT = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    print("usage: fund.py --post | fund.py <nonce>")
    sys.exit(2)

with open(f"{OUT}/wallet.json") as f:
    w = json.load(f)
addr = w["address"]

if sys.argv[1] == "--post":
    payload = json.dumps({"address": addr, "client": "flop-llms-txt"})
    r = subprocess.run(
        ["curl", "-s", "-m", "30", "-X", "POST",
         "https://faucet.flop.network/fund",
         "-H", "content-type: application/json",
         "-d", payload],
        capture_output=True, text=True)
    print("faucet reply:")
    print(r.stdout[:1500])
    if r.stderr:
        print("STDERR:", r.stderr[:300])
    sys.exit(0)

nonce = sys.argv[1]
kp = Keypair.create_from_mnemonic(w["mnemonic"], ss58_format=42)
assert kp.ss58_address == addr, "wallet address mismatch"

challenge = f"fund|{addr}|{nonce}".encode("utf-8")
sig_hex = "0x" + kp.sign(challenge).hex()
url = f"https://faucet.technocore.chat/faucet/fund/{addr}/{nonce}/{sig_hex}"
r = subprocess.run(["curl", "-s", "-m", "30", url],
                   capture_output=True, text=True)
print("faucet reply:")
print(r.stdout[:1500])
if r.stderr:
    print("STDERR:", r.stderr[:300])
