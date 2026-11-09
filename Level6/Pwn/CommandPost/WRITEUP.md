<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Command+Post" alt="Typing SVG" /></a>

</div>

# Command Post — PWN · JID-Pwn404 · Level 6 · 🟣 INSANE

- **Status:** 🟠 PARTIAL (1/4) — Flag 1 found; Flag 2 blocked (the "order" submission channel is hidden and was never found).
- **Points:** 350 / 4150
- **Flags:** Open TCP ports → Low privilege user → User flag → Root flag (`CTF{...}`; flags 1–2 plaintext)
- **Target:** `10.10.10.44` (lab, over VPN)
- **Prompt:** *boot2root — custom Python "Command post" app on `:8181`*

> **Level placement:** guessed `Level6` from the series numbering (Pwn2xx→L4, Pwn3xx→L5, Pwn4xx→L6). **Unconfirmed** — move if wrong.

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Open TCP ports | `22,8181` | ✅ |
| 2 | Low privilege user | submit an `EXEC` order to the hidden endpoint of the `:8181` app — channel not found | ❌ blocked |
| 3 | User flag | SSH :22 → `/home/user.txt` | ⏳ pending |
| 4 | Root flag | `sudo -l` misconfig → `/root/root.txt` | ⏳ pending |

---

## TL;DR

