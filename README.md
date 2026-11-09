# Centinela Digital I -- CTF Writeups

Writeups and solve scripts from the **Centinela Digital I** CTF (Go Hacking), remote edition -- November 2026.

57 challenges across 8 progressive levels, covering reverse engineering, exploitation (boot2root), cryptography, forensics, miscellaneous, AI/LLM and blue team/SOC.

## Result

| Metric | Value |
|--------|-------|
| Placement | 3rd overall / 1st in Brazil (125 teams, 14 countries) |
| Score | 83,929 pts -- 312 flags -- Level 8 reached |

## Structure

```
LevelN/
  Category/
    ChallengeName/
      README.md      # challenge card (prompt, target, difficulty)
      WRITEUP.md     # full walkthrough, flag table, what didn't work
      solve.py       # automated solver (when applicable)
      <artifacts>    # binaries, captures, configs provided by the CTF
```

Each writeup follows a consistent template: TL;DR, step-by-step analysis, failed approaches and conclusions.

## Challenges by category

### Reverse Engineering (26 challenges -- 56/66 flags)

| Challenge | Level | Difficulty | Flags | Status |
|-----------|-------|------------|-------|--------|
| [Slip Checker](Level1/Rev/SlipChecker/) | 1 | Medium | 3/3 | Solved |
| [Duty Program](Level1/Rev/DutyProgram/) | 1 | Medium | 3/3 | Solved |
| [Pier Client](Level1/Rev/PierClient/) | 1 | Medium | 1/3 | Partial |
| [Handset Image](Level2/Rev/Handset/) | 2 | Medium | 2/2 | Solved |
| [Ledger Program](Level2/Rev/LedgerProgram/) | 2 | Medium | 2/2 | Solved |
| [Second Class](Level2/Rev/SecondClass/) | 2 | Medium | 2/2 | Solved |
| [License Checker](Level2/Rev/LicenseChecker/) | 2 | Medium | 2/2 | Solved |
| [Pier Scale](Level3/Rev/PierScale/) | 3 | Medium | 2/2 | Solved |
| [Rewritten Page](Level3/Rev/RewrittenPage/) | 3 | Medium | 2/2 | Solved |
| [Reset Image](Level3/Rev/ResetImage/) | 3 | Medium | 2/2 | Solved |
| [Refused Sample](Level3/Rev/RefusedSample/) | 3 | Hard | 3/3 | Solved |
| [Two Builds](Level4/Rev/TwoBuilds/) | 4 | Hard | 3/3 | Solved |
| [Packed Checker](Level4/Rev/PackedChecker/) | 4 | Hard | 2/2 | Solved |
| [Parser And Slip](Level4/Rev/ParserAndSlip/) | 4 | Hard | 3/3 | Solved |
| [Cipher Slip](Level4/Rev/CipherSlip/) | 4 | Hard | 0/3 | Unsolved |
| [Three Fields](Level4/Rev/ThreeFields/) | 4 | Hard | 3/3 | Solved |
| [Mid Instruction](Level4/Rev/MidInstruction/) | 4 | Hard | 2/2 | Solved |
| [Native Method](Level4/Rev/NativeMethod/) | 4 | Hard | 2/2 | Solved |
| [Command Tape](Level4/Rev/CommandTape/) | 4 | Hard | 0/3 | Unsolved |
| [Exception Path](Level4/Rev/ExceptionPath/) | 4 | Hard | 2/2 | Solved |
| [Constructor](Level4/Rev/Constructor/) | 4 | Hard | 3/3 | Solved |
| [Signal Handler](Level4/Rev/SignalHandler/) | 4 | Hard | 3/3 | Solved |
| [Linked Libraries](Level4/Rev/LinkedLibraries/) | 4 | Hard | 3/3 | Solved |
| [Hidden Tally](Level4/Rev/HiddenTally/) | 4 | Hard | 3/3 | Solved |
| [Go Checker](Level4/Rev/GoChecker/) | 4 | Hard | 0/2 | Unsolved |
| [Gadget Chain](Level4/Rev/GadgetChain/) | 4 | Hard | 3/3 | Solved |

### Pwn / Boot2Root (17 challenges -- 49/68 flags)

