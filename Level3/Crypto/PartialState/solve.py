A, C, M = 1664525, 1013904223, 2**32
R = [1708, 3974, 196, 180, 3216, 4036]
step = lambda s: (A * s + C) % M
sols = []
for x in range(1 << 20):
    s0 = (R[0] << 20) | x
    s, ok = s0, True
    for r in R[1:]:
        s = step(s)
        if s >> 20 != r: ok = False; break
    if ok: sols.append(s0)
print("survivors:", len(sols))
for s0 in sols:
    s, rs = s0, []
    for _ in R: rs.append(s >> 20); s = step(s)
    print("state", s0, hex(s0), "readings", rs, rs == R)
    # s is now state after 6th reading's step (= state for 7th reading)
    s6 = s0
    for _ in range(5): s6 = step(s6)
    print("last state", s6, hex(s6), "next state", s, hex(s), "next reading", s >> 20)
# 642 check: line 1 interpretations
print("1708 as full state -> next>>20:", step(1708) >> 20, "| 1708<<20 ->", step(1708 << 20) >> 20)
print("reading 642 candidates among 1708-prefixed:", [s0 for s0 in sols if step(s0) >> 20 == 642])
