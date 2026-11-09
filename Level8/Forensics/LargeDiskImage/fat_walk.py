import struct,sys,mmap
f=open(sys.argv[1],'rb'); m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
bs=m[:512]
bps,spc,rsv,nf=struct.unpack('<HBHB',bs[11:17]); spf=struct.unpack('<I',bs[36:40])[0]
root=struct.unpack('<I',bs[44:48])[0]; fsi,bk=struct.unpack('<HH',bs[48:52]); tot=struct.unpack('<I',bs[32:36])[0]
print('bps',bps,'spc',spc,'rsv',rsv,'nf',nf,'spf',spf,'root',root,'fsinfo',fsi,'bkboot',bk,'tot',tot)
fat0=rsv*bps; data=(rsv+nf*spf)*bps; cs=spc*bps
ncl=(tot-rsv-nf*spf)//spc
fat=struct.unpack('<%dI'%(spf*bps//4),m[fat0:fat0+spf*bps])
print('ncl',ncl,'data off',data)
def off(c): return data+(c-2)*cs
def chain(c):
    r=[]
    while 2<=c<0x0FFFFFF8 and len(r)<ncl and c not in r: r.append(c); c=fat[c]&0x0FFFFFFF
    return r
claimed=set(); 
def walk(c,path):
    for cl in chain(c):
        claimed.add(cl)
        b=m[off(cl):off(cl)+cs]; lfn=''
        for i in range(0,cs,32):
            e=b[i:i+32]
            if e[0]==0: break
            at=e[11]
            if at==0x0F:
                lfn=''.join(chr(x) for x in struct.unpack('<5H',e[1:11])+struct.unpack('<6H',e[14:26])+struct.unpack('<2H',e[28:32]) if x not in(0,0xFFFF))+lfn; continue
            dele=e[0]==0xE5
            name=e[:8].decode('latin1').strip()+('.'+e[8:11].decode('latin1').strip() if e[8:11].strip() else '')
            hi,lo=struct.unpack('<HH',e[20:22]+e[26:28]); sc=hi<<16|lo; sz=struct.unpack('<I',e[28:32])[0]
            nm=lfn or name; lfn=''
            if at&8: print('VOLLABEL',name); continue
            if name in('.','..'): continue
            print(('DEL ' if dele else '')+('D ' if at&0x10 else 'F ')+path+'/'+nm,'attr',hex(at),'cl',sc,'sz',sz,'chain',len(chain(sc)) if sc else 0)
            if not dele:
                if sc: claimed.update(chain(sc))
                if at&0x10 and sc: walk(sc,path+'/'+nm)
walk(root,'')
orph=[c for c in range(2,ncl+2) if fat[c]&0x0FFFFFFF not in(0,) and c not in claimed]
print('orphan allocated clusters',len(orph),orph[:20])
nz=[c for c in range(2,ncl+2) if c not in claimed and any(m[off(c):off(c)+cs])]
print('unclaimed nonzero clusters',len(nz),nz[:40])
import pickle;pickle.dump((nz,orph),open('nz.pkl','wb'))
