# Como o Docker pode expor seu banco de dados mesmo com o firewall ativo (e como corrigir)

> Um lab prático mostrando por que `ufw deny 5432` **não** bloqueia um PostgreSQL publicado com Docker, o que acontece por baixo dos panos (NAT + iptables) e as formas corretas de proteger.

![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Security](https://img.shields.io/badge/Blue%20Team-Hardening-0A66C2)

---

## TL;DR

```yaml
# ERRADO: expõe o banco para TODA a rede (e talvez para a internet)
ports:
  - "5432:5432"

# CERTO: só a própria máquina acessa
ports:
  - "127.0.0.1:5432:5432"

# Melhor ainda: não publique. A API acessa o banco pela rede interna do Docker.
```

E o firewall? **O `ufw` não vê esse tráfego.** O Docker cria regras de NAT que desviam o pacote **antes** de ele passar pelas regras do `ufw`.

---

## Sumário

1. [O problema](#o-problema)
2. [Por que acontece: o caminho do pacote](#por-que-acontece-o-caminho-do-pacote)
3. [Reproduzindo no lab](#reproduzindo-no-lab)
4. [Como corrigir](#como-corrigir)
5. [Validando a correção](#validando-a-correção)
6. [E no Windows / Docker Desktop / WSL2?](#e-no-windows--docker-desktop--wsl2)
7. [Checklist de hardening](#checklist-de-hardening)
8. [O que aprendi](#o-que-aprendi)
9. [Referências](#referências)

---

## O problema

Cenário comum em projetos pessoais e até em produção:

1. Você sobe uma API (Node.js/Express + Prisma) e um **PostgreSQL** com `docker compose`.
2. Para conectar pelo DBeaver/pgAdmin, publica a porta: `"5432:5432"`.
3. Por segurança, ativa o firewall:

   ```bash
   sudo ufw default deny incoming
   sudo ufw allow 22/tcp
   sudo ufw deny 5432/tcp
   sudo ufw enable
   ```

4. `sudo ufw status` diz que a 5432 está **bloqueada**. Tudo certo… certo?

**Não.** De outra máquina da rede, o banco **continua acessível**. Se esse servidor tiver IP público (uma VPS, por exemplo), o banco fica exposto **para a internet inteira** — e portas de banco de dados são varridas por robôs o tempo todo, com tentativas de login começando em pouco tempo.

---

## Por que acontece: o caminho do pacote

O `ufw` é uma "interface amigável" para o **iptables/nftables**. As regras que ele cria ficam principalmente na cadeia **`INPUT`**, que trata pacotes **destinados ao próprio host**.

Quando você publica uma porta, o Docker cria uma regra de **DNAT** (NAT de destino) na tabela `nat`, cadeia **`PREROUTING`** — que é avaliada **antes** da decisão de roteamento:

```
 Pacote chega: cliente → 192.168.56.10:5432
        │
        ▼
 ┌──────────────────────────────┐
 │ nat / PREROUTING             │  ← Docker: DNAT 192.168.56.10:5432 → 172.18.0.2:5432
 └──────────────────────────────┘
        │  o destino agora é o CONTAINER, não o host
        ▼
   Decisão de roteamento: "não é para mim, é para encaminhar"
        │
        ├──────────────► INPUT   ← onde está o "ufw deny 5432"  o pacote NEM passa aqui
        │
        ▼
 ┌──────────────────────────────┐
 │ filter / FORWARD             │  ← Docker: DOCKER-USER → regras do Docker → ACCEPT
 └──────────────────────────────┘
        │
        ▼
   Container PostgreSQL 172.18.0.2:5432  conexão estabelecida
```

Resumindo:

| Etapa | Quem controla | Resultado |
|---|---|---|
| `PREROUTING` (nat) | Docker | Troca o destino para o IP do container |
| `INPUT` (filter) | **ufw** | **Nunca é consultada** — o pacote não é mais "para o host" |
| `FORWARD` (filter) | Docker | Aceita o tráfego para a porta publicada |

> **Dica:** A documentação oficial do Docker deixa isso claro: ao publicar portas, o Docker manipula as regras de firewall do host, e ferramentas como `ufw` e `firewalld` podem não se aplicar a esse tráfego. Para filtrar, ele oferece a cadeia **`DOCKER-USER`**.

---

## Reproduzindo no lab

>  Faça **somente** no seu próprio lab (VMs em rede *host-only*/interna). Não teste em servidores de terceiros.

### Ambiente

| Máquina | Papel | IP (exemplo) |
|---|---|---|
| **VM-SERVIDOR** | Ubuntu Server + Docker + ufw | `192.168.56.10` |
| **VM-CLIENTE** | Qualquer Linux na mesma rede host-only | `192.168.56.20` |

### 1. No servidor: firewall "fechado"

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw deny 5432/tcp
sudo ufw enable
sudo ufw status verbose
```

### 2. No servidor: compose **vulnerável**

```yaml
# docker-compose.yml  (versão vulnerável)
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: senha_de_lab_apenas
      POSTGRES_DB: dashfintrack
    ports:
      - "5432:5432"        # publica em 0.0.0.0 → todas as interfaces
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

```bash
docker compose up -d
docker ps --format "table {{.Names}}\t{{.Ports}}"
# NAMES     PORTS
# lab-db-1  0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   ← todas as interfaces!
```

### 3. No servidor: veja a regra que o Docker criou

```bash
sudo iptables -t nat -L DOCKER -n -v
# DNAT  tcp  --  !br-xxxx  *  0.0.0.0/0  0.0.0.0/0  tcp dpt:5432 to:172.18.0.2:5432
```

### 4. No cliente: teste a porta

```bash
nc -vz 192.168.56.10 5432
# Connection to 192.168.56.10 5432 port [tcp/postgresql] succeeded!   ← o banco está exposto
```

Ou tente conectar de fato:

```bash
psql -h 192.168.56.10 -U app -d dashfintrack
# Password for user app:     ← o banco está respondendo para a rede
```

*Sugestão: coloque aqui um print do `ufw status` mostrando `5432 DENY` lado a lado com o `nc ... succeeded`.*

---

## Como corrigir

Há várias camadas de correção. **Use a mais restritiva que atender ao seu caso.**

### Opção 1 — Não publicar a porta do banco (a melhor)

Se só a **API** precisa do banco, os dois containers se falam pela **rede interna do Docker**, pelo **nome do serviço**. Nenhuma porta precisa ser publicada.

```yaml
services:
  api:
    build: .
    environment:
      DATABASE_URL: postgresql://app:${DB_PASSWORD}@db:5432/dashfintrack   # "db" = nome do serviço
    ports:
      - "127.0.0.1:3000:3000"
    depends_on:
      - db
    networks:
      - backend

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: dashfintrack
    # sem "ports:" → inacessível de fora do Docker
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - backend

networks:
  backend:

volumes:
  pgdata:
```

> **Dica:** Repare também no `${DB_PASSWORD}`: a senha vem de um arquivo `.env` (que **não** vai para o Git — confira o `.gitignore`).

### Opção 2 — Publicar só no loopback (para usar DBeaver/pgAdmin localmente)

```yaml
    ports:
      - "127.0.0.1:5432:5432"
```

Agora só a **própria máquina** acessa. Se o servidor for remoto, use um **túnel SSH** em vez de abrir a porta:

```bash
ssh -L 5432:127.0.0.1:5432 usuario@servidor
# e conecte o DBeaver em localhost:5432
```

### Opção 3 — Mudar o padrão do Docker para loopback

Em `/etc/docker/daemon.json`:

```json
{
  "ip": "127.0.0.1"
}
```

```bash
sudo systemctl restart docker
```

Assim, qualquer `-p 8080:80` sem IP explícito passa a publicar **só em 127.0.0.1**. É uma ótima "rede de segurança" contra esquecimentos.

### Opção 4 — Filtrar na cadeia `DOCKER-USER`

Quando uma porta **precisa** ficar publicada na rede, mas só para alguns IPs. A `DOCKER-USER` é avaliada **antes** das regras do Docker na `FORWARD`:

```bash
# Permitir acesso ao 5432 publicado apenas a partir da rede de administração
sudo iptables -I DOCKER-USER -i eth0 -p tcp -m conntrack --ctorigdstport 5432 --ctdir ORIGINAL \
  ! -s 192.168.56.0/24 -j DROP
```

> **Observação:** Usa-se `--ctorigdstport` (porta de destino **original**, antes do DNAT) porque, quando o pacote chega na `FORWARD`, o destino já foi reescrito para o IP/porta do container.
> Regras de iptables feitas à mão **não sobrevivem ao reboot** — persista com `iptables-persistent`/`netfilter-persistent` ou com a configuração do seu firewall.

### Não recomendado: `"iptables": false` no Docker

Desligar o gerenciamento de iptables do Docker até "faz o ufw funcionar", mas costuma **quebrar a rede dos containers** (saída para a internet, comunicação entre redes) e exige recriar tudo manualmente. Só use se souber exatamente o que está fazendo.

### Resumo das opções

| Opção | Quando usar | Exposição |
|---|---|---|
| 1. Não publicar | Só outros containers precisam do serviço | Nenhuma |
| 2. `127.0.0.1:porta` | Acesso local (ferramentas no próprio host / túnel SSH) | Só localhost |
| 3. `daemon.json` → `"ip": "127.0.0.1"` | Padrão seguro contra esquecimento | Só localhost por padrão |
| 4. `DOCKER-USER` | Precisa ficar na rede, mas restrito por IP | Controlada |
| `"5432:5432"` sem filtro | **Nunca para banco de dados** | Rede inteira / internet (crítica) |

---

## Validando a correção

**Nunca confie só no "ficou configurado". Teste de fora.**

### No servidor

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
# lab-db-1   5432/tcp                       ← Opção 1: não publicada
# lab-db-1   127.0.0.1:5432->5432/tcp       ← Opção 2: só loopback

ss -tlnp | grep 5432
# LISTEN 0 4096 127.0.0.1:5432 ...          ← nada de 0.0.0.0
```

### No cliente

```bash
nc -vz -w 3 192.168.56.10 5432
# nc: connect to 192.168.56.10 port 5432 (tcp) failed: Connection refused   ← corrigido
```

### Antes x depois

| Teste | Antes (`"5432:5432"`) | Depois (sem publicar / `127.0.0.1`) |
|---|---|---|
| `ufw status` | 5432 DENY | 5432 DENY |
| `docker ps` | `0.0.0.0:5432->5432` | `5432/tcp` ou `127.0.0.1:5432->5432` |
| `nc` do cliente | succeeded (exposto) | refused / timeout (protegido) |
| API funciona? | Sim | Sim (via rede interna `db:5432`) |

---

## E no Windows / Docker Desktop / WSL2?

No **Docker Desktop** (Windows/macOS), os containers rodam dentro de uma VM e as portas publicadas são encaminhadas para o **host Windows/macOS**. O comportamento muda:

- Quem filtra o acesso vindo da rede é o **Firewall do Windows** (ou do macOS), não o `ufw`.
- Mesmo assim, o princípio continua: `"5432:5432"` escuta em **todas as interfaces** do host; `"127.0.0.1:5432:5432"` escuta só localmente.
- Verifique com `netstat -ano | findstr 5432` se aparece `0.0.0.0:5432` ou `127.0.0.1:5432`.

**Conclusão:** em qualquer sistema, **publique em `127.0.0.1` por padrão** e só abra para a rede quando houver um motivo explícito.

---

## Checklist de hardening

- [ ] Banco de dados **não** tem porta publicada (ou só em `127.0.0.1`)
- [ ] `daemon.json` com `"ip": "127.0.0.1"` como padrão
- [ ] API publicada só onde precisa (atrás de um reverse proxy com TLS em produção)
- [ ] Senhas em `.env`, `.env` no `.gitignore`, sem senhas padrão
- [ ] Acesso administrativo remoto via **túnel SSH** ou **VPN**, nunca porta aberta
- [ ] Portas publicadas que precisam de rede restringidas na **`DOCKER-USER`**
- [ ] `docker ps` revisado: nenhum `0.0.0.0:` inesperado
- [ ] Teste **de outra máquina** (`nc -vz`) após cada mudança
- [ ] Em VPS/nuvem: **security group** do provedor também restringindo as portas

---

## O que aprendi

- **Firewall configurado ≠ firewall eficaz.** O `ufw status` mostrava "DENY", mas o tráfego nunca passava por aquela regra.
- **NAT muda o caminho do pacote.** O DNAT do Docker acontece em `PREROUTING`, então o tráfego vai para `FORWARD`, e não para `INPUT`, onde o `ufw` filtra.
- **NAT não é firewall.** Ele só traduz endereços; a filtragem é outra camada, que precisa ser pensada à parte.
- **Princípio do menor privilégio na infraestrutura:** se um serviço não precisa ser acessado da rede, ele não deve escutar na rede.
- **Valide de fora.** Testar só de dentro da própria máquina (`localhost`) esconde exatamente esse tipo de problema.
- Segurança não é só tarefa do time de segurança: uma linha no `docker-compose.yml` escrita pelo dev define a **superfície de ataque** da aplicação.

---

## Referências

- Docker Docs — *Packet filtering and firewalls* (seções sobre `DOCKER-USER` e integração com ufw/firewalld)
- Docker Docs — *Published ports* / opção `ip` do `daemon.json`
- Docker Docs — *Networking in Compose*
- Ubuntu — documentação do `ufw`
- Netfilter/iptables — fluxo de pacotes (`PREROUTING`, `INPUT`, `FORWARD`, `POSTROUTING`)

---

<sub>Lab feito em ambiente isolado (VMs em rede host-only). IPs e credenciais são fictícios. Parte da minha série de estudos de **redes e cybersecurity** — veja também os guias sobre NAT, TCP x UDP e roteamento no meu GitHub.</sub>