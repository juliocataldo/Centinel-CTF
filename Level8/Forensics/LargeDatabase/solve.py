"""JID For401: recover the visit at 2026-03-14 21:05:00 UTC from a deleted SQLite cell.

Live table `visits` only holds seen = 1700000000..1700099999, so the target row is not queryable.
It survives as a freed cell in the unallocated gap of a leaf page (found by raw byte search).

Usage: python3 -I solve.py visits.db
"""
import datetime
import mmap
import struct
import sys

TARGET = int(datetime.datetime(2026, 3, 14, 21, 5, 0, tzinfo=datetime.timezone.utc).timestamp())  # 1773522300
PAGE = 4096


def main(path):
    with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
        needle = struct.pack(">I", TARGET)  # seen is stored as a 4-byte big-endian int (serial type 4)
        i = m.find(needle)
        while i != -1:
            # record header: hdrlen=7 | NULL(id) | text host | text file | int32 | text pad(varint, 2 bytes)
            # so host/file/seen are contiguous: host(n) file(m) seen
            blob = m[i - 31:i]  # host is 20 bytes (serial type 0x35), file 11 bytes (0x23)
            host, file_ = bytes(blob[:20]).decode(), bytes(blob[20:]).decode()
            page = i // PAGE + 1
            print(f"page {page} off {i % PAGE}: seen={TARGET} "
                  f"({datetime.datetime.fromtimestamp(TARGET, datetime.timezone.utc):%Y-%m-%d %H:%M:%S} UTC)")
            print("hdr bytes:", bytes(m[i - 31 - 7:i - 31]).hex())
            print("Host:", host)
            print("File:", file_)
            i = m.find(needle, i + 1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "visits.db")
