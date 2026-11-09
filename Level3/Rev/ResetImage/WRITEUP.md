<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Reset+Image" alt="Typing SVG" /></a>

</div>

# Reset Image — REV · JID-Rev109 · Level 3 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (2/2) — both values read statically from the copied bank; all flags accepted by the platform.
- **Points:** —
- **Flags:** Boat → Litres (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `reset` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The image the reset routine copies. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `IRIS` | ✅ |
| 2 | Litres | `48` | ✅ |

---

## TL;DR

1. `.rodata` holds two `bank` structs; `main` prints the decoy `ROCA` bank and copies the second (`IRIS`) to the stack.
2. The reset routine sums civil (`kind == 'c'`), non-voided (`mark != 'x'`) records, stored ×10 (`imul 0xcccd; shr 19` = divide by 10).
3. Boat = the copied bank's name `IRIS`; Litres = 20 + 16 + 12 = `48`.

## Recon

The only import is `puts`. `nm` shows `main` and one data symbol:

```
0000000000002020 r banks
```

`strings` shows two bank names and two texts:

```
ROCA  posted: ROCA, 40 pax, 240 litres
IRIS  A stored 10 stands for 1 litre. The mark x voids the line. Add the civil lines.
```

## The banks

`banks` is an array of two 0x7c-byte structs in `.rodata`, where vaddr equals file offset:

```c
struct bank {
    char name[8];        // +0x00
    char text[0x60];     // +0x08
    struct { uint8_t kind, mark; uint16_t value; } rec[5];   // +0x68
};
```

| Bank | Addr     | Name   | Role |
|------|----------|--------|------|
| 0    | `0x2020` | `ROCA` | decoy ("posted"); `main` only `puts` its text |
| 1    | `0x209c` | `IRIS` | copied to the stack by the reset routine |

## main (0x1139)

```
1140  puts(banks[0].text)                       ; prints the decoy line
114c  movdqu xmm0..xmm7 <- 0x209c..0x2118       ; copy banks[1] (0x7c bytes) to rsp
11da  for each rec in copy.rec[0..4]:
          if rec.mark == 'x'  -> skip           ; cmp [rax+0x69], 0x78
          if rec.kind == 'c'  -> sum += rec.value / 10   ; imul 0xcccd ; shr 0x13
11e8  if (sum < 0) puts(copy.name)              ; never taken
11ec  puts("Reset complete.")
```

`imul edx, 0xcccd ; shr edx, 19` is the compiler's unsigned divide-by-10 for 16-bit values.
That matches the bank's own note: "A stored 10 stands for 1 litre".

## The records of bank 1

```
0x2104  63 2e c8 00   c . 200  -> 20
0x2108  63 2e a0 00   c . 160  -> 16
0x210c  63 78 8c 00   c x 140  -> voided
0x2110  63 2e 78 00   c . 120  -> 12
0x2114  6d 2e 20 03   m . 800  -> not civil
```

- **Boat** = name of the copied bank = **`IRIS`**.
- **Litres** = 20 + 16 + 12 = **48**.

## Solve

[`solve.py`](solve.py) slices `banks[1]` out of the file, applies the same filter and
asserts the result:

```
$ python3 -I solve.py reset
c . 200 kept
c . 160 kept
c x 140 skip
c . 120 kept
m . 800 skip
Boat   = IRIS
Litres = 48
```

## Notes

- The flags are plaintext. Submit `IRIS`, then `48`.
- Running the binary only prints the decoy line and `Reset complete.`. The answer branch
  (`sum < 0`) can never be taken, so everything comes from static analysis.
- The traps: the decoy bank (`ROCA`, 240 litres) is the one that is printed. The values are
  stored ×10. And `movups [rsp+0x6c]` overlaps the previous store, so the copy is exactly
  0x7c bytes, not 0x80.
