<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Large+Disk+Image" alt="Typing SVG" /></a>

</div>

# Large Disk Image — FORENSICS · JID-For402 · Level 8 · 🔴 HARD

Artifact not included in the repo (≈1 GB); sha256 below.

- **Status:** ✅ SOLVED (2/2) — recovered the one free (unclaimed) FAT32 cluster.
- **Points:** — / — (per-flag points not recorded)
- **Flags:** Code → Name (chained, plaintext, no `CTF{}` wrapper)
- **Attachment:** `volume.img` (1 GiB raw FAT32 image), sha256 `87a4af0766b30481ffa741bc6350b8e6772d60293702d275143e84e5bf282752`
- **Prompt:** *"A large disk image from a liaison stick. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Code | `sorrel` | ✅ |
| 2 | Name | `briar` | ✅ |

---

## TL;DR

The image is a single FAT32 volume packed with decoys: 400 small files and a
1 GiB filler file all say `Posted code ...`, and the slack of the small files
hides two more words. The real data sits in **one free cluster** (FAT entry 0,
no directory entry points at it), stored as UTF-16LE so plain `strings` misses
it: `sorrel\nbriar\n`. The first line is the code and the second line is the name stored with it.

## Layout

No partition table: the image is one FAT32 filesystem from sector 0.

| Field              | Value                       |
|--------------------|-----------------------------|
| Label / OEM        | `STICK` / `MSDOS5.0`        |
| Bytes per sector   | 512                         |
| Cluster size       | 4096 bytes                  |
| Reserved sectors   | 32 (FSInfo = 1, backup boot = 6) |
| FATs               | 2 × 2048 sectors (identical) |
| Data region start  | byte 2113536                |

The data region ends exactly at the end of the image, so there is no hidden
gap after the filesystem. Reserved sectors outside boot/FSInfo/backup are zero.

Sleuthkit was not available, so a small read-only FAT32 walker
(`fat_walk.py`) parses the root directory, follows every cluster chain, and
reports non-zero clusters that no file claims.

## Decoys (all inside clusters some file claims)

| Where                         | Content                          |
|-------------------------------|----------------------------------|
| `/R0001.TXT` … `/R0400.TXT` (18 bytes, clusters 6–405) | `Posted code 31880` |
| `/NOISE.TXT` (1,069,871,104 bytes, clusters 406–261604) | `Posted code 77410` repeated |
| Slack of every `R*.TXT` cluster (after byte 18) | `pollen\n` (ASCII) + `willow\n` (UTF-16LE) |

The "Posted" codes are the obvious bait. The slack words are subtler, but each
cluster is still owned by an `R*.TXT` directory entry, so a file *does* claim
that space. No deleted entries, subdirectories or orphan FAT chains exist.

## The unclaimed cluster

Exactly one non-zero cluster is free:

- **Cluster 261612**, image offset `2113536 + (261612 - 2) * 4096 = 1073668096`
- FAT entry = `0x00000000` (free), no directory entry references it
- FSInfo "next free cluster" hint = **261612** (free count 25), consistent with
  the cluster having been written and then released

```
$ dd if=volume.img bs=1 skip=1073668096 count=32 status=none | od -c
0000000   s  \0   o  \0   r  \0   r  \0   e  \0   l  \0  \n  \0   b  \0
0000020   r  \0   i  \0   a  \0   r  \0  \n  \0  \0  \0  \0  \0  \0  \0
```

UTF-16LE decodes to:

```
sorrel
briar
```

- **Code:** `sorrel`
- **Name** ("the short name stored with that code"): `briar`

## Takeaways

- "Where no file claims it" means walking the allocation structures (FAT /
  directory entries), not just grepping: slack *is* claimed space.
- Search for UTF-16LE (`strings -el`) as well as ASCII. The real answer and one decoy were both UTF-16.
- The FSInfo next-free hint points at recently freed space, which is useful for finding the last deletion on a FAT volume.

## Reproduce

`solve.sh` (read-only, about 3–5 min for the full FAT walk).
