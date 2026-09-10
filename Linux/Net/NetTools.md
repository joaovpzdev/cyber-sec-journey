# Ferramentas de Redes no Linux

> Este documento apresenta ferramentas fundamentais para diagnóstico, monitoramento e análise de redes no Linux, incluindo `ip`, `ss`, `netstat`, `ping`, `traceroute`, `tcpdump`, `dig`, `nc` e outras ferramentas úteis.

---

# Sumário

- [1. Por que ferramentas de rede são importantes](#1-por-que-ferramentas-de-rede-são-importantes)
- [2. Estratégia de troubleshooting](#2-estratégia-de-troubleshooting)
- [3. ip](#3-ip)
- [4. Interfaces de rede](#4-interfaces-de-rede)
- [5. Endereços IP](#5-endereços-ip)
- [6. Rotas](#6-rotas)
- [7. Gateway](#7-gateway)
- [8. ARP e vizinhos](#8-arp-e-vizinhos)
- [9. ss](#9-ss)
- [10. Portas TCP](#10-portas-tcp)
- [11. Portas UDP](#11-portas-udp)
- [12. Conexões estabelecidas](#12-conexões-estabelecidas)
- [13. netstat](#13-netstat)
- [14. ping](#14-ping)
- [15. ICMP](#15-icmp)
- [16. traceroute](#16-traceroute)
- [17. tracepath](#17-tracepath)
- [18. tcpdump](#18-tcpdump)
- [19. Captura por interface](#19-captura-por-interface)
- [20. Filtros do tcpdump](#20-filtros-do-tcpdump)
- [21. Analisando DNS](#21-analisando-dns)
- [22. dig](#22-dig)
- [23. host](#23-host)
- [24. nslookup](#24-nslookup)
- [25. nc](#25-nc)
- [26. curl](#26-curl)
- [27. wget](#27-wget)
- [28. lsof](#28-lsof)
- [29. journalctl](#29-journalctl)
- [30. Estratégia de diagnóstico](#30-estratégia-de-diagnóstico)
- [31. Cenários práticos](#31-cenários-práticos)
- [32. Exercícios](#32-exercícios)
- [33. Resumo](#33-resumo)

---

# 1. Por que ferramentas de rede são importantes

Problemas de rede podem ocorrer em diversos pontos.

Exemplo:

```text
Aplicação
   |
   v
DNS
   |
   v
TCP / UDP
   |
   v
IP
   |
   v
Interface
   |
   v
Roteador
   |
   v
Internet
```

Quando algo falha, precisamos descobrir:

```text
ONDE está falhando?
```

Ferramentas de rede permitem investigar cada camada.

---

# 2. Estratégia de troubleshooting

Uma sequência útil:

```text
1. Interface está ativa?
2. Possui IP?
3. Existe rota?
4. Gateway responde?
5. DNS funciona?
6. Destino responde?
7. Porta está aberta?
8. Aplicação está funcionando?
```

Isso evita investigar aleatoriamente.

---

# 3. ip

A ferramenta `ip` é uma das principais ferramentas modernas de rede no Linux.

Ela pode mostrar:

- Interfaces.
- Endereços IP.
- Rotas.
- Vizinhos.
- Links.

---

## Ver interfaces

```bash
ip link
```

Exemplo:

```text
1: lo
2: eth0
3: wlan0
```

---

## Interface específica

```bash
ip link show eth0
```

---

# 4. Interfaces de rede

Uma interface pode estar:

```text
UP
```

ou:

```text
DOWN
```

Verifique:

```bash
ip link
```

Ativar:

```bash
sudo ip link set eth0 up
```

Desativar:

```bash
sudo ip link set eth0 down
```

---

# 5. Endereços IP

Ver endereços:

```bash
ip addr
```

Forma curta:

```bash
ip a
```

Exemplo:

```text
inet 192.168.1.10/24
```

Isso significa:

```text
IP:      192.168.1.10
Prefixo: /24
```

---

# 6. Rotas

Ver tabela de roteamento:

```bash
ip route
```

Exemplo:

```text
default via 192.168.1.1 dev eth0
```

Isso significa:

```text
Gateway padrão:

192.168.1.1
```

---

## Ver rota até um destino

```bash
ip route get 8.8.8.8
```

Isso ajuda a entender:

```text
Qual interface será utilizada?
Qual gateway?
Qual endereço de origem?
```

---

# 7. Gateway

O gateway normalmente conecta a rede local a outras redes.

```text
Computador
192.168.1.10
      |
      v
Gateway
192.168.1.1
      |
      v
Internet
```

Teste:

```bash
ping 192.168.1.1
```

---

# 8. ARP e vizinhos

Ver vizinhos conhecidos:

```bash
ip neigh
```

Exemplo:

```text
192.168.1.1 dev eth0 lladdr AA:BB:CC:DD:EE:FF REACHABLE
```

Isso relaciona:

```text
IP
↓
MAC
```

---

# 9. ss

`ss` é uma ferramenta moderna para analisar sockets.

Ver conexões:

```bash
ss
```

Ver portas TCP:

```bash
ss -t
```

Ver portas UDP:

```bash
ss -u
```

Ver portas em escuta:

```bash
ss -l
```

---

# 10. Portas TCP

Ver portas TCP em escuta:

```bash
ss -tln
```

Com processos:

```bash
sudo ss -tlnp
```

Exemplo:

```text
LISTEN 0 128 0.0.0.0:22
```

Significa que existe um serviço escutando TCP na porta:

```text
22
```

---

# 11. Portas UDP

Ver sockets UDP:

```bash
ss -uln
```

Com processos:

```bash
sudo ss -ulnp
```

---

# 12. Conexões estabelecidas

Ver conexões TCP:

```bash
ss -tan
```

Estados comuns:

```text
LISTEN
ESTABLISHED
TIME-WAIT
CLOSE-WAIT
SYN-SENT
SYN-RECV
```

Exemplo:

```text
ESTABLISHED
```

Significa que a conexão TCP está estabelecida.

---

# 13. netstat

`netstat` é uma ferramenta mais antiga, mas ainda encontrada em alguns sistemas.

Exemplo:

```bash
netstat -tulpn
```

Pode mostrar:

```text
TCP
UDP
Portas
Processos
```

Em sistemas modernos:

```text
ss
```

geralmente é preferível.

---

# 14. ping

`ping` testa conectividade utilizando ICMP.

Exemplo:

```bash
ping 8.8.8.8
```

Fluxo:

```text
Seu computador
     |
     | ICMP Echo Request
     v
Destino
     |
     | ICMP Echo Reply
     v
Seu computador
```

---

## Limitar pacotes

```bash
ping -c 4 8.8.8.8
```

Envia:

```text
4 pacotes
```

---

# 15. ICMP

ICMP é utilizado para mensagens de controle e diagnóstico.

Exemplos:

```text
Echo Request
Echo Reply
Destination Unreachable
Time Exceeded
```

Importante:

```text
Ping falhar
≠
necessariamente host desligado
```

ICMP pode ser bloqueado por firewall.

---

# 16. traceroute

`traceroute` mostra os saltos entre origem e destino.

Exemplo:

```bash
traceroute google.com
```

Representação:

```text
Seu computador
      |
      v
Roteador 1
      |
      v
Roteador 2
      |
      v
Roteador 3
      |
      v
Destino
```

---

# 17. tracepath

Uma alternativa:

```bash
tracepath google.com
```

Pode ser útil para diagnóstico de:

```text
Rota
Saltos
MTU
```

---

# 18. tcpdump

`tcpdump` permite capturar e analisar pacotes.

Exemplo:

```bash
sudo tcpdump
```

É recomendável especificar:

```text
Interface
Filtro
```

---

# 19. Captura por interface

Ver interfaces:

```bash
ip link
```

Capturar:

```bash
sudo tcpdump -i eth0
```

Capturar em todas as interfaces disponíveis:

```bash
sudo tcpdump -i any
```

---

# 20. Filtros do tcpdump

## TCP

```bash
sudo tcpdump -i any tcp
```

## UDP

```bash
sudo tcpdump -i any udp
```

## ICMP

```bash
sudo tcpdump -i any icmp
```

## Porta

```bash
sudo tcpdump -i any port 53
```

## DNS

```bash
sudo tcpdump -i any udp port 53
```

## SSH

```bash
sudo tcpdump -i any tcp port 22
```

## Host específico

```bash
sudo tcpdump -i any host 192.168.1.10
```

---

# 21. Analisando DNS

Para diagnosticar DNS:

```text
1. Nome resolve?
2. Qual servidor DNS responde?
3. Qual IP foi retornado?
4. Existe registro correto?
```

Ferramentas:

```text
dig
host
nslookup
```

---

# 22. dig

Consulta básica:

```bash
dig example.com
```

Consultar registro A:

```bash
dig example.com A
```

Consultar AAAA:

```bash
dig example.com AAAA
```

Consultar MX:

```bash
dig example.com MX
```

Resposta resumida:

```bash
dig example.com +short
```

Consultar servidor específico:

```bash
dig @8.8.8.8 example.com
```

---

# 23. host

Uso simples:

```bash
host example.com
```

Exemplo:

```bash
host -t MX example.com
```

Útil para consultas rápidas.

---

# 24. nslookup

Exemplo:

```bash
nslookup example.com
```

Pode ser usado para testes básicos de resolução DNS.

---

# 25. nc

`nc`, também conhecido como Netcat, é útil para testar conectividade TCP e UDP.

Testar porta TCP:

```bash
nc -vz 192.168.1.10 22
```

Exemplo conceitual:

```text
Cliente
   |
   | TCP connect
   v
192.168.1.10:22
```

Útil para verificar:

```text
Servidor alcançável?
Porta aberta?
Firewall bloqueando?
```

---

# 26. curl

`curl` é muito utilizado para testar serviços HTTP e HTTPS.

Exemplo:

```bash
curl https://example.com
```

Mostrar cabeçalhos:

```bash
curl -I https://example.com
```

Modo detalhado:

```bash
curl -v https://example.com
```

Pode ajudar a observar:

```text
DNS
Conexão TCP
TLS
HTTP
```

---

# 27. wget

`wget` permite obter arquivos via rede.

Exemplo:

```bash
wget https://example.com/arquivo
```

Também pode ser utilizado para testes simples de conectividade HTTP.

---

# 28. lsof

`lsof` significa:

```text
List Open Files
```

No Linux, sockets também podem ser representados como arquivos.

Ver processo utilizando uma porta:

```bash
sudo lsof -i :22
```

Exemplo:

```text
sshd
```

Também pode ser útil para descobrir:

```text
Qual processo está utilizando uma porta?
```

---

# 29. journalctl

Em sistemas com `systemd`, logs podem ser analisados com:

```bash
journalctl
```

Para um serviço:

```bash
sudo journalctl -u ssh
```

Ou:

```bash
sudo journalctl -u NetworkManager
```

Acompanhar logs:

```bash
sudo journalctl -f
```

Isso é útil durante troubleshooting.

---

# 30. Estratégia de diagnóstico

Imagine:

```text
Não consigo acessar um servidor.
```

Investigue em ordem.

---

## Passo 1 — DNS

```bash
dig servidor.exemplo
```

Se falhar:

```text
Possível problema de DNS.
```

---

## Passo 2 — IP

Teste:

```bash
ping IP_DO_SERVIDOR
```

---

## Passo 3 — Rota

```bash
ip route get IP_DO_SERVIDOR
```

---

## Passo 4 — Caminho

```bash
traceroute IP_DO_SERVIDOR
```

ou:

```bash
tracepath IP_DO_SERVIDOR
```

---

## Passo 5 — Porta

```bash
nc -vz IP_DO_SERVIDOR 22
```

---

## Passo 6 — Serviço

No servidor:

```bash
ss -tlnp
```

---

## Passo 7 — Firewall

Verifique:

```bash
sudo nft list ruleset
```

ou:

```bash
sudo iptables -L -v -n
```

---

## Passo 8 — Pacotes

Capture:

```bash
sudo tcpdump -i any host IP_DO_CLIENTE
```

Observe:

```text
SYN chegou?
SYN-ACK foi enviado?
```

---

# 31. Cenários práticos

## Cenário 1 — Sem internet

Verifique interface:

```bash
ip link
```

Depois:

```bash
ip addr
```

Depois:

```bash
ip route
```

Teste o gateway:

```bash
ping GATEWAY
```

Teste um IP externo:

```bash
ping 8.8.8.8
```

Teste DNS:

```bash
dig example.com
```

Fluxo:

```text
Interface
   ↓
IP
   ↓
Gateway
   ↓
Internet IP
   ↓
DNS
```

---

## Cenário 2 — SSH não conecta

Cliente:

```bash
ssh -vvv usuario@host
```

Teste porta:

```bash
nc -vz host 22
```

Servidor:

```bash
sudo ss -tlnp
```

Logs:

```bash
sudo journalctl -u ssh
```

Firewall:

```bash
sudo nft list ruleset
```

---

## Cenário 3 — DNS não resolve

Teste:

```bash
dig example.com
```

Teste outro resolvedor:

```bash
dig @1.1.1.1 example.com
```

Capture:

```bash
sudo tcpdump -i any port 53
```

Verifique se:

```text
Consulta sai?
Resposta chega?
```

---

# 32. Exercícios

## Exercício 1 — Interfaces

Execute:

```bash
ip link
```

Identifique:

```text
Interface loopback
Interface Ethernet
Interface Wi-Fi
```

---

## Exercício 2 — Endereços

Execute:

```bash
ip addr
```

Identifique:

```text
IPv4
IPv6
Máscara / Prefixo
```

---

## Exercício 3 — Rotas

Execute:

```bash
ip route
```

Identifique:

```text
Gateway padrão
Interface utilizada
Rede local
```

---

## Exercício 4 — Portas

Execute:

```bash
sudo ss -tlnp
```

Identifique:

```text
Porta
Serviço
Processo
```

---

## Exercício 5 — Ping

Execute:

```bash
ping -c 4 8.8.8.8
```

Observe:

```text
Latência
Pacotes enviados
Pacotes recebidos
Perda
```

---

## Exercício 6 — DNS

Execute:

```bash
dig example.com
```

Depois:

```bash
dig example.com A
```

Depois:

```bash
dig example.com AAAA
```

---

## Exercício 7 — TCP

Teste uma porta:

```bash
nc -vz example.com 443
```

Compare com:

```bash
nc -vz example.com 22
```

---

## Exercício 8 — Captura

Capture ICMP:

```bash
sudo tcpdump -i any icmp
```

Em outro terminal:

```bash
ping IP_DO_DESTINO
```

Observe:

```text
Echo Request
Echo Reply
```

---

## Exercício 9 — SSH

Capture:

```bash
sudo tcpdump -i any tcp port 22
```

Em outro terminal:

```bash
ssh usuario@host
```

Observe o estabelecimento TCP.

---

# 33. Resumo

Principais ferramentas:

```text
ip
├── interfaces
├── IPs
├── rotas
└── vizinhos

ss
├── sockets
├── portas
└── conexões

ping
└── conectividade ICMP

traceroute
└── caminho entre redes

tcpdump
└── captura de pacotes

dig
├── DNS
└── registros

nc
└── teste de portas

curl
└── HTTP/HTTPS

lsof
└── processos e portas

journalctl
└── logs
```

Fluxo recomendado para diagnóstico:

```text
INTERFACE
   ↓
IP
   ↓
ROTA
   ↓
GATEWAY
   ↓
DNS
   ↓
PORTA
   ↓
SERVIÇO
   ↓
FIREWALL
   ↓
CAPTURA DE PACOTES
```

> A habilidade mais importante em troubleshooting de redes não é decorar comandos, mas saber qual camada investigar e utilizar a ferramenta adequada para confirmar ou eliminar hipóteses.