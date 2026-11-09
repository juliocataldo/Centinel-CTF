<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Second+Class" alt="Typing SVG" /></a>

</div>

# Second Class — REV · JID-Rev105 · Level 2 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (2/2) — both values read from the decrypted class; all flags accepted by the platform.
- **Points:** —
- **Flags:** Boat → Word (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `desk.jar` (Java archive, `Main-Class: Desk`, built with JDK 17)
- **Prompt:** *"The desk program loads a second class. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `LUNA` | ✅ |
| 2 | Word | `linen` | ✅ |

---

## TL;DR

1. `Desk extends ClassLoader` and builds a 414-byte array in `main`; running the jar only prints the decoy.
2. The array is XORed with the repeating key `(23 + 60*(i&7)) & 0xff` and passed to `defineClass("Loaded", ...)`.
3. Decrypting it statically gives a valid class (`CAFEBABE`) whose `acceptsBoat` / `acceptsWord` compare against `LUNA` / `linen`.

Fifth in the series. As in **Handset image** (Rev103), the real logic is a second
program hidden inside the first. This time it is a JVM class that the outer class
decrypts and loads at runtime with its own `ClassLoader`.

## Recon

```
$ unzip -l desk.jar
  META-INF/MANIFEST.MF
  Desk.class            (4065 bytes)
```

The jar contains only one class, so the "second class" is not stored as a file. Running
`javap -c -p -constants Desk.class` shows:

- `public class Desk extends java.lang.ClassLoader`, which is the hint that it defines classes itself.
- `main` prints the decoy: `Posted board: boat ROCA, word barrel. This board is not loaded.`
- It initializes `int a = 23; int b = 60;`.
- It builds a 414-element `byte[]` one element at a time (`dup / push idx / push val / bastore`).
  That is why `Desk.class` is 4 KB for very little code.

## The loader

Reconstructed from the bytecode at the end of `main`:

```java
byte[] enc = { -35, -83, 53, 117, 7, 67, 127, -116, ... };   // 414 bytes
byte[] dec = new byte[enc.length];
for (int i = 0; i < enc.length; i++) {
    int k = (a + b * (i & 7)) & 255;        // 23 + 60*(i&7)
    dec[i] = (byte) (enc[i] ^ k);
}
Class<?> c = new Desk().defineClass("Loaded", dec, 0, dec.length);
boolean boat = (Boolean) c.getMethod("acceptsBoat", String.class).invoke(null, "x");
boolean word = (Boolean) c.getMethod("acceptsWord", String.class).invoke(null, "x");
if (boat && word) System.out.println("open");
System.out.println("Class sealed.");
```

The key repeats every 8 bytes: `17 53 8f cb 07 43 7f bb`. A quick sanity check:
`0xdd ^ 0x17 = 0xca`, `0xad ^ 0x53 = 0xfe`, `0x35 ^ 0x8f = 0xba`, `0x75 ^ 0xcb = 0xbe`.
The result starts with `CAFEBABE`, the class-file magic.

`main` always tests the literal `"x"`, so running the jar only prints the decoy and
`Class sealed.`.

## The loaded class

Decrypting the array gives a valid 414-byte class file. `javap -c -p -constants Loaded.class` shows:

```java
public class Loaded {
  public static boolean acceptsBoat(String s) { return s.equals("LUNA"); }
  public static boolean acceptsWord(String s) { return s.equals("linen"); }
}
```

So the boat the loaded class accepts is **LUNA**, and the word is **linen**. As before,
the decoy maps one-to-one: `boat ROCA` → **LUNA** and `word barrel` → **linen**.

## Solve

[`solve.py`](solve.py) reads `Desk.class` straight out of the jar. It recovers `a`/`b`
from the `bipush; istore_1; bipush; istore_2` prologue and rebuilds the byte array from
the `dup / push / push / bastore` initializer. It then decrypts the array, asserts the
`CAFEBABE` magic, and writes `Loaded.class`:

```
$ python3 -I solve.py desk.jar
key = (23 + 60*(i&7)) & 0xff, 414 bytes -> Loaded.class
$ javap -c -p -constants Loaded.class
  ... ldc "LUNA" ... String.equals
  ... ldc "linen" ... String.equals
```

## Notes

- No JVM code was executed. Everything comes from `javap` and static decryption.
- Hooking `ClassLoader.defineClass` (for example with a Java agent) would also dump the class at runtime. Static decryption is shorter here.
- Flags are plaintext (no `CTF{}`). Submit `LUNA` first, then `linen`.
