"""JID For403: list Desk programs in the ShimCache, mark the Run-key one, print mtimes.

Usage: python3 -I solve.py SYSTEM
"""
import datetime
import mmap
import re
import struct
import sys

NEEDLE = "C:\\Users\\Public\\Desk\\".encode("utf-16le")
PATH = re.compile(rb"(?:[\x20-\x7e]\x00)+")


def filetime(ft):
    return (datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ft // 10)).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(hive):
    with open(hive, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
        shim, other = {}, set()
        i = m.find(NEEDLE)
        while i != -1:
            start = i
            path = PATH.match(m, start).group().decode("utf-16le")
            # Win10 ShimCache entry: "10ts" | u32 | u32 entry size | u16 path len | path | u64 FILETIME
            if m[start - 14:start - 10] == b"10ts" and struct.unpack("<H", m[start - 2:start])[0] == len(path) * 2:
                end = start + len(path) * 2
                shim[path] = struct.unpack("<Q", m[end:end + 8])[0]
            else:
                other.add(path)
            i = m.find(NEEDLE, i + 1)

    for path, ft in sorted(shim.items()):
        tag = "Run key (starts at logon)" if path in other else "NOT in Run key  <-- answer"
        print(f"{path:40} mtime {filetime(ft)}  {tag}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "SYSTEM")
