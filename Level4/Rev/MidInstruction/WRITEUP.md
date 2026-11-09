<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Mid+Instruction" alt="Typing SVG" /></a>

</div>

# Mid Instruction — REV · JID-Rev206 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (2/2) — `WREN/8` recovered and verified locally (stdin/stdout only).
- **Points:** — (unknown)
- **Flags:** Boat → Berth (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `checker` (ELF 64-bit PIE x86-64, not stripped)
- **Prompt:** *"The checker jumps into the middle of an instruction. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `WREN` | ✅ |
| 2 | Berth | `8` | ✅ |

---

## TL;DR

1. `main` has an `argc==1000` decoy path (`ROCA`/`9`); the real path reads Boat/Berth and calls `check_entry`.
2. `check_entry` is `eb 01` (jmp +1) over a junk `0xe8` byte, so a linear disassembler desyncs; the real check (`mid`) starts at the jump target.
3. `mid` checks boat via `swap_nibbles(c) ^ (0x27+k)` vs `want` and berth `== '8'` → invert → **WREN / 8**.

## Recon

```
Posted check compares boat ROCA and berth 9.
ROCA  9  Boat:  Berth:  pass  fail
```

The imports are `fgets`, `strcspn`, `strcmp`, `fwrite` and `puts`. The symbols give the trick
away: `mid` sits 3 bytes into `check_entry`.

```
000000000000128c T check_entry
000000000000128f t mid
000000000000130d t fail
```

## main

**Decoy path, `argc == 1000`** (`0x1257`): `strcmp(argv[1], "ROCA") && strcmp(argv[2], "9")`.
This is the "posted check", and it never touches stdin.

**Real path:** it reads Boat and Berth (fgets + strcspn), calls `check_entry(boat, berth)`
and prints `pass` / `fail` with a `cmovne`.

## check_entry: the overlapping instruction

```
128c  eb 01        jmp  0x128f      ; skip one byte
128e  e8           (junk)           ; first byte of a fake 5-byte "call rel32"
128f  0f b6 07 ... movzx eax, [rdi] ; mid: the real check
```

A linear sweep that starts at `0x128c` decodes `e8 0f b6 07 89` as a `call` into nowhere,
and everything after it is misaligned. The real code starts at `0x128f`. Here `objdump` only
gets it right because the `mid` symbol forces a resync. On a stripped build, you would have to
start the disassembly at the jump target by hand.

## mid (0x128f)

```c
for k in 0..3:
    if ((swap_nibbles(boat[k]) ^ (0x27 + k)) != want[k]) return 0;   // want = 52 0d 7d ce
return berth[0] == '8' && berth[1] == 0;
```

Inverting with `boat[k] = swap_nibbles(want[k] ^ (0x27 + k))`:

```
52 ^ 27 = 75 -> 57 'W'
0d ^ 28 = 25 -> 52 'R'
7d ^ 29 = 54 -> 45 'E'
ce ^ 2a = e4 -> 4e 'N'
```

- **Boat** = **`WREN`**
- **Berth** = **`8`**

## Solve

[`solve.py`](solve.py) checks the `eb 01 e8` stub, pulls the `xor eax, KK ; cmp al, TT`
pairs and the berth `cmp al, imm8` from the bytes after the jump target, and asserts the
result:

```
$ python3 -I solve.py checker
Boat  = WREN
Berth = 8
```

Local confirmation (stdin/stdout only):

```
$ printf 'WREN\n8\n' | ./checker   -> pass
$ printf 'ROCA\n9\n' | ./checker   -> fail
$ printf 'WREN\n9\n' | ./checker   -> fail
```

## Notes

- The flags are plaintext. Submit `WREN`, then `8`.
- The traps: the posted `ROCA` / `9` decoy on the `argc == 1000` path, and the junk `0xe8`
  that hides the real comparisons from a linear disassembler.
- Boat length is not checked. Only the first 4 bytes are compared.
