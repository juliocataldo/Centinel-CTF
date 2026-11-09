<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Packed+Checker" alt="Typing SVG" /></a>

</div>

# Packed Checker — REV · JID-Rev202 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (2/2) — `NILE/64` recovered by re-implementing the unpacker and verified locally (stdin/stdout only).
- **Points:** — (unknown)
- **Flags:** Boat → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `packed` (ELF 64-bit PIE x86-64, not stripped)
- **Prompt:** *"A packed checker. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `NILE` | ✅ |
| 2 | Litres | `64` | ✅ |

---

## TL;DR

1. The expected bytes exist only after a tiny LZ unpacker in `main` expands a 10-byte `.rodata` blob (`strings` sees only the `ROCA`/`240` decoy manual).
2. Boat check: `rol(c,4) ^ (k+0x19) == out[k]`; litres check: `litres*3+9 == out[4]|out[5]<<8` (`0x00c9 = 201`).
3. Invert → **Boat `NILE`, Litres (201−9)/3 = `64`**.

## Recon

The imports are `fgets`, `strcspn`, `strlen`, `strtol`, `puts` and `fwrite`. `nm` shows
`main`, `line` (fgets + strcspn) and one data symbol:

```
0000000000002078 r packed
```

`strings` shows the decoy:

```
Packed manual: boat ROCA, litres 240. This manual is not the checker.
Boat:  Litres:  accepted  rejected
```

`packed` is 10 bytes in `.rodata` (vaddr equals file offset):

```
0x2078  06 fd 8e df 48 c9 00 84 06 00
```

## The unpacker (main 0x123a)

`main` unpacks the blob into a buffer at `rsp` with a tiny LZ scheme:

```c
for (i = 0, n = 0; i <= 9 && (c = packed[i]); ) {
    if (c & 0x80) {                       // backref
        len = c & 0x7f; off = packed[i+1];
        for (k = 0; k < len; k++) out[n+k] = out[n+k-off];
        n += len; i += 2;
    } else {                              // literal run
        memcpy(out+n, packed+i+1, c);
        n += c; i += 1 + c;
    }
}
if (n <= 5) reject;
```

Running it by hand:

| Control  | Meaning                     | Output so far                    |
|----------|-----------------------------|----------------------------------|
| `06`     | literal, 6 bytes            | `fd 8e df 48 c9 00`              |
| `84 06`  | backref, len 4, offset 6    | `fd 8e df 48 c9 00 fd 8e df 48`  |
| `00`     | end                         |                                  |

## The checks

```
12e6  strlen(boat) == 4
1300  for k in 0..3:  rol(boat[k], 4) ^ (k + 0x19) == out[k]
131c  litres * 3 + 9 == out[4] | out[5] << 8          ; 0x00c9 = 201
1341  cmove -> "accepted" / "rejected"
```

Inverting the two checks:

```
boat[k] = rol(out[k] ^ (k + 0x19), 4)
  fd ^ 19 = e4 -> 4e 'N'
  8e ^ 1a = 94 -> 49 'I'
  df ^ 1b = c4 -> 4c 'L'
  48 ^ 1c = 54 -> 45 'E'

litres = (201 - 9) / 3 = 64
```

## Solve

[`solve.py`](solve.py) re-implements the unpacker, inverts both checks and asserts the result:

```
$ python3 -I solve.py packed
unpacked = fd 8e df 48 c9 00 fd 8e df 48
Boat   = NILE
Litres = 64
```

Local confirmation (stdin/stdout only):

```
$ printf 'NILE\n64\n' | ./packed     -> accepted
$ printf 'ROCA\n240\n' | ./packed    -> rejected
$ printf 'NILE\n65\n' | ./packed     -> rejected
```

## Notes

- The flags are plaintext. Submit `NILE`, then `64`.
- The trap is the printed "manual" (`ROCA` / `240`). The real expected bytes only exist after
  unpacking, so `strings` cannot find them.
- The second half of the unpacked buffer (the backref copy) is never read by the checks. Only
  `out[0..5]` matter.
