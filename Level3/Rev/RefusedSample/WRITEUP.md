<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Refused+Sample" alt="Typing SVG" /></a>

</div>

# Refused Sample — REV · JID-Rev200 · Level 3 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — the inverted input is accepted by the local binary; all flags accepted by the platform.
- **Points:** —
- **Flags:** Boat → Berth → Word (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `slip` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The slip checker. The sample on the screen is refused. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `VELA` | ✅ |
| 2 | Berth | `4` | ✅ |
| 3 | Word | `cedar` | ✅ |

---

## TL;DR

1. The three inputs are packed into one 10-byte buffer, and a chained shift/XOR hash (`mix_at`) is checked on every prefix.
2. The low byte of each step depends only on the previous low byte, so the chain peels back one byte at a time: `buf[k] = (h[k] ^ 2*h[k-1]) ^ 13k`.
3. The unique preimage is `VELA | 4 | cedar`. Watch the indirect `h5+h6` and `h6^h7` checks.

This is the hard sequel to **Slip checker** (Rev100). The prompts and decoy are the same,
but the check is different. There are no expected-byte arrays and no `memcmp`. Instead, a
chained hash runs over every prefix of the combined input, and each prefix is checked
against an immediate in `main`.

## Recon

```
Sample slip: boat ROCA, berth 9, word barrel. This slip is not accepted.
Boat:  Berth:  Word:  accepted  rejected
```

The imports are `fgets`, `strcspn`, `strlen`, `puts` and `fwrite`. There is no `memcmp`.

`nm` shows the useful symbols:

```
0000000000001179 t mix_at
00000000000011ad t line      # fgets + strcspn("\r\n")
00000000000011dc T main
```

## main

`main` reads three lines into 32-byte buffers. It requires `strlen` = 4 / 1 / 5, then packs
them into one 10-byte buffer at `rsp+0x16`:

```
buf = boat[0:4] | berth[0] | word[0:5]
```

Then it calls `mix_at(buf, k)` for `k = 0..9` and checks the low byte of each result:

| k | Check (0x1398..0x1400)    | h[k] |
|---|---------------------------|------|
| 0 | `h0 == 0x3c`              | 0x3c |
| 1 | `h1 == 0x30`              | 0x30 |
| 2 | `h2 == 0x36`              | 0x36 |
| 3 | `h3 == 0x0a`              | 0x0a |
| 4 | `h4 == 0x14`              | 0x14 |
| 5 | `h5 == 0x0a`              | 0x0a |
| 6 | `h5 + h6 == 0x49`         | 0x3f |
| 7 | `h6 ^ h7 == 0x7e`         | 0x41 |
| 8 | `h8 == 0x8b`              | 0x8b |
| 9 | `h9 == 0x11` (`cmove`)    | 0x11 |

The last check picks `accepted` / `rejected` with a `cmove`, so there is no branch to patch
that would give you anything useful.

## mix_at (0x1179)

```c
uint32_t mix_at(uint8_t *buf, int n) {
    uint32_t h = 0x35;
    for (int k = 0; k <= n; k++)
        h = (h * 2) ^ ((13 * k) ^ buf[k]);
    return h;            // main only compares the low byte
}
```

Two details matter:

- `xor sil, [rdx]` only touches the low byte of `13k`. Since `13k < 256` for `k <= 9`, the
  term is just `buf[k] ^ 13k`.
- Doubling and XOR only push bits upward. So the low byte of `h` after step `k` depends only
  on the low byte after step `k-1`.

## Inversion

Every prefix is checked, so the hash can be peeled one byte at a time:

```
buf[k] = (h[k] ^ 2*h[k-1]) ^ 13k      (mod 256),  with h[-1] = 0x35
```

The solution is unique:

```
VELA | 4 | cedar
```

## Solve

[`solve.py`](solve.py) rebuilds `h[0..9]` from the checks (including the `+` and `^`
ones), inverts the chain and asserts the forward hash:

```
$ python3 -I solve.py
Boat  = VELA
Berth = 4
Word  = cedar
```

Local confirmation (the binary only uses stdin/stdout):

```
$ printf 'VELA\n4\ncedar\n' | ./slip
...
accepted
$ printf 'ROCA\n9\nbarrel\n' | ./slip
...
rejected
```

## Notes

- The flags are plaintext. Submit `VELA`, then `4`, then `cedar`.
- The traps are the indirect checks on `h6`/`h7` (`h5+h6` and `h6^h7`). If you read them
  as direct comparisons, you get garbage bytes for `word[1..2]`.
