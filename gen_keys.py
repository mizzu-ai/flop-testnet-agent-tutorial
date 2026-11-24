"""Generate FLOP testnet agent identity: Ed25519 DID + Sr25519 Substrate wallet.

Prints ONLY public values (DID, SS58 address). Secrets go to 0600 files only.
Never print the contents of did-key.json or wallet.json.
"""
import json
import os

import base58
from nacl.signing import SigningKey
from substrateinterface import Keypair

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

# --- DID identity key (Ed25519, did:key) ---
did_sk = SigningKey.generate()
did_pk = did_sk.verify_key.encode()  # 32 bytes
did = "did:key:z" + base58.b58encode(b"\xed\x01" + did_pk).decode()
with open(f"{OUT}/did-key.json", "w") as f:
    json.dump({"did": did, "seed_hex": did_sk.encode().hex()}, f)
os.chmod(f"{OUT}/did-key.json", 0o600)

# --- Wallet (Sr25519, standard Substrate, SS58 prefix 42) ---
mnemonic = Keypair.generate_mnemonic()
kp = Keypair.create_from_mnemonic(mnemonic, ss58_format=42)
addr = kp.ss58_address
with open(f"{OUT}/wallet.json", "w") as f:
    json.dump(
        {"address": addr, "mnemonic": mnemonic, "ss58_format": 42,
         "crypto_type": "sr25519", "network": "flop-testnet"},
        f,
    )
os.chmod(f"{OUT}/wallet.json", 0o600)

with open(f"{OUT}/public.json", "w") as f:
    json.dump(
        {"did": did, "wallet_address": addr, "network": "flop-testnet",
         "created": "2026-11-24"},
        f,
        indent=2,
    )

print("DID:", did)
print("WALLET:", addr)
print("saved: did-key.json wallet.json public.json (0600 for secrets)")
