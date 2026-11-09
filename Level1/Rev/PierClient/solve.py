import sys, re, struct
d = open(sys.argv[1], 'rb').read()
# main: 8 x "mov BYTE PTR [rsp+0x8+i], imm8" (c6 44 24 xx imm) then init mov eax,imm32 (b8)
m = re.search(rb'(?:\xc6\x44\x24[\x08-\x0f].){8}', d, re.S)
frame = bytes(m.group(0)[i*5+4] for i in range(8))
init = struct.unpack('<I', d[d.index(b'\xb8', m.end()) + 1:][:4])[0]
body = frame.rstrip(b'\0')
a = init & 0xffff
for b in frame:  # loop covers all 8 bytes incl. trailing NUL
    a = ((a << 3) | (a >> 13)) & 0xffff
    a = ((a ^ b) + 0x27) & 0xffff
assert body == b'LD3SOLA' and init == 0x6c11 and a == 0x4f99
print('Boat    :', body.decode())
print('Checksum: %d = 0x%04x (16-bit, ax)' % (a, a))
print('Frame kept' if a == 0 else 'client prints "frame dropped" (ax != 0)')
