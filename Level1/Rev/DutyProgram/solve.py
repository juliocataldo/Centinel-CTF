#!/usr/bin/env python3
"""Emula a VM de bytecode do `desk` e extrai os 3 flags (Boat/Litres/Word).
Rode: python3 solve.py [caminho_do_desk]   (default: ./desk no mesmo dir)"""
import sys, pathlib

def load_program(path):
    data = pathlib.Path(path).read_bytes()
    # .rodata começa em file offset 0x2000; símbolo `program` em VA 0x2060 == offset 0x2060
    return data[0x2060:0x2088]  # 40 bytes do bytecode

def run(prog):
    number = [0] * 16          # r9: inteiros (16-bit)
    length = [0] * 16          # r11: tamanho de cada slot de text
    text   = [bytearray(16) for _ in range(16)]  # r10: slots de 16 bytes
    pc = 0
    while pc <= 0x27:
        op = prog[pc]
        if op == 1:            # number[dst] = imm16 LE ; pc+=4
            dst = prog[pc+1]; number[dst] = prog[pc+2] | (prog[pc+3] << 8); pc += 4
        elif op == 2:          # text[d] = prog[pc+3 : pc+3+n] ; length[d]=n ; pc+=3+n
            d = prog[pc+1]; n = prog[pc+2]
            text[d][:n] = prog[pc+3:pc+3+n]; length[d] = n; pc += 3 + n
        elif op == 3:          # xor length[d] bytes de text[d] com k ; pc+=3
            d = prog[pc+1]; k = prog[pc+2]
            for i in range(length[d]): text[d][i] ^= k
            pc += 3
        elif op == 4:          # number[a] = (number[a]+number[b]) & 0xffff ; pc+=3
            a = prog[pc+1]; b = prog[pc+2]
            number[a] = (number[a] + number[b]) & 0xffff; pc += 3
        elif op == 5:          # halt
            break
        else:
            raise SystemExit(f"opcode desconhecido {op} em pc={pc}")
    return number, length, text

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).with_name("desk"))
    number, length, text = run(load_program(path))
    boat = text[0][:length[0]].decode()
    litres = number[1]
    word = text[4][:length[4]].decode()
    print(f"Boat   = {boat!r}")
    print(f"Litres = {litres}")
    print(f"Word   = {word!r}")
    assert boat == "KITE" and litres == 52 and word == "maple", "trace divergiu do esperado"
    print("ok: trace confere")
