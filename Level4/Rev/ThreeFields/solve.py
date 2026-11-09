import re, sys

d = open(sys.argv[1], 'rb').read()

# main @ 0x1149..0x1171: nine `mov BYTE PTR [rsp+off], imm8` build the message bytes.
# c6 44 24 <off> <imm>
msg = bytes(m[1][0] for m in re.finditer(rb'\xc6\x44\x24.(.)', d[0x1139:0x11a1], re.S))
assert len(msg) == 9, msg.hex()

# two messages, each [type][counter][payload]
m1, m2 = msg[:6], msg[6:]
boat = m1[2:].decode()
counter2 = m2[1]   # second message counter

# the mac that seals the exchange: 32-bit hash over the 8 content bytes msg[0:8]
# h = rol32(b ^ h, 5) * 0x45d9f3b, seed 0x4314 (gdb-confirmed r8d = 0x0ad38c32)
rol = lambda x, n: ((x << n) | (x >> (32 - n))) & 0xffffffff
h = 0x4314
for b in msg[:8]:
    h = (rol(b ^ h, 5) * 0x45d9f3b) & 0xffffffff

assert (boat, counter2, h) == ('BORA', 0x43, 0x0ad38c32)
print('Boat    =', boat)
print('Counter =', counter2)   # 67
print('Mac     =', h)          # 181636146
