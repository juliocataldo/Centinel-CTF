import sys

d = open(sys.argv[1], 'rb').read()

def leb(p):
    v = s = 0
    while True:
        b = d[p]; p += 1
        v |= (b & 0x7f) << s; s += 7
        if b < 0x80:
            return v, p

# walk sections to the data section (id 11)
i = 8
while True:
    size, body = leb(i + 1)
    if d[i] == 11:
        break
    i = body + size
seg = d[body:]
assert seg[0] == 1 and seg[1:5] == b'\x00\x41\x00\x0b'  # 1 segment, memory 0, offset i32.const 0
mem = seg[6:6 + seg[5]]

# pier_count / pier_litres: 5 records of 4 bytes at 0x40: [kind, litres, tag, pad]
# a record counts when kind == 1 (civil) and tag != 'x'
recs = [mem[a:a + 4] for a in range(0x40, 0x54, 4)]
kept = [r for r in recs if r[0] == 1 and r[2] != ord('x')]
for r in recs:
    print(r.hex(), 'kept' if r in kept else 'skip')

count, litres = len(kept), sum(r[1] for r in kept)
assert (count, litres) == (3, 58)
print('Records =', count)
print('Litres  =', litres)
