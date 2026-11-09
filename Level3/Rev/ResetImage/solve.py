import struct, sys

d = open(sys.argv[1], 'rb').read()

# banks @ 0x2020 (.rodata, vaddr == file offset), 0x7c bytes each:
#   +0x00 name[8] | +0x08 text[0x60] | +0x68 5 records of [kind u8, mark u8, value u16]
# main @ 0x114c copies banks[1] (0x209c..0x2118) to the stack, then for each record:
#   skip if mark == 'x'; if kind == 'c' (civil) add value / 10  (imul 0xcccd >> 19)
BANKS, SIZE = 0x2020, 0x7c
bank = d[BANKS + SIZE:BANKS + 2 * SIZE]
boat = bank[:8].rstrip(b'\0').decode()

litres = 0
for i in range(5):
    kind, mark, value = struct.unpack_from('<BBH', bank, 0x68 + 4 * i)
    kept = mark != ord('x') and kind == ord('c')
    print(chr(kind), chr(mark), value, 'kept' if kept else 'skip')
    if kept:
        litres += value // 10

assert (boat, litres) == ('IRIS', 48)
print('Boat   =', boat)
print('Litres =', litres)
