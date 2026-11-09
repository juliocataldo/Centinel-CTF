import re, sys

d = bytearray(open(sys.argv[1], 'rb').read())

# main installs the real checker by decrypting the `desk` section (live_check) in place:
# mprotect RWX, XOR bytes 0x1322..0x13a3 with key 0x512c7a13 (13 7a 2c 51),
# index = (addr - 0x1322) mod 4. Section fileoff == vaddr.
start, end = 0x1322, 0x13a4
key = (0x512c7a13).to_bytes(4, 'little')
for a in range(start, end):
    d[a] ^= key[(a - start) & 3]
code = bytes(d[start:end])

# live_check: each compared byte is `movzx eax,BYTE PTR [rax]` (0f b6 00) followed
# (after an optional `add rax,imm`) by `cmp al, imm8` (3c XX). Anchor on 0f b6 00
# to avoid matching stray 0x3c bytes (e.g. jump displacements).
chars = [m.group(1)[0] for m in re.finditer(rb'\x0f\xb6\x00(?:\x48\x83\xc0.)?\x3c(.)', code, re.S)]
boat  = bytes(chars[:4]).decode()     # [rbp-8]  = rdi
berth = bytes(chars[4:5]).decode()    # [rbp-10] = rsi

assert (boat, berth) == ('NEVA', '5'), (boat, berth, chars)
print('Boat  =', boat)
print('Berth =', berth)
