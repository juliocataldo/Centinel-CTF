<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Night-Watch+Roster" alt="Typing SVG" /></a>

</div>

# Night-Watch Roster — PWN · JID-Pwn100 · Level 1 · 🟢 EASY

- **Status:** 🟠 PARTIAL (1/4) — Flag 1 (ports) solved; foothold (flags 2–4) blocked on SSH credential derivation (the clerk's full first name is never spelled out).
- **Points:** 100 / 650 (ports 100 · user 125 · user flag 175 · root 250)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}` for the file flags)
- **Target:** `10.10.10.10` (lab, over WireGuard VPN)
- **Prompt:** *"Joint duty roster" — boot2root chain.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2222,8080` | ✅ |
| 2 | Low privilege user | unresolved (username derivation blocked) | ❌ |
| 3 | User flag | not reached (locked behind foothold) | ⬜ |
| 4 | Root flag | not reached (locked behind user flag) | ⬜ |

---

## TL;DR

1. `nmap` → `2222,8080`; the `:8080` "Joint duty roster" board says the SSH user is the civil clerk's first name and the password is assembled from `shift.txt` callsign + `badges.txt` badge.
2. Civil clerk = `M. Hale`, callsign `NORTH-DESK`, badge `B-4419` — but only the initial `M.` of the first name is ever served.
3. Every sensible `username × password` assembly is rejected and no source spells Hale's full first name; the foothold is unresolved.

A boot2root chain parallel to `HarborWatch` (same author/format): recon → derive SSH creds from a web hint → foothold → privesc. We are stuck at the credential-derivation step.

---

## Recon — Flag 1: Open TCP ports ✅

Full TCP scan:

```bash
nmap -p- -T4 --min-rate 2000 -oN nmap-full.txt 10.10.10.10
```

```
2222/tcp open  ssh         (EtherNetIP-1 guess)
8080/tcp open  http-proxy
# 28 ports filtered (no-response); WARNING: retransmission cap hit (6)
```

> The `--min-rate 2000` tripped the retransmission cap (dropped probes). A reliable re-scan (`-p- -T4 --max-retries 3`) was started but never completed in-session. Given the HarborWatch parallel (exactly 2 open ports), `2222,8080` is almost certainly complete.

Service/version:

```bash
nmap -sV -sC -p 2222,8080 -oN nmap-services.txt 10.10.10.10
```

```
2222/tcp open ssh  OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
8080/tcp open http BaseHTTPServer 0.6 (Python 3.11.2)  -- title "Joint duty roster"
```

**Flag 1** = open ports only, ascending, comma-separated, plaintext:

```
2222,8080
```

> SSH 9.2p1 is patched — not the vector. The custom Python `BaseHTTPServer` on :8080 is the attack surface (identical setup to HarborWatch).

---

## Foothold — Flag 2: Low privilege user ⛔ BLOCKED

### The web hint (:8080)

`GET /` renders a "Joint duty roster" board that pins two notices and states the credential rules verbatim:

> "SSH user is the civil clerk's first name, in lowercase. The password is assembled from the callsign in shift.txt and the badge in badges.txt."

```bash
curl -sS http://10.10.10.10:8080/notices/shift.txt
```
```
Night watch callsign for the civil desk is NORTH-DESK.
The military pier uses SOUTH-PIER.
```

```bash
curl -sS http://10.10.10.10:8080/notices/badges.txt
```
```
name | badge | post
M. Hale | B-4419 | civil clerk
A. Voss | B-1002 | decoy
R. Pell | B-2280 | gate
```

Decoded per the rules:
- **Civil clerk** = `M. Hale` (Voss = decoy, Pell = gate).
- **Callsign** (civil) = `NORTH-DESK` (`SOUTH-PIER` = military decoy).
- **Badge** (Hale) = `B-4419`.
- **Username** = civil clerk's first name, lowercase → only the initial `M.` is ever given → literal reading = `m`.
- **Password** = `NORTH-DESK` + `B-4419`, some assembly.

### Why we're stuck

Every sensible `username × password` combination is rejected (`Permission denied (publickey,password)`), and **no source anywhere spells Hale's full first name** — only the initial `M.`

### What was ruled out (do not repeat)

