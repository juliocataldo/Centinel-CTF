#!/usr/bin/env python3
# Probe the RIGHT-half trigger of the spectrum desk service. Seed is fixed (left stayed 4f91c0aa),
# so each payload runs on a fresh connection. Dumps raw repr so we see the exact format.
# Run manually: python3 probe.py
import socket
HOST, PORT = "10.10.10.31", 8800

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

payloads = [
    b"AUTH A?",
    b"AUTH " + b"A"*13 + b"?",
    b"AUTH " + b"A"*15 + b"?",
    b"AUTH " + b"A"*20 + b"?",
    b"AUTH " + b"A"*30 + b"?",
    b"AUTH name?",
    b"AUTH ?",
    b"AUTH " + b"A"*12 + b"?",
    b"AUTH " + b"A"*16,          # control: left again, confirm seed stable
]
for p in payloads:
    try:
        s = socket.create_connection((HOST, PORT), timeout=6)
        recv(s)                   # drain banner
        s.sendall(p + b"\n")
        print(f"{p!r:40} -> {recv(s)!r}")
        s.close()
    except Exception as e:
        print(f"{p!r:40} -> ERR {e}")
