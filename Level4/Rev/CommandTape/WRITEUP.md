<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Command+Tape" alt="Typing SVG" /></a>

</div>

# Command Tape — REV · JID-Rev208 · Level 4 · 🔴 HARD

- **Status:** ❌ UNSOLVED (0/3) — the shipped binary only prints a decoy; it has no state table, edge list or tape. Decoy-only / incomplete attachment. No flags submitted.
- **Points:** — (unknown)
- **Flags:** Command → Edges → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `tape` (ELF 64-bit PIE x86-64, not stripped), sha256 `6aa2c6a30c6599c38eaa8dceacd5b7975a60e548aaf2bf650f0e559276e86cf6`; `tape_v2` is a re-download.
- **Prompt:** *"The command tape. The file is on this page."* — Flag 1: *"Submit the command on the edge that enters the accepted state."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Command | unknown | ❌ |
| 2 | Edges | unknown | ❌ |
| 3 | Litres | unknown | ❌ |

---

## TL;DR

1. `tape` prints two decoy strings (`stay` ×6, `Total 240`) and nothing else — no state machine, no edges, no input.
2. Byte-for-byte it matches the "posted decoy build" profile (same family as Two Builds / Cipher Slip); the real state machine and its tape are absent from the file.
3. Unresolved — with the real build, dump the transition table, find the edge into the accepted state (Command), count edges taken (Edges) and sum the litres along the path.

## Status

Paused. No submissions so far. It was reported to official support together with
[Cipher slip (Rev204)](../CipherSlip/WRITEUP.md), which has the same problem.

## Recon

The only import is `puts`. The source file is `tape.c` (GCC 12.2.0, Debian). There are no
data symbols.

```
Tape stay stay stay stay stay stay. Total 240.
Tape sealed.
```

## main (0x1139)

```
113d  puts("Tape stay stay stay stay stay stay. Total 240.")
1149  puts("Tape sealed.")
1155  return 0
```

That is the whole program. There is no state table, no edge list, no transition loop and no
input. `.init_array` only holds the stock `frame_dummy`, so nothing runs before `main` either.

## What was checked

| Check | Result |
|-------|--------|
| Bytes outside every section/header | 0 non-zero; file ends exactly at the section headers |
| `.rodata` | only the two strings |
| `.data` / `.bss` | `data_start`, `__dso_handle`, `completed.0` |
| `.init_array` | one entry (`frame_dummy`) |
| Section-by-section diff against `cipher` (Rev204) | every difference is explained by the strings / `main` size and the `tape.c` vs `cipher.c` file name |
| Search for `accept`, `edge`, `state` | none; `stay` only in the decoy string |

## Working hypothesis

The file matches the profile of a "posted" decoy build, like `1-posted` in Two builds
(Rev201). It prints the decoy and has none of the data the flags ask about. The real build
(the state machine and its tape) is likely missing from the page, or its tables were dropped
by the optimiser because `main` never references them.

## Next steps

- Wait for support (a corrected file or a second attachment).
- With the real build: dump the transition table, find the edge into the accepted state
  (Command), count the edges taken (Edges) and sum the litres along the path. Expect the decoy
  `stay` ×6 / 240.
