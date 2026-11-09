<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Large+Database" alt="Typing SVG" /></a>

</div>

# Large Database — FORENSICS · JID-For401 · Level 8 · 🔴 HARD

Artifact not included in the repo (≈1 GB); sha256 below.

- **Status:** ✅ SOLVED (2/2) — carved the deleted row from leaf-page slack.
- **Points:** 2140 / 2140 (640 + 1500)
- **Flags:** Host → File (chained, plaintext)
- **Attachment:** `visits.db` (SQLite 3.x, last written by 3.40.1, 261639 pages × 4096 = 1071673344 bytes)
- **sha256:** `595153e650dacce2152c987ca82585bc538f8dd2d2cbf65a61a77f7c50b76514`
- **Prompt:** *"A large visit database from the desk. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Host | `ledger.liaison.local` | ✅ |
| 2 | File | `south-9.pdf` | ✅ |

---

## TL;DR

The live table has 17.66M filler rows, and none of them is from March 2026. The 21:05:00 UTC visit was **deleted**. Its cell is still present in the unallocated gap of the last leaf page. Carve it by searching the raw file for the timestamp's 4 bytes, `69 b5 cd 7c`. The carved row gives host **`ledger.liaison.local`** and file **`south-9.pdf`**.

## Schema and live data

`sqlite_master` holds a single table:

```
visits(id, host, file, seen, pad)
```

- 17,660,000 rows. `seen` is Unix seconds, but it only spans `1700000000..1700099999` (November 2023).
- The rows follow a fixed pattern. Odd ids are `ledger.liaison.local` / `posted.pdf`. Even ids are `box<N>.liaison.local` / `south-9.pdf`. `pad` is a large run of filler that inflates the file to 1 GiB.
- 2026-03-14 21:05:00 UTC = Unix `1773522300`. A query for that value returns nothing, whether you read `seen` as seconds, milliseconds or microseconds, and so do range queries around it.
- `PRAGMA freelist_count` = 0, with no `-wal` and no `-journal` file. Every page is a table leaf or interior page.

So the record is not in the live b-tree, and it is not on a freelist page either.

## Carving the deleted cell

When SQLite deletes a row, it unlinks the cell from the page's cell pointer array and turns the space into a freeblock. The bytes stay on disk until something overwrites them.

The value `1773522300` fits in 32 bits, so SQLite stores it as serial type 4, a big-endian int32: `69 b5 cd 7c`. A raw `mmap` search for those 4 bytes over the whole file has **exactly one hit**:

```
page 261639 (last leaf page), offset 335
```

The bytes around the hit decode to this layout:

```
[freeblock hdr: next=0, size=0x0be8]  <- first 4 bytes of the cell, overwritten on free
07 00 35 23 04 ae 7d                  <- record header (len 7)
  00     id    -> NULL (INTEGER PRIMARY KEY alias, value lives in the rowid)
  35     host  -> text, (0x35-13)/2 = 20 bytes
  23     file  -> text, (0x23-13)/2 = 11 bytes
  04     seen  -> int32
  ae 7d  pad   -> text, 3000 bytes ('Q' * 3000, partly overwritten by later live cells)
"ledger.liaison.local" "south-9.pdf" 69b5cd7c ...
```

The freeing step overwrote the cell's payload-length and rowid varints with the freeblock header. The record header and body are intact.

```
$ python3 -I solve.py visits.db
page 261639 off 335: seen=1773522300 (2026-03-14 21:05:00 UTC)
hdr bytes: 0700352304ae7d
Host: ledger.liaison.local
File: south-9.pdf
```

## Answers

| Flag | Answer                 | Reasoning |
|------|------------------------|-----------|
| Host | `ledger.liaison.local` | Host column of the only record with `seen = 1773522300`, carved from slack space |
| File | `south-9.pdf`          | File column of the same deleted record |

## Pitfalls

- Any SQL query misses the record, whatever epoch unit you assume, because the row was deleted. Only raw page slack has it.
- The freelist is empty, so freelist-based recovery tools find nothing. The data sits inside freeblocks on a live leaf page.
- The deleted record breaks the table's pattern. Live `ledger` rows always carry `posted.pdf`, and `south-9.pdf` always goes with the `box<N>` hosts. Guessing either column from the pattern gives the wrong answer.
- A text search such as `strings | grep 2026` finds nothing, because the timestamp is a binary int32 and not text. Search for the packed bytes instead.
- The gaps on other pages (261637 and 261638) hold leftovers of normal filler rows. Those are decoys, not the target.
- At 1 GiB, read the file in place (`mmap`, or `?mode=ro&immutable=1`) instead of copying it or opening it read-write. A read-write open could create a WAL or vacuum the database, and the slack would be lost.

## Tools

`file`, `sqlite3 -readonly`, and Python (`mmap` plus `struct`). Dedicated carvers such as `undark` or `sqlite-deleted-records-parser` should also recover the cell, since it is a standard freeblock on a leaf page.
