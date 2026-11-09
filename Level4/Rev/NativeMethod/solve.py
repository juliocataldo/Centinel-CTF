import ctypes, io, struct, sys, zipfile

apk = zipfile.ZipFile(sys.argv[1])
so = apk.read('lib/x86_64/libdesk.so')

# table @ 0x4020 (JNINativeMethod): {"accept", "(Ljava/lang/String;I)I", native_accept @ 0x1109}
# native_accept @ 0x1138: strlen(s) == 4 and rol(s[k], 4) ^ (k + 0x51) == want[k]; then channel == 6
WANT = 0x2000  # want.0 in .rodata, vaddr == file offset
want = so[WANT:WANT + 4]
ror4 = lambda b: ((b >> 4) | (b << 4)) & 0xff
callsign = bytes(ror4(want[k] ^ (k + 0x51)) for k in range(4)).decode()
assert so[0x1153:0x1156] == b'\x83\xfd\x06'  # cmp ebp, 6
channel = so[0x1155]

assert (callsign, channel) == ('HERN', 6)
print('Callsign =', callsign)
print('Channel  =', channel)

# optional live check: python3 -I solve.py desk.apk /path/to/extracted/libdesk.so
if len(sys.argv) > 2:
    lib = ctypes.CDLL(sys.argv[2])
    base = ctypes.cast(lib.JNI_OnLoad, ctypes.c_void_p).value - 0x1170
    f = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int)(base + 0x1109)
    for s, c in ((b'HERN', 6), (b'ROCA', 9), (b'HERN', 9)):
        print(s.decode(), c, '->', f(s, c))
    assert f(b'HERN', 6) == 1 and f(b'ROCA', 9) == 0
