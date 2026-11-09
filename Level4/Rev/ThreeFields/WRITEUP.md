<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Three+Fields" alt="Typing SVG" /></a>

</div>

# Three Fields — REV · JID-Rev205 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — `BORA/67/181636146` recovered from the hardcoded bytes and cross-checked against gdb (`r8d = 0x0ad38c32`).
- **Points:** — (unknown)
- **Flags:** Boat → Counter → Mac (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `client` (ELF 64-bit PIE x86-64, not stripped)
- **Prompt:** *"The pier client builds three fields into two messages."* — Flag 2: *"the counter of the second message"*; Flag 3: *"the mac that seals the exchange, in decimal"*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `BORA` | ✅ |
| 2 | Counter | `67` | ✅ |
| 3 | Mac | `181636146` | ✅ |

---

## TL;DR

1. `client` reads no input: `main` hardcodes 9 stack bytes as two messages `[type][counter][payload]` and runs a MAC over them.
2. Msg 1 = type 1, counter 0x14, payload `BORA`; msg 2 = type 2, counter 0x43 (=67), 0x12 mac slot (a decoy).
3. The real MAC is a `rol32`/multiply hash seeded `0x4314` over the 8 content bytes → `0x0ad38c32` = **181636146**.

## Recon

The only import is `puts`. `strings` shows the decoy and the two outcomes:

```
Example exchange: boat ROCA, counter 1, mac 240. This exchange fails.
dropped  Exchange kept.
```

The program reads no input. `main` hardcodes 9 bytes on the stack, runs a MAC over them and
prints `Exchange kept.`. Everything comes from those bytes.

## main (0x1139): the 9 bytes

```
rsp+0x7  01        rsp+0x8  14  rsp+0x9  42 'B'  rsp+0xa 4f 'O'  rsp+0xb 52 'R'  rsp+0xc 41 'A'
rsp+0xd  02        rsp+0xe  43  rsp+0xf  12
```

The "three fields into two messages" split, each message `[type][counter][payload]`:

```
msg 1:  01 | 14 | 42 4f 52 41   ->  type 1, counter 0x14 (20), boat "BORA"
msg 2:  02 | 43 | 12            ->  type 2, counter 0x43 (67), mac 0x12 (18)
```

- **Boat** = **`BORA`** (payload of message 1)
- **Counter** of the second message = `0x43` = **`67`**

The seed `0x4314` is in memory `14 43`: the counter of message 1 (`0x14`) then the counter of
message 2 (`0x43`). The seed is built from the two counters, which is why `0x43` is the counter
and not the leading `0x02` type byte, and the trailing `0x12` is only a placeholder mac slot.

## The MAC loop (0x1185)

```c
uint32_t h = 0x4314;                       // seed
for (b in bytes[0..7])                      // the 8 content bytes, not the 0x12 slot
    h = rol32(b ^ h, 5) * 0x45d9f3b;
// at main+0x68:  cmp esi, r8d   -> esi = 0x12 (slot), r8d = h = computed mac
// esi != r8d  -> jne -> "Exchange kept."   (the slot byte is a decoy, never equals the mac)
```

The **mac that seals the exchange** is that computed 32-bit hash over the 8 content bytes.
gdb (break at `main+0x68`) confirms `r8d = 0x0ad38c32`:

```
0x0ad38c32 = 181636146 (decimal)
```

- **Mac** = **`181636146`**

## Solve

[`solve.py`](solve.py) reads the `mov BYTE PTR [rsp+..], imm8` immediates, splits the two
messages, recomputes the hash over the 8 content bytes and asserts all three fields. The
recomputed hash matches the gdb register value (`0x0ad38c32`), which cross-validates it.

```
$ python3 -I solve.py client
Boat    = BORA
Counter = 67
Mac     = 181636146
```

## Notes

- The flags are plaintext. Submit `BORA`, then `67`, then `181636146`.
- The trap is the decoy line (`ROCA` / `counter 1` / `mac 240`), and the `0x12` placeholder
  byte in the message — the real mac is the computed hash, and the prompt asks for it *in
  decimal*.
- Field order is `[type][counter][payload]`. Reading the leading `01`/`02` type byte as the
  counter gives the wrong answer (`2`); the seed `0x4314` confirms `0x14` and `0x43` are the
  counters.
