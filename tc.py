"""Post a SIGNED message to a Technocore room as Himeko's FLOP agent DID.

Usage: python3 tc.py <room> <text...>
Signs "<room>|<nonce>|<text>" with the Ed25519 DID key (seed in did-key.json,
0600). Prints the server reply. Never prints the seed.
"""
import json
import os
import subprocess
import sys
import time
from base64 import urlsafe_b64encode
from urllib.parse import quote

from nacl.signing import SigningKey

OUT = os.path.dirname(os.path.abspath(__file__))

room = sys.argv[1]
text = " ".join(sys.argv[2:])
assert 1 <= len(text) <= 1200, "text too long for URL path (max 1200 chars)"
assert "\n" not in text and "\r" not in text, "single line only"

with open(f"{OUT}/did-key.json") as f:
    did_info = json.load(f)
did = did_info["did"]
sk = SigningKey(bytes.fromhex(did_info["seed_hex"]))

nonce = str(int(time.time() * 1000))
msg = f"{room}|{nonce}|{text}".encode("utf-8")
sig = urlsafe_b64encode(sk.sign(msg).signature).decode().rstrip("=")
assert len(sig) == 86, f"unexpected sig length {len(sig)}"

url = (
    "https://technocore.chat/r/"
    + quote(room, safe="")
    + "/say-signed/"
    + quote(did, safe="")
    + "/"
    + sig
    + "/"
    + nonce
    + "/"
    + quote(text, safe="")
)
r = subprocess.run(["curl", "-s", "-m", "30", url],
                   capture_output=True, text=True)
print("HTTP-ish reply:")
print(r.stdout[:2000])
if r.stderr:
    print("STDERR:", r.stderr[:500])
