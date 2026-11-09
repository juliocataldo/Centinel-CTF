<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=License+Checker" alt="Typing SVG" /></a>

</div>

# License Checker — REV · JID-Rev106 · Level 2 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (2/2) — both values decoded statically and accepted by the local binary; all flags accepted by the platform.
- **Points:** —
- **Flags:** Boat → Word (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `license` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The license checker. The file is on this page."* Flag text: *"Submit the boat on a license the checker accepts."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `LYRA` | ✅ |
| 2 | Word | `kelson` | ✅ |

---

## TL;DR

1. A stdin checker: `main` decodes an 11-byte `sealed` blob from `.rodata` onto the stack right before comparing.
2. The transform is `b*17 + 3 (mod 256)`, giving the record `[boat:4][word:6][version:1]`.
3. Decoding gives `LYRA` / `kelson` / version 2 (which is why the "version 1" sample is always refused).

Sixth in the series. This is a classic stdin checker, like **Slip checker** (Rev100).
The expected values are not stored in plaintext: they are an encoded blob that `main`
decodes onto the stack right before comparing. The flag text: *"Submit the boat on a
license the checker accepts."*

## Recon

`strings` shows the prompts, the verdicts, and the decoy:

```
accepted
rejected
Boat:
Word:
Sample license: boat ROCA, word barrel, version 1. This sample is not accepted.
```

The imports are `fgets`, `strcspn`, `strlen`, `memcmp`, `puts` and `fwrite`. `nm` shows
two local symbols worth looking at:

```
0000000000001189 t line      # fgets + strip "\r\n"
0000000000002078 r sealed    # 11 bytes in .rodata
```

```
$ objdump -s -j .rodata license
 2070 ........ ........ b9f65f5e e842d970   ........._^.B.p
 2080 acbb0f                                ...
```

So `sealed = b9 f6 5f 5e e8 42 d9 70 ac bb 0f`.

## main

From `objdump -d -M intel`, reconstructed:

```c
puts("Sample license: boat ROCA, word barrel, version 1. ...");
fputs("Boat: ", stdout); line(boat, 32);     // rsp+0x30
fputs("Word: ", stdout); line(word, 32);     // rsp+0x10

uint8_t lic[11];                             // rsp+0x05
for (int i = 0; i < 11; i++)
    lic[i] = sealed[i] + (sealed[i] << 4) + 3;   // lea edx,[rdx+rcx*1+0x3], i.e. b*17 + 3

if (lic[10] == 2 &&                              // cmp byte [rsp+0xf], 2  -> version
    strlen(boat) == 4 && !memcmp(boat, &lic[0], 4) &&
    strlen(word) == 6 && !memcmp(word, &lic[4], 6))
    puts("accepted");
else
    puts("rejected");
```

The decoded 11-byte license record is laid out as `[boat:4][word:6][version:1]`.

## Decoding

`b*17 + 3 (mod 256)` for each byte of `sealed`:

| i  | sealed | ×17+3 | char |
|----|--------|-------|------|
| 0  | `b9`   | `4c`  | `L`  |
| 1  | `f6`   | `59`  | `Y`  |
| 2  | `5f`   | `52`  | `R`  |
| 3  | `5e`   | `41`  | `A`  |
| 4  | `e8`   | `6b`  | `k`  |
| 5  | `42`   | `65`  | `e`  |
| 6  | `d9`   | `6c`  | `l`  |
| 7  | `70`   | `73`  | `s`  |
| 8  | `ac`   | `6f`  | `o`  |
| 9  | `bb`   | `6e`  | `n`  |
| 10 | `0f`   | `02`  | version 2 |

That gives Boat **LYRA**, Word **kelson**, and license version **2**. The version byte is
checked before anything else, which is why the sample "version 1" license can never be
accepted. As in the earlier challenges, the decoy maps one-to-one: `boat ROCA` →
**LYRA** and `word barrel` → **kelson**.

## Solve

[`solve.py`](solve.py) finds `sealed` through the ELF `.symtab`, applies `b*17 + 3`, and
asserts that the version byte is 2:

```
$ python3 -I solve.py license
Boat    = LYRA
Word    = kelson
version = 2
```

You can check it locally with `printf 'LYRA\nkelson\n' | ./license`, which should print `accepted`.

## Notes

- `b*17 + 3` is invertible mod 256 because 17 is odd, so each expected byte comes from exactly one `sealed` byte. No brute force is needed.
- Both length checks (`strlen == 4` and `strlen == 6`) block prefix tricks. The input has to be exact.
- Flags are plaintext (no `CTF{}`). Submit `LYRA` first, then `kelson`.
