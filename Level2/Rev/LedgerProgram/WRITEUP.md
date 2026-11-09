<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Ledger+Program" alt="Typing SVG" /></a>

</div>

# Ledger Program — REV · JID-Rev104 · Level 2 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (2/2) — both values read from the IL (`solve.py` asserts the opcode shapes); all flags accepted by the platform.
- **Points:** —
- **Flags:** Boat → Litres (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `ledger.dll` (PE32 .NET assembly, .NET 8.0, 5 KB)
- **Prompt:** *"The ledger program. The file is on this page."* Flag text: *"Submit the boat at the state where the ledger opens."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `VELA` | ✅ |
| 2 | Litres | `73` | ✅ |

---

## TL;DR

1. `ledger.dll` is a .NET 8 assembly whose `Main` only prints the decoy (`Boat ROCA`, `Morning total 240`).
2. The static field `tape = { 4 }` set in `.cctor` is the opening state; `Boat(4)` builds `VELA` from four `s*MUL + ADD` chars.
3. `Litres(4)` hits the only non-decoy `switch` case: `73`. Everything comes from parsing the IL by hand, without running it.

Fourth in the series. The pattern is the same (a decoy "posted" value plus the real
answers computed in code), but this time the target is managed .NET IL instead of
native code. The flag text: *"Submit the boat at the state where the ledger opens."*

## Recon

```
$ file ledger.dll
ledger.dll: PE32 executable for MS Windows 4.00 (console), Intel i386 Mono/.Net assembly, 3 sections
```

The user-string heap (`strings -el`) has the decoy and a closing line:

```
ROCA
Morning total 240. Boat ROCA. This is the posted sheet.
Ledger sealed.
```

The `#Strings` heap names everything that matters: one type `Desk`, one static field
`tape`, and the methods `OpenState`, `Boat`, `Litres` and `Main`.

No .NET decompiler was available, so a small Python script parsed the PE/CLI header,
the metadata tables (TypeDef, Field, MethodDef, MemberRef) and the method bodies,
then disassembled the IL. The binary was never executed.

## The IL

**`.cctor`** sets the static field that holds the state:

```
ldc.i4.1; newarr Byte; dup; ldc.i4.0; ldc.i4.4; stelem.i1; stsfld tape
```

So `tape = new byte[] { 4 }`.

**`OpenState()`** returns `tape[0]`, which is **4**. This is "the state where the ledger opens".

**`Boat(int s)`**:

```
ldarg.0; call OpenState; beq.s BUILD
ldstr "ROCA"; ret                       ; decoy for any other state
BUILD:
new char[4] {
  (char)(s*20 + 6),
  (char)(s*16 + 5),
  (char)(s*18 + 4),
  (char)(s*15 + 5) }
newobj string(char[]); ret
```

With `s = 4`: `86 69 76 65` gives **"VELA"**.

**`Litres(int s)`** is a `switch` over 5 cases:

| s       | returns |
|---------|---------|
| 0..3    | 240     |
| **4**   | **73**  |
| default | 240     |

**`Main`**:

```csharp
Console.WriteLine("Morning total 240. Boat ROCA. This is the posted sheet.");
int st = OpenState();
string boat = Boat(st);
int litres = Litres(st);
if (boat.Length == litres && litres >= 0) Console.WriteLine(boat);   // never true: 4 != 73
Console.WriteLine("Ledger sealed.");
```

`Main` never prints the real answers. As before, the decoys map one-to-one:
`Boat ROCA` → **VELA** and `Morning total 240` → **73**.

## Solve

[`solve.py`](solve.py) reads the values straight from the IL bytes: the `ldc.i4.N` in
`.cctor` for the state, the four `ldc.i4.s MUL / ldc.i4.ADD` pairs in `Boat`, and the
switch target for that state in `Litres`. It asserts the expected opcode shapes along
the way:

```
$ python3 -I solve.py ledger.dll
state  = 4
Boat   = VELA
Litres = 73
```

## Notes

- Running the assembly only prints the decoy and `Ledger sealed.`, so the answer has to come from the IL.
- `Boat` is guarded by `s == OpenState()`. Any other state returns the decoy `ROCA`,
  so guessing a state gives a plausible-looking but wrong answer.
- Flags are plaintext (no `CTF{}`). Submit `VELA` first, then `73`.
