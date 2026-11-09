<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Radio+Note" alt="Typing SVG" /></a>

</div>

# Radio Note — MISC · JID-Misc303 · Level 7 · 🔴 HARD

- **Status:** ✅ SOLVED (3/3) — all three chained flags recovered from the AFSK burst.
- **Points:** 980 / 980 (180 + 300 + 500)
- **Flags:** Boat → Berth → Litres (chained, plaintext)
- **Attachment:** `pier-note.wav` (RIFF WAVE, PCM 16-bit mono, 48 kHz, ~10 s)
- **sha256:** `091c9043b62a00dbbec0b98740433deb6e19c4a0a7d7dadffe1f9943bb28c52e`
- **Prompt:** *"A radio note from the pier. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `ANA` | ✅ |
| 2 | Berth | `4` | ✅ |
| 3 | Litres | `67` | ✅ |

---

## TL;DR

The WAV has three layers. Two of them are decoys and both say `ROCA / 9 / 240`. The real answers sit in a half-second Bell 202 AFSK burst at the very end: `ANA / 4 / 67`.

## Layer 1: RIFF metadata (decoy)

```bash
strings -n 8 pier-note.wav | grep -iE 'boat|INFO|ICMT'
```

A `LIST/INFO` chunk holds an `ICMT` comment:

```
Pier desk. Boat ROCA. Berth 9. Civil litres 240.
```

This is plausible but not authoritative. The question asks for the boat carried in the *tone page*, and this is metadata.

## Layer 2: Speech (decoy plus pointer)

The first ~9.2 s are a TTS voice. A local Whisper transcription gives:

```
Pier desk. Boat ROCA. Berth nine. Civil litres 240. The tones are at 1200.
```

The voice repeats the decoy, but its last sentence points to the real layer: tones at 1200 (Hz / baud).

## Layer 3: Tone page (authoritative)

The spectrogram (`sox pier-note.wav -n spectrogram -o spec.png`) shows a short, noise-like burst after the speech, at **9.78 s to 10.36 s**. Measuring the tones in it:

- Two tones: **1200 Hz (mark)** and **2200 Hz (space)**
- Symbol length 40 samples at 48 kHz = **1200 baud**

That is **Bell 202 AFSK**, the classic pager/APRS modem tone. It is the "tone page".

### Demodulation

For each 1/1200 s symbol window, compare the signal's energy at 1200 Hz and 2200 Hz using a single-bin DFT. The bit is mark (1) if 1200 Hz wins, otherwise space (0).

The bitstream starts with an `0xFF` preamble (idle marks). It decodes as plain **async 8N1** serial: a 0 start bit, 8 data bits LSB first, and a 1 stop bit. The burst is 700 bits (70 frames), and every frame has valid start and stop bits.

```python
sr, x = wavfile.read(wav); x = x.astype(float)
nz = first sample after 9.5 s with |x| > 100           # burst start
b  = sr / 1200                                         # samples per bit
bit = 1 if E(1200) > E(2200) else 0                    # per window
frames = [bits[i:i+10] for i in range(0, len(bits), 10)]
byte = int(''.join(map(str, f[1:9][::-1])), 2)         # LSB-first payload
```

The full script is `solve.py`: `python -I solve.py pier-note.wav`, needs numpy and scipy.

### Decoded payload

```
\xff\xff\xff
boat ANA
berth 4
civil 40
civil 15
civil 12
military 80
check 67
\xff\xff
```

## Answers

| Flag   | Answer | Reasoning |
|--------|--------|-----------|
| Boat   | `ANA`  | `boat ANA` line of the tone page |
| Berth  | `4`    | `berth 4` line of the tone page |
| Litres | `67`   | Civil litres only: 40 + 15 + 12 = 67, matching the `check 67` line. The `military 80` entry is excluded. |

## Pitfalls

- The metadata and the voice agree with each other (`ROCA`, `9`, `240`). That agreement is bait, so don't submit it.
- The `check` line is a checksum for the sum: it confirms which entries count (civil only, not 40+15+12+80 = 147).
- If the burst is decoded MSB-first or without stripping the start and stop bits, the output is garbage. Look for the 10-bit framing (`0 xxxxxxxx 1`).

## Tools

`strings`, `sox` (spectrogram), Whisper (speech transcript), and Python with numpy and scipy (a hand-rolled Goertzel-style Bell 202 demodulator). `minimodem --rx 1200` should also decode the burst, since it handles Bell 202 with 8N1 framing.
