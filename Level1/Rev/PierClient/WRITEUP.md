<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Pier+Client" alt="Typing SVG" /></a>

</div>

# Pier Client — REV · JID-Rev102 · Level 1 · 🟡 MEDIUM

- **Status:** 🟠 PARTIAL (1/3) — Boat `SOLA` accepted; Port stuck (6 of 10 tries used, meaning unresolved); Checksum locked behind Port (candidate `20377` computed, not submitted).
- **Points:** — / —
- **Flags:** Boat → Port → Checksum (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `client` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The pier client. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `SOLA` (offsets 3–6 of frame `LD3SOLA\0`) | ✅ |
| 2 | Port | unknown (6 wrong tries; field meaning not confirmed) | ❌ |
| 3 | Checksum | candidate `20377` / `0x4f99` (16-bit `ax`), not submitted | ⬜ locked |

---

## TL;DR

1. `client` reads no input and opens no socket; `main` builds the 8-byte frame `LD3SOLA\0` on the stack and runs a 16-bit ARX checksum over it.
2. Boat `SOLA` (offsets 3–6) was accepted; `LD3SOLA` was not, so the 3 header bytes `4c 44 33` hold the port — but the binary names no port field and no guess has landed.
3. Checksum candidate is the final `ax = 0x4f99 = 20377`; pending the Port and the flag's format line.

This is the third twin after **Slip checker** (Rev100, stdin checker) and **Duty
program** (Rev101, bytecode VM). Here the binary builds an 8-byte frame on the stack and
runs a 16-bit checksum over it. It never reads input and never opens a socket.

## Recon

The only import is `puts`. There is no `socket`, `connect`, `htons` or `sockaddr`, and
`argv` is never used. `main` is the only real function, with no helpers.

The two strings are decoys:

```
0x2008  Example only: GET /fuel?boat=ROCA&litres=240 HTTP/1.0
0x2040  Example port 80. This example is not the frame.
0x2070  frame dropped
0x207e  Frame kept.
```

I found nothing hidden in the file:

- there is no data after the section headers (the file is 15960 bytes and `shoff + shnum*64` is also 15960);
- `.data` holds only `__dso_handle`;
- `.comment` is stock GCC 12.2.0 (Debian);
- the notes are the standard ones.

## main (0x1139)

```
1155..1178  mov BYTE PTR [rsp+0x8+i], imm8     ; frame = 4c 44 33 53 4f 4c 41 00  ("LD3SOLA\0")
1187        mov eax, 0x6c11                    ; checksum seed
118c        rol ax, 3                          ; loop over the 8 frame bytes (NUL included)
1190        movzx ecx, BYTE PTR [rdx]
1193        xor eax, ecx
1195        add eax, 0x27
119c..119f  cmp rsi, rdx / jne 118c
11a1        test ax, ax / jne → "frame dropped", else "Frame kept."
```

The checksum, as C:

```c
uint16_t ax = 0x6c11;
for (int i = 0; i < 8; i++) { ax = rol16(ax, 3); ax ^= frame[i]; ax += 0x27; }
// result: 0x4f99 = 20377  ->  "frame dropped"
```

## Frame layout (what is confirmed)

```
offset  0  1  2 | 3  4  5  6 | 7
bytes  4c 44 33 | 53 4f 4c 41 | 00
       " L D 3" |  "SOLA"     | NUL
```

- **Boat = `SOLA`** (offsets 3–6) was accepted. `LD3SOLA` was not the answer, so the
  frame does have fields, and the 3 bytes before the boat hold the header/port.
- The binary never says what bytes 0–2 mean. There is no parser, no field names and no
  integer port constant anywhere.

## Port — rejected submissions (6 of 10 used, 4 left)

| Tried    | Reasoning |
|----------|-----------|
| `17459`  | bytes 1–2 `44 33`, big-endian (type `L` + port in network order) |
| `13124`  | bytes 1–2 `44 33`, little-endian |
| `51`     | `"LD"` magic + 1-byte port `0x33` |
| `3`      | same, `0x33` read as ASCII digit `'3'` |
| `19524`  | bytes 0–1 `4c 44`, big-endian, with `'3'` as type |
| `LD3`    | header bytes as text |

Not tried yet, and all of these are unconfirmed guesses: `17484` (bytes 0–1 LE), `LD`, `68`
(`'D'`), `211` (`"D3"` read as hex), `27665`/`4460` (checksum seed `0x6c11` as port).

Dead end checked: **no** 1-byte or 2-byte change at any offset of the frame makes the
checksum 0. That means "Frame kept." is unreachable, and the port cannot be "the value that
makes the frame kept".

## Checksum (pending)

The candidate is `20377` (`0x4f99`, 16-bit, the final `ax`). Read the flag's "Format:" line
before submitting: it may want decimal, hex, or a specific byte order (`4f99` vs `994f`).

## Where to resume

1. Do **not** spend more Port tries on guesses (4 left).
2. Options: buy the challenge hint (costs points, not refunded), or ask official Discord
   support (not public channels) whether the Port prompt matches this binary.
3. Once the Port meaning is known, check it against the layout above. Then confirm the
   Checksum format and update `solve.py`.

## Solve

[`solve.py`](solve.py) pulls the frame bytes and the seed straight out of `client`,
recomputes the checksum and asserts the result:

```
$ python3 -I solve.py client
Boat    : LD3SOLA          # prints the whole 7-byte body; the accepted field is SOLA (offsets 3-6)
Checksum: 20377 = 0x4f99 (16-bit, ax)
client prints "frame dropped" (ax != 0)
```
