import sys,struct
d=open(sys.argv[1],'rb').read()
# locate .handset via ELF section headers
shoff,=struct.unpack_from('<Q',d,0x28);esz,n,si=struct.unpack_from('<HHH',d,0x3a)
nm=struct.unpack_from('<Q',d,shoff+si*esz+0x18)[0]
for i in range(n):
    s=shoff+i*esz;a=struct.unpack_from('<I',d,s)[0]
    if d[nm+a:].split(b'\0')[0]==b'.handset':
        off,sz=struct.unpack_from('<QQ',d,s+0x18);img=d[off:off+sz]
open('handset.img','wb').write(img)
# Cortex-M image: [SP][reset][..] code @0x10: ldr r0,=0x0800002c; movs r1,#0x5a; movs r2,#4; xor loop; movs r0,#6; b .
assert img[0x10:0x12]==bytes([5,0x48]) and img[0x12:0x14]==bytes([0x5a,0x21])
key=img[0x12];cnt=img[0x14];addr=struct.unpack_from('<I',img,0x28)[0]-0x08000000
call=bytes(b^key for b in img[addr:addr+cnt]).decode()
assert img[0x23]==0x20; chan=img[0x22]
print("Callsign:",call);print("Channel:",chan)
