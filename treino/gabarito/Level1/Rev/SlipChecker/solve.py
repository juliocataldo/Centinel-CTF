import sys
d=open(sys.argv[1] if len(sys.argv)>1 else 'slip','rb').read()
# .rodata vaddr 0x2000 == file offset 0x2000
ror3=lambda x:((x>>3)|(x<<5))&255
rol3=lambda x:((x<<3)|(x>>5))&255
def fwd(s,seed):
    p=seed;o=[]
    for i,c in enumerate(s):
        e=(13*i+c+p)&255; e^=(17*i)&255; e^=0xa7
        o.append(rol3(e)); p=o[-1]
    return bytes(o)
def inv(exp,seed):
    p=seed;r=[]
    for i,x in enumerate(exp):
        e=ror3(x); c=((e^0xa7^(17*i&255))-13*i-p)&255
        r.append(c); p=x
    return bytes(r)
for n,off,l,seed in [('boat',0x207f,4,0x21),('berth',0x207e,1,0x44),('word',0x2079,5,0x19)]:
    exp=d[off:off+l]; s=inv(exp,seed); assert fwd(s,seed)==exp
    print(n,exp.hex(),s,s.hex())
