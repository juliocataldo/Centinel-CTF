import re, sys, zipfile
c = zipfile.ZipFile(sys.argv[1]).read('Desk.class')

# main: bipush A; istore_1; bipush B; istore_2  -> key base and step
a, b = re.search(rb'\x10(.)\x3c\x10(.)\x3d', c, re.S).groups()
a, b = a[0], b[0]

# byte-array initializer: dup; <push index>; <push value>; bastore
push = rb'([\x02-\x08]|\x10.|\x11..)'
def val(op):
    if op[0] == 0x10: return int.from_bytes(op[1:], 'big', signed=True)
    if op[0] == 0x11: return int.from_bytes(op[1:], 'big', signed=True)
    return op[0] - 3
enc = {}
for i, v in re.findall(rb'\x59' + push + push + rb'\x54', c, re.S):
    enc[val(i)] = val(v) & 0xff
assert sorted(enc) == list(range(len(enc)))
blob = bytes(enc[i] ^ ((a + b * (i & 7)) & 0xff) for i in range(len(enc)))
assert blob[:4] == b'\xca\xfe\xba\xbe'
open('Loaded.class', 'wb').write(blob)
print(f'key = ({a} + {b}*(i&7)) & 0xff, {len(blob)} bytes -> Loaded.class')
