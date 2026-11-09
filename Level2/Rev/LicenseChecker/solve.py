import struct, sys
d = open(sys.argv[1], 'rb').read()

# locate the `sealed` symbol (11 bytes in .rodata) via the ELF symtab
shoff, = struct.unpack_from('<Q', d, 0x28); esz, n, si = struct.unpack_from('<HHH', d, 0x3a)
sh = [struct.unpack_from('<IIQQQQIIQQ', d, shoff + i * esz) for i in range(n)]
symtab = next(s for s in sh if s[1] == 2); strtab = sh[symtab[6]]
for o in range(symtab[4], symtab[4] + symtab[5], 24):
    name, _, _, _, val, size = struct.unpack_from('<IBBHQQ', d, o)
    if d[strtab[4] + name:].split(b'\0')[0] == b'sealed':
        break
sealed = d[val:val + size]          # PIE: .rodata vaddr == file offset here
assert size == 11

# main: buf[i] = sealed[i] + 16*sealed[i] + 3  (i.e. *17 + 3, truncated to a byte)
buf = bytes((b * 17 + 3) & 0xff for b in sealed)
boat, word, version = buf[0:4], buf[4:10], buf[10]
assert version == 2                 # cmp byte [rsp+0xf], 2
print('Boat    =', boat.decode())
print('Word    =', word.decode())
print('version =', version)
