<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Signal+Handler" alt="Typing SVG" /></a>

</div>

# Signal Handler — REV · JID-Rev301 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `PINE/7/moss` recovered statically from the handler and verified with `solve.py`.
- **Points:** — (unknown)
- **Flags:** Boat → Berth → Word (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `trap` (ELF 64-bit PIE x86-64, not stripped)
- **Prompt:** *"The slip checker. The check that accepts a slip runs from the signal handler. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `PINE` | ✅ |
| 2 | Berth | `7` | ✅ |
| 3 | Word | `moss` | ✅ |

---

## TL;DR

1. `main` installs a SIGTRAP handler (`SA_SIGINFO`), reads Boat/Berth/Word, loads them into `rdi/rsi/rdx`, then `int3` — the `strcmp` chain after it is dead decoy code.
2. The real comparator is the handler: it reads the saved registers from the signal `ucontext` and compares each buffer byte-by-byte against literal ASCII.
3. The literals spell **Boat `PINE`, Berth `7`, Word `moss`**.
| 3 | Word  | `moss` |

## Recon

Imports: `sigaction`, `__isoc99_scanf`, `strcmp`, `write`, `puts`, `_exit`. User code is `main`
(0x1246) and `handler` (0x1189). `.rodata`:

```
0x2004 "pass\n"   0x200a "fail\n"       (the 5-byte write() strings)
0x2010 "pass"     0x2015 "fail"
0x201a "%31s %31s %31s"
0x2029 "ROCA"  0x202e "9"  0x2030 "barrel"
0x2038 "Posted slip. Boat ROCA. Berth 9. Word barrel."
```

## main (0x1246)

```c
struct sigaction sa = {0};
sa.sa_sigaction = handler;
sa.sa_flags     = SA_SIGINFO;            // [rsp+0x88] = 4
sigaction(SIGTRAP, &sa, NULL);           // signal 5
puts("Posted slip. Boat ROCA. ...");     // decoy
if (scanf("%31s %31s %31s", boat, berth, word) != 3) return 1;
// put the three input pointers into RDI / RSI / RDX, then:
__asm__("int3");                         // 0xcc -> raises SIGTRAP
// ---- everything below is dead code: handler _exit()s and never returns ----
if (!strcmp(boat,"ROCA") ... ) puts("pass"); else puts("fail");   // decoy
```

The `scanf` reads boat→`[rsp+0xe0]`, berth→`[rsp+0xc0]`, word→`[rsp+0xa0]`. Right before the
`int3`, `main` loads `rdi=boat`, `rsi=berth`, `rdx=word`. The `strcmp`s after `int3` (against
`ROCA`/`9`/`barrel`) are a decoy — control never comes back from the handler.

## handler (0x1189) — the real check

Registered for SIGTRAP with `SA_SIGINFO`, so it is `void handler(int, siginfo_t*, ucontext_t*)`
with the `ucontext` in `rdx`. It pulls the saved registers out of `uc_mcontext.gregs`
(`gregs[i]` at `ucontext + 0x28 + 8*i`):

```
rax = [rdx+0x68]  -> gregs[8]  = saved RDI = boat
rcx = [rdx+0x70]  -> gregs[9]  = saved RSI = berth
rdx = [rdx+0x88]  -> gregs[12] = saved RDX = word
```

Then it compares each buffer against literal ASCII, byte by byte, each terminated by a NUL
check:

```
boat : 50 49 4e 45 00            -> "PINE"
berth: 37 00                     -> "7"
word : 6d 6f 73 73 00            -> "moss"
```

On full match it `write(1, "pass\n", 5)` and `_exit(0)`; otherwise `write(1, "fail\n", 5)` and
`_exit(1)`. (The `cmp [rdx+4],1 ; setb` plus `cmp [rdx+4],0` just encode "word[4] == 0".)

- **Boat** = **`PINE`**, **Berth** = **`7`**, **Word** = **`moss`**

## Solve

[`solve.py`](solve.py) parses the handler's `cmp BYTE PTR [reg(+disp)], imm8` opcodes
(`0x80 /7`), maps `rax/rcx/rdx` to boat/berth/word, reads each expected string up to its NUL
terminator, and asserts the result — fully static, no execution:

```
$ python3 -I solve.py trap
Boat  = PINE
Berth = 7
Word  = moss
```

## Notes

- The flags are plaintext: `PINE`, `7`, `moss`.
- The trap (pun intended): the real comparator never appears on the straight-line path from
  `main`. It runs only inside the SIGTRAP handler fired by `int3`, reading the inputs from the
  saved register file in the signal `ucontext` — not from the stack directly. The visible
  `strcmp` chain in `main` is dead decoy code.
- The author's usual decoy strings (`ROCA` / `9` / `barrel`) are present only to mislead.