- **Byte check**: `od -c` on both notices → **clean ASCII**, hyphens are `0x2d` (no Unicode en-dash trap), no trailing/hidden chars. Strings are exactly `NORTH-DESK` and `B-4419`.
- **LFI / path traversal** on :8080: `/../../../etc/passwd`, `....//`, `%2e%2e/` → all return the themed **"missing"** page. `..` is normalized/rejected; file serving is a **whitelist** (`/`, `/notices/shift.txt`, `/notices/badges.txt` only). No arbitrary file read → cannot pull `/etc/passwd` for the real username.
- **Hidden API (HarborWatch-style IDOR)**: `/api/badge?id=7`, `/api/clerk?id=7` → "missing". No API.
- **Hidden notices**: looped `/notices/{roster,names,staff,personnel,clerks,clerk,hale,duty,nightwatch,watch,firstnames,contacts,directory,civil}.txt` → **no hit**. (`/notices/` listing and `/robots.txt` also "missing".)
- **Extra ports**: fast scan = `2222,8080` only; reliable scan pending but HarborWatch parallel implies no missed open port.
- **fail2ban**: appears **inactive** — after ~12 failed auths we still get a password prompt (not a connection timeout), so no IP ban observed. Still, we stopped to avoid brute-forcing.

### Credentials attempted (all DENIED)

| Username | Passwords tried |
|----------|-----------------|
| `m`      | `NORTH-DESKB-4419`, `NORTH-DESK-B-4419`, `NORTHDESKB4419`, `NORTH-DESK_B-4419`, `north-desk-b-4419`, `NORTHDESK-B-4419`, `4419`, `NORTH-DESK-4419` |
| `hale`   | `NORTH-DESK-B-4419` |
| `mhale`  | `NORTH-DESK-B-4419` |
| `clerk`  | `NORTH-DESK-B-4419`, `NORTH-DESKB-4419`, `north-desk-b-4419` |

SSH command used (one deliberate attempt per invocation to control the failure count):
```bash
ssh -p 2222 -o NumberOfPasswordPrompts=1 <user>@10.10.10.10
```

### Open hypotheses / next steps

1. **The username is the real blocker.** The riddle says "first name" but only the initial `M.` exists. Either the account is literally `m` (and the password format is still wrong), or the full first name must come from somewhere not yet found.
2. **HarborWatch cross-reference** (`Level1/Pwn/HarborWatch/WRITEUP.md`): there, `username = role` (`civil-pilot` → `pilot`) and `password = full literal value` (the `-7` was NOT strippable). Applied here: role = `clerk` (tried, failed); don't strip `B-` (so `4419` alone is wrong — confirmed denied).
3. **Untried password assemblies** (grid under-sampled per username): badge dehyphenated (`NORTH-DESKB4419`, `NORTH-DESK-B4419`), reversed order (`B-4419-NORTH-DESK`), and the glue/lowercase variants against `hale`/`mhale`. Continuing this is brute-force-adjacent → only with a sharper hypothesis.
4. **Re-examine the reliable full scan** once it completes, in case a service was missed behind the retransmission cap.
5. Consider that the NightWatch foothold mechanic may differ from "notes → ssh" entirely — re-read for a vector not yet mapped.

---

## User flag — Flag 3 ⛔ (locked behind foothold)

Not reached. HarborWatch hint: `user.txt` sat one level above `~` (`/home/user.txt`, owner-readable). Check `find / -iname 'user.txt' 2>/dev/null` after foothold.

## Root flag — Flag 4 ⛔ (locked behind user flag)

Not reached. HarborWatch pattern: privesc was a **group-readable file** holding the root password (secondary group → `cat` a `640 root:<group>` file → `su -`). After foothold, enumerate `id` groups and `find / -group <secondary_group> 2>/dev/null`.

---

## Summary / Chain

| # | Flag | Status | Vector |
|---|------|--------|--------|
| 1 | Open TCP ports | ✅ | `nmap -p-` → `2222,8080` |
| 2 | Low privilege user | ⛔ | Derive SSH creds from :8080 notes — **blocked on username/password format** |
| 3 | User flag | ⛔ | Likely `user.txt` near `/home` (per HarborWatch) |
| 4 | Root flag | ⛔ | Likely group-readable root password → `su -` (per HarborWatch) |

### Note
- Claude does not run anything against the target; all commands are executed manually by the player.
