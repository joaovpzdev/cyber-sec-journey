# Firewall

> Este documento apresenta os fundamentos de firewalls no Linux, filtragem de tráfego, regras de entrada e saída, `iptables`, `nftables`, políticas padrão, chains, tabelas, stateful firewall e boas práticas de segurança.

---

# Sumário

- [1. O que é um Firewall](#1-o-que-é-um-firewall)
- [2. Por que utilizar um Firewall](#2-por-que-utilizar-um-firewall)
- [3. Firewall e camadas de rede](#3-firewall-e-camadas-de-rede)
- [4. Fluxo de um pacote](#4-fluxo-de-um-pacote)
- [5. Conceitos fundamentais](#5-conceitos-fundamentais)
- [6. Entrada, saída e encaminhamento](#6-entrada-saída-e-encaminhamento)
- [7. Stateful e Stateless Firewall](#7-stateful-e-stateless-firewall)
- [8. Políticas padrão](#8-políticas-padrão)
- [9. Ações possíveis](#9-ações-possíveis)
- [10. Netfilter](#10-netfilter)
- [11. iptables](#11-iptables)
- [12. Tabelas do iptables](#12-tabelas-do-iptables)
- [13. Chains do iptables](#13-chains-do-iptables)
- [14. Regras do iptables](#14-regras-do-iptables)
- [15. Permitindo SSH](#15-permitindo-ssh)
- [16. Loopback](#16-loopback)
- [17. Conexões estabelecidas](#17-conexões-estabelecidas)
- [18. Bloqueando portas](#18-bloqueando-portas)
- [19. Removendo regras](#19-removendo-regras)
- [20. NAT](#20-nat)
- [21. nftables](#21-nftables)
- [22. Conceitos do nftables](#22-conceitos-do-nftables)
- [23. Tabelas e Chains no nftables](#23-tabelas-e-chains-no-nftables)
- [24. Regras no nftables](#24-regras-no-nftables)
- [25. Configuração básica](#25-configuração-básica)
- [26. Firewall para servidor SSH](#26-firewall-para-servidor-ssh)
- [27. Firewall em um roteador](#27-firewall-em-um-roteador)
- [28. Logging](#28-logging)
- [29. Ordem das regras](#29-ordem-das-regras)
- [30. Troubleshooting](#30-troubleshooting)
- [31. Boas práticas](#31-boas-práticas)
- [32. Exercícios](#32-exercícios)
- [33. Resumo](#33-resumo)

---

# 1. O que é um Firewall

Um firewall é um mecanismo que controla o tráfego de rede com base em regras.

Simplificando:

```text
Pacote
   |
   v
Firewall
   |
   +----> PERMITIR
   |
   +----> BLOQUEAR
```

Um firewall pode analisar informações como:

- Endereço IP de origem.
- Endereço IP de destino.
- Protocolo.
- Porta.
- Interface de rede.
- Estado da conexão.
- Flags TCP.

Exemplo:

```text
Permitir:
TCP
Origem: qualquer
Destino: servidor
Porta: 22
```

---

# 2. Por que utilizar um Firewall

Um firewall reduz a superfície de ataque de um sistema.

Imagine um servidor com vários serviços:

```text
Servidor
│
├── SSH       22
├── HTTP      80
├── HTTPS     443
├── Banco     3306
└── Serviço interno 8080
```

Talvez você queira permitir acesso externo apenas a:

```text
22
80
443
```

E bloquear:

```text
3306
8080
```

O firewall permite definir essa política.

---

# 3. Firewall e camadas de rede

Firewalls podem atuar principalmente sobre informações das camadas de:

```text
Camada 3
IP
```

e:

```text
Camada 4
TCP / UDP
```

Exemplo:

```text
IP origem
IP destino
Protocolo
Porta
```

Alguns firewalls também conseguem analisar camadas superiores, dependendo da tecnologia utilizada.

---

# 4. Fluxo de um pacote

Imagine:

```text
Cliente
   |
   v
Internet
   |
   v
Firewall
   |
   v
Servidor
```

O firewall analisa:

```text
Origem
Destino
Protocolo
Porta
Estado
```

Depois toma uma decisão:

```text
                Pacote
                   |
                   v
              Firewall
              /       \
             v         v
          ACCEPT      DROP
```

---

# 5. Conceitos fundamentais

## Regra

Uma regra define uma condição.

Exemplo:

```text
Se:
TCP
Porta 22

Então:
ACCEPT
```

---

## Chain

Uma chain é uma sequência de regras.

```text
INPUT
│
├── Regra 1
├── Regra 2
├── Regra 3
└── Política padrão
```

---

## Política

Define o comportamento caso nenhuma regra corresponda.

Exemplo:

```text
INPUT
DROP
```

Significa:

```text
Se nenhuma regra permitir
↓
Bloquear
```

---

# 6. Entrada, saída e encaminhamento

Existem três direções principais.

## INPUT

Tráfego destinado à própria máquina.

```text
Internet
   |
   v
Servidor
```

Exemplo:

```text
Cliente -> SSH do servidor
```

---

## OUTPUT

Tráfego gerado pela própria máquina.

```text
Servidor
   |
   v
Internet
```

Exemplo:

```text
Servidor -> DNS
```

---

## FORWARD

Tráfego que passa através da máquina.

```text
Cliente
   |
   v
Roteador Linux
   |
   v
Internet
```

A máquina não é o destino final.

---

# 7. Stateful e Stateless Firewall

## Stateless

Analisa pacotes individualmente.

```text
Pacote A
↓
Decisão

Pacote B
↓
Decisão
```

Não necessariamente acompanha a conexão.

---

## Stateful

Mantém informações sobre conexões.

Exemplo:

```text
Cliente
   |
   | SYN
   v
Servidor

Cliente
   |
   | ACK
   v
Servidor
```

O firewall pode identificar:

```text
NEW
ESTABLISHED
RELATED
INVALID
```

Isso permite regras mais inteligentes.

---

# 8. Políticas padrão

Duas estratégias comuns.

## Default Allow

```text
Tudo permitido
Exceto o que for bloqueado
```

Representação:

```text
POLICY = ACCEPT
```

---

## Default Deny

```text
Tudo bloqueado
Exceto o que for permitido
```

Representação:

```text
POLICY = DROP
```

Para servidores, uma abordagem comum é:

```text
Bloquear por padrão
Permitir apenas o necessário
```

---

# 9. Ações possíveis

Algumas ações comuns.

## ACCEPT

Permite o tráfego.

```text
Pacote
↓
ACCEPT
↓
Continua
```

---

## DROP

Descarta silenciosamente.

```text
Pacote
↓
DROP
```

O cliente normalmente não recebe uma resposta explícita do firewall.

---

## REJECT

Bloqueia e envia uma resposta de rejeição.

```text
Pacote
↓
REJECT
```

---

# 10. Netfilter

No Linux, o mecanismo de filtragem de pacotes está relacionado ao subsistema:

```text
Netfilter
```

Ferramentas como:

```text
iptables
nftables
```

permitem configurar regras relacionadas ao processamento de tráfego pelo sistema.

Representação:

```text
Aplicação
   |
   v
Kernel Linux
   |
   v
Netfilter
   |
   v
Firewall Rules
```

---

# 11. iptables

`iptables` é uma ferramenta tradicional para gerenciamento de regras de firewall.

Ver regras:

```bash
sudo iptables -L
```

Com mais detalhes:

```bash
sudo iptables -L -v -n
```

Onde:

```text
-L = listar
-v = modo detalhado
-n = não resolver nomes
```

---

# 12. Tabelas do iptables

As principais tabelas incluem:

```text
filter
nat
mangle
raw
```

A tabela mais comum para filtragem é:

```text
filter
```

Para NAT:

```text
nat
```

---

# 13. Chains do iptables

Na tabela `filter`, as principais chains são:

```text
INPUT
FORWARD
OUTPUT
```

Representação:

```text
                Pacote
                   |
                   v

            +--------------+
            | Destino local?|
            +--------------+
              |          |
             Sim        Não
              |          |
              v          v
            INPUT      FORWARD
```

Pacotes criados pela própria máquina passam por:

```text
OUTPUT
```

---

# 14. Regras do iptables

Formato geral:

```bash
iptables -A CHAIN ...
```

`-A` significa:

```text
Append
Adicionar ao final
```

Exemplo:

```bash
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

Significa:

```text
INPUT
↓
Protocolo TCP
↓
Porta destino 22
↓
ACCEPT
```

---

# 15. Permitindo SSH

Uma regra comum:

```bash
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

Para uma porta SSH personalizada:

```bash
sudo iptables -A INPUT -p tcp --dport 2222 -j ACCEPT
```

---

# 16. Loopback

A interface loopback é fundamental.

```text
127.0.0.1
```

Permitir loopback:

```bash
sudo iptables -A INPUT -i lo -j ACCEPT
```

Também é comum permitir saída pela interface loopback:

```bash
sudo iptables -A OUTPUT -o lo -j ACCEPT
```

---

# 17. Conexões estabelecidas

Uma regra importante em firewalls stateful:

```bash
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

Isso permite pacotes pertencentes a conexões já estabelecidas ou relacionadas.

Exemplo:

```text
Cliente
   |
   | Requisição SSH
   v
Servidor
   |
   | Resposta
   v
Cliente
```

O firewall reconhece que a resposta pertence a uma conexão existente.

---

# 18. Bloqueando portas

Exemplo:

```bash
sudo iptables -A INPUT -p tcp --dport 3306 -j DROP
```

Isso bloqueia tráfego TCP destinado à porta:

```text
3306
```

Porém, a ordem das regras é extremamente importante.

---

# 19. Removendo regras

Liste regras numeradas:

```bash
sudo iptables -L --line-numbers
```

Exemplo:

```text
1 ACCEPT tcp -- anywhere anywhere tcp dpt:22
2 DROP   tcp -- anywhere anywhere tcp dpt:3306
```

Remover:

```bash
sudo iptables -D INPUT 2
```

---

# 20. NAT

NAT pode alterar informações de endereçamento.

Exemplo:

```text
Rede interna

192.168.1.10
      |
      v
Roteador
      |
      | NAT
      v
Internet
```

Um exemplo conceitual de masquerade:

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

O objetivo é permitir que múltiplos dispositivos internos compartilhem um endereço público, dependendo da arquitetura da rede.

---

# 21. nftables

`nftables` é uma tecnologia moderna para gerenciamento de regras de firewall no Linux.

Comando principal:

```bash
nft
```

Ver regras:

```bash
sudo nft list ruleset
```

---

# 22. Conceitos do nftables

O `nftables` utiliza conceitos como:

```text
tables
chains
rules
sets
```

Representação:

```text
TABLE
  |
  └── CHAIN
        |
        ├── RULE
        ├── RULE
        └── RULE
```

---

# 23. Tabelas e Chains no nftables

Uma tabela IPv4:

```bash
sudo nft add table ip filter
```

Uma chain:

```bash
sudo nft add chain ip filter input '{ type filter hook input priority 0; policy drop; }'
```

Essa chain processa tráfego destinado à máquina.

---

# 24. Regras no nftables

Permitir loopback:

```bash
sudo nft add rule ip filter input iif lo accept
```

Permitir conexões estabelecidas:

```bash
sudo nft add rule ip filter input ct state established,related accept
```

Permitir SSH:

```bash
sudo nft add rule ip filter input tcp dport 22 accept
```

---

# 25. Configuração básica

Um modelo conceitual:

```text
INPUT

1. Loopback
2. Established / Related
3. SSH
4. HTTP
5. HTTPS
6. Política DROP
```

Representação:

```text
Pacote
   |
   v
Loopback?
   | sim
   v
ACCEPT

Conexão existente?
   | sim
   v
ACCEPT

SSH?
   | sim
   v
ACCEPT

HTTP?
   | sim
   v
ACCEPT

HTTPS?
   | sim
   v
ACCEPT

Nada correspondeu?
   |
   v
DROP
```

---

# 26. Firewall para servidor SSH

Um servidor que precisa apenas de SSH pode ter uma política semelhante a:

```text
INPUT
│
├── ACCEPT loopback
├── ACCEPT established,related
├── ACCEPT TCP 22
└── DROP todo o restante
```

Representação:

```text
Internet
   |
   |
   +---- TCP/22 ----> ACCEPT
   |
   +---- TCP/80 ----> DROP
   |
   +---- TCP/3306 --> DROP
```

---

# 27. Firewall em um roteador

Em um roteador Linux:

```text
LAN
 |
 v
[ Linux Router ]
 |
 v
Internet
```

O tráfego encaminhado passa por:

```text
FORWARD
```

Você pode ter regras para controlar:

```text
LAN -> Internet
Internet -> LAN
```

Normalmente, o tráfego iniciado internamente é tratado de maneira diferente do tráfego iniciado externamente.

---

# 28. Logging

É possível registrar eventos de firewall.

Conceitualmente:

```text
Pacote bloqueado
      |
      v
Firewall
      |
      +----> DROP
      |
      +----> LOG
```

Logging pode ajudar em:

- Troubleshooting.
- Auditoria.
- Identificação de tráfego inesperado.

Mas cuidado:

```text
Muito logging
=
Muitos dados
=
Possível dificuldade para análise
```

---

# 29. Ordem das regras

Firewalls normalmente analisam regras em ordem.

Exemplo:

```text
1. DROP TCP 22
2. ACCEPT TCP 22
```

A segunda regra pode nunca ser alcançada.

Fluxo:

```text
Pacote TCP/22
       |
       v
Regra 1
       |
       v
DROP
```

Portanto:

```text
A ordem das regras é fundamental.
```

---

# 30. Troubleshooting

Quando uma conexão é bloqueada, investigue:

```text
1. Serviço está ativo?
2. Porta está escutando?
3. Firewall permite?
4. Rota existe?
5. IP está correto?
6. Interface está correta?
```

Ver portas:

```bash
ss -tlnp
```

Ver regras:

```bash
sudo iptables -L -v -n
```

Ou:

```bash
sudo nft list ruleset
```

Testar conectividade:

```bash
nc -vz HOST PORTA
```

---

# 31. Boas práticas

```text
[ ] Utilizar política restritiva
[ ] Permitir apenas serviços necessários
[ ] Permitir loopback
[ ] Permitir conexões established/related
[ ] Revisar regras periodicamente
[ ] Remover regras antigas
[ ] Testar antes de aplicar remotamente
[ ] Manter acesso administrativo seguro
[ ] Documentar portas abertas
```

Ao administrar remotamente:

```text
ALTEROU O FIREWALL?
       |
       v
TESTOU EM OUTRA SESSÃO?
       |
       v
CONFIRMOU O ACESSO?
       |
       v
SÓ ENTÃO ENCERRA A SESSÃO ATUAL
```

---

# 32. Exercícios

## Exercício 1

Liste as portas em escuta:

```bash
ss -tln
```

Identifique:

```text
Porta
Protocolo
Endereço
```

---

## Exercício 2

Liste regras do `iptables`:

```bash
sudo iptables -L -v -n
```

---

## Exercício 3

Liste regras do `nftables`:

```bash
sudo nft list ruleset
```

---

## Exercício 4

Em um ambiente de laboratório, crie uma regra permitindo SSH:

```bash
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

---

## Exercício 5

Observe contadores:

```bash
sudo iptables -L -v -n
```

Faça uma conexão e observe quais regras recebem tráfego.

---

## Exercício 6

Crie um diagrama:

```text
Cliente
   |
   v
Firewall
   |
   v
Servidor
```

E identifique:

```text
INPUT
OUTPUT
FORWARD
```

---

# 33. Resumo

Firewall controla:

```text
Quem pode comunicar
Com quem
Utilizando qual protocolo
Utilizando qual porta
Em qual direção
```

Estrutura conceitual:

```text
NETFILTER
   |
   +---- INPUT
   |
   +---- OUTPUT
   |
   +---- FORWARD
```

Ferramentas:

```text
iptables
nftables
```

Princípio importante:

```text
Permitir apenas o necessário.
Bloquear o restante.
```

> Um firewall não substitui outras medidas de segurança, mas é uma camada fundamental para reduzir exposição desnecessária de serviços.