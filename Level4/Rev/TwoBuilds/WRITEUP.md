<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Two+Builds" alt="Typing SVG" /></a>

</div>

# Two Builds — REV · JID-Rev201 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `10/3/53` recovered from the desk build's code and verified with `solve.py`.
- **Points:** — (unknown)
- **Flags:** Divisor → Lines → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `1-posted`, `2-desk` (ELF 64-bit PIE x86-64, not stripped)
- **Prompt:** *"Two builds of the same watch. The files are on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Divisor | `10` | ✅ |
| 2 | Lines | `3` | ✅ |
| 3 | Litres | `53` | ✅ |

---

## TL;DR

1. Trusting the `1-posted` build (banner: divisor 1, add every line, "Total 240") is the trap — its numbers are decoys.
2. The `2-desk` build uses divisor 10 and filters records: skip `mark=='x'`, skip non-`'c'` kind, sum `value/10`.
3. Kept records 200/150/180 → **Divisor `10`, Lines `3`, Litres 20+15+18 = `53`**.

## Recon

Both binaries are the same size (15992 bytes) and only import `puts`. `nm` shows `main` and
one data symbol called `lines`. `strings` gives the two banners:

```
1-posted: Posted build. Boat IRIS. Add every line. Divisor 1. Lines 5. Total 240.
2-desk:   Desk build. Boat IRIS.
```

The posted build spells out its parameters. The desk build only gives the boat name, so the
desk numbers have to come from its code.

## The records

Both builds share the same 5 records of `[kind u8, mark u8, value u16]`. They are at
`0x2060` in posted and at `0x2020` in desk, and vaddr equals file offset in both:

```
63 2e c8 00   c . 200
63 2e 96 00   c . 150
63 78 82 00   c x 130
63 2e b4 00   c . 180
6d 2e 20 03   m . 800
```

## Posted build main

```
113e  mov DWORD [rsp+0xc], 0x1          ; divisor 1
1156  loop over all 5 records:
          ebx += value / divisor        ; no filter
117c  if (ebx < 0) puts("x")            ; never taken
```

It adds every line, which matches its banner. The "Total 240" in the banner is not even what
this code computes (1460). It is a decoy.

## Desk build main

```
113f  mov DWORD [rsp+0xc], 0xa          ; divisor 10
1177  for each record:
          if rec.mark == 'x' -> skip    ; cmp [rcx+1], 0x78
          if rec.kind != 'c' -> skip    ; cmp [rcx],   0x63
          ebp += value / 10             ; idiv
          ebx += 1                      ; line counter
1194  if ((ebx | ebp) < 0) puts("x")    ; never taken
```

| Record    | Result         |
|-----------|----------------|
| `c . 200` | kept → 20      |
| `c . 150` | kept → 15      |
| `c x 130` | voided         |
| `c . 180` | kept → 18      |
| `m . 800` | not civil      |

- **Divisor** = **`10`**
- **Lines** = number of records counted = **`3`**
- **Litres** = 20 + 15 + 18 = **`53`**

## Solve

[`solve.py`](solve.py) reads the divisor from the `mov DWORD [rsp+0xc], imm32` immediate,
replays the desk filter over the records and asserts the result:

```
$ python3 -I solve.py 2-desk
c . 200 kept
c . 150 kept
c x 130 skip
c . 180 kept
m . 800 skip
Divisor = 10
Lines   = 3
Litres  = 53
```

## Notes

- The flags are plaintext. Submit `10`, then `3`, then `53`.
- The trap is trusting the posted build. Its banner, its divisor of 1 and its no-filter loop
  all differ from the desk build. Only the desk build's code gives the answers.
- Neither binary prints a result (the output branch needs a negative sum), so everything comes
  from static analysis.
