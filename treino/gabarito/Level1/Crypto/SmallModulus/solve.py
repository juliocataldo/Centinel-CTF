
n, e = 988027, 65537
cts = {"boat": 86874, "word": 452946, "litres": 626309}
p = next(i for i in range(2, n) if n % i == 0)
q = n // p
d = pow(e, -1, (p - 1) * (q - 1))
print("p", p, "q", q, "d", d)


def b26(m, w, off):
    s = []
    for _ in range(w):
        s.append(m % 26); m //= 26
    return "".join(chr(65 + x - off) if 0 <= x - off < 26 else "?" for x in s[::-1]), m


for k, c in cts.items():
    m = pow(c, d, n)
    print(k, "m =", m, hex(m), m.to_bytes((m.bit_length() + 7) // 8, "big"))
    for off in (0, 1):
        print("  b26 A=%d w4:" % off, b26(m, 4, off), " w6:", b26(m, 6, off))
