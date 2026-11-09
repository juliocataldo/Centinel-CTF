#!/bin/bash
# Usage: ./solve.sh   (run in this dir; read-only; no sleuthkit needed)
IMG=volume.img
# Identify artifact: FAT32, label STICK, 4096-byte clusters, data region at byte 2113536 (solves: FS type/layout).
file $IMG
# Walk dir tree + FAT, list claimed clusters, report unclaimed non-zero clusters (solves: finds cluster 261612; slow ~3-5 min).
python3 -I fat_walk.py $IMG | grep -v -E '^F /R[0-9]{4}\.TXT'
# Dump the unclaimed cluster 261612 (offset 1073668096) and decode as UTF-16LE (solves: the Code candidate).
python3 -I -c "
f=open('$IMG','rb');f.seek(2113536+(261612-2)*4096);b=f.read(4096).rstrip(b'\0');print(b);print(b.decode('utf-16le'))"
# Show FSInfo free-cluster hint (next free = 261612) (goal: corroborate the cluster is free and was written last).
python3 -I -c "
import struct;f=open('$IMG','rb');f.seek(512);print(struct.unpack('<II',f.read(512)[488:496]))"
# Show slack of R0001.TXT (cluster 6) = decoy words claimed by files (goal: distinguish decoys).
python3 -I -c "
f=open('$IMG','rb');f.seek(2113536+4*4096);print(f.read(4096)[:60])"
