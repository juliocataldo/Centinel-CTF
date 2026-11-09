<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=SOC700" alt="Typing SVG" /></a>

</div>

# SOC700 — BLUETEAM · JID-SOC700 · Level 8 · 🔴 HARD

- **Status:** ❌ UNSOLVED (0/11) — ran out of competition time during Kibana setup; no flag confirmed.
- **Points:** — / — (per-flag points not recorded)
- **Flags:** 11 sequential, plaintext (not `CTF{}`), Flag 1 lowercase.
- **Target:** remote **Security Onion** Elastic stack (`<HOST>`, user `<USER>`), hunted manually in Kibana
- **Prompt:** *"The same intrusion reached the Windows side of the estate. A user ran a planted binary. Follow the callback, then the credential theft on that host."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Infected host | — | ❌ |
| 2 | Malicious file | — | ❌ |
| 3 | Directory | — | ❌ |
| 4 | Domain user | — | ❌ |
| 5 | Execution timestamp | — | ❌ |
| 6 | C2 address | — | ❌ |
| 7 | C2 port | — | ❌ |
| 8 | Credential tool | — | ❌ |
| 9 | Tickets | — | ❌ |
| 10 | Ticket timestamp | — | ❌ |
| 11 | Command line | — | ❌ |

---

## TL;DR

1. Windows-side intrusion to be hunted in a remote Security Onion / Elastic stack: planted binary → C2 callback → credential theft → Kerberos ticket dump, pivoting on `process.entity_id`.
2. The kill chain and full KQL/ES|QL playbook were prepared (see `queries.md`), but the Kibana time range defaulted to the last 24h (incident is older).
3. Fixing the range cost the remaining time (the relative picker was stuck on "Years from now" instead of "ago"), so no query ever returned data and nothing was submitted.

## Brief

> The same intrusion reached the Windows side of the estate. A user ran a planted
> binary. Follow the callback, then the credential theft on that host.

All hunting was to be done manually in Kibana; answers are plaintext (not `CTF{}`), Flag 1 lowercase.

## Intended kill chain

1. User executes a planted binary from a user-writable dir (Sysmon EID 1 / `event.category:process`).
2. That process makes an outbound callback to the C2 (Sysmon EID 3 / `event.category:network`) → C2 IP + port.
3. A credential-theft tool (Mimikatz/Rubeus, possibly renamed) runs on the host → tool name + full command line.
4. Kerberos tickets dumped/exported (`.kirbi` via Sysmon EID 11, or Security 4768/4769) → ticket count + timestamp.

Pivot everything on `process.entity_id` / ProcessGuid (or `process.pid` → `process.parent.*`).

## What blocked us

Security Onion dashboard loaded with the default **Last 24 hours** range → `0` events (incident
is older). Fixing the range cost the remaining time: the relative picker was set to
**"Years from now"** (future) instead of **"Years ago"**, so it stayed on an invalid future
window until the clock ran out. No query ever returned data, so **no host, file, or IOC was
observed** and nothing was submitted (per rules: never submit an unconfirmed flag).

## To finish next time (first 60 seconds)

1. Time range → **Absolute**, start `Jan 1, 2020` → **Update** (do not use the relative picker).
2. `queries.md` Step 0: `FROM logs-*,winlogbeat-*,.ds-* | STATS count() BY host.hostname, host.os.type`
   to list Windows hosts (Flag 1 candidate).
3. Run the Flags 1–5 KQL (binary from suspicious dir), pivot on entity_id for the rest.

Full query playbook: see `queries.md` in this folder.

## Lessons

- Security Onion defaults to a tiny time window — widen it before anything else.
- The relative time picker defaults to "from now"; for historical incidents switch to "ago"
  or just use Absolute. A 20-second config mistake cost the whole challenge.
