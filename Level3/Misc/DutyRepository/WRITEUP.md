<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Duty+Repository" alt="Typing SVG" /></a>

</div>

# Duty Repository — MISC · JID-Misc300 · Level 3 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — all three values derived locally from the bundle and submitted manually by the player; all flags accepted by the platform.
- **Points:** 980 / 980 (Boat 180, Litres 300, Word 500)
- **Flags:** Boat → Litres → Word (chained, plaintext format, each unlocks the next)
- **Attachment:** `desk.bundle` (git bundle)
- **Prompt:** *"Duty repository. The duty desk repository. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `ANA` | ✅ |
| 2 | Litres | `87` | ✅ |
| 3 | Word | `linen` | ✅ |

---

## TL;DR

1. `desk.bundle` is a git bundle with two revisions: the signed tag `desk-14` (`bdd2cbc`) and a later, tampered `posted` HEAD.
2. "The revision the duty officer signed" is the tagged commit; read everything with `git show desk-14:<file>`.
3. At that revision: Boat `ANA`, civil-only litres 40 + 15 + 20 + 12 = `87`, order word `linen`. HEAD's ROCA / 240 / barrel are decoys.

## Challenge

> ***** BEGIN SECURE COMMUNIQUE *****
> Duty repository. The duty desk repository. The file is on this page.
> ***** END SECURE COMMUNIQUE *****

Attachment: `desk.bundle`. Three chained flags (plaintext, each unlocks the next):

1. **Boat** (180) — "Submit the boat on the revision the duty officer signed. Format: plaintext."
2. **Litres** (300) — locked by Boat.
3. **Word** (500) — locked by Litres.

## Key insight

`desk.bundle` is a **git bundle** (a packed git repository), not a binary:

```
file desk.bundle         -> Git bundle
git bundle list-heads desk.bundle
  e41aeee... refs/heads/posted
  0300bd6... refs/tags/desk-14
  e41aeee... HEAD
```

Clone it into an empty dir and fetch the tag:

```
git clone desk.bundle deskrepo
cd deskrepo
git fetch ../desk.bundle 'refs/tags/*:refs/tags/*'
git log --all --oneline --decorate
  e41aeee (HEAD -> posted, origin/posted) Post the checked morning slip
  bdd2cbc (tag: desk-14)                   Desk copy for 14 March
```

Two revisions:

- `bdd2cbc` "Desk copy for 14 March" — pointed to by the annotated tag **`desk-14`**,
  tagger *L. Varga <varga@liaison.local>*, tag message `Signed, L. Varga.`
- `e41aeee` "Post the checked morning slip" — branch `posted` / HEAD, created **after** the
  signing and **tampered** with (`rates.txt`, `slip.txt`, `manifest.csv`, `README.md` all changed).

**"The revision the duty officer signed" = the tagged commit `bdd2cbc` (`desk-14`).**
Everything must be read at that revision; the `posted` HEAD is the decoy.

```
git show desk-14:slip.txt
git show desk-14:manifest.csv
git show desk-14:rates.txt
```

## Flag 1 — Boat = `ANA`

`slip.txt` at the signed revision:

```
Boat ANA
Passengers 18
Order word linen
```

Decoy: HEAD rewrites it to `Boat ROCA`.

## Flag 2 — Litres = `87`

`rates.txt` at the signed revision:

```
A drum holds 20 litres.
Add the civil lines only.
```

`manifest.csv` at the signed revision — sum **civil** lines only, converting drums to litres:

| item   | side     | qty | unit  | litres |
|--------|----------|-----|-------|--------|
| fuel   | civil    | 40  | litre | 40     |
| water  | civil    | 15  | litre | 15     |
| rope   | civil    | 1   | drum  | 20     |
| lamp   | civil    | 12  | litre | 12     |
| bowser | military | 80  | litre | — (excluded: military) |

Total = 40 + 15 + 20 + 12 = **87 litres**.

Decoy: HEAD says a drum holds 10 litres, "Add every line", adds a planted `stores,civil,83`
line and keeps the military bowser → 240, which matches the planted `README.md` ("Total 240 litres").
Ignore it.

## Flag 3 — Word = `linen`

`slip.txt` at the signed revision: `Order word linen`.
Decoy: HEAD rewrites it to `barrel`.

## Notes

- Pure local analysis of the downloaded bundle; nothing executed against the challenge
  infrastructure.
- The whole trick is reading the **signed** revision (`desk-14` / `bdd2cbc`) instead of the
  tampered `posted` HEAD. The `README.md` on HEAD exists only to lure you to the 240/ROCA/barrel
  decoys.
