<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Fixed+Distance" alt="Typing SVG" /></a>

</div>

# Fixed Distance — CRYPTO · JID-Crypto302 · Level 3 · 🔴 HARD

- **Status:** ✅ SOLVED (2/2) — both flags accepted.
- **Points:** 480 / 480 (First 180, Second 300)
- **Flags:** First → Second (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `related.txt`
- **Prompt:** *"Fixed distance. Two integers sealed under one modulus, one a fixed distance from the other. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | First | `98747107080075315531909162460300428200` | ✅ |
| 2 | Second | `98747107080075315531909162460300432296` | ✅ |

---

## TL;DR

1. Textbook RSA with `e = 3` and two related messages `m2 = m1 + 4096`; the plain cube root fails because `m1^3` wraps mod `n`.
2. The difference `c2 - c1 = 3d·m^2 + 3d^2·m + d^3` is ~2^267, below `n`, so it does not wrap.
3. Solving that quadratic over the integers gives `m1` exactly; `m2 = m1 + 4096`.

## Challenge

> ***** BEGIN SECURE COMMUNIQUE *****
> Fixed distance. Two integers sealed under one modulus, one a fixed distance from the other. The file is on this page.
> ***** END SECURE COMMUNIQUE *****

Attachment: `related.txt`. Two chained flags (plaintext):

1. **First** (180) — "Submit the first sealed integer. Format: plaintext."
2. **Second** (300) — "Submit the second sealed integer. Format: plaintext."

```
Cube-root sample: 24031
Exponent 3. The second integer is the first plus 4096.
n  = 2396910216...38831   (327 bits, ~98 digits)
c1 = 3286740885...37623
c2 = 3286740885...07959
```

So it's textbook RSA with `e = 3` and two related messages: `m2 = m1 + d`, `d = 4096`.

## Dead ends

- **Plain cube root** (`iroot(c1, 3)`): not exact. `m1` is ~127 bits, so `m1^3` is ~380 bits > `n` — the
  ciphertext wrapped. The "Cube-root sample: 24031" line is a decoy pushing toward this.
- **Franklin–Reiter** (`gcd(x^3 - c1, (x+d)^3 - c2)` over Z_n) would work, but isn't needed.

## Key insight

Subtract the two ciphertexts:

```
(m+d)^3 - m^3 = 3d·m^2 + 3d^2·m + d^3
```

With `m ~ 2^127` and `d = 2^12`, the right-hand side is ~2^267, far below `n ~ 2^327`. Each cube wraps
mod `n`, but the **difference doesn't**, so `c2 - c1` (mod n) equals that polynomial over the integers.
That leaves an ordinary quadratic in `m`:

```
3d·m^2 + 3d^2·m + (d^3 - D) = 0,   D = (c2 - c1) mod n
```

Its discriminant is a perfect square and the positive root is exact.

## Solve

```python
import re, sys
from math import isqrt

t = open(sys.argv[1]).read()
g = lambda k: int(re.search(k + r"\s*[=:]\s*(\d+)", t).group(1))
n, c1, c2, d = g("n"), g("c1"), g("c2"), 4096

D = (c2 - c1) % n
a, b, c = 3*d, 3*d*d, d**3 - D
disc = b*b - 4*a*c
s = isqrt(disc)
assert s*s == disc
m1 = (-b + s) // (2*a)
assert pow(m1, 3, n) == c1 and pow(m1 + d, 3, n) == c2
print(m1, m1 + d)
```

Both checks pass when you re-encrypt under the given `n`. Neither integer decodes to printable bytes, so the
integers themselves are the answers.

## Takeaway

When `e` is small and messages are related by a small known offset, check whether the *difference* of the
ciphertexts fits below `n` before reaching for Franklin–Reiter. If it does, the problem reduces to a quadratic
over the integers.
