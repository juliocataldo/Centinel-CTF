#!/usr/bin/env python3
# Local HMAC candidate generator for Coastal radar /login. Does NOT contact the target.
# Hint (protocol.txt): "Station: 18. Example HMAC key is radar. Production pads the key with the station number."
# Usage: python3 hmac_gen.py <message>     e.g.  python3 hmac_gen.py admin
import hmac, hashlib, sys

msg = (sys.argv[1] if len(sys.argv) > 1 else "admin").encode()
station = "18"
keys = [f"radar{station}", f"{station}radar", f"radar-{station}", f"radar_{station}", "radar"]
algos = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}

for k in keys:
    for name, h in algos.items():
        d = hmac.new(k.encode(), msg, h).hexdigest()
        print(f"key={k:<10} {name:<6} HMAC({k!r}, {msg.decode()!r}) = {d}")
