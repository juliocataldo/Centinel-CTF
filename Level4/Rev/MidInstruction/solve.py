import re, sys

d = open(sys.argv[1], 'rb').read()

# check_entry @ 0x128c: eb 01 (jmp +1) skips a junk 0xe8 byte and lands at mid @ 0x128f.
# A linear disassembler that starts at 0x128c decodes e8 as a call and loses the real checks.
assert d[0x128c:0x128f] == b'\xeb\x01\xe8'
code = d[0x128f:0x130d]

# per boat byte: swap_nibbles(b) ^ key == target   (83 f0 KK ; 3c TT)
pairs = re.findall(rb'\x83\xf0(.)\x3c(.)', code, re.S)
swap = lambda b: ((b << 4) | (b >> 4)) & 0xff
boat = bytes(swap(t[0] ^ k[0]) for k, t in pairs).decode()

# berth: movzx eax, [rsi] ; cmp al, imm8 ; then berth[1] == 0
m = re.search(rb'\x0f\xb6\x06\x3c(.)', code, re.S)
berth = chr(m[1][0])

assert (boat, berth) == ('WREN', '8')
print('Boat  =', boat)
print('Berth =', berth)
