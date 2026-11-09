import re, sys

d = open(sys.argv[1], 'rb').read()
handler = d[0x1189:0x1246]   # the SIGTRAP handler

# In the handler the saved regs from ucontext are:
#   rax = saved RDI = boat ptr, rcx = saved RSI = berth ptr, rdx = saved RDX = word ptr
# Expected chars come from `cmp BYTE PTR [reg(+disp8)], imm8`  (opcode 0x80 /7).
#   modrm: rax -> 0x38 (no disp) / 0x78 (disp8); rcx -> 0x39/0x79; rdx -> 0x3a/0x7a
bases = {'boat': (0x38, 0x78), 'berth': (0x39, 0x79), 'word': (0x3a, 0x7a)}

def extract(nodisp, disp):
    out = {}
    i = 0
    while i < len(handler):
        if handler[i] == 0x80 and handler[i+1] == nodisp:        # cmp [reg], imm8  (offset 0)
            out[0] = handler[i+2]; i += 3; continue
        if handler[i] == 0x80 and handler[i+1] == disp:          # cmp [reg+disp8], imm8
            out[handler[i+2]] = handler[i+3]; i += 4; continue
        i += 1
    # build string from offset 0 up to the first 0x00 (NUL terminator check)
    s = bytearray()
    k = 0
    while k in out and out[k] != 0:
        s.append(out[k]); k += 1
    return bytes(s).decode()

boat  = extract(*bases['boat'])
berth = extract(*bases['berth'])
word  = extract(*bases['word'])

assert (boat, berth, word) == ('PINE', '7', 'moss'), (boat, berth, word)
print('Boat  =', boat)
print('Berth =', berth)
print('Word  =', word)
