<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Go+Checker" alt="Typing SVG" /></a>

</div>

# Go Checker — REV · JID-Rev307 · Level 4 · 🔴 HARD

- **Status:** ❌ UNSOLVED (0/2) — the captured boat `NEVA` was rejected by the platform (Incorrect, then Duplicate); the shipped build ships only the decoy checker, the real init-installed one is absent. No further submissions.
- **Points:** — (Hint #1 taken, −50)
- **Flags:** Boat → Berth (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `checker` (ELF x86-64, not stripped; `desk` section XOR-encrypted)
- **Prompt:** *"init installs the checker that actually runs. The posted comparison is the other checker. The installed one unpacks each byte with a constant mixed with the index."* (Hint #1)

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `NEVA` (decoy build; rejected) | ❌ |
| 2 | Berth | `5` (decoy build) | ❌ |

---

## TL;DR

1. `main` decrypts an XOR-packed `live_check` (`desk` section, 4-byte key `0x512c7a13`) and calls it; it does a direct compare boat == "NEVA", berth == "5".
2. Hint #1 reveals that direct-compare checker is the **decoy** — the real checker is installed by an init constructor and unpacks each byte with a constant mixed with the index.
3. This shipped file has no such constructor (`.init_array` = `frame_dummy` only; `desk` is untouched at `main` entry), so the real boat is not derivable from it. `NEVA` was rejected; a corrected download is needed.

## What the shipped `checker` contains
- `live_check` (section `desk`, 0x1322) is XOR-encrypted on disk; `main` decrypts it
  (mprotect RWX, XOR with 4-byte key 0x512c7a13 indexed by pos mod 4), then calls it.
- Decrypted `live_check` does a **direct** byte compare: boat == "NEVA", berth == "5".
- Running the binary: only `NEVA`/`5` prints `pass` (unique, case-sensitive). solve.py reproduces this.

## Why NEVA is wrong (Hint #1, -50)
Hint: "init installs the checker that actually runs. The posted comparison is the other
checker. The installed one unpacks each byte with a constant mixed with the index."
=> the direct-compare `live_check` is the DECOY; the real checker is installed by an
init constructor and uses a const+index unpack.

## Evidence this file is the decoy-only build (same defect class as Rev300 Constructor)
- gdb: `mprotect` is called ONLY from `main` (0x…5218 and 0x…525a); no init/constructor call.
- At `main` entry the `desk` section is still the on-disk ciphertext (46 32 a5 b4 …) —
  nothing modified it beforehand, so no init-installed checker exists in this binary.
- `.init_array` has a single standard entry (`frame_dummy`); no `.ctors`/`.preinit_array`.
- Brute-forcing the hint's const+index unpack over the decoy literals (N,E,V,A / 5) yields
  no recognizable boat — the real expected boat is not derivable from this file.

## Action
Needs a corrected `checker` download (the init-installed real checker is absent here).
Do NOT submit guesses. 3 teams captured it, so a complete build exists somewhere.
