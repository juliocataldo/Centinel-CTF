# Treino

5 challenges selecionados para praticar offline. Todos os artefatos estao incluidos -- nenhuma infra remota necessaria.

## Challenges

| # | Challenge | Categoria | Dificuldade | Artefato | O que voce vai praticar |
|---|-----------|-----------|-------------|----------|------------------------|
| 1 | [Small Modulus](Level1/Crypto/SmallModulus/) | Crypto | Easy | `seal.txt` | RSA com modulo pequeno, fatoracao |
| 2 | [Slip Checker](Level1/Rev/SlipChecker/) | Reverse | Medium | `slip` (ELF) | Analise estatica, stdin checker |
| 3 | [Two AES Blobs](Level2/Crypto/TwoAESBlobs/) | Crypto | Easy | `desk.txt` | AES-ECB, identificacao de modo de cifra |
| 4 | [Duty Program](Level1/Rev/DutyProgram/) | Reverse | Medium | `desk` (ELF) | Bytecode VM customizada, emulacao |
| 5 | [Radio Note](Level7/Misc/RadioNote/) | Misc | Hard | `pier-note.wav` | Demodulacao de audio (Bell 202 AFSK) |

## Como usar

1. Abra o `README.md` de cada challenge para ver o enunciado
2. Analise o artefato com suas ferramentas (objdump, Ghidra, python3, Audacity, etc.)
3. Encontre as flags no formato `CTF{...}` ou plaintext conforme indicado

## Toolkit sugerido

`file` `strings` `xxd` `objdump` `gdb` `Ghidra` `python3` `Audacity` `openssl` `CyberChef`

## Gabarito

A pasta [`gabarito/`](gabarito/) contem o writeup completo e o script de solucao (`solve.py`) de cada challenge. Consulte apenas depois de tentar resolver.
