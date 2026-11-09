<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Parser+And+Slip" alt="Typing SVG" /></a>

</div>

# Parser And Slip — REV · JID-Rev203 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `TIDE/3/59` recovered by walking the slip like the parser and verified with `solve.py`.
- **Points:** — (unknown)
- **Flags:** Boat → Records → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `parser` (ELF 64-bit PIE x86-64, not stripped), `slip.bin` (87 bytes, data)
- **Prompt:** *"The parser and the slip it reads. The files are on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `TIDE` | ✅ |
| 2 | Records | `3` | ✅ |
| 3 | Litres | `59` | ✅ |

---

## TL;DR

1. `parser` reads `slip.bin` (a plaintext decoy line + a binary `SLP` blob) and sums records, but never prints the result.
2. Group 1 (`ROCA`, tag 1) is the decoy; group 2 (`TIDE`, tag 2) is summed, and only its type-`0x10` (civil) records enter — names are XOR-`0x11` so `strings` misses them.
3. **Boat `TIDE`, Records = 3 civil (22,19,18), Litres = `59`.**

## Recon

The parser imports `fopen`, `fread`, `memmem`, `strchr`, `fwrite` and `puts`. Its only
strings are `slip.bin`, `SLP` and `Sum sealed.`. It never prints the result.

`slip.bin` starts with a plaintext decoy line, then a binary blob:

```
000000  Boat ROCA. Litres 240. Records 4.\n
000022  53 4c 50 02 02 00 01 13 00 43 5e 52 50 04 10 3c
000032  00 10 3c 00 10 3c 00 10 3c 00 f0 00 02 16 00 45
000042  58 55 54 05 10 16 00 10 13 00 12 28 00 10 12 00
000052  11 50 00 3b 00
```

## main (0x1199)

```
11d3  fread(buf, 1, 0x1ff, fopen("slip.bin"))
123c  fwrite(first line)                       ; prints the decoy line
1253  p = memmem(buf, "SLP")
1264  ngroups = u16 [p+4]
12bc  off = 6; repeat ngroups times:
          tag = p[off]; len = u16 p[off+1]; next = off + 3 + len
12d4      if tag != 2 -> skip group
12e4      name[0..3] = body[0..3] ^ 0x11
12fa      n = body[4]
1299      for each of n records [type u8, value u16]:
              if type == 0x10: sum += value; count += 1
1318  puts("Sum sealed.")
```

The layout:

```
header : "SLP" | version u8 | ngroups u16
group  : tag u8 | len u16 | body[len]
body   : name[4] (^0x11) | n u8 | n x [type u8, value u16] | tail
```

## The groups

| Group | Tag | Name (`^0x11`) | Records                                           | Tail          |
|-------|-----|----------------|---------------------------------------------------|---------------|
| 1     | 1   | `ROCA`         | 4 × (0x10, 60)                                    | `f0 00` = 240 |
| 2     | 2   | `TIDE`         | (0x10,22) (0x10,19) (0x12,40) (0x10,18) (0x11,80) | `3b 00` = 59  |

Group 1 is the decoy from the header line: tag 1 is never summed. Group 2 is the one the
parser sums, and only its type `0x10` (civil) records enter:

- **Boat** = **`TIDE`**
- **Records** = civil records that enter the sum = **`3`** (22, 19, 18)
- **Litres** = 22 + 19 + 18 = **`59`**

The tail of each group stores its own sum (240 for ROCA, 59 for TIDE). That is a nice
cross-check.

## Solve

[`solve.py`](solve.py) walks the slip the same way the parser does and asserts the result:

```
$ python3 -I solve.py slip.bin
group tag=1 name=ROCA recs=[('0x10', 60), ('0x10', 60), ('0x10', 60), ('0x10', 60)] tail=f000
group tag=2 name=TIDE recs=[('0x10', 22), ('0x10', 19), ('0x12', 40), ('0x10', 18), ('0x11', 80)] tail=3b00
Boat    = TIDE
Records = 3
Litres  = 59
```

## Notes

- The flags are plaintext. Submit `TIDE`, then `3`, then `59`.
- The traps:
  - The decoy line and the decoy group agree with each other (ROCA / 240 / 4).
  - The names are XOR-ed, so `strings` cannot find `TIDE`.
  - The TIDE group lists 5 records, but only 3 of them are civil and enter the sum.