| Challenge | Level | Difficulty | Flags | Pts | Status |
|-----------|-------|------------|-------|-----|--------|
| [Night-Watch Roster](Level1/Pwn/NightWatchRoster/) | 1 | Easy | 1/4 | 100 | Partial |
| [Harbor Watch](Level1/Pwn/HarborWatch/) | 1 | Easy | 4/4 | 725 | Solved |
| [Escort Convoy](Level1/Pwn/EscortConvoy/) | 1 | Easy | 4/4 | 812 | Solved |
| [Visitor Badges](Level1/Pwn/VisitorBadges/) | 1 | Easy | 4/4 | 1,025 | Solved |
| [Radio Shack](Level1/Pwn/RadioShack/) | 1 | Medium | 4/4 | 1,400 | Solved |
| [Coastal Radar](Level1/Pwn/CoastalRadar/) | 1 | Medium | 1/4 | 175 | Partial |
| [Embassy Gate](Level1/Pwn/EmbassyGate/) | 1 | Medium | 4/4 | 1,800 | Solved |
| [Aid Shipments](Level4/Pwn/AidShipments/) | 4 | Medium | 4/4 | 1,700 | Solved |
| [Blackout Bridge](Level5/Pwn/BlackoutBridge/) | 5 | Hard | 1/4 | 200 | Partial |
| [Radio Spectrum](Level5/Pwn/RadioSpectrum/) | 5 | Hard | 4/4 | 2,400 | Solved |
| [Convoy Orders](Level5/Pwn/ConvoyOrders/) | 5 | Hard | 4/4 | 2,600 | Solved |
| [Liaison Switchboard](Level5/Pwn/LiaisonSwitchboard/) | 5 | Hard | 4/4 | -- | Solved |
| [Civil Night Shift](Level5/Pwn/CivilNightShift/) | 5 | Hard | 1/4 | 275 | Partial |
| [Radar Mesh](Level6/Pwn/RadarMesh/) | 6 | Insane | 4/4 | 3,344 | Solved |
| [Command Post](Level6/Pwn/CommandPost/) | 6 | Insane | 1/4 | 350 | Partial |
| [Fusion Cell](Level7/Pwn/FusionCell/) | 7 | Insane | 2/4 | 700 | Partial |
| [Treaty Orders](Level8/Pwn/TreatyOrders/) | 8 | Insane | 2/4 | -- | Partial |

### Cryptography (6 challenges -- 13/13 flags)

| Challenge | Level | Difficulty | Flags | Status |
|-----------|-------|------------|-------|--------|
| [Small Modulus](Level1/Crypto/SmallModulus/) | 1 | Easy | 3/3 | Solved |
| [Two AES Blobs](Level2/Crypto/TwoAESBlobs/) | 2 | Easy | 3/3 | Solved |
| [Fixed Distance](Level3/Crypto/FixedDistance/) | 3 | Hard | 2/2 | Solved |
| [Partial State](Level3/Crypto/PartialState/) | 3 | Hard | 2/2 | Solved |
| [Quadratic Shares](Level4/Crypto/QuadraticShares/) | 4 | -- | 1/1 | Solved |
| [Smooth Order](Level6/Crypto/SmoothOrder/) | 6 | Hard | 2/2 | Solved |

### Forensics (4 challenges -- 8/8 flags)

| Challenge | Level | Difficulty | Flags | Pts | Status |
|-----------|-------|------------|-------|-----|--------|
| [Long Capture](Level8/Forensics/LongCapture/) | 8 | Hard | 2/2 | 2,320 | Solved |
| [Large Database](Level8/Forensics/LargeDatabase/) | 8 | Hard | 2/2 | 2,140 | Solved |
| [Large Disk Image](Level8/Forensics/LargeDiskImage/) | 8 | Hard | 2/2 | -- | Solved |
| [Large System Hive](Level8/Forensics/LargeSystemHive/) | 8 | Hard | 2/2 | 2,800 | Solved |

### Misc (2 challenges -- 6/6 flags)

| Challenge | Level | Difficulty | Flags | Pts | Status |
|-----------|-------|------------|-------|-----|--------|
| [Duty Repository](Level3/Misc/DutyRepository/) | 3 | Hard | 3/3 | 980 | Solved |
| [Radio Note](Level7/Misc/RadioNote/) | 7 | Hard | 3/3 | 980 | Solved |

### AI / LLM (1 challenge -- 0/5 flags)

| Challenge | Level | Difficulty | Flags | Status |
|-----------|-------|------------|-------|--------|
| [AI300](Level3/AI/AI300/) | 3 | Medium | 0/5 | Unsolved |

### Blue Team / SOC (1 challenge -- 0/11 flags)

| Challenge | Level | Difficulty | Flags | Status |
|-----------|-------|------------|-------|--------|
| [SOC700](Level8/BlueTeam/SOC700/) | 8 | Hard | 0/11 | Unsolved |

## Techniques covered

- **Reverse Engineering:** static analysis (objdump, Ghidra), stack strings, ELF/PE/JVM/.NET binaries, WASM, packing, signal handlers, gadget chains, Go binaries
- **Pwn / Boot2Root:** port scanning, web enumeration, credential derivation, SSH exploitation, SUID abuse, sudo misconfigurations, command injection, IDOR, header-based auth bypasses
- **Cryptography:** RSA (small modulus, smooth order), AES (ECB/CBC), related-message attacks, PRNG state recovery, secret sharing
- **Forensics:** PCAP analysis, database extraction, disk image forensics, Windows registry hive analysis
- **Misc:** git history analysis, steganography (audio)

## Tools

Primary toolkit used throughout the competition:

`nmap` `curl` `python3` `objdump` `gdb` `Ghidra` `strings` `file` `binwalk` `xxd` `openssl` `wireshark/tshark` `volatility` `sqlitebrowser` `hashcat`

## Notes

- Platform credentials and public infra hostnames were anonymized (`<HOST>`, `<USER>`)
- Lab IPs (`10.10.10.0/24`), challenge-derived passwords and flags were kept as-is
- Level 8 forensics artifacts (~1 GB each) are not included; their sha256 hashes are in each writeup
