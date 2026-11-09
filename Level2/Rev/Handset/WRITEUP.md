<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Handset+Image" alt="Typing SVG" /></a>

</div>

# Handset Image — REV · JID-Rev103 · Level 2 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (2/2) — both values recovered and checked by static analysis (`solve.py` asserts the opcodes); all flags accepted by the platform.
- **Points:** —
- **Flags:** Callsign → Channel (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `handset` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The host file carries the handset image. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Callsign | `NARU` | ✅ |
| 2 | Channel | `6` | ✅ |

---

## TL;DR

1. The x86-64 ELF is only a carrier that prints the decoy `Boat ROCA. Channel 9.`
2. An unreferenced custom section `.handset` (0x30 bytes) holds an ARM Cortex-M Thumb firmware image (vector table at the start).
3. Hand-decoding the reset handler: it XORs 4 bytes with `0x5a` → callsign `NARU`, then leaves `6` in `r0` → channel.

Third in the series after **Slip checker** (Rev100) and **Duty program** (Rev101). This
time the x86-64 ELF is only a *carrier*: the real program is a second binary, for a
different architecture, stored inside one of its sections.

## Recon

`strings` shows the usual decoy line:

```
Host copy. Boat ROCA. Channel 9.
```

`main` just `puts` this line and returns. Its only libc import is `puts`, and it never
touches the rest of the file. The interesting part is in the section table:

```
$ readelf -S handset | grep -A1 handset
  [18] .handset          PROGBITS         0000000000002029  00002029
       0000000000000030  0000000000000000   A       0     0     1
```

The custom section `.handset` is 0x30 bytes at file offset `0x2029`, and nothing
references it. Dump it:

```
$ objcopy -O binary --only-section=.handset handset handset.img
$ od -An -tx1 handset.img
 00 10 00 20 11 00 00 08 00 00 00 00 00 00 00 00
 05 48 5a 21 04 22 03 78 4b 40 03 70 01 30 01 3a
 f9 d1 06 20 fe e7 00 00 2c 00 00 08 14 1b 08 0f
```

## The handset image

The first two words are an ARM Cortex-M vector table:

- `0x20001000`: initial stack pointer (top of 4 KiB of SRAM at `0x20000000`).
- `0x08000011`: reset vector, which is flash base `0x08000000` + `0x10`, with bit 0 set to mark Thumb mode.

So the image is raw Thumb firmware loaded at `0x08000000`, and its code starts at
offset `0x10`. Decoded by hand (16-bit little-endian Thumb opcodes):

| addr       | bytes   | insn                 | note |
|------------|---------|----------------------|------|
| 0x08000010 | `05 48` | `ldr r0, [pc, #20]`  | literal at `0x28` → `r0 = 0x0800002c` |
| 0x08000012 | `5a 21` | `movs r1, #0x5a`     | XOR key |
| 0x08000014 | `04 22` | `movs r2, #4`        | length |
| 0x08000016 | `03 78` | `ldrb r3, [r0]`      | loop: |
| 0x08000018 | `4b 40` | `eors r3, r1`        | |
| 0x0800001a | `03 70` | `strb r3, [r0]`      | decode in place |
| 0x0800001c | `01 30` | `adds r0, #1`        | |
| 0x0800001e | `01 3a` | `subs r2, #1`        | |
| 0x08000020 | `f9 d1` | `bne 0x08000016`     | |
| 0x08000022 | `06 20` | `movs r0, #6`        | **channel** |
| 0x08000024 | `fe e7` | `b .`                | halt (spin forever) |
| 0x08000028 | `2c 00 00 08` | literal `0x0800002c` | |
| 0x0800002c | `14 1b 08 0f` | encoded buffer | |

The reset handler XOR-decodes the last 4 bytes of the image with `0x5a`:

```
14 1b 08 0f  ^ 5a  =  4e 41 52 55  =  "NARU"
```

It then loads `6` into `r0` and spins. The image has no compare step. The "accepted"
callsign is the decoded buffer, and the channel is the value the firmware leaves in `r0`.

As in the earlier challenges, the decoy maps one-to-one to the real answers:
`Boat ROCA` → **NARU** and `Channel 9` → **6**.

## Solve

[`solve.py`](solve.py) parses the ELF section headers, extracts `.handset`, writes it to
`handset.img`, asserts the expected opcodes, and decodes both values from the image
bytes:

```
$ python3 -I solve.py handset
Callsign: NARU
Channel: 6
```

## Notes

- The host binary is a decoy wrapper. Running `./handset` only prints the "Host copy"
  line. Everything comes from static analysis of the embedded Thumb blob, and no ARM
  emulator is needed.
- The key insight is the section table: a small, non-standard, unreferenced `PROGBITS`
  section in an otherwise trivial binary is the payload.
- Flags are plaintext (no `CTF{}`). Submit `NARU` first, then `6`, because the first one unlocks the second.