1. Two ports: SSH on `:22` (patched → decoy, a break from the series' high-port habit) and a GET-only Python "Command post" app on `:8181`.
2. The app documents an order format (`CIV1` + `EXEC <cmd>`) via `/samples/form.txt`, but the submission channel is hidden by design.
3. Query strings, request bodies, headers, ~90 themed routes and raft-small-words discovery all left the baseline unchanged — Flag 2 stayed blocked.

10th+ sibling of the JID boot2root series. It **breaks the series skeleton**: SSH is on the **standard port 22** (not a high port), and the whole challenge hinges on a custom Python web app on `:8181` whose order-submission endpoint is deliberately hidden.

> Flag format: `CTF{...}`. Every command was executed manually by the player against the box.

---

## 0. Connect

```bash
cd /home/felipebc2/repo/CTF/CentinelI
sudo wg-quick up ./team-71-player-a.conf
ping -c1 10.10.10.44
```

---

## Flag 1 — Open TCP ports ✅ (350 pts)

```bash
sudo nmap -sS -p- --min-rate 5000 -T4 --max-retries 2 -Pn -n 10.10.10.44 -oN nmap-44-full.txt
sudo nmap -sC -sV -p 22,8181 -Pn -n 10.10.10.44 -oN nmap-44-svc.txt
```
```
22/tcp   open  ssh   OpenSSH 9.2p1 Debian 2+deb12u10   # patched → decoy (not the vector)
8181/tcp open  http  BaseHTTP/0.6 (Python 3.11.2)      # title "Command post" → attack surface
```

**Flag 1 = `22,8181`** (ascending, comma-separated, plaintext)

> Series break: SSH on 22 (every prior sibling used a high port). Still a patched OpenSSH → decoy, same as the siblings.

---

## Flag 2 — Low privilege user ⏸️ BLOCKED (700 pts)

### App map (GET-only Python `http.server`)

Only `do_GET` is implemented. Every other method → `501 Unsupported method`.

| route | status | body |
|-------|--------|------|
| `/` | 200 (1575 B) | landing, links `/rooms` and `/samples/form.txt` |
| `/rooms` | 200 | `<ol>dock / alpha / bravo</ol>` + **"Posted order is the API, not this list."** |
| `/samples/form.txt` | 200 | the order format (see below) |
| everything else | 404 | skin page whose dynamic body is the literal word `no` |

`/samples/form.txt` (exact bytes, 22 B — confirmed with `hexdump -C`):
```
CIV1
EXEC echo sample
```
Reading: line 1 `CIV1` = a magic/clearance tag (theme "civ-mil", cf. ConvoyOrders' `CIVMIL`); line 2 `EXEC <cmd>` = a directive that (by the name) runs a shell command. The sample's `echo sample` is the benign example.

**The blocker:** the order format is documented, but **how/where you submit an order is hidden** and we did not find it. The `/rooms` hint ("Posted order **is the API**, not this list") confirms the real surface is a *posted order*, and that dock/alpha/bravo are decoys.

### Everything tested for the order channel — all negative (do NOT repeat on resume)

Method / verb:
- `POST`, `PUT`, `ORDER`, `EXEC`, `OPTIONS` → all `501 Unsupported method`. Server is **GET-only**. (So "Posted order" is thematic, not literal HTTP POST, and `EXEC` is not an HTTP method.)

Channel on the real routes (`/`, `/rooms`) — verified by **response size**, not just by eyeballing (see gotcha below):
- Query string: `?order=`, `?o=`, `?cmd=`, `?file=`, `?name=`, `?form=`, `?exec=`, … → `/` stays **exactly 1575 B** (landing) for a good order, junk, or nothing. Param is **ignored**.
- GET **with a request body** (`curl -X GET --data-binary $'CIV1\nEXEC echo sample\n'`) on `/` and `/rooms` → unchanged (1575 B / rooms list). Ignored.
- Request **headers** (`Clearance: CIV1` + `Exec: echo sample`, `X-Order: …`) → ignored.

Routing (all 404 "no"):
- `/dock`, `/alpha`, `/bravo` (the room names are **404**, not endpoints), `/rooms/<room>`, `/CIV1`, `/civ1`.
- ~90 hand-picked themed words (order, orders, post, submit, dispatch, brief, command, commandpost, map, maproom, board, pin, situation, sitrep, api, v1, exec, run, task, directive, signal, console, panel, admin, status, new, issue, queue, inbox, message, memo, report, ops, mission, relay, radio, desk, bulletin, …) — plain GET **and** GET-with-order-body.
- `ffuf` / `xargs` content discovery with **raft-small-words (~6.4k)** → zero non-404 hits.
- Parameter fuzz with **burp-parameter-names** on `/?FUZZ=<order>` → nothing changed the 1575 B baseline.

File read / source leak (all failed):
- Path traversal in `/samples/`: `../`, URL-encoded `%2e%2e`, double-encoded, `....//`, with `--path-as-is` → all return "no". **Guarded** (likely a realpath/allowlist check).
- No `robots.txt`, `.git/HEAD`, `server.py`, `app.py`, `*.bak`, `*~`, `*.swp`, `README*`, `index.html`, `style.css` exposed.
- `OPTIONS` gives no `Allow` header (501).
- No Python traceback leaked on any malformed input seen so far.

### Key gotcha recorded for the next session
The landing page contains the word **"sample"** inside the link text `sample form` / `/samples/form.txt`. An early `grep` for `sample` produced a **false positive** that looked like RCE ("echo sample" reflected) when the server had actually just returned the plain landing page. **Confirm order processing by `Content-Length`/`%{size_download}` (processed ≠ 1575), never by grepping for `sample`.**

### Open hypotheses for resume (ranked)
1. **Hidden endpoint/param not in the small wordlists.** Re-run discovery with a *larger* list (`raft-large-words`, `dirsearch`, `raft-*-directories`) **and** with the order in the body so a body-gated route activates:
   `ffuf -w BIG -u http://10.10.10.44:8181/FUZZ -X GET -d $'CIV1\nEXEC echo sample\n' -mc all -fs <404-size>`
   Also fuzz params on **`/rooms`**, not only `/`, and try two-param layouts (`?CIV1=…&EXEC=…`, `?clearance=CIV1&order=…`).
2. **Source is the intended first step.** Hunt harder for an LFI/source leak: a param that reads a file (once found via #1), a `/samples/` filename trick we missed, or a verbose error via malformed `Content-Length`/bad percent-encoding. The exact order mechanism (channel, magic validation, EXEC filter, privesc) all fall out of the source.
3. **The 4 pins** in the HTML (`.pins i` → red, yellow, green, blue) may encode a code/sequence or a clearance beyond `CIV1` (DEFCON-style). Possibly the real magic or a room selector.
4. **Buy the official challenge hint** — costs points and is **not** refunded (warn before using). Given this is reported *Insane* and the submit endpoint is non-derivable from the exposed surface, a hint may directly name it. Worth it only while the submission window is open.

---

## Flag 3 — User flag (1100 pts) — PENDING
Once the order channel → RCE (or SSH creds) is found: `ssh <user>@10.10.10.44` (port **22**), `cat /home/user.txt`. Confirm creds with `id` before submitting.

## Flag 4 — Root flag (2000 pts) — PENDING
Series ending: `sudo -n -l` → a NOPASSWD wrapper that sources/execs a user-writable file, does an unconstrained file read, or reuses a leaked key → `cat /root/root.txt`.

---

## Takeaways
- GET-only app; real routes `/`, `/rooms`, `/samples/form.txt`; order format documented (`CIV1` + `EXEC <cmd>`) but **submission surface hidden by design**.
- Validate "did the order run?" by **response size**, not by string-matching the page (the landing contains the word "sample").
- SSH moved to :22 (series break) but still a patched decoy.
- VPN `team-71-player-a.conf` never read/uploaded/committed. Remember to `wg-quick down` when done.
