import re, sys
d = open(sys.argv[1], 'rb').read()

# .cctor: newarr Byte[1]; dup; ldc.i4.0; ldc.i4.N; stelem.i1 -> tape[0] = N (the open state)
m = re.search(rb'\x8d....\x25\x16([\x16-\x1e])\x9c\x80', d, re.S)
state = m[1][0] - 0x16

# Boat: 4x (dup; ldc.i4.k; ldarg.0; ldc.i4.s MUL; mul; ldc.i4.ADD; add; conv.u2; stelem.i2)
chars = re.findall(rb'\x25([\x16-\x19])\x02\x1f(.)\x5a([\x16-\x1e])\x58\xd1\x9d', d, re.S)
assert [c[0][0] - 0x16 for c in chars] == [0, 1, 2, 3]
boat = ''.join(chr(state * mul[0] + (add[0] - 0x16)) for _, mul, add in chars)

# Litres: ldarg.0; switch(5) -> case `state` returns its constant
s = d.index(b'\x02\x45\x05\x00\x00\x00') + 2
base = s + 4 + 5 * 4
tgt = base + int.from_bytes(d[s + 4 + 4 * state: s + 8 + 4 * state], 'little', signed=True)
op = d[tgt]
litres = d[tgt + 1] if op == 0x1f else int.from_bytes(d[tgt + 1:tgt + 5], 'little')
assert op in (0x1f, 0x20) and d[tgt + (2 if op == 0x1f else 5)] == 0x2a

print('state  =', state)
print('Boat   =', boat)
print('Litres =', litres)
