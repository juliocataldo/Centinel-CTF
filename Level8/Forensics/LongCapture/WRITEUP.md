<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Long+Capture" alt="Typing SVG" /></a>

</div>

# Long Capture — FORENSICS · JID-For400 · Level 8 · 🔴 HARD

Artifact not included in the repo (≈1 GB); sha256 below.

- **Status:** ✅ SOLVED (2/2) — found the overlapping same-seq segment on the duplicated form.
- **Points:** 2320 / 2320 (720 + 1600)
- **Flags:** Account → Code (chained, plaintext)
- **Attachment:** `form.pcap` (pcap, Ethernet, snaplen 65535, 1073744814 bytes, 531997 packets, 531.96 s)
- **sha256:** `893170c37141c7a850689ff974c32d989f424bcef09db32f7b1c147ef1c02ce0`
- **Prompt:** *"A long capture of forms posted to the desk. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Account | `a.ramos` | ✅ |
| 2 | Code | `osprey` | ✅ |

---

## TL;DR

Every packet is raw TCP from `10.10.4.10` to `10.10.4.20:80`. Each payload is a form, `account=<x>\ncode=<y>\n` padded with `P`. Of about 156k forms, the only exact duplicate is `a.ramos` / `66120`, posted in frame 4 and again in frame 298576. The later copy is on port 25000. One millisecond after it, frame 298577 resends the **same sequence number (seq=1)** on the same connection with different bytes: `n.vale` / `osprey`.

- **Account:** the later copy as first received is `a.ramos`. That is what Wireshark's reassembly keeps.
- **Code:** the code on that copy is the one carried by the conflicting resend, **`osprey`**. The plain value `66120` is rejected.

## What the capture contains

`capinfos` and a raw walk of every pcap record (ethertype, IP header, TCP header, checksums) find nothing unusual. All frames are IPv4/TCP with valid checksums. There are no IP options, TCP options, fragments, Ethernet trailers or urgent data, and the file is not truncated (0 leftover bytes after the last record). Each connection is a SYN, a SYN/ACK, an ACK, then one or more 1100-byte or 8000-byte data segments. There is no HTTP framing.

| Kind | Segments | Content |
|------|----------|---------|
| Filler | 125368 x 8000 B | `account=uNNNNNN`, unique account and code, each posted once |
| Flood | 30505 x 1100 B | `c.mendes` / `44821`, one connection (port 21000), advancing seq. One stream, not "twice" |
| Special | 5 x 1100 B | See below |

The special forms:

| Frame | Time (epoch) | Src port | Seq | Account | Code | Note |
|-------|--------------|----------|-----|---------|------|------|
| 4      | 1710432000.003 | 20000 | 1 | a.ramos | 66120  | first copy |
| 8      | 1710432000.007 | 20001 | 1 | n.vale  | 66120  | decoy |
| 12     | 1710432000.011 | 20002 | 1 | h.nunes | osprey | decoy |
| 298576 | 1710432298.553 | 25000 | 1 | a.ramos | 66120  | **later copy** |
| 298577 | 1710432298.554 | 25000 | 1 | n.vale  | osprey | same connection, same seq, different bytes (tshark: "suspected retransmission") |

## Finding the duplicate

Grouping all forms by the full `(account, code)` pair gives exactly one pair with count 2: `a.ramos` / `66120` (frames 4 and 298576). Grouping by account alone or by code alone is ambiguous:

- `a.ramos` and `n.vale` both appear twice.
- `66120` appears three times.

So the intended key is the whole form. The later copy is the port 25000 connection, and its account is **`a.ramos`**.

## The overlapping segment

The port 25000 connection carries two 1100-byte segments at seq=1. Wireshark's reassembly (Follow TCP Stream) keeps the first, so it shows only `a.ramos` / `66120` and labels frame 298577 as a retransmission. A "retransmission" with different bytes is not a real retransmission. It is the planted twist on the later copy. The Code flag asks for the code on that copy, and the conflicting segment carries `osprey`. `osprey` is also the only non-numeric code in the whole capture, which suggests it was planted on purpose.

## Solve

Decode the port 25000 conversation:

```bash
tshark -r form.pcap -Y 'tcp.port==25000 && tcp.len>0' -T fields -e frame.number -e tcp.seq -e tcp.payload \
  | python3 -c 'import sys; [print(f"frame={n} seq={s} ->", bytes.fromhex(p).decode().rstrip("P").replace(chr(10)," ")) for n,s,p in (l.split() for l in sys.stdin)]'
```

```
frame=298576 seq=1 -> account=a.ramos code=66120
frame=298577 seq=1 -> account=n.vale code=osprey
```

`solve.py` groups every form by `(account, code)` and prints every non-filler group with its count and frames. Its input is a full field dump, about 2 GB:

```bash
tshark -r form.pcap -T fields -e frame.number -e tcp.srcport -e tcp.seq -e tcp.payload > all.tsv
python3 -I solve.py all.tsv
```

## Answers

| Flag    | Answer    | Reasoning |
|---------|-----------|-----------|
| Account | `a.ramos` | Only exact duplicate form. The later copy (port 25000, frame 298576) as first received |
| Code    | `osprey`  | Carried by the same-seq conflicting segment on that copy (frame 298577) |

## Pitfalls

- `66120`, the code literally in both `a.ramos` copies, is **rejected**. The Code flag depends on the overlapping segment, not on the visible form.
- `n.vale`, the account in the overlapping segment, is **not** the Account answer. The two flags take different halves of the conflict.
- Follow TCP Stream and Export Objects hide frame 298577 completely: there is no HTTP, and the reassembly keeps the first copy. Dump `tcp.payload` per frame instead.
- Port reuse across the ~156k connections makes tshark mark many filler segments as "suspected retransmission". That label alone is noise. Only a same-seq segment with *different* bytes matters.
- The `c.mendes` flood is the most-repeated form, but it is one connection, not a form posted twice.
- 1 GiB: avoid repeated full passes. A raw Python walk of the pcap records (16-byte record headers) is faster than tshark and checks checksums and headers in the same pass.

## Tools

`capinfos`, `tshark` (field export of `tcp.payload`), and Python (a raw pcap record walker for header and checksum checks, and grouping by `(account, code)`).
