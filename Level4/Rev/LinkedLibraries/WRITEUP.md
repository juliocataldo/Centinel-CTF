<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Linked+Libraries" alt="Typing SVG" /></a>

</div>

# Linked Libraries — REV · JID-Rev302 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `NARA/4/56` recovered from the actually-linked library and verified with `solve.py`.
- **Points:** — (unknown)
- **Flags:** Boat → Lines → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `watch` (ELF PIE x86-64), `libslip.so.1` and `libslip.so` (shared objects); all not stripped.
- **Prompt:** *"The watch and the libraries shipped with it. The files are on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `NARA` | ✅ |
| 2 | Lines | `4` | ✅ |
| 3 | Litres | `56` | ✅ |

---

## TL;DR

1. `watch` NEEDs the soname `libslip.so.1` (resolved from `$ORIGIN`); the identically-exporting `libslip.so` (with the `ROCA` decoy) is never loaded.
2. `weigh` in `libslip.so.1` sums `side==1 && mark==0` records (indices 0,1,3,5 → 200+150+120+90), writes boat `"NARA"`, lines = count, litres = sum/10.
3. **Boat `NARA`, Lines `4`, Litres 560/10 = `56`.**

## Recon — which library is actually linked

```
$ readelf -d watch | grep -E 'NEEDED|RUNPATH'
 (NEEDED)   Shared library: [libslip.so.1]
 (NEEDED)   Shared library: [libc.so.6]
 (RUNPATH)  Library runpath: [$ORIGIN]
```

`watch` is linked against the **soname `libslip.so.1`** and resolves it from `$ORIGIN` (its own
directory). So at runtime it loads `libslip.so.1`, **not** `libslip.so`. The two `.so` files are
different builds:

- `libslip.so.1` — source `.real.c`, data symbols `amt.0` / `mark.1` / `side.2`.
- `libslip.so` — source `.decoy.c`, contains the string `ROCA`. Never loaded; pure decoy.

Both export the same symbol `weigh`, so the decoy is there to tempt you into reversing the wrong
file. The boat "named by the library the watch is linked against" comes from `libslip.so.1`.

## watch main (0x1169)

```c
char boat_want[...]; int lines_want, litres_want;
weigh(boat_want, &lines_want, &litres_want);        // fills all three from the lib
puts("Posted weigh. Boat ROCA. Lines 5. Litres 240.");   // decoy line
char boat_in[..]; int lines_in, litres_in;
if (scanf("%31s %d %d", boat_in, &lines_in, &litres_in) != 3) return 1;
if (strcmp(boat_in, boat_want) == 0
    && lines_in  == lines_want
    && litres_in == litres_want) puts("pass"); else puts("fail");
```

So all three answers are whatever `weigh` computes.

## weigh (libslip.so.1, 0x10f9)

```c
void weigh(char *boat, int *lines, int *litres) {
    int count = 0, sum = 0;
    for (int i = 0; i < 6; i++)
        if (side[i] == 1 && mark[i] == 0) { count++; sum += amt[i]; }
    memcpy(boat, "NARA", 5);          // mov bytes 4e 41 52 41 00
    *lines  = count;
    *litres = sum / 10;               // imul 0x66666667 ; sar 0x22  (signed /10)
}
```

`.rodata` of `libslip.so.1`:

```
amt.0  @ 0x2000 (6 x i32) = 200, 150, 180, 120, 800, 90
mark.1 @ 0x2018 (6 x u8)  =   0,   0, 120,   0,   0,  0
side.2 @ 0x2020 (6 x i32) =   1,   1,   1,   1,   2,  1
```

Records with `side==1 && mark==0`: indices **0, 1, 3, 5**.

- count = **4** → Lines
- sum = 200 + 150 + 120 + 90 = 560; 560 / 10 = **56** → Litres
- boat = **`NARA`**

## Solve

[`solve.py`](solve.py) reads the three arrays from `libslip.so.1` (`.rodata` VMA == file offset
`0x2000`), reproduces `weigh`'s count/sum/÷10, and asserts:

```
$ python3 -I solve.py libslip.so.1
Boat   = NARA
Lines  = 4
Litres = 56
```

## Notes

- The flags are plaintext: `NARA`, `4`, `56`.
- The trap is the library split: `watch` NEEDs `libslip.so.1`, and the identically-exporting
  `libslip.so` (with the `ROCA` decoy) is never loaded. Reversing the wrong `.so` yields the
  decoy. The in-binary `Posted weigh. Boat ROCA. Lines 5. Litres 240.` line is also a decoy.
- `litres` is a signed divide-by-10 (`imul 0x66666667 ; sar 0x22`), the author's recurring idiom.
