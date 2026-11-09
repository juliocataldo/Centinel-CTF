<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Native+Method" alt="Typing SVG" /></a>

</div>

# Native Method — REV · JID-Rev207 · Level 4 · 🔴 HARD

- **Status:** ✅ SOLVED (2/2) — `HERN/6` recovered by inverting the native check and verified with `solve.py` (static + ctypes).
- **Points:** — (unknown)
- **Flags:** Callsign → Channel (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `desk.apk` (Android package: `classes.dex` + `lib/x86_64/libdesk.so`)
- **Prompt:** *"The desk application and its native method. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Callsign | `HERN` | ✅ |
| 2 | Channel | `6` | ✅ |

---

## TL;DR

1. The dex is decoy-only (`posted()` → `ROCA`/`9`); the real `accept(String,int)` is a JNI native method in `libdesk.so`.
2. `native_accept` checks the callsign via `rol8(c,4) ^ (k+0x51)` against `want` (`d5 06 76 b0`) and `channel == 6`.
3. Invert `want` → **Callsign `HERN`, Channel `6`**.

## Recon

```
$ unzip -l desk.apk
      580  classes.dex
    15528  lib/x86_64/libdesk.so
```

### classes.dex

The dex is tiny (580 bytes). Its string table gives the whole Java side:

```
Lcom/liaison/Desk;
posted   ()Ljava/lang/String;        -> "Boat ROCA. Channel 9."
accept   (Ljava/lang/String;I)I      -> native
```

`posted()` is the decoy. `accept(String callsign, int channel)` is the native method.

### libdesk.so

The only import is `strlen`. The symbols are not stripped:

```
0000000000001109 t native_accept
0000000000001170 T JNI_OnLoad
0000000000002000 r want.0
0000000000004020 d table
```

`table` is a `JNINativeMethod` entry, and `JNI_OnLoad` just returns its address:

```
0x4020  -> 0x2004 "accept"
0x4028  -> 0x200b "(Ljava/lang/String;I)I"
0x4030  -> 0x1109 native_accept
```

## native_accept (0x1109)

```c
int native_accept(const char *s, int channel) {
    if (!s || strlen(s) != 4) return 0;
    for (int k = 0; k < 4; k++)
        if (want[k] != (rol8(s[k], 4) ^ (k + 0x51))) return 0;
    return channel == 6;                 // cmp ebp, 6 ; sete al
}
```

`want.0` = `d5 06 76 b0`. Inverting gives `s[k] = rol8(want[k] ^ (k + 0x51), 4)`:

```
d5 ^ 51 = 84 -> 48 'H'
06 ^ 52 = 54 -> 45 'E'
76 ^ 53 = 25 -> 52 'R'
b0 ^ 54 = e4 -> 4e 'N'
```

- **Callsign** = **`HERN`**
- **Channel** = **`6`**

## Solve

[`solve.py`](solve.py) reads `libdesk.so` straight out of the APK, inverts the check and
asserts the result. If you also pass an extracted copy of the lib, it calls `native_accept`
through `ctypes` (base = `JNI_OnLoad` - 0x1170, + 0x1109):

```
$ python3 -I solve.py desk.apk /path/to/libdesk.so
Callsign = HERN
Channel  = 6
HERN 6 -> 1
ROCA 9 -> 0
HERN 9 -> 0
```

## Notes

- The flags are plaintext. Submit `HERN`, then `6`.
- The trap is `posted()` in the dex (`ROCA` / `9`). The real check only exists in the
  native lib.
- The native function takes a plain `char *` and an `int` (no `JNIEnv *` / `jobject`), so it
  can be called directly from `ctypes` without an Android runtime.
