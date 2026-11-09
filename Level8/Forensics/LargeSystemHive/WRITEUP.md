<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Large+System+Hive" alt="Typing SVG" /></a>

</div>

# Large System Hive — FORENSICS · JID-For403 · Level 8 · 🔴 HARD

Artifact not included in the repo (≈1 GB); sha256 below.

- **Status:** ✅ SOLVED (2/2) — found the non-autostart desk program in the ShimCache.
- **Points:** 2800 / 2800 (1000 + 1800)
- **Flags:** File → Modified (chained, plaintext)
- **Attachment:** `SYSTEM` (MS Windows registry file, NT/2000+, exactly 1 GiB = 1073741824 bytes)
- **sha256:** `a1764ec4200b419c3e5248ee6d71686d816f47ec57bf6368de352bb8957839d5`
- **Prompt:** *"A large system hive from the desk machine. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | File | `linencopy.exe` | ✅ |
| 2 | Modified | `2026-03-14T19:05:00Z` | ✅ |

---

## TL;DR

The hive is almost entirely one giant `AppCompatCache` (ShimCache) value. It holds about 66k entries, and nearly all of them are filler. Only two entries point to `C:\Users\Public\Desk\`. The `Run` key lists one of them (`posted.exe`). The other one, **`linencopy.exe`**, is the answer. Its ShimCache timestamp is **`2026-03-14T19:05:00Z`**.

## Why the hive is "large"

The `regf` header is valid, and its hive-bins length is `0x3FFFF000`, so the whole 1 GiB is allocated hive data and not trailing padding. A walk of the key tree with a small custom parser shows a synthetic hive with very few keys:

```
Select                                                (Current = 1)
ControlSet001\Control\Session Manager\AppCompatCache  (AppCompatCache value, ~1 GiB)
Software\Microsoft\Windows\CurrentVersion\Run         (Desk = C:\Users\Public\Desk\posted.exe)
```

There are no `Services` keys and no `ControlSet002`, and every key LastWrite time is zero (1601-01-01). The size comes from a single value cell: the `AppCompatCache` blob, which starts near file offset `0x1024`. GUI registry viewers stall on a value this large. A streaming parser over `mmap` handles it without trouble.

## ShimCache (AppCompatCache)

The blob uses the Windows 10 format. Each entry has this layout:

```
"10ts" | u32 unknown | u32 entry data size | u16 path length (bytes) | UTF-16LE path | u64 FILETIME | u32 data size | data
```

There are 65881 entries. 65879 are filler (`C:\Windows\System32\nXXXXXXX.exe`). Only two are under the desk folder:

| Path | ShimCache entry | FILETIME | UTC |
|------|-----------------|----------|-----|
| `C:\Users\Public\Desk\posted.exe`    | index 0, offset `0x1062`         | `134180063400000000` | `2026-03-14T23:59:00Z` |
| `C:\Users\Public\Desk\linencopy.exe` | index 32941, offset `0x1ffc10da` | `134179887000000000` | `2026-03-14T19:05:00Z` |

`strings -el SYSTEM | grep -i desk` agrees: across the whole file, only these two paths and the `Desk` value name appear.

## Logon autostart

`HKLM\Software\Microsoft\Windows\CurrentVersion\Run` has exactly one value, `Desk` = `C:\Users\Public\Desk\posted.exe`. So `posted.exe` starts at logon. `linencopy.exe` was seen by the system, since it is in the ShimCache, but it was **not** set to start at logon.

The ShimCache FILETIME is the file's **last modification time** (`$STANDARD_INFORMATION`), not an execution time. That is exactly what the "Modified" flag asks for.

## Solve script

`solve.py` mmaps the hive and finds every UTF-16LE `C:\Users\Public\Desk\` path. A hit counts as a ShimCache entry when the `10ts` signature sits 14 bytes before it and the path-length field matches. Any other hit is the Run value. The script then decodes the FILETIME that follows the path.

```
$ python3 -I solve.py SYSTEM
C:\Users\Public\Desk\linencopy.exe       mtime 2026-03-14T19:05:00Z  NOT in Run key  <-- answer
C:\Users\Public\Desk\posted.exe          mtime 2026-03-14T23:59:00Z  Run key (starts at logon)
```

## Answers

| Flag     | Answer                 | Reasoning |
|----------|------------------------|-----------|
| File     | `linencopy.exe`        | The only Desk program in the ShimCache that is not in the `Run` key |
| Modified | `2026-03-14T19:05:00Z` | FILETIME in the `linencopy.exe` ShimCache entry |

## Pitfalls

- "Start at logon" in a SYSTEM hive tempts you to check `Services\*\Start`, but there are no services here. The planted `Run` key is the reference.
- `linencopy.exe` sits in the middle of 66k filler entries, so scrolling through the cache by hand will miss it. Search for the folder instead.
- The UTF-16 path-length field just before each path can read as a printable character (`0x44` = `D`, `0x3e` = `>`). A naive backward scan for the start of the string will absorb it, and the `10ts` check then fails. Anchor on the known `C:\` prefix.
- `posted.exe` carries the newest timestamp in the cache (`23:59:00`). It is the logon program, not the answer.

## Tools

`file`, `strings -el`, and Python (mmap plus a hand-rolled regf walker and ShimCache parser). Tools such as `regipy` (`AppCompatCache` plugin) or Eric Zimmerman's `AppCompatCacheParser` should also parse this blob, provided they cope with the 1 GiB value.
