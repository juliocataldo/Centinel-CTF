import struct, sys

d = open(sys.argv[1], 'rb').read()  # 2-desk

# main @ 0x113f: mov DWORD [rsp+0xc], imm32 -> divisor
i = d.index(b'\xc7\x44\x24\x0c')
divisor = struct.unpack_from('<I', d, i + 4)[0]

# lines @ 0x2020 (.rodata, vaddr == file offset): 5 records [kind u8, mark u8, value u16]
# loop: skip if mark == 'x'; if kind == 'c': ebx += 1 (lines), ebp += value / divisor (litres)
lines = litres = 0
for k in range(5):
    kind, mark, value = struct.unpack_from('<BBH', d, 0x2020 + 4 * k)
    kept = mark != ord('x') and kind == ord('c')
    print(chr(kind), chr(mark), value, 'kept' if kept else 'skip')
    if kept:
        lines += 1
        litres += value // divisor

assert (divisor, lines, litres) == (10, 3, 53)
print('Divisor =', divisor)
print('Lines   =', lines)
print('Litres  =', litres)
