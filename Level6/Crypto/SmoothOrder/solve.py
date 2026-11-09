p=97767475431570134191;g=7;h=28690494907310954915;peer=6709581214550667291
def isp(n):
    d=n-1;s=0
    while d%2==0:d//=2;s+=1
    for a in [2,3,5,7,11,13,17,19,23,29,31,37]:
        x=pow(a,d,n)
        if x in(1,n-1):continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1:break
        else:return False
    return True
def fac(n):
    f={};q=2
    while q<100000 and n>1:
        while n%q==0:f[q]=f.get(q,0)+1;n//=q
        q+=1
    if n>1:f[n]=1
    return f
F=fac(p-1);print(isp(p),F)
def order(a):
    o=p-1
    for q in F:
        while o%q==0 and pow(a,o//q,p)==1:o//=q
    return o
og=order(g);print("ord g",og,"ord h",order(h),"ord peer",order(peer))
print("posted ok",pow(g,240183,p)==h)
def dlog(t):
    # PH over order og
    from math import prod
    rs=[];ms=[]
    for q,e in fac(og).items():
        qe=q**e;gam=pow(g,og//qe,p);tt=pow(t,og//qe,p)
        # brute force within subgroup size qe (<=53^k small)
        c=1
        for k in range(qe):
            if c==tt:rs.append(k);ms.append(qe);break
            c=c*gam%p
        else:return None
    x=0;M=1
    for r,m in zip(rs,ms):
        x+=M*((r-x)*pow(M,-1,m)%m);M*=m
    return x,M
x,M=dlog(h);print("x",x,"mod",M,pow(g,x,p)==h)
print("shared",pow(peer,x,p),"alt x+M",pow(peer,x+M,p))
r=dlog(peer);print("peer dlog",r, r and pow(g,r[0],p)==peer, r and pow(h,r[0],p))
