from fractions import Fraction as F
p = 10007
desk = [(2, 1809), (5, 2457), (7, 3079)]
extra = (1, 1792)
assert all(p % d for d in range(2, int(p**.5) + 1))  # p prime

def lag(pts, x0, mod=None):
    t = F(0)
    for i, (xi, yi) in enumerate(pts):
        l = F(1)
        for j, (xj, _) in enumerate(pts):
            if i != j:
                l *= F(x0 - xj, xi - xj)
        t += yi * l
    if mod is None:
        return t
    return t.numerator * pow(t.denominator, -1, mod) % mod

f = lambda x: lag(desk, x, p)
a0 = f(0)
a2 = (f(1) + f(-1) - 2 * a0) * pow(2, -1, p) % p
a1 = (f(1) - a0 - a2) % p
assert all((a0 + a1 * x + a2 * x * x) % p == y for x, y in desk)
print("coeffs a0,a1,a2 =", a0, a1, a2)
print("Secret f(0) mod p =", a0)
print("f(1) =", f(1), "extra y =", extra[1], "match:", f(1) == extra[1])
print("90211 mod p =", 90211 % p)
print("integer Lagrange f(0) =", lag(desk, 0))
print("deg3 w/ extra, mod p f(0) =", lag(desk + [extra], 0, p))
for x, y in desk:
    m = (y - extra[1]) * pow(x - 1, -1, p) % p
    print("line extra+(%d,%d): slope=%d f(0)=%d" % (x, y, m, (extra[1] - m) % p))
