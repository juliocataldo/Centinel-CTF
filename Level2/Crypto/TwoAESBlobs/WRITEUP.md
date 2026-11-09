<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Two+AES+Blobs" alt="Typing SVG" /></a>

</div>

# Two AES Blobs — CRYPTO · JID-Crypto107 · Level 2 · 🟢 EASY

- **Status:** ✅ SOLVED (3/3) — Berth `2` was accepted after `two` was rejected (so Boat was accepted too, the flags are chained); all flags accepted by the platform.
- **Points:** —
- **Flags:** Boat → Berth → Word (chained, plaintext format, no `CTF{}` wrapper)
- **Attachment:** `desk.txt`
- **Prompt:** *"Two AES blobs and their keys. The file is on this page."*

| # | Flag | Answer | Status |
|---|------|--------|--------|
| 1 | Boat | `CORA` | ✅ (implied: Berth unlocked) |
| 2 | Berth | `2` | ✅ (`two` rejected) |
| 3 | Word | `palm` | ✅ |

---

## TL;DR

1. `desk.txt` hands over two AES-128-ECB key/blob pairs; nothing needs to be attacked.
2. Decrypt the desk blob (the sample blob is the recurring ROCA / barrel / 240 decoy): `Boat CORA. Berth two. Word palm.`
3. The trap is the answer format: the berth is spelled out in the plaintext but the platform expects the digit `2`.

## The file

```
AES-128-ECB, PKCS7.

Sample key: 00112233445566778899aabbccddeeff
Sample blob: 911d837bc6841c89ccb77d45258ac3623f8911b7e4055ba2ce75a667235ea326d2513511990dfbc75d82a23350cd1977

Desk key: 0f1e2d3c4b5a69788796a5b4c3d2e1f0
Desk blob: 8a2126b95aeaef5535cfabd4c26b67c549a8b18e0e8430985d717a057f533b427e3319b5bd2419dc2c61ca1cacaf2642
```

The file names the mode and padding and gives both keys, so nothing needs to be attacked. Each blob is 48 bytes (3 AES blocks).

## Decrypting

Decrypt each blob with its own key in AES-128-ECB, then strip the PKCS7 padding:

| Blob   | Plaintext                                          | Padding        |
|--------|----------------------------------------------------|----------------|
| Sample | `Boat ROCA. Berth nine. Word barrel. Litres 240.`  | `\x01` × 1     |
| Desk   | `Boat CORA. Berth two. Word palm.`                 | `\x10` × 16    |

Both paddings are valid. The desk plaintext is exactly 32 bytes, so PKCS7 appends a full block of `\x10`. This confirms that the key and mode are correct.

The flag text says to submit "the boat in the desk blob", so the sample is a decoy. It is the same ROCA / barrel / 240 decoy used across the other JID challenges.

## The Berth gotcha

The desk plaintext spells the berth out as `two`, and the platform **rejected** `two`. The decoy gives away the right format. In SlipChecker (Rev), the same decoy slip reads `boat ROCA, berth 9, word barrel`, and here it reads `Berth nine`. The author spells berths out as words inside the ciphertext but expects a digit as the answer, just as SlipChecker's Berth was `7`. So `two` → `2`, which was accepted.

## Solver

`solve.py` pulls both key/blob pairs out of `desk.txt`, decrypts them with pycryptodome and prints the raw and unpadded plaintexts:

```
python3 -I solve.py desk.txt
```

Equivalent one-liner with OpenSSL:

```
echo '<blob hex>' | xxd -r -p | openssl enc -d -aes-128-ecb -K <key hex>
```

## Takeaway

When the key is handed to you, the crypto is just a decrypt call. The real trap was the answer format. If a plaintext answer gets rejected, check the recurring decoy data across the CTF for the expected format before you spend more attempts.
