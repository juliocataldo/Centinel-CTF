import sys

d = open(sys.argv[1], 'rb').read()

# packed @ 0x2078 (.rodata, vaddr == file offset). main @ 0x123a unpacks it to rsp:
#   c = 0            -> stop
#   c & 0x80 == 0    -> literal: copy next c bytes
#   c & 0x80         -> backref: len = c & 0x7f, off = next byte, copy out[-off] len times
# the loop also stops once the read index passes 9
blob = d[0x2078:0x2078 + 10]
out, i = bytearray(), 0
while i <= 9 and blob[i]:
    c = blob[i]
    if c & 0x80:
        n, off = c & 0x7f, blob[i + 1]
        for _ in range(n):
            out.append(out[-off])
        i += 2
    else:
        out += blob[i + 1:i + 1 + c]
        i += 1 + c
print('unpacked =', out.hex(' '))
assert len(out) > 5

# check @ 0x1300: rol(boat[k], 4) ^ (k + 0x19) == out[k], k = 0..3
rol4 = lambda b: ((b << 4) | (b >> 4)) & 0xff
boat = bytes(rol4(out[k] ^ (k + 0x19)) for k in range(4)).decode()

# check @ 0x131c: litres * 3 + 9 == out[4] | out[5] << 8
target = out[4] | out[5] << 8
assert (target - 9) % 3 == 0
litres = (target - 9) // 3

assert (boat, litres) == ('NILE', 64)
print('Boat   =', boat)
print('Litres =', litres)
