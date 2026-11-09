import struct, sys

d = open(sys.argv[1], 'rb').read()  # slip.bin

# parser main @ 0x1253: memmem(buf, "SLP") -> header: "SLP" | ver u8 | ngroups u16
# groups from +6: [tag u8, len u16, body[len]]
# tag 2 only (0x12d4): name = body[0:4] ^ 0x11, n = body[4], records [type u8, value u16] x n
#   type 0x10 -> sum += value, count += 1   (0x1299)
p = d.index(b'SLP')
ngroups = struct.unpack_from('<H', d, p + 4)[0]
off = p + 6
boat, records, litres = None, 0, 0
for _ in range(ngroups):
    tag, ln = struct.unpack_from('<BH', d, off)
    body = d[off + 3:off + 3 + ln]
    name = bytes(b ^ 0x11 for b in body[:4]).decode()
    n = body[4]
    recs = [struct.unpack_from('<BH', body, 5 + 3 * i) for i in range(n)]
    tail = body[5 + 3 * n:]
    print(f'group tag={tag} name={name} recs={[(hex(t), v) for t, v in recs]} tail={tail.hex()}')
    if tag == 2:
        boat = name
        for t, v in recs:
            if t == 0x10:
                records += 1
                litres += v
    off += 3 + ln

assert (boat, records, litres) == ('TIDE', 3, 59)
print('Boat    =', boat)
print('Records =', records)
print('Litres  =', litres)
