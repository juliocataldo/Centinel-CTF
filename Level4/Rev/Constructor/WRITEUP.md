<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Constructor" alt="Typing SVG" /></a>

</div>

# Constructor — REV · JID-Rev300 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `MIRA/7/chalk` confirmed by running the binary. On the platform the Boat submission returned *"Duplicate submission — already attempted by your team"* (already in the team's history, not a rejection).
- **Points:** — (Hint #1 taken, −50)
- **Flags:** Boat → Berth → Word (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `slip` (ELF 64-bit PIE x86-64, not stripped)
- **Prompt:** *"The slip checker. A constructor runs before the prompt. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `MIRA` | ✅ |
| 2 | Berth | `7` | ✅ |
| 3 | Word | `chalk` | ✅ |

---

## TL;DR

1. `slip` reads Boat/Berth/Word and checks each with a seeded per-byte chained hash (`rol`/`xor`, state carries), printing a decoy line.
2. The "constructor" flavor is a red herring: `.init_array` holds only `frame_dummy`, and gdb confirms the on-disk `.rodata` targets are never rewritten.
3. Forward-simulate each hash and invert per position → **MIRA / 7 / chalk**.

## Recon

```
Boat:   Berth:   Word:
accepted   rejected
Posted slip: boat ROCA, berth 9, word barrel. This slip is not accepted.
.slip.c  boat.2  berth.1  word.0
```

Imports: `fgets`, `strcspn`, `strlen`, `memcmp`, `puts`, `fwrite`. User code: `main` (0x123c),
`line` (0x1189, a fgets+newline-strip helper), `same` (0x11b8, the comparator).

## main (0x123c)

```c
puts("Posted slip: boat ROCA, berth 9, word barrel. ...");   // decoy
line(boat, 0x20);   // Boat:
line(berth, 0x20);  // Berth:
line(word, 0x20);   // Word:
if ( same(boat,  &boat.2,  4, 0x21)      // seed 0x21
  && same(berth, &berth.1, 1, 0x44)      // seed 0x44
  && same(word,  &word.0,  5, 0x19) )    // seed 0x19
    puts("accepted");
else
    puts("rejected");
```

## same(input, expected, len, seed) — the per-byte chained hash (0x11b8)

```c
if (strlen(input) != len) return 0;
uint32_t state = seed;                       // r13d
for (k = 0; k < len; k++) {
    uint32_t e = (0xd*k + input[k]) & 0xff;  // mov eax,ecx(=0xd*k); add al,input
    e = (e + state) & 0xffffffff;            // add eax, r13d
    e ^= (0x11*k);                           // xor eax, esi(=0x11*k)
    e ^= 0xffffffa7;                         // xor eax, 0xffffffa7
    uint8_t al = rol8(e & 0xff, 3);          // rol al,3
    state = (e & 0xffffff00) | al;           // r13d = eax   (32-bit state carries)
    buf[k] = al;
}
return memcmp(buf, expected, len) == 0;
```

Each output byte is a bijection of its input byte (given the running `state`), so the input is
recovered by forward-simulating and picking, per position, the single byte that reproduces the
stored target; the state then carries to the next position.

Stored targets in `.rodata` (file offset == VMA):

```
word.0  @ 0x2079 (len 5) = de 2f 79 c4 04   seed 0x19
berth.1 @ 0x207e (len 1) = e6               seed 0x44
boat.2  @ 0x207f (len 4) = 4e 90 cb 3d      seed 0x21
```

Inversion yields **`MIRA`**, **`7`**, **`chalk`**.

## The "constructor" trap

The flavor (and Hint #1) points at a constructor in `.init_array` that rewrites the comparison
bytes before `main`, implying the on-disk `.rodata` values are stale. In **this** build that is
not the case:

- `.init_array` holds a single entry, `0x1180` = `frame_dummy` (the stock GCC
  `jmp register_tm_clones`); there is no byte-patching constructor.
- gdb, broken at `main` (after all constructors have run), shows the bytes at `word.0/berth.1/
  boat.2` are **identical** to the on-disk `.rodata` — the constructor changes nothing.

So the straightforward static inversion is valid here, and running the binary confirms it.

## Solve

[`solve.py`](solve.py) reads the three targets from `.rodata`, inverts each by forward
simulation, and asserts the forward transform reproduces the stored bytes:

```
$ python3 -I solve.py slip
Boat  = MIRA
Berth = 7
Word  = chalk
```

Ground-truth check — executing the binary locally (stdin/stdout only):

```
$ printf 'MIRA\n7\nchalk\n' | ./slip
Posted slip: boat ROCA, berth 9, word barrel. This slip is not accepted.
Boat: Berth: Word: accepted
```

## Notes

- The flags are plaintext: `MIRA`, `7`, `chalk`.
- Decoy line is the usual `ROCA` / `9` / `barrel`.
- The comparator is case-sensitive and length-checked (4 / 1 / 5).
- gdb was used only on a local copy in the scratchpad; nothing was run against the platform.
