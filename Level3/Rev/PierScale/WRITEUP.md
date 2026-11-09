<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Pier+Scale" alt="Typing SVG" /></a>

</div>

# Pier Scale — REV · JID-Rev107 · Level 3 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (2/2) — both values decoded by hand and cross-checked by instantiating the module locally; all flags accepted by the platform.
- **Points:** —
- **Flags:** Records → Litres (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `pier.wasm` (WebAssembly MVP module, 441 bytes)
- **Prompt:** *"The pier scale module. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Records | `3` | ✅ |
| 2 | Litres | `58` | ✅ |

---

## TL;DR

1. A 441-byte wasm module exports `weigh` (returns the decoy `240`), `pier_count` and `pier_litres`.
2. Both real exports walk five 4-byte records `[kind, litres, tag, pad]` and keep only civil (`kind == 1`), non-struck (`tag != 'x'`) ones.
3. Three records survive: Records `3`, Litres 20 + 15 + 23 = `58`.

## Recon

`strings` shows three export names and one decoy line:

```
weigh
pier_count
pier_litres
Posted weigh: boat ROCA, litres 240.
```

The module has no imports. It has one memory, one data segment at address 0 and three
`() -> i32` functions. No `wabt` was installed, so I decoded the module by hand from an
`od` hex dump.

## The functions

| Export        | Body |
|---------------|------|
| `weigh`       | `i32.const 240` (the decoy value) |
| `pier_count`  | sum of 5 unrolled `select(1, 0, cond)` |
| `pier_litres` | sum of 5 unrolled `select(load8_u(rec+1), 0, cond)` |

For each record `rec` in `0x40, 0x44, 0x48, 0x4c, 0x50`:

```
cond = (load8_u(rec+0) == 1) & (load8_u(rec+2) != 0x78)   ; 0x78 = 'x'
```

So each record is 4 bytes, `[kind, litres, tag, pad]`. A record is counted only when it is
civil (`kind == 1`) and not struck out (`tag != 'x'`).

## The records

The data segment starts with the decoy string, and its records are at `0x40`:

```
0x40  01 14 00 00   civil, 20 L        -> kept
0x44  01 0f 00 00   civil, 15 L        -> kept
0x48  01 17 00 00   civil, 23 L        -> kept
0x4c  01 0c 78 00   civil, tagged 'x'  -> skipped
0x50  02 5a 00 00   kind 2 (not civil) -> skipped
```

- **Records** = 3 kept records.
- **Litres** = 20 + 15 + 23 = **58**.

The decoy (`litres 240`, which is also what `weigh()` returns) is wrong, as in the twins.

## Solve

[`solve.py`](solve.py) walks the wasm sections (LEB128 sizes) to the data segment, applies
the same filter and asserts the result:

```
$ python3 -I solve.py pier.wasm
01140000 kept
010f0000 kept
01170000 kept
010c7800 skip
025a0000 skip
Records = 3
Litres  = 58
```

Cross-check by instantiating the module locally in Node (it has no imports, so nothing
leaves the sandbox):

```
weigh 240 pier_count 3 pier_litres 58
```

## Notes

- The flags are plaintext. Submit `3`, then `58`.
- One trap to watch: the code section size is a 2-byte LEB128 (`91 02`), so a naive
  "1-byte size" section walker crashes before it reaches the data segment.
