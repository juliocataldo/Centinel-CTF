import sys

d = open(sys.argv[1], 'rb').read()

# .rdata VMA 0x140004000 == file off 0x2200 (PE: vma = 0x140000000 + file_off adjust).
# want.0 @ vma 0x140004041 -> file off 0x2241, 4 bytes.
want = d[0x2241:0x2245]
assert want == bytes.fromhex('2ff8192a'), want.hex()

# handler (VEH) per boat byte: (rol(b,4) ^ (k+0x3b)) == want[k]
# invert: b = swap_nibbles(want[k] ^ (k+0x3b))
swap = lambda b: ((b << 4) | (b >> 4)) & 0xff
boat = bytes(swap(want[k] ^ (k + 0x3b)) for k in range(4)).decode()

# berth: cmp byte, 0x33  -> '3'  (and strlen==1)
berth = chr(0x33)

# forward-check the recovered boat reproduces want
rol = lambda b, n: ((b << n) | (b >> (8 - n))) & 0xff
assert all((rol(ord(boat[k]), 4) ^ (k + 0x3b)) == want[k] for k in range(4))
assert (boat, berth) == ('ALBA', '3')

print('Boat  =', boat)
print('Berth =', berth)
