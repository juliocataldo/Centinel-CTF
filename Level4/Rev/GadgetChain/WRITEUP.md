<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Gadget+Chain" alt="Typing SVG" /></a>

</div>

# Gadget Chain — REV · JID-Rev308 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `ARGO/4/51` recovered by emulating the chain and verified with `solve.py`.
- **Points:** — (unknown)
- **Flags:** Boat → Berth → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `chain` (ELF 64-bit **non-PIE** x86-64, not stripped)
- **Prompt:** *"The checker pivots into a chain of gadgets. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `ARGO` | ✅ |
| 2 | Berth | `4` | ✅ |
| 3 | Litres | `51` | ✅ |

---

## TL;DR

1. `main` prints a decoy, then does `mov rsp, &chain ; ret` — a stack pivot onto a `.data` object read as a ROP return chain.
2. The chain is `pop_rdi/pop_rsi/g_write` triples that spell `"ARGO\0"` into `.bss`, then sets `rsi=4`, `rdx=0x33` for `g_finish`.
3. Answers are the sealed values: Boat `ARGO`, Berth = `rsi` = `4`, Litres = `rdx` = `0x33` = **51** (decimal).

## Recon

Not stripped, and the symbol names give the whole trick away:

```
401126 T main
401182 T g_pop_rdi      pop rdi ; ret
401184 T g_pop_rsi      pop rsi ; ret
401186 T g_pop_rdx      pop rdx ; ret
401188 T g_write        mov [rdi], sil ; ret
40118c T g_finish       the real check
404040 O chain          256-byte data object = the ROP chain
```

The only string is the decoy: `Posted chain. Boat ROCA. Berth 9.`. The program reads no
input — everything is static.

## main (0x401126): the stack pivot

```c
puts("Posted chain. Boat ROCA. Berth 9.");
if (argc == 0x3e8) {               // 1000 -> decoy path
    return argv[1] == "ROCA";      // byte compare R O C A, never reached normally
}
// real path:
rax = &chain;                      // lea rax,[rip+0x2ef4] -> 0x404040
rsp = rax;                         // mov rsp, rax   <-- STACK PIVOT
ret;                               // start executing the chain as a return chain
```

`mov rsp, &chain ; ret` repoints the stack at the `chain` data object and returns into it.
From here each `ret` pops the next qword out of `chain` — a classic ROP return chain, except
the "stack" is a `.data` array baked into the binary.

## The chain (0x404040)

Because the binary is **non-PIE**, the `.data` vaddr maps straight to a file offset
(`0x404040` → file `0x3020 + (0x404040-0x404020)`). Parsed as qwords, the chain is five
`pop_rdi / pop_rsi / write` triples that spell a string into the `.bss` buffer at `0x404148`,
then a final setup for `g_finish`:

```
pop_rdi 0x404148 ; pop_rsi 'A' ; write   -> buf[0]='A'
pop_rdi 0x404149 ; pop_rsi 'R' ; write   -> buf[1]='R'
pop_rdi 0x40414a ; pop_rsi 'G' ; write   -> buf[2]='G'
pop_rdi 0x40414b ; pop_rsi 'O' ; write   -> buf[3]='O'
pop_rdi 0x40414c ; pop_rsi 0   ; write   -> buf[4]=0
pop_rdi 0x404148 ; pop_rsi 4   ; pop_rdx 0x33 ; g_finish
```

`g_write` is `mov BYTE PTR [rdi], sil` — it stores the low byte of `rsi`, so each triple writes
one character. The buffer ends up `"ARGO\0"`.

## g_finish (0x40118c): the seal

```c
if (buf[0..3] == "ARGO" && buf[4] == 0 && rsi == 4 && rdx == 0x33)
    write(1, "pass\n", 5);
else
    write(1, "fail\n", 5);
_exit(0);
```

The three answers are exactly the three sealed values:

- **Boat** = the string the chain writes = **`ARGO`**
- **Berth** = the value placed in `rsi` = **`4`**
- **Litres** = the value placed in `rdx` = `0x33` = **`51`** (prompt asks for the litre *total*, i.e. decimal)

## Solve

[`solve.py`](solve.py) reads the `chain` object out of `.data`, emulates the four gadgets over
it (rsp walking the array, `ret` popping the next gadget), reconstructs the written buffer and
the final `rsi`/`rdx`, and asserts the seal:

```
$ python3 -I solve.py chain
Boat   = ARGO
count  = rsi = 4
rdx    = 0x33 = 3
```

## Notes

- The flags are plaintext. Submit `ARGO`, then `4`, then `51`.
- Traps: the `Posted ... ROCA / Berth 9` decoy string and the `argc == 1000` decoy path that
  checks `argv[1] == "ROCA"` — neither is on the normal execution path.
- The "checker" is data, not code: `mov rsp, &chain ; ret` turns a `.data` object into the
  instruction stream. Reading `chain` as a gadget array (not as bytes) is the whole challenge.
- Berth vs Litres: both are register-immediate checks in `g_finish`; the flag prompts
  disambiguate them — Berth is the `rsi` value (`4`), Litres is the `rdx` value as a decimal
  total (`0x33` = `51`).
