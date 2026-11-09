#!/usr/bin/env bash
# ===========================================================
# Importa os 15 flags (5 challenges x 3 flags) no CTFd via API
#
# Uso:
#   export CTFD_URL="http://localhost:8000"
#   export CTFD_TOKEN="ctfd_seu_token_aqui"
#   bash import-challenges.sh
# ===========================================================

set -euo pipefail

: "${CTFD_URL:?Defina CTFD_URL (ex: http://localhost:8000)}"
: "${CTFD_TOKEN:?Defina CTFD_TOKEN (gere em Admin > Settings > Access Tokens)}"

API="$CTFD_URL/api/v1"
AUTH="Authorization: Token $CTFD_TOKEN"
CT="Content-Type: application/json"

create_challenge() {
  local name="$1" category="$2" description="$3" value="$4" flag="$5" max_attempts="${6:-10}"

  echo "[+] Criando: $name ($category) - $value pts"

  # Criar challenge
  local resp
  resp=$(curl -s -X POST "$API/challenges" \
    -H "$AUTH" -H "$CT" \
    -d "{
      \"name\": \"$name\",
      \"category\": \"$category\",
      \"description\": \"$description\",
      \"value\": $value,
      \"max_attempts\": $max_attempts,
      \"type\": \"standard\",
      \"state\": \"visible\"
    }")

  local cid
  cid=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)

  if [ -z "$cid" ]; then
    echo "    ERRO ao criar challenge: $resp"
    return 1
  fi

  # Criar flag
  curl -s -X POST "$API/flags" \
    -H "$AUTH" -H "$CT" \
    -d "{
      \"challenge_id\": $cid,
      \"content\": \"$flag\",
      \"type\": \"static\",
      \"data\": \"case_sensitive\"
    }" > /dev/null

  echo "    OK (id=$cid)"
}

echo "============================================"
echo "  Importando challenges para CTFd"
echo "  URL: $CTFD_URL"
echo "============================================"
echo ""

# -------------------------------------------------------
# Small Modulus (Crypto Easy) - 100 pts cada
# -------------------------------------------------------
create_challenge \
  "Small Modulus - Boat" \
  "Crypto" \
  "RSA com modulo pequeno. Artefato: seal.txt. Submeta o nome do barco. Format: plaintext." \
  100 "PEAK"

create_challenge \
  "Small Modulus - Word" \
  "Crypto" \
  "Mesmo artefato (seal.txt). Submeta a palavra decifrada. Format: plaintext." \
  100 "CAIR"

create_challenge \
  "Small Modulus - Litres" \
  "Crypto" \
  "Mesmo artefato (seal.txt). Submeta a quantidade de litros. Format: plaintext." \
  100 "64"

# -------------------------------------------------------
# Slip Checker (Rev Medium) - 150 pts cada
# -------------------------------------------------------
create_challenge \
  "Slip Checker - Boat" \
  "Reverse" \
  "ELF x86-64 stdin checker. Artefato: slip. Submeta o nome do barco. Format: plaintext." \
  150 "MIRA"

create_challenge \
  "Slip Checker - Berth" \
  "Reverse" \
  "Mesmo artefato (slip). Submeta o numero do berth. Format: plaintext." \
  150 "7"

create_challenge \
  "Slip Checker - Word" \
  "Reverse" \
  "Mesmo artefato (slip). Submeta a palavra. Format: plaintext." \
  150 "chalk"

# -------------------------------------------------------
# Two AES Blobs (Crypto Easy) - 100 pts cada
# -------------------------------------------------------
create_challenge \
  "Two AES Blobs - Boat" \
  "Crypto" \
  "Dois blobs AES. Artefato: desk.txt. Submeta o nome do barco. Format: plaintext." \
  100 "CORA"

create_challenge \
  "Two AES Blobs - Berth" \
  "Crypto" \
  "Mesmo artefato (desk.txt). Submeta o numero do berth. Format: plaintext." \
  100 "2"

create_challenge \
  "Two AES Blobs - Word" \
  "Crypto" \
  "Mesmo artefato (desk.txt). Submeta a palavra. Format: plaintext." \
  100 "palm"

# -------------------------------------------------------
# Duty Program (Rev Medium) - 150 pts cada
# -------------------------------------------------------
create_challenge \
  "Duty Program - Boat" \
  "Reverse" \
  "ELF x86-64 com VM de bytecode customizada. Artefato: desk. Submeta o nome do barco. Format: plaintext." \
  150 "KITE"

create_challenge \
  "Duty Program - Litres" \
  "Reverse" \
  "Mesmo artefato (desk). Submeta a quantidade de litros. Format: plaintext." \
  150 "52"

create_challenge \
  "Duty Program - Word" \
  "Reverse" \
  "Mesmo artefato (desk). Submeta a palavra. Format: plaintext." \
  150 "maple"

# -------------------------------------------------------
# Radio Note (Misc Hard) - 200 pts cada
# -------------------------------------------------------
create_challenge \
  "Radio Note - Boat" \
  "Misc" \
  "Sinal de audio Bell 202 AFSK. Artefato: pier-note.wav. Submeta o nome do barco. Format: plaintext." \
  200 "ANA"

create_challenge \
  "Radio Note - Berth" \
  "Misc" \
  "Mesmo artefato (pier-note.wav). Submeta o numero do berth. Format: plaintext." \
  200 "4"

create_challenge \
  "Radio Note - Litres" \
  "Misc" \
  "Mesmo artefato (pier-note.wav). Submeta a quantidade de litros. Format: plaintext." \
  200 "67"

echo ""
echo "============================================"
echo "  15 challenges importados com sucesso!"
echo "  Pontuacao total: 2100 pts"
echo "============================================"
echo ""
echo "Proximo passo: distribua os artefatos para o time."
echo "  - seal.txt, slip, desk.txt, desk, pier-note.wav"
echo "  - Ou compartilhe o link do repo (pasta treino/, sem gabarito)."
