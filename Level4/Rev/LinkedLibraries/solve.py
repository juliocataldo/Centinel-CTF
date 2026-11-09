import struct, sys

# The library the watch is linked against is its NEEDED soname: libslip.so.1
# (RUNPATH $ORIGIN). libslip.so (.decoy.c, "ROCA") is a decoy and is never loaded.
lib = open(sys.argv[1], 'rb').read()   # pass libslip.so.1

# .rodata vma == file offset 0x2000 here.
amt  = list(struct.unpack_from('<6i', lib, 0x2000))   # amt.0
mark = list(lib[0x2018:0x2018+6])                     # mark.1 (bytes)
side = list(struct.unpack_from('<6i', lib, 0x2020))   # side.2

# weigh(): boat written literally; lines = count, litres = sum/10 over
# records where side[i]==1 and mark[i]==0.
boat = 'NARA'                                         # mov bytes 4e 41 52 41 in weigh
lines, total = 0, 0
for i in range(6):
    if side[i] == 1 and mark[i] == 0:
        lines += 1
        total += amt[i]
litres = total // 10                                  # imul 0x66666667 ; sar -> /10

assert (amt, mark, side) == ([200,150,180,120,800,90], [0,0,120,0,0,0], [1,1,1,1,2,1])
assert (boat, lines, litres) == ('NARA', 4, 56), (boat, lines, litres)
print('Boat   =', boat)
print('Lines  =', lines)
print('Litres =', litres)
