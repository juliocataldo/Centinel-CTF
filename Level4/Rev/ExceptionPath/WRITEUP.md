<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Exception+Path" alt="Typing SVG" /></a>

</div>

# Exception Path — REV · JID-Rev209 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (2/2) — `ALBA/3` recovered by inverting the check and verified with `solve.py`.
- **Points:** — (unknown)
- **Flags:** Boat → Berth (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `handler.exe` (PE32+ x86-64 console, mingw/GCC, DWARF debug info, not stripped)
- **Prompt:** *"The checker raises an exception before it accepts a slip. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `ALBA` | ✅ |
| 2 | Berth | `3` | ✅ |

---

## TL;DR

1. `main` registers a vectored exception handler, prints a decoy (`ROCA`/`9`) and raises a software exception — it compares nothing itself.
2. The real check runs inside the VEH: boat via `rol8(c,4) ^ (k+0x3b)` against `want`, berth `== '3'`.
3. Invert `want` (`2f f8 19 2a`) → **ALBA / 3**.

## Recon

```
Boat:   Berth:
Posted page. Boat ROCA. Berth 9.
pass  fail
AddVectoredExceptionHandler  RaiseException
```

Imports of note: `AddVectoredExceptionHandler`, `RaiseException`, `fgets`, `strcspn`,
`strlen`, `puts`, `ExitProcess`. The symbols are not stripped; the user code is `main` and a
function literally named `handler`.

## main (0x1681)

```c
AddVectoredExceptionHandler(1, handler);     // real check registered as first VEH
puts("Posted page. Boat ROCA. Berth 9.");    // decoy
RaiseException(0xe0000019, 0, 0, NULL);      // -> transfers control into handler
return 1;
```

`main` never reads input and never compares anything. It prints the decoy and raises a
software exception; the vectored handler installed just above is what runs the real prompt.
The "exception path" is the control-flow trick: the whole challenge lives in the VEH.

## handler (0x1530) — the vectored exception handler

```c
fwrite("Boat: ", ..); fgets(boat, 0x20, stdin);
fwrite("Berth: ", ..); fgets(berth, 0x20, stdin);
boat[strcspn(boat, "\r\n")]  = 0;            // strip newline
berth[strcspn(berth, "\r\n")] = 0;
if (strlen(boat) != 4)  { puts("fail"); ExitProcess(0); }
if (strlen(berth) != 1) { puts("fail"); ExitProcess(0); }
for (k = 0; k < 4; k++)
    if ((rol8(boat[k], 4) ^ (k + 0x3b)) != want[k])   // want.0 = 2f f8 19 2a
        { puts("fail"); ExitProcess(0); }
puts(berth[0] == '3' ? "pass" : "fail");     // cmp byte,0x33 ; cmovne
ExitProcess(0);
```

`want.0` (at `0x140004041`) = `2f f8 19 2a`. Inverting
`boat[k] = swap_nibbles(want[k] ^ (k + 0x3b))` (a rol by 4 on a byte is a nibble swap):

```
2f ^ 3b = 14 -> 41 'A'
f8 ^ 3c = c4 -> 4c 'L'
19 ^ 3d = 24 -> 42 'B'
2a ^ 3e = 14 -> 41 'A'
```

- **Boat** = **`ALBA`**
- **Berth** = **`3`**  (`cmp byte, 0x33`)

## Solve

[`solve.py`](solve.py) reads `want.0` straight from `.rdata` (PE VMA `0x140004000` == file
offset `0x2200`), inverts the four boat bytes, forward-checks that they reproduce `want`, and
asserts the result:

```
$ python3 -I solve.py handler.exe
Boat  = ALBA
Berth = 3
```

## Notes

- The flags are plaintext. Submit `ALBA`, then `3`.
- The traps: the `ROCA` / `9` decoy printed by `main`, and the exception-dispatch indirection
  — a reader who only disassembles `main` sees no comparison at all. The check is reached only
  through the VEH fired by `RaiseException`.
- Boat length is checked (==4) and berth length (==1); only `boat[0..3]` and `berth[0]` matter.
