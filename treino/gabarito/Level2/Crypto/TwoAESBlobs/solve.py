import re,sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
t=open(sys.argv[1] if len(sys.argv)>1 else "desk.txt").read()
for n in("Sample","Desk"):
    k=bytes.fromhex(re.search(n+r" key: (\w+)",t)[1]);b=bytes.fromhex(re.search(n+r" blob: (\w+)",t)[1])
    p=AES.new(k,AES.MODE_ECB).decrypt(b)
    print(n,p)
    try:print(" unpadded:",unpad(p,16))
    except ValueError as e:print(" pad err",e)
