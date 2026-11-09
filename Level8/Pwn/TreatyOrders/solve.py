#!/usr/bin/env python3
# Treaty orders (Pwn401) — RSA broadcast e=3, m^3 < n => plain integer cube root.
c = 20367490240561972735595702852095121766721734685010856076181864963972849449057117444715667682768911876290664334691886656576

def icbrt(n):
    x = 1 << ((n.bit_length() + 2)//3 + 1)
    while True:
        y = (2*x + n//(x*x))//3
        if y >= x:
            return x
        x = y

m = icbrt(c)
assert m**3 == c, "not a perfect cube"
print(bytes.fromhex(format(m, 'x')))   # b'PASS:quorum-5:END'
