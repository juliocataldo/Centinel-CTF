<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Duty+Program" alt="Typing SVG" /></a>

</div>

# Duty Program — REV · JID-Rev101 · Level 1 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (3/3) — all three answers produced by re-implementing the VM and asserting the trace against the binary's bytecode.
- **Points:** — / —
- **Flags:** Boat → Litres → Word (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `desk` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The program the duty desk executes. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `KITE` | ✅ |
| 2 | Litres | `52` | ✅ |
| 3 | Word | `maple` | ✅ |

---

## TL;DR

1. `desk` reads no input; `main` is a small bytecode interpreter over a 40-byte `program` in `.rodata`.
2. Five opcodes load 16-bit numbers, copy bytes into string slots, XOR-decode them, add numbers, and halt.
3. Tracing the program yields `KITE` (XOR 0x2b), `52` (18+22+12), `maple` (XOR 0x2b).

This is the twin of **Slip checker** (Rev100), but the mechanism is different. `slip`
was an interactive stdin checker; `desk` reads no input at all — its only libc import
is `puts`. The answers are produced entirely by code running inside the binary.

## Recon

`strings` shows a single decoy line and a halt message:

```
Posted program: boat ROCA. Add every line. Total 240. Word barrel.
Desk halted.
```

As in the twin, the "posted" slip is a decoy (`ROCA` / `240` / `barrel` are wrong).

`nm` gives the useful symbols. There is no `fgets`/`scanf`/`memcmp` — only `main`,
plus four globals:

```
0000000000002060 r program     # .rodata, 40 bytes of bytecode
0000000000004040 b number      # int array
0000000000004060 b length      # int array
0000000000004080 b text        # 16-byte string slots
```

`main` is a **bytecode interpreter**. It walks `program` with a program counter in
`eax`, dispatching on the opcode byte (1..5). The globals are the VM's memory.

## The VM

Reconstructed from the disassembly of `main` (`0x1139`). Register map inside the loop:
`r8 = program`, `r9 = number`, `r11 = length`, `r10 = text`.

```
01 dst lo hi       number[dst] = lo | (hi << 8)                 ; pc += 4
02 d  n  <n bytes> copy n bytes (program+pc+3) into text[d*16]  ; length[d] = n ; pc += 3 + n
03 d  k            for i in length[d]: text[d][i] ^= k          ; pc += 3
04 a  b            number[a] = (number[a] + number[b]) & 0xffff ; pc += 3
05                 halt ("Desk halted.")
```

- `text` slots are 16 bytes apart (`shl rcx,0x4` → `d*16`).
- Opcode 2 copies with a `test n,4 / test n,2 / test n,1` byte-splice fast path
  (and a `rep movsq` path for `n > 7`), i.e. an inlined `memcpy` of `n` bytes.
- Opcode 4 keeps the accumulator 16-bit (`and edx,0xffff`).

## The program

`program` (`.rodata` @ `0x2060`, 40 bytes):

```
02 00 04 60 62 7f 6e   03 00 2b
01 01 12 00   01 02 16 00   01 03 0c 00
04 01 02   04 01 03
02 04 05 46 4a 5b 47 4e   03 04 2b
05
```

Trace:

| pc   | insn                | effect |
|------|---------------------|--------|
| 0x00 | `02 00 04 60 62 7f 6e` | `text[0] = 60 62 7f 6e`, `length[0] = 4` |
| 0x07 | `03 00 2b`          | `text[0] ^= 0x2b` → `4b 49 54 45` = **"KITE"** |
| 0x0a | `01 01 12 00`       | `number[1] = 18` |
| 0x0e | `01 02 16 00`       | `number[2] = 22` |
| 0x12 | `01 03 0c 00`       | `number[3] = 12` |
| 0x16 | `04 01 02`          | `number[1] += number[2]` → 40 |
| 0x19 | `04 01 03`          | `number[1] += number[3]` → **52** |
| 0x1c | `02 04 05 46 4a 5b 47 4e` | `text[4] = 46 4a 5b 47 4e`, `length[4] = 5` |
| 0x24 | `03 04 2b`          | `text[4] ^= 0x2b` → `6d 61 70 6c 65` = **"maple"** |
| 0x27 | `05`                | halt |

So the decoys map one-to-one to the real answers: `ROCA`→**KITE**, `Total 240`→**52**
(18+22+12), `barrel`→**maple**.

## Solve

[`solve.py`](solve.py) re-implements the VM, runs it over the real `program` bytes read
straight from `desk`, and asserts the result:

```
$ python3 solve.py desk
Boat   = 'KITE'
Litres = 52
Word   = 'maple'
ok: trace confere
```

## Notes

- The binary never validates input — running `./desk` only prints the decoy line and
  `Desk halted.`. Everything comes from static analysis of the bytecode.
- Flags are plaintext (no `CTF{}`). Submit `KITE`, then `52`, then `maple`, in order
  (each unlocks the next). Read each flag's "Format:" line before submitting.
