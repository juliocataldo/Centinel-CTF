# Setup do CTFd para Treino

Guia para subir a plataforma CTFd com os 5 challenges ja configurados, acessivel externamente via Cloudflare Tunnel (gratis).

## Requisitos

- Docker instalado
- Conta gratuita no Cloudflare com um dominio apontando pra la (DNS gerenciado pelo Cloudflare)
- `cloudflared` instalado

## Passo a passo

### 1. Subir o CTFd

```bash
docker run -d --name ctfd -p 8000:8000 --restart unless-stopped ctfd/ctfd
```

Acesse `http://localhost:8000` e faca o setup inicial:
- Nome do evento: **Treino CTF - Centinela Digital**
- Admin user: defina seu usuario/senha de admin
- Modo: **Users** (individual) ou **Teams** (se quiser duplas)
- Visibilidade do scoreboard: **Public**

### 2. Importar os challenges

Apos o setup inicial, rode o script que popula os challenges automaticamente:

```bash
# Ajuste a URL e o token de admin
export CTFD_URL="http://localhost:8000"
export CTFD_TOKEN="seu_token_aqui"

# Para gerar o token: CTFd > Admin Panel > Settings > Access Tokens > Generate

bash setup/import-challenges.sh
```

### 3. Expor via Cloudflare Tunnel

```bash
# Instalar cloudflared (Debian/Ubuntu)
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
  | sudo tee /usr/share/keyrings/cloudflare.gpg > /dev/null

echo "deb [signed-by=/usr/share/keyrings/cloudflare.gpg] \
  https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/cloudflared.list

sudo apt update && sudo apt install -y cloudflared

# Autenticar (abre o browser, faz login no Cloudflare, seleciona o dominio)
cloudflared tunnel login

# Criar o tunnel
cloudflared tunnel create ctf-treino

# Apontar DNS (substitua pelo seu dominio)
cloudflared tunnel route dns ctf-treino ctf.seudominio.com

# Rodar
cloudflared tunnel run --url http://localhost:8000 ctf-treino
```

O time acessa `https://ctf.seudominio.com` com HTTPS automatico.

### 4. No dia do treino

1. Suba o Docker e o tunnel
2. Compartilhe o link com o time
3. Cada pessoa cria conta e comeca a resolver
4. Scoreboard em tempo real em `/scoreboard`

### 5. Encerrar

```bash
# Parar tunnel (Ctrl+C no terminal ou)
cloudflared tunnel delete ctf-treino

# Parar CTFd
docker stop ctfd && docker rm ctfd
```

## Pontuacao

| Challenge | Flag 1 | Flag 2 | Flag 3 | Total |
|-----------|--------|--------|--------|-------|
| Small Modulus (Crypto Easy) | 100 | 100 | 100 | 300 |
| Slip Checker (Rev Medium) | 150 | 150 | 150 | 450 |
| Two AES Blobs (Crypto Easy) | 100 | 100 | 100 | 300 |
| Duty Program (Rev Medium) | 150 | 150 | 150 | 450 |
| Radio Note (Misc Hard) | 200 | 200 | 200 | 600 |
| **Total** | | | | **2100** |

Scoring estatico. Quem acumula mais pontos ganha; desempate por timestamp (quem submeteu primeiro).

## Estrutura de challenges no CTFd

Cada challenge tem 3 flags independentes. No CTFd, crie como 15 challenges separados (um por flag) agrupados por categoria. O script `import-challenges.sh` faz isso automaticamente.

## Alternativa sem Cloudflare (rede local)

Se todo mundo esta na mesma rede, pule os passos 3-5. O time acessa direto:

```
http://SEU-IP-LOCAL:8000
```
