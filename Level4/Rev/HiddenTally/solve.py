# Recovered from desk.pyc (CPython 3.11). The module marshals an obfuscated code
# `blob` (each byte XOR 61) and exec()s it; the hidden tally is the inner check():
#
#   def check(boat, word, litres):
#       rows = [(1,220,0),(1,150,0),(1,80,120),(2,900,0),(1,140,0),(1,110,0)]  # (side,amt,mark)
#       kept = [r[1] for r in rows if r[0]==1 and r[2]==0]
#       total = sum(kept)//10
#       name  = chr(83)+chr(65)+chr(73)+chr(76)                # "SAIL"
#       cloth = chr(108)+chr(105)+chr(110)+chr(101)+chr(110)   # "linen"
#       return boat==name and word==cloth and litres==total
#
# This script reproduces that tally and asserts, independent of the pyc version.

rows = [(1,220,0),(1,150,0),(1,80,120),(2,900,0),(1,140,0),(1,110,0)]
kept = [r[1] for r in rows if r[0] == 1 and r[2] == 0]
total = sum(kept) // 10
boat  = ''.join(map(chr, (83, 65, 73, 76)))
word  = ''.join(map(chr, (108, 105, 110, 101, 110)))

assert (boat, word, total) == ('SAIL', 'linen', 62), (boat, word, total)
print('Boat   =', boat)
print('Word   =', word)
print('Litres =', total)
