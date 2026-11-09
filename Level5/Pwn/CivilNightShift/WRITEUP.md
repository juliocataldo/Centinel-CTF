<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Civil+Night+Shift" alt="Typing SVG" /></a>

</div>

# Civil Night Shift — PWN · JID-Pwn304 · Level 5 · 🔴 HARD

- **Status:** 🟠 PARTIAL (1/4) — Flag 1 accepted; Flag 2 blocked (`civil` submitted and rejected; real username not recovered).
- **Points:** 275 / 2975
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}`; flags 1–2 plaintext)
- **Target:** `10.10.10.34` (lab, over VPN). No downloadable artifact.
- **Prompt:** *boot2root — ports → low-priv user → `/home/user.txt` → `/root/root.txt`*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `22,8808` | ✅ |
| 2 | Low privilege user | desk token `a91c0e44b217` → archive token `712b44e0c19a4`; consumer/username not found | ❌ blocked |
| 3 | User flag | SSH :22 → `/home/user.txt` | ⏳ pending |
| 4 | Root flag | `sudo -l` NOPASSWD → `/root/root.txt` | ⏳ pending |

---

## TL;DR

1. SSH on `:22` (patched → decoy) and a custom Python `BaseHTTPServer` app "Night shift" on `:8808`.
2. `POST /shift bureau=civil` returns the desk token `a91c0e44b217`; the calendar recipe ("desk token reversed, plus the shift index 4") yields archive token `712b44e0c19a4`.
3. The archive token has no discoverable consumer, and `civil` is rejected as the username — Flag 2 (the real low-priv user) was never recovered, so the chain stopped there.

10th sibling of the JID boot2root series (cf. `BlackoutBridge` .30, `RadioSpectrum` .31, `ConvoyOrders` .32, `AidShipments`). Same 4-flag skeleton (ports → low-priv user → `/home/user.txt` → `/root/root.txt` via sudo). The foothold app is fully mapped but the web→SSH credential bridge was not solved.

> Flag format: `CTF{...}`. Every command was executed manually by the player against the box.

---

## 0. Connect

```bash
cd /home/felipebc2/repo/CTF/CentinelI
sudo wg-quick up ./team-71-player-a.conf
ping -c1 10.10.10.34
```

---

## Flag 1 — Open TCP ports ✅ (275 pts, ACCEPTED)

```bash
sudo nmap -sS -p- --min-rate 2000 -T4 -Pn -n 10.10.10.34 -oN nmap-34-full.txt
sudo nmap -sC -sV -p 22,8808 -Pn -n 10.10.10.34 -oN nmap-34-svc.txt
```
```
22/tcp   open  ssh   OpenSSH 9.2p1 Debian 2+deb12u10   # patched → NOT the vector
8808/tcp open  http  BaseHTTP/0.6 Python/3.11.2        # app "Night shift"  (nmap mislabels it ssports-bcast?)
```
- Only 2 ports open; all others returned RST (closed, not filtered) → recon reliable.
- **Note vs siblings:** SSH is on the standard port **22** here, not a high port. The app port is **8808**.
- 8808 returns a Python `BaseHTTPServer` 400 error on a non-HTTP line (`help`) → it is HTTP, nmap just couldn't fingerprint it.

**Flag 1 = `22,8808`** ✅ (submit in ascending order, comma-separated, plaintext)

---

## Flag 2 — Low privilege user ⏸️ BLOCKED (500 pts — "Submit the low privilege username. Format: plaintext.")

### Full app map (8808 — only `do_GET` + `do_POST` implemented; every other method → `501`)

| Route | Method | Behaviour |
|-------|--------|-----------|
| `/` | GET | Landing. Title "Night shift". Body: **"POST bureau to /shift. Calendar at /shift/calendar."** |
| `/shift` | POST | Reads **only** the `bureau` field. `bureau=civil` → `a91c0e44b217` (`text/plain`, 12 bytes = the **desk token**). Any other value → `no`. |
| `/shift/calendar` | GET | **"Shift index is 4. Archive tokens are the desk token reversed, plus the shift index."** |
| anything else | — | `no` (404, 1147-byte HTML "no" page) |

### What is confirmed solid
- **`civil` is the only valid bureau** (fuzzed ~30 themed names by hand + a generated 184-word themed list → only `civil` returns a token).
- Desk token is **stable** (`a91c0e44b217` for 40+ min, not rotating, not per-connection).
- `POST /shift` reads **only** `bureau`; every extra field (archive, token, key, code, pass, sig, …) is ignored — `bureau=civil` short-circuits and returns the desk token regardless.
- Derived **archive token** per the calendar recipe: `reverse("a91c0e44b217") + "4"` = **`712b44e0c19a4`**.

### The blocker
The archive token has **no consumer anywhere**:
- Not a valid `bureau` in **any** transformation (tested ~119 forms as `bureau`: char-reverse / byte-reverse / nibble-swap × index append/prepend/`04`/none × upper/lowercase, numeric hex `+4`, **and** md5/sha1/sha256[:12/:16/full] of every sensible input — all `no`).
- Not consumed as any POST field, GET query, URL path, or cookie (swept `/`, `/shift`, `/shift/calendar` with param names archive/token/log/read/view/… and cookie names archive/token/desk/shift/duty/session/auth — nothing changes the response).
- No hidden routes (curated ~55 themed route names at `/` and `/shift/` → all `no`; no wordlists installed on this box to run a large `ffuf`).

SSH (`publickey,password` offered) with user **`civil`** was tried against every finite form of the recipe (reverse, reverse+4, 4+reverse, byte-reverse ±4, nibble-swap, hex `+4`, double-reverse `a91c0e44b2174`, zero-pad, uppercase) → **all "Permission denied."** Token-as-username swaps (`712b44e0c19a4@`, `a91c0e44b217@`, with every token as password) also denied.

**`civil` was submitted as Flag 2 on the platform and REJECTED** → the low-priv username is **not** `civil`. It must be revealed by correctly consuming the archive token (as in the siblings, where the solved app dumps `ssh <user> / <pass>`), but that consumption point was not found.

**Flag 2 = PENDING** (username unknown; SSH password is almost certainly the archive token `712b44e0c19a4`, user is the missing piece).

---

## Flag 3 — User flag (800 pts) — PENDING
Once creds surface: `ssh <user>@10.10.10.34 'cat /home/user.txt'` (or `cat user.txt`). Confirm with `id` before submitting.

## Flag 4 — Root flag (1400 pts) — PENDING
Series ending: `sudo -n -l` → NOPASSWD python wrapper giving arbitrary file read / source / HMAC bypass as root → `/root/root.txt`.

---

## Where to restart (ranked hypotheses)

1. **Find the archive-token consumer / real username.** The recipe exists to be *used*; in every sibling the solved app prints the SSH creds. Re-read the calendar wording for an exact field/endpoint we normalised away. Consider that the archive token might be the SSH **password** for a user whose name is a themed word we didn't hit with that exact password (`712b44e0c19a4`): try a proper username wordlist (install seclists / `names.txt`) with password fixed to `712b44e0c19a4`, user list = common Debian/CTF accounts + maritime/desk/guard theme.
2. **The desk token may be per-bureau and `civil` is a decoy key.** Re-fuzz `bureau` with a *large* wordlist (seclists `raft-*-words`) — a second bureau whose name is the real username would make everything click. (No wordlists were installed locally during the session; that blocked a proper fuzz.)
3. **Re-read the recipe literally once more.** "the desk token reversed, plus the shift index" — if `reverse+4` is right as the *password*, the only remaining unknown is the username; focus energy there, not on more token transforms (that space is exhausted).
4. **Low-priv username might be given out-of-band** (the VPN email / platform page) rather than by the app — worth checking.
