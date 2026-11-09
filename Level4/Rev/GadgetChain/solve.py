import struct, sys

d = open(sys.argv[1] if len(sys.argv) > 1 else 'chain', 'rb').read()

# non-PIE: vaddr 0x404040 (.data) == file offset 0x3020 + (0x404040-0x404020)
CHAIN_VA = 0x404040
DATA_VA, DATA_OFF = 0x404020, 0x3020
off = DATA_OFF + (CHAIN_VA - DATA_VA)
chain = [struct.unpack_from('<Q', d, off + 8*i)[0] for i in range(32)]  # 256 bytes / 8

G = {0x401182:'pop_rdi', 0x401184:'pop_rsi', 0x401186:'pop_rdx',
     0x401188:'write', 0x40118c:'finish'}

# emulate the ROP chain: rsp walks the array, ret pops the next gadget
mem = {}
rdi = rsi = rdx = 0
i = 0
while i < len(chain):
    g = G.get(chain[i])
    if g == 'pop_rdi':  rdi = chain[i+1]; i += 2
    elif g == 'pop_rsi': rsi = chain[i+1]; i += 2
    elif g == 'pop_rdx': rdx = chain[i+1]; i += 2
    elif g == 'write':   mem[rdi] = rsi & 0xff; i += 1
    elif g == 'finish':  break
    else: i += 1  # trailing zeros

# read the NUL-terminated string the chain built, starting at the finish rdi
boat = bytearray()
a = rdi
while mem.get(a, 0) != 0:
    boat.append(mem[a]); a += 1
boat = boat.decode()

# g_finish seals: buffer=="ARGO", rsi==4, rdx==0x33
assert (boat, rsi, rdx) == ('ARGO', 4, 0x33), (boat, rsi, rdx)
print('Boat   =', boat)              # ARGO
print('count  = rsi =', rsi)         # 4
print('rdx    =', hex(rdx), "=", chr(rdx))  # 0x33 = '3'
