<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Slip+Checker" alt="Typing SVG" /></a>

</div>

# Slip Checker — REV · JID-Rev100 · Level 1 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (3/3) — all three inputs recovered; `printf 'MIRA\n7\nchalk\n' | ./slip` prints `accepted` locally.
- **Points:** — / —
- **Flags:** Boat → Berth → Word (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `slip` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The slip checker from the duty desk. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `MIRA` | ✅ |
| 2 | Berth | `7` | ✅ |
| 3 | Word | `chalk` | ✅ |

---

## TL;DR

1. `slip` is a stdin checker that runs each input through a reversible per-byte ARX transform (`13*i + in[i] + prev`, XOR, `rol8(_,3)`) and `memcmp`s against stored bytes.
2. The chain uses the previous *rotated* output byte, so every input byte inverts independently from the known expected bytes.
3. Reversing the three checks yields `MIRA` / `7` / `chalk`.

## Recon

`strings` shows a small stdin checker:

```
Boat:
Berth:
Word:
accepted
rejected
Posted slip: boat ROCA, berth 9, word barrel. This slip is not accepted.
```

The "posted slip" is a decoy. The binary says outright that it is not accepted.

The binary is not stripped, so `nm` gives the useful symbols right away:

```
0000000000001189 t line
00000000000011b8 t same
000000000000123c T main
0000000000002079 r word.0
000000000000207e r berth.1
000000000000207f r boat.2
```

The imports are `fgets`, `strcspn`, `strlen`, `memcmp`, `puts` and `fwrite`. There is no anti-debug, no crypto library and no network code.

## main

`main` prints the slip banner and reads three lines (32-byte buffers) with `line()`, which is `fgets` + `strcspn("\n")`. It then calls the same check function three times:

```c
if (same(boat,  boat_2,  4, 0x21) &&
    same(berth, berth_1, 1, 0x44) &&
    same(word,  word_0,  5, 0x19))
    puts("accepted");
else
    puts("rejected");
```

## same()

Reconstructed from the disassembly at `0x11b8`:

```c
int same(char *in, uint8_t *expected, int len, uint8_t seed) {
    uint8_t out[24], prev = seed;
    if (strlen(in) != len) return 0;
    for (int i = 0; i < len; i++) {
        uint8_t e = (13*i + in[i] + prev) ^ (17*i) ^ 0xa7;
        out[i] = rol8(e, 3);
        prev = out[i];              // chained on the *rotated* output byte
    }
    return memcmp(out, expected, len) == 0;
}
```

Every step can be undone, and `prev` is the previous output byte, which we know from the expected bytes. Each input byte can therefore be recovered on its own:

```
in[i] = (ror8(expected[i], 3) ^ 0xa7 ^ 17*i) - 13*i - prev     (mod 256)
prev  = seed for i = 0, otherwise expected[i-1]
```

The easy mistake is to chain on the value *before* the rotation. `r13d` is loaded right after the `rol`, so it holds the rotated byte. Getting this wrong produces non-printable bytes.

## Expected bytes

In `.rodata` the virtual address equals the file offset (`0x2000`), so the constants can be read straight from the file:

| Symbol    | Offset   | Len | Seed   | Bytes        |
|-----------|----------|-----|--------|--------------|
| `boat.2`  | `0x207f` | 4   | `0x21` | `4e90cb3d`   |
| `berth.1` | `0x207e` | 1   | `0x44` | `e6`         |
| `word.0`  | `0x2079` | 5   | `0x19` | `de2f79c404` |

## Solve

[`solve.py`](solve.py) reverses each check and asserts that the forward transform gives back the stored bytes:

```
$ python3 solve.py slip
boat 4e90cb3d b'MIRA' 4d495241
berth e6 b'7' 37
word de2f79c404 b'chalk' 6368616c6b
```

Local confirmation:

```
$ chmod +x slip && printf 'MIRA\n7\nchalk\n' | ./slip
...
accepted
```

## Notes

- The flags are plaintext. `CTF{MIRA}` was rejected and `MIRA` was accepted. Read the per-flag "Format:" line before you submit.
- The decoy slip (`ROCA` / `9` / `barrel`) fails the check, as its own text says.
