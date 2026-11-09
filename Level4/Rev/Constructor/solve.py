import sys

d = open(sys.argv[1], 'rb').read()
# rodata vma == file offset here
word_exp  = d[0x2079:0x2079+5]   # de 2f 79 c4 04
berth_exp = d[0x207e:0x207e+1]   # e6
boat_exp  = d[0x207f:0x207f+4]   # 4e 90 cb 3d

rol8 = lambda b, n: ((b << n) | (b >> (8 - n))) & 0xff

def transform(inp, seed):
    """Reproduce same()'s per-byte chained hash; returns the output buffer."""
    state = seed & 0xffffffff
    out = bytearray()
    for k, e in enumerate(inp):
        eax = (0xd * k + e) & 0xff            # mov eax,ecx(=0xd*k); add al,input
        eax = (eax + state) & 0xffffffff      # add eax, r13d
        eax ^= (0x11 * k)                      # xor eax, esi(=0x11*k)
        eax ^= 0xffffffa7                      # xor eax, 0xffffffa7
        al = rol8(eax & 0xff, 3)               # rol al,3
        eax = (eax & 0xffffff00) | al
        state = eax                            # r13d = eax
        out.append(al)
    return bytes(out)

def invert(expected, seed):
    """Each output byte is bijective in its input byte; recover forward."""
    res = bytearray()
    for k in range(len(expected)):
        for cand in range(256):
            if transform(bytes(res) + bytes([cand]), seed)[k] == expected[k]:
                res.append(cand)
                break
        else:
            raise SystemExit(f'no byte at {k}')
    return bytes(res)

boat  = invert(boat_exp,  0x21)
berth = invert(berth_exp, 0x44)
word  = invert(word_exp,  0x19)

# verify the forward transform reproduces the stored expected bytes
assert transform(boat,  0x21) == boat_exp
assert transform(berth, 0x44) == berth_exp
assert transform(word,  0x19) == word_exp

print('Boat  =', boat.decode())
print('Berth =', berth.decode())
print('Word  =', word.decode())
