<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Partial+State" alt="Typing SVG" /></a>

</div>

# Partial State — CRYPTO · JID-Crypto303 · Level 3 · 🔴 HARD

- **Status:** ✅ SOLVED (2/2) — the recovered state reproduces all six readings; all flags accepted by the platform.
- **Points:** —
- **Flags:** State → Next (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `readings.txt`
- **Prompt:** *"Readings that keep only the top of a 32-bit state. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | State | `1791209874` | ✅ |
| 2 | Next | `2638` | ✅ |

---

## TL;DR

1. An LCG with the Numerical Recipes constants (mod 2^32) leaks only the top 12 bits of each state (`state >> 20`).
2. The first reading fixes the top bits, so brute force over the 2^20 hidden low bits, filtered by the next five readings, leaves one state: `1791209874`.
3. Stepping past the sixth reading gives the next reading `2638`. The "next card shows 642" line is a decoy.

## The file

```
If the first reading is the whole state, the next card shows 642.
Multiplier 1664525, increment 1013904223, modulus 2^32.
Each reading is state >> 20.
1708
3974
196
180
3216
4036
```

This is a linear congruential generator with the Numerical Recipes constants:

```
s_{n+1} = (1664525 * s_n + 1013904223) mod 2^32
reading_n = s_n >> 20
```

Each reading leaks only the top 12 bits of the 32-bit state. The low 20 bits stay hidden.

## The decoy line

The first line pushes you to take the first reading as if it were the whole state. Taken literally, with `s = 1708`, the next reading would be `3678`. The only way to get `642` is to assume the hidden low bits are zero (`s = 1708 << 20`), and the next real reading is `3974`, not `642`. So the line describes a wrong assumption and is not data. It is the same kind of "sample result" decoy used in the other JID challenges.

## Recovering the state

The first reading fixes the top 12 bits, which leaves only 2^20 (about one million) candidates for the first state:

```
s0 = (1708 << 20) | x,   x in [0, 2^20)
```

For each candidate, step the LCG and keep it only if the next five readings match `3974, 196, 180, 3216, 4036`. Each extra reading cuts the candidate count by about 2^12, so five readings are far more than enough. Exactly one candidate survives:

```
s0 = 1791209874 (0x6ac3b192)
```

Running the generator from `s0` reproduces all six readings: `[1708, 3974, 196, 180, 3216, 4036]`.

**Flag 1 (State):** `1791209874`

## Predicting the next reading

The state after the sixth reading is `4232705805` (`0xfc49f70d`). One more step gives `2766449928` (`0xa4e4ad08`), and `2766449928 >> 20 = 2638`.

**Flag 2 (Next):** `2638`

## Solver

`solve.py` brute-forces the 2^20 low bits, checks each candidate against the remaining readings, and prints the next state and the next reading.

## Takeaway

Truncating an LCG's output does not hide its state. With a 32-bit state and 12 visible bits, plain brute force over the hidden bits is trivial. For larger states (e.g. 64-bit with the top 32 bits visible), the standard tool is a lattice/LLL attack on the truncated outputs.
