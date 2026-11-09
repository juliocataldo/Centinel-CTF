<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Cipher+Slip" alt="Typing SVG" /></a>

</div>

# Cipher Slip — REV · JID-Rev204 · Level 4 · 🔴 HARD

- **Status:** ❌ UNSOLVED (0/3) — the shipped binary only prints a decoy and contains none of the ciphertext the flags need; likely a decoy-only / incomplete attachment. No flags submitted.
- **Points:** — (unknown)
- **Flags:** Boat → Word → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `cipher` (ELF 64-bit PIE x86-64, not stripped), sha256 `75fa2b4ddc6fe736b21122c2eb5588c93aef81dbd2e755c4c713db69f16668a7`; `cipher_v2` is a byte-identical re-download.
- **Prompt:** *"The cipher slip. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | unknown | ❌ |
| 2 | Word | unknown | ❌ |
| 3 | Litres | unknown | ❌ |

---

## TL;DR

1. `cipher` prints three decoy strings (`boat ROCA`, `word barrel`, `litres 240`) and a known header `LD4` — it reads no input, opens no file and decrypts nothing.
2. Every section and slack byte was scanned: the ciphertext the flags refer to is **not in the file** (likely dropped by the optimiser, or shipped as a missing second attachment).
3. Unresolved — with the real ciphertext, recover the key from the `LD4` known-plaintext header and decrypt Boat/Word/Litres.

## Status

Paused. No submissions so far. Official support was asked whether the attachment is complete
(14:24). The first answer was "in principle it is correct", and they are checking with the
team. A second download gave a byte-identical file.

## Recon

The only import is `puts`. The symbols show the source was `cipher.c` (GCC 12.2.0, Debian),
built with optimisation. There are no data symbols at all.

```
Plain slip: boat ROCA, word barrel, litres 240.
Known header: LD4
Cipher slip sealed.
```

## main (0x1139)

```
113d  puts("Plain slip: boat ROCA, word barrel, litres 240.")
1149  puts("Known header: LD4")
1155  puts("Cipher slip sealed.")
1161  return 0
```

That is the whole program. It reads no input, opens no file and decrypts nothing.

## Where the ciphertext was searched for

| Area | Result |
|------|--------|
| `.rodata` (0x2000, 0x5e bytes) | only the three strings |
| `.data` (0x4008, 0x10 bytes) | `data_start` + `__dso_handle` |
| `.text` | only CRT stubs + `main`, normal padding |
| `.eh_frame` / `.eh_frame_hdr` | standard CIE/FDEs for `_start` and `main` |
| `.dynstr`, `.symtab`, `.strtab`, `.comment` | standard names only |
| Notes / ELF header padding | standard, `e_ident` padding zero |
| Bytes outside every section/header | none non-zero, nothing appended after the section headers |
| Known-plaintext scan for `LD4` (single-byte XOR, single-byte add, XOR with incrementing key) | no hit anywhere in the file |

## Working hypothesis

The binary plays the same role as `parser` in Rev203: it says the slip is "sealed" and gives
a known header (`LD4`, like the `LD3...` frame in Pier client) for a known-plaintext attack.
But the ciphertext is not in the file. Most likely it was a static array in `cipher.c` that
`main` never references, so the optimiser dropped it. The other option is a missing second
attachment.

## Next steps

- Obtain the real ciphertext (a corrected file, or wherever the slip actually lives).
- With the ciphertext in hand: recover the key from the `LD4` header, decrypt, then read
  Boat / Word / Litres. Expect the decoy plaintext layout `ROCA` / `barrel` / `240`.
