import re, sys

d = open(sys.argv[1], 'rb').read()

# main @ 0x11de: key = mov DWORD [rsp+0xc], 0x512c7a13 -> bytes 13 7a 2c 51
# main xors live_check (section "desk", vaddr == file offset 0x1322..0x13a4) with key[i % 4]
key = bytes.fromhex('137a2c51')
assert b'\xc7\x44\x24\x0c' + key in d
code = bytes(b ^ key[i % 4] for i, b in enumerate(d[0x1322:0x13a4]))
assert code[:4] == b'\x55\x48\x89\xe5'  # push rbp; mov rbp, rsp

# decrypted live_check compares byte-by-byte: movzx eax, [rax] (0f b6 00) ; cmp al, imm8 (3c xx)
cmps = [m[1][0] for m in re.finditer(rb'\x0f\xb6\x00\x3c(.)', code, re.S)]
boat, berth = bytes(cmps[:4]).decode(), bytes(cmps[4:5]).decode()
assert (boat, berth) == ('NEVA', '5')
print('Boat  =', boat)
print('Berth =', berth)
