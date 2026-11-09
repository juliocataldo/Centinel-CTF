<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Coastal+Radar" alt="Typing SVG" /></a>

</div>

# Coastal Radar — PWN · JID-Pwn202 · Level 1 · 🟡 MEDIUM

- **Status:** 🟠 PARTIAL (1/4) — Flag 1 (ports `2222,8448`) accepted; Flag 2 blocked on the HMAC-gated web login; flags 3–4 locked behind the foothold.
- **Points:** 175 / 1600 (ports 175 · user 275 · user flag 450 · root 700)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}` for the file flags)
- **Target:** `10.10.10.22` (lab, over WireGuard VPN)
- **Prompt:** *"Radar calibration" — boot2root chain.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2222,8448` | ✅ |
| 2 | Low privilege user | blocked on HMAC-gated `/login` forge | ❌ |
| 3 | User flag | not reached (locked behind foothold) | ⬜ |
| 4 | Root flag | not reached (locked behind user flag) | ⬜ |

---

## TL;DR

1. `nmap` → `2222,8448`; the `:8448` Python HTTP app has `POST /login` (`u`,`p`) and `/admin` sharing one credential validator; `/docs/protocol.txt` leaks HMAC key `radar18`.
2. Auth needs the correct `u`+`p`; `p` is some HMAC under `radar18`, but the signed message/encoding is unknown and no sweep has forged a valid `p`.
3. Flag 1 accepted; Flag 2 blocked after exhaustive key/algo/encoding/delivery sweeps (all denied). Next: curl-based username sweep; hunt a valid (msg, MAC) pair to enable hash length-extension.

6th sibling of the JID boot2root series (`NightWatchRoster`, `HarborWatch`, `EscortConvoy`, `VisitorBadges`, `RadioShack`). Same skeleton: 2 open ports (SSH high port + Python `BaseHTTPServer` HTTP), Flag1 = open ports, Flag2 = theme-derived username revealed by the foothold, Flag3 = `user.txt`, Flag4 = `root.txt` via sudo misconfig. The "Medium" twist here is a **crypto auth step** (HMAC) on the web app — not yet broken.

> Flag format: `CTF{...}` (case-sensitive, underscores). Claude never touches the target; all commands below are run **manually by the player**.

---

## 0. Connect

```bash
wg-quick up team71-player-a && ping -c1 10.10.10.22
```

---

## Recon — Flag 1: Open TCP ports ✅ (+175)

```bash
sudo nmap -sS -p- -T4 --max-retries 6 10.10.10.22 -oN nmap-22-full.txt   # ~5 min over VPN; reliable (no high --min-rate)
sudo nmap -sC -sV -p 2222,8448 10.10.10.22 -oN nmap-22-svc.txt
```
```
2222/tcp open ssh   OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)   # same build as every sibling
8448/tcp open http  BaseHTTP/0.6 Python/3.11.2  (nmap guessed "matrix-fed" by port number; it is plain HTTP, not TLS)
```
**Flag 1 = `2222,8448`** ✅ (open only, ascending, comma-separated).

---

## Foothold — Flag 2: Low privilege user  ⛔ BLOCKED

### Attack-surface map (8448, confirmed)
| Request | Response |
|---|---|
| `GET /` | 200 — "Radar calibration" page; form `POST /login` with fields **`u`,`p`**; link `/docs/protocol.txt` |
| `GET /docs/protocol.txt` | 200 — the HMAC hint (below) |
| `GET /docs/<anything else>` | "no" (whitelist; **traversal blocked** — `/docs/../../../etc/passwd` → "no") |
| `POST /login u=&p=` (wrong) | 403 — body **"denied"** |
| `GET /admin` | 403 — body **"admin only"** |
| `POST /admin u=admin&p=x` | 403 — body **"denied"** (⚠️ same validator as `/login`) |
| everything else | 404 — body "no" |

**Key fact:** `/admin` and `/login` share the same credential check. `GET /admin` just says "admin only"; authenticating is a **POST with the correct `u`+`p`** (no cookie is ever set — `GET /` sends no `Set-Cookie`, and no forged cookie changes `/admin`).

### The hint (`/docs/protocol.txt`)
```
Station: 18
Example HMAC key is radar. Production pads the key with the station number.
```
→ Leaked HMAC key = **`radar18`** ("radar" + station 18). The app signs *something* with it; we must forge a valid `p`. **The message being signed and/or its encoding is still unknown.**

