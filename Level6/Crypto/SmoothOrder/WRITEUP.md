<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Smooth+Order" alt="Typing SVG" /></a>

</div>

# Smooth Order — CRYPTO · JID-Crypto300 · Level 6 · 🔴 HARD

- **Status:** ✅ SOLVED (2/2) — both chained flags recovered.
- **Points:** — / — (per-flag points not recorded)
- **Flags:** Log → Shared (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `discrete.txt`
- **Prompt:** *"A discrete log in a group whose order is smooth. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Log | `68234299377316231179` | ✅ |
| 2 | Shared | `16464610837819041266` | ✅ |

---

## TL;DR

1. `p-1` is 53-smooth, so Pohlig-Hellman reduces the 67-bit discrete log `7^x ≡ h (mod p)` to a handful of ≤53-element searches.
2. Flag 1 is that log, `x = 68234299377316231179` (the "posted log" in the file is a decoy).
3. The setup is Diffie-Hellman; the shared secret `peer^x mod p = 16464610837819041266` is Flag 2.

## The file

```
Posted log: 240183
p = 97767475431570134191
g = 7
h = 28690494907310954915
peer = 6709581214550667291
Every prime factor of p - 1 is at most 53.
```

Flag 1 asks for the discrete log of `h` to base `g`: the `x` with `7^x ≡ h (mod p)`. The "posted log" is a decoy, in the same style as the other JID challenges. One modular exponentiation shows it's wrong: `pow(7, 240183, p) != h`.

## Why it breaks

`p` is about 67 bits and prime (Miller-Rabin). The hint is true. `p - 1` factors as:

```
p - 1 = 2 · 3² · 5 · 7 · 11 · 13 · 17 · 19 · 23 · 29 · 31 · 37 · 41 · 43 · 47 · 53
```

For every prime `q | p-1`, `7^((p-1)/q) ≠ 1 (mod p)`. That makes `7` a primitive root: `ord(7) = p - 1`. So the log is unique mod `p - 1`, and there's no ambiguity about which `x` to submit.

When the group order is smooth, Pohlig-Hellman reduces one 67-bit discrete log to a handful of tiny ones. For each prime power `qᵉ ‖ p-1`:

```
g_q = g^((p-1)/qᵉ)        # generator of the subgroup of order qᵉ
h_q = h^((p-1)/qᵉ)
x_q = log_{g_q}(h_q)      # brute force, at most 53 steps
```

The CRT then combines the residues `x ≡ x_q (mod qᵉ)` into `x mod (p-1)`. The largest subgroup has 53 elements, so the whole thing finishes instantly in pure Python. No Sage or sympy is needed.

## Flag 1: Log

```
x = 68234299377316231179
pow(7, x, p) == h   → True
```

## Flag 2: Shared

The setup is Diffie-Hellman: `h = g^x` is our public key, and `peer` is the other party's public key. The shared secret is `peer^x mod p`:

```
shared = pow(peer, x, p) = 16464610837819041266
```

I checked it from the other side too. Running Pohlig-Hellman on `peer` gives `y = 54856293887286781200` with `7^y ≡ peer`, and `pow(h, y, p)` gives the same `16464610837819041266`.

## Reproduce

`solve.py` is standalone Python with no dependencies. It checks primality, factors `p-1`, computes element orders, runs the decoy check and Pohlig-Hellman for both logs, and prints the shared secret.

```
python3 -I solve.py
```

## Takeaway

DH or ElGamal over `Z_p*` is only as strong as the largest prime factor of the group order. A safe prime (`p = 2q + 1` with `q` prime) is what stops this attack. Here the largest factor is 53, so the 67-bit log costs about the same as a 53-element search.
