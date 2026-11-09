<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Small+Modulus" alt="Typing SVG" /></a>

</div>

# Small Modulus — CRYPTO · JID-Crypto106 · Level 1 · 🟢 EASY

- **Status:** ✅ SOLVED (3/3) — `PEAK` confirmed accepted on the platform, which fixed the base-26 convention; `CAIR` and `64` follow from the same rule.
- **Points:** — / —
- **Flags:** Boat → Word → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `seal.txt`
- **Prompt:** *"A seal under a small modulus. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `PEAK` | ✅ |
| 2 | Word | `CAIR` | ✅ |
| 3 | Litres | `64` | ✅ |

---

## TL;DR

1. `seal.txt` is textbook RSA: three ciphertexts under a 20-bit modulus `n = 988027`.
2. Factor `n = 991 × 997` by trial division, derive `d`, decrypt each value.
3. Boat/Word decode as 4-letter base-26 words (`A=0`, MSB first) → `PEAK`, `CAIR`; Litres is the raw integer `64`.

## The file

```
Sample result: boat ROCA, word barrel, litres 240.

n = 988027
e = 65537
boat = 86874
word = 452946
litres = 626309
```

This is textbook RSA. Three ciphertexts are encrypted under the same public key, one for each flag. The "sample result" line is a decoy, in the same style as the other JID challenges. It has no ciphertext to go with it, and its shape ("barrel" has 6 lowercase letters) doesn't even match the real Word flag.

## Breaking the key

`n` is only 20 bits, so you can factor it by trial division in microseconds:

```
n = 988027 = 991 × 997
phi = 990 × 996 = 986040
d = e^-1 mod phi = 919313
```

Decrypting with `m = c^d mod n` gives the following (each value was checked by re-encrypting, `m^e mod n == c`):

| Item   | c      | m      |
|--------|--------|--------|
| boat   | 86874  | 266354 |
| word   | 452946 | 35377  |
| litres | 626309 | 64     |

## Decoding

The flag text asks for "four letters … in capitals", and `26^4 = 456976 < n`. That points to a 4-letter word packed as a base-26 integer, with `A = 0` and the most significant letter first:

```
266354 = 15·26³ + 4·26² + 0·26 + 10  → P E A K
 35377 =  2·26³ + 0·26² + 8·26 + 17  → C A I R
```

Both values decode to exactly four letters (the leading digit is non-zero), so there is no padding ambiguity. With `A = 1` the output is garbage. After `PEAK` was accepted, that confirmed the convention, and `CAIR` followed from the same rule. It isn't an English word, but the flag calls it an "order word", meaning a code word.

Litres is not encoded at all. The decrypted integer `64` is the answer.

## Solver

`solve.py` factors `n`, derives `d`, decrypts all three values and prints their base-26 readings for both alphabet offsets:

```
python3 -I solve.py
```

## Takeaway

RSA with a toy modulus gives no security. Anything below a few hundred bits falls to trial division, Pollard rho or factordb. The only real work here was guessing the plaintext packing, and the "four letters, in capitals" wording plus `26^4 < n` gave it away.
