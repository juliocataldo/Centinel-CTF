<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Hidden+Tally" alt="Typing SVG" /></a>

</div>

# Hidden Tally — REV · JID-Rev303 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `SAIL/linen/62` recovered from the hidden tally and verified with `solve.py`.
- **Points:** — (unknown)
- **Flags:** Boat → Word → Litres (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `desk.pyc` (byte-compiled Python module, CPython 3.11, magic 3495)
- **Prompt:** *"The posted module hides the tally it runs. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `SAIL` | ✅ |
| 2 | Word | `linen` | ✅ |
| 3 | Litres | `62` | ✅ |

---

## TL;DR

1. The posted `.pyc` prints a decoy and hides the real `check` in a marshalled, XOR-61 obfuscated code blob that it de-obfuscates and `exec`s.
2. De-obfuscate (`b ^ 61`) + unmarshal → a `check` that sums `side==1 && mark==0` rows (`220,150,140,110`), `total = sum // 10`, and builds the strings via `chr(...)`.
3. **Boat `SAIL`, Word `linen`, Litres 620//10 = `62`.**

## Recon

`file desk.pyc` → *CPython 3.11*. The local interpreter was 3.14, whose `marshal` cannot read a
3.11 code object, so a throwaway **3.11** was fetched with `uv python install 3.11` and used only
to `marshal.loads` + `dis` — **never** to execute the module (the module itself `exec()`s the
hidden code; we only disassemble it).

## The posted module (top level)

Disassembling the outer code object shows:

```python
import marshal
def posted(): ...                                   # decoy printer
print("Posted module. Boat ROCA. Word barrel. Litres 240.")   # decoy
blob = bytes((94, 61, 61, ...))                     # ~1226 obfuscated bytes
code = marshal.loads(bytes(b ^ 61 for b in blob))   # de-obfuscate, then unmarshal
ns = {}
exec(code, ns)                                      # defines ns['check']
boat   = input().strip()
word   = input().strip()
litres = int(input().strip())
print('pass' if ns['check'](boat, word, litres) else 'fail')
posted()
```

The tally is hidden twice: it lives in a **marshalled** code blob, and that blob is **XOR 61**
(`0x3d`) obfuscated. The de-obfuscating generator expression disassembles to exactly
`item ^ 61`.

## The hidden tally (inner `check`)

De-obfuscating (`b ^ 61`) and unmarshalling the blob yields a module that defines:

```python
def check(boat, word, litres):
    rows = [(1,220,0),(1,150,0),(1,80,120),(2,900,0),(1,140,0),(1,110,0)]   # (side, amt, mark)
    kept = [r[1] for r in rows if r[0] == 1 and r[2] == 0]
    total = sum(kept) // 10
    name  = chr(83)+chr(65)+chr(73)+chr(76)                 # "SAIL"
    cloth = chr(108)+chr(105)+chr(110)+chr(101)+chr(110)    # "linen"
    return boat == name and word == cloth and litres == total
```

Rows kept (`side==1 and mark==0`): `220, 150, 140, 110`.

- sum = 620, `total = 620 // 10` = **62** → Litres
- name = **`SAIL`** → Boat
- cloth = **`linen`** → Word

## Solve

[`solve.py`](solve.py) reproduces the recovered tally and asserts (version-independent):

```
$ python3 -I solve.py
Boat   = SAIL
Word   = linen
Litres = 62
```

Cross-check — extraction straight from the pyc under 3.11 (no exec):

```
$ uv run --python 3.11 python -I verify.py desk.pyc
rows = ((1,220,0),(1,150,0),(1,80,120),(2,900,0),(1,140,0),(1,110,0))
Litres = 62
```

## Notes

- The flags are plaintext: `SAIL`, `linen`, `62`.
- The traps: the `posted()`/print decoy (`ROCA` / `barrel` / `240`), the marshalled-and-`exec`'d
  blob, and the `XOR 61` layer on top of it. The `chr(...)` concatenations hide the strings
  `SAIL` / `linen` from a plain `strings` dump.
- `litres` is again a divide-by-10 tally — the author's recurring pattern.
- Analysis only: `marshal.loads` + `dis` on a local copy; the module was never executed.