### Ruled OUT (do not retry — all returned "denied"/"admin only")
Tested methodically (scripts below). Confirmed the Python-urllib results match `curl` (so Content-Type was **not** the problem — the final check used `curl` which sets `application/x-www-form-urlencoded`):
1. `p = ENC(HMAC(key, msg))` for key ∈ {radar18, radar, 18radar, radar-18, radar_18, radar018, radar\x12, "radar 18"}, algo ∈ {md5, sha1, sha256, sha512}, ENC ∈ {hex, HEX, base64, base64url}, msg ∈ {username, "18", "admin18", "18admin", "u=admin", "admin:18", "radar", ""} — for **20 usernames** (`login_spray.py`, `login_v2.py`) and specifically `admin` re-verified with `curl` (`hmac_gen.py` → curl loop).
2. **Signed token in `p`**: `p = data<sep>sig` / `base64(data<sep>sig)` / `base64(data)<sep>sig`, data ∈ {admin, role=admin, user=admin, admin=1, ...}, sep ∈ {| : . ~ -} (`login_v3.py`, partial — it was oversized, killed; the common cases ran).
3. **Signed token in `u`** (`u = data<sep>sig`, `p=""`) (`login_v4.py`).
4. **Extra signature parameter** the form doesn't show: `sig`/`h`/`hmac`/`mac`/`token`/`signature` alongside `u` (`login_v4.py`).
5. **HTTP header** carries the sig: `X-Signature`/`X-Sig`/`X-Hmac`/`X-Token`/`Authorization`; and **HTTP Basic** `admin:<sig>` (`login_v4.py`).
6. **Cookie forgery**: no cookie name (`session/auth/user/token/sid/login/...`) with value `admin`/`admin.<sig>`/`b64(admin).<sig>` changes `/admin` from "admin only" (`admin_forge.py` idea + manual loop).
7. **Signed query on GET /admin**: `?sig=`/`?token=`/... = HMAC(key, {/admin, admin, 18, ...}) (`admin_sig.py`) — GET always says "admin only" (GET doesn't validate creds; must POST).
8. **Plain passwords** for `admin`: radar, radar18, 18, admin, password, station18, calibration, coastal — denied. SQLi `' OR '1` — denied.
9. **Content/source discovery**: only `/`, `/login`, `/admin`, `/docs/protocol.txt` exist. No `/.git`, no source files, no backups, no other endpoints, no `/docs/*.py` (`discover.py`, `docs_brute.py`). No verbose error/traceback (handler catches everything).

### Resume plan — next hypotheses (ranked)
1. **Re-run the 20-username sweep with `curl`** (not urllib), i.e. `p = HMAC(radar18, u)` hex for u ∈ {operator, radar, calib, station18, coastal, watch, sensor, tech, ...}. The clean curl re-test only covered `u=admin`; a non-admin user might authenticate and reveal the scheme / creds. **Cheapest high-value retry.**
2. **Message = a server-provided value we're ignoring**: the `Date` header (daily token), or the station as an int. Try `p = HMAC(radar18, "admin|" + "2026-11-05")`, `HMAC(radar18, "admin|18")`, `HMAC(radar18, str(epoch//window))`.
3. **Hand-rolled MAC, not real HMAC** → if the server does `sha256(key + msg)` and we can obtain ONE valid (msg, mac) pair, **hash length-extension** (hashpump/`hlextend`) forges another. We have no pair yet — look again for an example pair (a second docs file? a comment in `/`? view full `GET /` HTML raw, re-read for hidden fields/comments).
4. **Key-padding re-reading**: "pads the key with the station number" → maybe pad to a fixed width, e.g. key = `radar` zero/space-padded then station, or key length = 18 bytes (`radar` + 13 pad). Try `radar` right-padded with `0`/space to 8/16/18 then `18`.
5. **Fuzz `/login` for a nonce/challenge flow**: does a first POST return a challenge in the body we then sign? Re-read raw `POST /login` body for any token.
6. **Bigger dirbust** with a real wordlist (`gobuster ... directory-list-2.3-medium.txt -x txt,py,bak,zip`) in case a source/backup exists off the small list.

### Once Flag 2 (web auth) breaks — expected continuation (series pattern)
- Authenticated `/admin` should reveal the **SSH username + password** (or confirm the themed username = Flag 2).
- `ssh -p 2222 <user>@10.10.10.22` → `user.txt` (`~` or `/home/user.txt`) = **Flag 3**.
- `sudo -l` + planted file → `source`/`pickle`/leaked-pw+`su`/group-readable → `/root/root.txt` = **Flag 4**.

---

## Scripts (in this folder)
| File | Purpose |
|---|---|
| `hmac_gen.py <msg>` | local HMAC candidate generator (no target contact) |
| `login_spray.py` | username × key × algo spray of `p=HMAC(key,u)` (urllib) |
| `login_v2.py` | focused `admin`: key paddings × algos × encodings; captures Set-Cookie |
| `login_v3.py` | "signed token in p" model (⚠️ oversized — trim before reuse) |
| `login_v4.py` | distinct delivery models: extra param / u-token / header / basic-auth |
| `admin_sig.py` | signed-query/header on `GET /admin` (dead end — GET never validates) |
| `admin_forge.py` | cookie-forgery sweep (⚠️ oversized — trim; cookies are ignored anyway) |
| `docs_brute.py` | `/docs/` filename brute (only `protocol.txt` exists) |
| `discover.py` | endpoint + source + `.git`/backup discovery (nothing beyond the 4 known paths) |

### State summary for next session
`radar18` is the leaked HMAC key. Auth = POST `u`+`p` to `/login` (or `/admin`), shared validator, no cookies, no source leak. `p` is **not** `enc(HMAC(radar18, <username/obvious-msg>))` in any algo/encoding, nor a signed token in `p`/`u`, nor an extra param/header/basic-auth/cookie. **Start the next session at resume-plan step 1 (curl-based username sweep) and step 3 (hunt for a valid message/MAC pair to enable length extension).**

### Note
- Claude never runs anything against the target; every command is for manual execution by the player.
