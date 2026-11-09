<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Quadratic+Shares" alt="Typing SVG" /></a>

</div>

# Quadratic Shares — CRYPTO · JID-? · Level 4 · ❓ UNKNOWN

- **Status:** ✅ SOLVED (1/1) — secret `1567` recovered from the 3 desk shares; all flags accepted by the platform.
- **Points:** — (unknown)
- **Flags:** Secret (plaintext number, format unconfirmed)
- **Attachment:** `shares.txt` (challenge parameters + shares) · `solve.py` (local Lagrange solver)
- **Prompt:** *Shamir-style secret sharing over a prime field; recover the secret.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Secret | `1567` | ✅ |

---

## TL;DR

1. Shamir secret sharing over GF(10007), threshold 3 → the hidden polynomial is **quadratic** (degree 2).
2. Lagrange-interpolate the 3 **desk** shares to `f(0)` → secret = **1567**.
3. The "Posted secret" `90211` and the "Extra point" `(1,1792)` are decoys: `90211 mod 10007 = 148`, and the extra point is **not** on the quadratic (`f(1)=1669 ≠ 1792`), so folding it in (degree-3 interpolation) gives the wrong `9431`.

## Parameters (`shares.txt`)

```
Posted secret: 90211        <- decoy
Modulus:       10007        (prime)
Threshold:     3            -> degree-2 polynomial
Desk shares (x, y): (2,1809) (5,2457) (7,3079)
Extra point (not a desk share): (1,1792)   <- decoy
```

## Analysis

Threshold 3 means any 3 shares define the degree-2 polynomial `f(x) = a0 + a1·x + a2·x²` over
`GF(p)`, with the secret `a0 = f(0)`. Interpolating the three desk shares:

```
coeffs a0, a1, a2 = 1567, 83, 19
Secret f(0) mod p = 1567
```

The recovered polynomial reproduces all three desk shares (`assert` in `solve.py` passes). The
integer-field Lagrange of the same 3 points also gives `1567`, so the secret is `1567`.

## What didn't work (the decoys)

| Hypothesis | Result | Why |
|---|---|---|
| "Posted secret" `90211` is the answer | ✗ | `90211 mod 10007 = 148`; not `f(0)`. Pure decoy. |
| Include the "Extra point" `(1,1792)` | ✗ | `f(1) = 1669 ≠ 1792` — the point is not on the quadratic. Interpolating 4 points as degree-3 gives `9431`. |
| Treat extra point as a 2-point line with each desk share | ✗ | Yields inconsistent `f(0)` (1775 / 9131 / 6581). |

Only the three genuine desk shares, interpolated at the stated threshold (degree 2), agree.

## Solve

`solve.py` interpolates the desk shares (rational + modular), extracts the coefficients, and
checks every decoy path. Run locally (reads only the in-script parameters, no network):

```
$ python3 -I solve.py
coeffs a0,a1,a2 = 1567 83 19
Secret f(0) mod p = 1567
f(1) = 1669 extra y = 1792 match: False
90211 mod p = 148
integer Lagrange f(0) = 1567
deg3 w/ extra, mod p f(0) = 9431
```

## Conclusion

Secret = **`1567`**. Accepted by the platform.

---

## Appendix — tools

- `solve.py` — `python3 -I solve.py`: Lagrange interpolation of the desk shares + decoy checks.
