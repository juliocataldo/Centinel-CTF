#!/usr/bin/env python3
"""Radio shack (JID/Pwn200) flag2 — unmask /log.bin.
/about: "Callsign BLACKOUT. Traffic is masked with the duty pad.
Vowels are stripped, then the pad repeats."
=> repeating-key XOR, key = BLACKOUT with vowels stripped = BLCKT.
Usage: python3 -I solve.py [log.bin]   (defaults to the captured bytes)
"""
import sys

CAPTURED = bytes.fromhex(
    "313f2b6b2727223739 2d62 6363 2735 2f3c 6e7c 6348".replace(" ", "")
)

def unmask(data: bytes, callsign: str = "BLACKOUT") -> str:
    key = bytes(c for c in callsign.encode() if c not in b"AEIOUaeiou")  # BLCKT
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data)).decode()

def main() -> None:
    data = open(sys.argv[1], "rb").read() if len(sys.argv) > 1 else CAPTURED
    out = unmask(data).strip()
    print(repr(out))
    # expected: "ssh sentry / lamp-77"  -> user=sentry  pass=lamp-77 (literal, keep -77)
    assert out == "ssh sentry / lamp-77", out
    user, pw = out[4:].split(" / ")
    print(f"user={user} pass={pw}")

if __name__ == "__main__":
    main()
