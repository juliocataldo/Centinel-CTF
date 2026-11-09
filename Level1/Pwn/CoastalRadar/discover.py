#!/usr/bin/env python3
# Content discovery on Coastal radar 8448: find hidden endpoints + try to read app source.
# YOU run it. Prints status for each probe that is NOT a plain 404-"no" page.
import urllib.request, re

BASE = "http://10.10.10.22:8448"

# 1) root-level paths (endpoints + source/backup files + VCS)
paths = [
    "/", "/login", "/admin", "/docs/", "/calibrate", "/calibration", "/signal",
    "/radar", "/station", "/report", "/reports", "/panel", "/console", "/debug",
    "/source", "/src", "/app.py", "/server.py", "/main.py", "/radar.py", "/web.py",
    "/index.py", "/cal.py", "/calib.py", "/app.py.bak", "/app.py~", "/server.py.bak",
    "/.git/HEAD", "/.git/config", "/backup", "/backup.zip", "/app.zip", "/.env",
    "/robots.txt", "/sitemap.xml", "/favicon.ico", "/static/", "/assets/",
    "/login?debug=1", "/admin?debug=1", "/version", "/health", "/status",
]
# 2) source files via the /docs file server (same dir as protocol.txt?)
docs = ["app.py", "server.py", "main.py", "radar.py", "web.py", "cal.py", "calib.py",
        "handler.py", "auth.py", "__main__.py", "app.py.bak", "source.txt", "app.txt"]

def probe(url):
    try:
        r = urllib.request.urlopen(url, timeout=5)
        return r.getcode(), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")
    except Exception as ex:
        return None, str(ex)

def body_tail(b):
    m = re.search(r'RADAR CALIBRATION</p>(.*?)</div>', b, re.S)
    return (m.group(1).strip() if m else b[:200].strip())

print("== root paths ==")
for p in paths:
    code, body = probe(BASE + p)
    t = body_tail(body)
    # skip the boring 404 "no" and the known pages
    if code == 404 and t == "no":
        continue
    flag = " <== INTERESTING" if (code not in (404,) and t not in ("no", "denied", "admin only")) else ""
    print(f"[{code}] {p:28} -> {t[:80]!r}{flag}")

print("\n== /docs/ source guesses ==")
for d in docs:
    code, body = probe(f"{BASE}/docs/{d}")
    t = body_tail(body)
    if t == "no":
        continue
    print(f"[{code}] /docs/{d} ->\n{body[:500]}\n")
print("done.")
