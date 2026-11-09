import sys

# main compares the low byte of mix_at(buf, k) for k = 0..9, buf = boat(4) | berth(1) | word(5).
# Checks at 0x1398..0x1400: h0..h4 direct, h5 direct, h5+h6, h6^h7, h8, h9.
h = [0x3c, 0x30, 0x36, 0x0a, 0x14, 0x0a]
h.append((0x49 - h[5]) & 0xff)
h.append(0x7e ^ h[6])
h += [0x8b, 0x11]


def mix_at(buf, n):  # mix_at @ 0x1179
    eax = 0x35
    for k in range(n + 1):
        eax = (eax * 2) ^ ((13 * k) ^ buf[k])
    return eax & 0xff


prev, buf = 0x35, bytearray()
for k, hk in enumerate(h):
    buf.append((hk ^ (prev * 2)) & 0xff ^ (13 * k))
    prev = hk

assert all(mix_at(buf, k) == h[k] for k in range(10))
boat, berth, word = buf[:4].decode(), buf[4:5].decode(), buf[5:].decode()
print('Boat  =', boat)
print('Berth =', berth)
print('Word  =', word)
