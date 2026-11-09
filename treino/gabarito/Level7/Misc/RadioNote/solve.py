# usage: solve.py pier-note.wav ; demod Bell202 AFSK (1200 mark/2200 space, 1200 baud) tail burst
import sys,numpy as np
from scipy.io import wavfile
sr,x=wavfile.read(sys.argv[1]);x=x.astype(float)
nz=np.nonzero(np.abs(x[int(9.5*sr):])>100)[0][0]+int(9.5*sr)
b=sr/1200;print('start',nz/sr,'bits',(len(x)-nz)/b)
def bits(off,dec=lambda a,b:a>b):
    out=[];t=nz+off
    while t+b<=len(x):
        s=x[int(t):int(t+b)];n=np.arange(len(s))/sr
        e=lambda f:abs(np.sum(s*np.exp(-2j*np.pi*f*n)))
        out.append(1 if e(1200)>e(2200) else 0);t+=b
    return out
def asc(bs,msb,inv=0):
    r=''
    for i in range(0,len(bs)-7,8):
        v=bs[i:i+8]
        if inv:v=[1-q for q in v]
        if not msb:v=v[::-1]
        c=int(''.join(map(str,v)),2);r+=chr(c) if 32<=c<127 else '.'
    return r
for off in (0,):
    bs=bits(off);print(''.join(map(str,bs)))
    nr=[1-(bs[i]^bs[i-1]) for i in range(1,len(bs))]
    for name,s in (('raw',bs),('nrzi',nr)):
        for inv in (0,1):
            for msb in (0,1):
                for sh in range(8):print(name,inv,msb,sh,asc(s[sh:],msb,inv))
print('---framed')
bs=bits(0);fr=[bs[i:i+10] for i in range(0,len(bs),10)]
by=[]
for f in fr:
    ok=f[0]==0 and f[9]==1
    v=int(''.join(map(str,f[1:9][::-1])),2);by.append(v);print(ok,hex(v),chr(v) if 32<=v<127 else '.')
print(bytes(by))
