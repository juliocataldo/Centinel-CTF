<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Blackout+Bridge" alt="Typing SVG" /></a>

</div>

# Blackout Bridge — PWN · JID-Pwn300 · Level 5 · 🔴 HARD

- **Status:** 🟠 PARTIAL (1/4) — Flag 1 accepted; Flag 2 blocked on the `duty` signed-cookie forgery (scheme never matched).
- **Points:** 200 / 2200
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}`; flags 1–2 plaintext)
- **Target:** `10.10.10.30` (lab, over VPN)
- **Prompt:** *boot2root — ports → low-priv user → `/home/user.txt` → `/root/root.txt`*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `8083,22022` | ✅ |
| 2 | Low privilege user | forge signed `duty` cookie for `/panel` (key material `build=4a21`, `lane=3`) | ❌ blocked |
| 3 | User flag | SSH :22022 → `/home/user.txt` | ⏳ pending |
| 4 | Root flag | `sudo -l` NOPASSWD misconfig → `/root/root.txt` | ⏳ pending |

---

## TL;DR

1. Two ports: a custom Python `BaseHTTPServer` app on `:8083` plus SSH on `:22022` (patched → decoy).
2. `/panel` is gated by a signed `duty` cookie; `/about`+`/health`+a 404 leak the signing material `build=4a21` and `lane=3` (hint: joined by hyphen → `4a21-3`).
3. The cookie is meant to be forgeable from those public values, but the exact (message, algo, encoding, layout) was never matched, so the foothold stayed blocked at Flag 2.

9th sibling of the JID boot2root series (cf. `EmbassyGate`, `AidShipments`, `CoastalRadar`, …). Same skeleton — 2 open ports (SSH high port + custom Python `BaseHTTPServer 0.6`), Flag1 = ports, Flag2 = theme user, Flag3 = `/home/user.txt`, Flag4 = root via sudo misconfig. Reported **Hard**: the foothold is a **signed-cookie gate** on `/panel`, not a file-read/RCE/SQLi. The signing material is leaked but the exact signing scheme was not matched.

> Flag format: `CTF{...}`. Every command was executed manually by the player against the box.

---

## 0. Connect

```bash
cd /home/felipebc2/repo/CTF/CentinelI
sudo wg-quick up ./team-71-player-a.conf
ping -c1 10.10.10.30
```

---

## Flag 1 — Open TCP ports ✅ (200 pts, accepted)

```bash
sudo nmap -sS -p- -T4 --max-retries 6 -Pn -n 10.10.10.30 -oN nmap-30-full.txt
sudo nmap -sC -sV -p 8083,22022 -Pn -n 10.10.10.30 -oN nmap-30-svc.txt
```
```
8083/tcp  open  http  BaseHTTPServer 0.6 (Python 3.11.2)   -- title "Blackout bridge"
22022/tcp open  ssh   OpenSSH 9.2p1 Debian 2+deb12u10
```
SSH 9.2p1 patched → not the vector. The Python app on :8083 is the attack surface.

**Flag 1 = `8083,22022`** ✅

---

## Flag 2 — Low privilege user ⏸️ BLOCKED (400 pts)

### App map (only GET supported; POST/HEAD/OPTIONS → 501)

| route | result |
|-------|--------|
| `/` | landing, links to `/about` and `/health` |
| `/about` | **hint:** *"The desk signs cookies with the build and the lane, joined by a hyphen."* |
| `/health` | `lane=3` |
| any unknown route (e.g. `/zzz`) | body `missing\nbuild=4a21` — **leaks `build=4a21`** |
| `/panel` | **403** `duty cookie required` ← the gated route / foothold |

### What we know for sure
- Cookie name = **`duty`** (403 body literally "duty cookie required").
- Leaked signing material: **`build=4a21`**, **`lane=3`** → hint says joined by hyphen → **`4a21-3`**.
- `/panel` returns the **same** `duty cookie required` for a missing cookie AND for any wrong value (`duty=operator-deadbeef`, `duty=`, `duty=%00`, malformed, etc.) → **no oracle**: invalid signature is indistinguishable from absent, and no traceback leaks (robust handler).
- Signing uses **public** values (build+lane) → the cookie is **meant to be forgeable** without a secret. That is the intended vuln.

### What we tried (all failed — do NOT repeat)
- `forge_duty.py` (648 tries): HMAC(key=`4a21-3` and `3-4a21`), algos md5/sha1/sha256, **hex** sig, payloads {operator, admin, on, yes, true, 1, duty, root, chief, lead, supervisor, controller, lane=3, lane-3, 3, operator-3, duty=1, onduty}, layouts `{p}-{s}` `{p}.{s}` `{p}|{s}` `{p}:{s}` `{s}` `{p}-{s}-{lane}`. → no hit.
- `forge_duty2.py` (336 tries): **plain hash** (md5/sha1/sha256) of `role-4a21-3`, `4a21-3-role`, `role-3`, `role`, and of `4a21-3` itself (payload-less); plus HMAC(key=`4a21-3`) with **base64** sig. Truncated-16 variants too. → no hit.
- No cookie-issuing endpoint exists (swept ~40 clock-in/duty/shift route names → all 404).

### Open hypotheses to try on resume (ranked)
1. **Signed string includes a role/username we haven't guessed.** Flag 2 IS a username — the duty payload may be the low-priv username (theme: a bridge "operator"/"keeper"/"warden"/"tender"/"watchman"). Pull a themed wordlist and re-forge with the *already-tested* schemes but those payloads.
2. **Different message layout:** sig over `lane=3` exactly (with `=`), or over `{role}\n{build}\n{lane}`, or key = `{build}` and message = `{lane}` (not concatenated), or key=`{lane}` msg=`{build}`.
3. **Sig encoding we skipped:** base64 of a *plain* hash (we only did base64 for HMAC), url-safe base64, or sig truncated to 8/32.
4. **Cookie carries fields the panel validates separately** (e.g. `duty={role}-{lane}-{sig}` where panel checks lane==3): re-derive sig over `{role}-{lane}` and append lane in the cookie.
5. **Re-read `/about` / `/health` for a second hint** (maybe a role name or the exact field order) — the phrasing "the build AND the lane" might mean the signed message is `build-lane` and the cookie prefix is the *role*: `duty={role}-{sig}` with `sig=H(key?, "4a21-3")`. Only the key/algo differs from what we tried.

### Resume command skeleton
```bash
# themed username list for the duty payload, then re-run the forge with those as payloads
python3 -I .../forge_duty.py   # edit PAYLOADS to bridge-operator usernames
```

**Flag 2 = PENDING**

---

## Flag 3 — User flag (600 pts) — PENDING
Once `/panel` opens (or SSH creds surface): SSH `-p 22022 <user>@10.10.10.30`, `cat /home/user.txt`. Confirm creds with `id` before submitting.

## Flag 4 — Root flag (1000 pts) — PENDING
Series ending: `sudo -n -l` → NOPASSWD wrapper that runs/sources a user-controlled file → `cat /root/root.txt` as root.

---

### Key takeaway / where to restart
The whole box hinges on forging the `duty` cookie. Signing inputs are public (`4a21`, `3`) so it IS forgeable — the exact (message, algo, encoding, layout) was never hit. Best next move: assume the payload is a **themed username** (Flag 2) and/or re-read `/about` for the precise field order before spraying again. Scripts: `forge_duty.py`, `forge_duty2.py`.
