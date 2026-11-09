<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Rewritten+Page" alt="Typing SVG" /></a>

</div>

# Rewritten Page — REV · JID-Rev108 · Level 3 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (2/2) — the decrypted check passes with these values on the local binary; all flags accepted by the platform.
- **Points:** —
- **Flags:** Boat → Berth (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `checker` (ELF 64-bit PIE x86-64, dynamically linked, not stripped)
- **Prompt:** *"The checker rewrites its page before it runs. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `NEVA` | ✅ |
| 2 | Berth | `5` | ✅ |

---

## TL;DR

1. `live_check` sits in its own `desk` section and is encrypted on disk; `main` `mprotect`s the page RWX and XORs it with the 4-byte key `0x512c7a13`.
2. Decrypting the section straight from the file (vaddr equals file offset) gives a plain prologue and byte-by-byte compares.
3. The compares spell Boat `NEVA` and Berth `5`. The `argc == 1000` path with `ROCA` / `9` is the decoy "posted page".

## Recon

```
Posted page: boat ROCA, berth 9. That page is not the one that runs.
ROCA  9  Boat:  Berth:  pass  fail
```

The imports include `mprotect` and `strcmp`. `nm` shows `main`, `line` and
`live_check`. `live_check` lives in its own executable section called `desk`
(`0x1322`, `0x82` bytes), and its disassembly on disk is garbage
(`(bad)`, `int1`, `out`). The function is encrypted.

## main

There are two paths.

**Decoy path, `argc == 1000`** (`0x11d2` → `0x12eb`): it does
`strcmp(argv[1], "ROCA") && strcmp(argv[2], "9")`. This is the "posted page", and it is
never the code that checks stdin.

**Real path:**

```
11de  mov DWORD [rsp+0xc], 0x512c7a13        ; key = 13 7a 2c 51
11f0  page = live_check & ~0xfff
1213  mprotect(page, len, PROT_RWX)          ; 7
1231  for (p = live_check; p < _fini; p++)
          *p ^= key[(p - live_check) & 3]
1255  mprotect(page, len, PROT_RX)           ; 5
      read Boat, Berth (fgets + strcspn)
12be  live_check(boat, berth) ? "pass" : "fail"
```

So the "rewrite" is a repeating 4-byte XOR over `live_check` (`0x1322..0x13a4`). This
PIE maps the `desk` section with vaddr equal to file offset, so it can be decrypted
straight from the file.

## live_check (decrypted)

Once XOR-decrypted, it starts with a normal prologue (`55 48 89 e5`) and reads cleanly:

```c
int live_check(char *boat, char *berth) {
    if (boat[0]=='N' && boat[1]=='E' && boat[2]=='V' && boat[3]=='A' && boat[4]==0)
        return berth[0]=='5' && berth[1]==0;
    return 0;
}
```

## Solve

[`solve.py`](solve.py) takes the key from the `mov DWORD [rsp+0xc]` immediate, decrypts the
`desk` bytes, checks the prologue and pulls the `cmp al, imm8` operands that follow each
`movzx eax, [rax]`:

```
$ python3 -I solve.py checker
Boat  = NEVA
Berth = 5
```

Local confirmation (stdin/stdout only):

```
$ printf 'NEVA\n5\n' | ./checker
...
pass
$ printf 'ROCA\n9\n' | ./checker
...
fail
```

## Notes

- The flags are plaintext. Submit `NEVA`, then `5`.
- The trap in the scripted extraction: a bare `3c xx` regex also matches the `jne +0x3c`
  displacement (`75 3c`). Anchor the match on `0f b6 00 3c`.
