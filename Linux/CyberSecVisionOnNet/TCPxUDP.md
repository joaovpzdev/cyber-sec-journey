# TCP x UDP: um guia didático com olhar de Cybersecurity

> **Para quem é este material:** quem está estudando redes (ex.: Cisco *Conceitos Básicos de Redes*) e quer entender a **camada de transporte** de verdade: como TCP e UDP funcionam, quando cada um é usado e por que isso importa para firewall, monitoramento e resposta a incidentes. É continuação dos guias *Broadcasts e Roteadores* e *Endereçamento Dinâmico com DHCP*.

---

## Sumário

1. [Onde TCP e UDP se encaixam](#1-onde-tcp-e-udp-se-encaixam)
2. [Portas e sockets](#2-portas-e-sockets)
3. [TCP: o protocolo confiável](#3-tcp-o-protocolo-confiável)
4. [O three-way handshake](#4-o-three-way-handshake)
5. [Encerrando uma conexão TCP](#5-encerrando-uma-conexão-tcp)
6. [Os estados de uma conexão TCP](#6-os-estados-de-uma-conexão-tcp)
7. [Como o TCP garante a entrega](#7-como-o-tcp-garante-a-entrega)
8. [O cabeçalho TCP](#8-o-cabeçalho-tcp)
9. [UDP: o protocolo rápido](#9-udp-o-protocolo-rápido)
10. [TCP x UDP lado a lado](#10-tcp-x-udp-lado-a-lado)
11. [Quem usa o quê: protocolos e portas](#11-quem-usa-o-quê)
12. [QUIC: o UDP que virou "TCP moderno"](#12-quic)
13. [Por que a camada de transporte importa em segurança](#13-por-que-a-camada-de-transporte-importa-em-segurança)
14. [Ameaças comuns (visão conceitual)](#14-ameaças-comuns-visão-conceitual)
15. [Defesas](#15-defesas)
16. [TCP/UDP como fonte de evidência (SOC)](#16-tcpudp-como-fonte-de-evidência)
17. [Visão Red Team x Blue Team](#17-visão-red-team-x-blue-team)
18. [Mão na massa: comandos e filtros](#18-mão-na-massa-comandos-e-filtros)
19. [Troubleshooting](#19-troubleshooting)
20. [Exercícios para o seu lab](#20-exercícios-para-o-seu-lab)
21. [Resumo e glossário](#21-resumo-e-glossário)

---

## 1. Onde TCP e UDP se encaixam

| Camada OSI | Nome | Pergunta que responde | Exemplos |
|---|---|---|---|
| 7–5 | Aplicação | "**O que** estou dizendo?" | HTTP, DNS, SSH |
| **4** | **Transporte** | "**Para qual programa** e **com qual garantia**?" | **TCP, UDP** |
| 3 | Rede | "Para qual **máquina**?" | IP |
| 2 | Enlace | "Para qual **placa** da rede local?" | Ethernet, Wi-Fi |

A camada de rede (IP) leva o pacote até o **computador** certo. Mas dentro dele há dezenas de programas rodando: navegador, Discord, Spotify, atualizador do Windows… A **camada de transporte** entrega os dados ao **programa** certo e decide **como** entregar:

- **TCP:** "vou garantir que tudo chegue, inteiro e na ordem".
- **UDP:** "vou mandar o mais rápido possível; se algo se perder, paciência".

> 💡 **Analogia:**
> - **TCP** = **carta registrada com aviso de recebimento**. Você sabe que chegou, chegou inteira e na ordem. Mais lenta e burocrática.
> - **UDP** = **panfleto jogado na caixa de correio**. Rápido, barato, sem confirmação. Se um se perder, ninguém fica sabendo.

---

## 2. Portas e sockets

### 2.1 Portas

Uma **porta** é um número de 16 bits (**0 a 65535**) que identifica um serviço/programa dentro de uma máquina.

| Faixa | Nome | Uso |
|---|---|---|
| 0 – 1023 | **Well-known** (bem conhecidas) | Serviços padrão (80 HTTP, 443 HTTPS, 22 SSH) — no Linux exigem privilégio de root para escutar |
| 1024 – 49151 | **Registered** (registradas) | Aplicações conhecidas (3306 MySQL, 5432 PostgreSQL, 3389 RDP, 10050 Zabbix agent) |
| 49152 – 65535 | **Dinâmicas / efêmeras** | Portas temporárias que o **cliente** usa ao abrir uma conexão |

> TCP e UDP têm **espaços de portas independentes**: a porta 53/TCP e a 53/UDP são coisas diferentes (ambas usadas pelo DNS, por exemplo).

### 2.2 Socket

**Socket = IP + protocolo + porta.** Uma conexão é identificada por uma **5-tupla**:

```
(protocolo, IP origem, porta origem, IP destino, porta destino)
(TCP,       192.168.0.10, 51544,     142.250.79.14, 443)
```

> 🔐 **Visão cyber:** a 5-tupla é a "impressão digital" de cada conversa na rede. **Firewalls, IDS, NetFlow e logs** trabalham com ela. Saber lê-la é a base de qualquer análise de tráfego em SOC.

### 2.3 Serviço "escutando" (listening)

Quando um servidor web roda, ele **abre a porta 443 em modo de escuta** e espera conexões. Cada porta aberta é uma **porta de entrada** para a máquina — por isso:

> 🔐 **Princípio da superfície de ataque:** *cada porta aberta é um serviço que pode ter vulnerabilidade.* Porta que não precisa estar aberta deve estar **fechada** ou **bloqueada pelo firewall**.

---

## 3. TCP: o protocolo confiável

**TCP (Transmission Control Protocol)** — RFC 9293 (que atualizou a clássica RFC 793).

Características:

| Característica | O que significa |
|---|---|
| **Orientado à conexão** | Antes de trocar dados, os dois lados combinam a conversa (handshake) |
| **Confiável** | Cada segmento recebido é confirmado (ACK); o que se perde é **retransmitido** |
| **Ordenado** | Números de sequência permitem remontar os dados na ordem certa |
| **Controle de fluxo** | O receptor diz quanto consegue receber (janela) |
| **Controle de congestionamento** | O emissor desacelera se a rede estiver congestionada |
| **Full-duplex** | Os dois lados falam ao mesmo tempo |
| **Fluxo de bytes** | A aplicação vê um "cano" contínuo de dados |

Custo disso tudo: **mais cabeçalho, mais idas e vindas, mais latência**.

---

## 4. O three-way handshake

Antes de qualquer dado, o TCP faz o **aperto de mão em três etapas**:

```
   Cliente                                         Servidor (porta 443)
  192.168.0.10:51544                               142.250.79.14:443
       |                                                   |
       |  1) SYN        seq=1000                           |
       |   "Quero conversar. Começo meus números em 1000"  |
       |-------------------------------------------------->|
       |                                                   |
       |  2) SYN-ACK    seq=5000, ack=1001                 |
       |   "Ok! Recebi seu 1000. Eu começo em 5000"        |
       |<--------------------------------------------------|
       |                                                   |
       |  3) ACK        seq=1001, ack=5001                 |
       |   "Recebi seu 5000. Conexão estabelecida!"        |
       |-------------------------------------------------->|
       |                                                   |
       |  ========= dados (ex.: TLS + HTTP) =========      |
```

Pontos importantes:

- **SYN** = *synchronize*: sincroniza os números de sequência.
- O número inicial (**ISN – Initial Sequence Number**) é **aleatório** — e isso é uma **proteção de segurança**: se fosse previsível, um atacante poderia "adivinhar" a sequência e injetar dados numa conexão alheia (ataque histórico dos anos 90).
- O ACK sempre vale **"próximo byte que espero receber"** (por isso `ack = seq + 1`).

### E se a porta estiver fechada?

```
Cliente → SYN       → Servidor
Cliente ← RST, ACK  ← Servidor   ("não tem ninguém escutando aqui")
```

### E se um firewall bloquear?

- **Drop (descartar):** o cliente não recebe nada → **timeout**.
- **Reject (rejeitar):** o firewall responde com **RST** (TCP) ou **ICMP Port Unreachable**.

> 🔐 **Visão cyber:** essas três respostas possíveis — **SYN-ACK (aberta)**, **RST (fechada)** e **silêncio (filtrada)** — são a base conceitual do **mapeamento de portas** (*port scanning*). Para o Blue Team, isso explica por que **drop** costuma ser preferido na borda: revela menos sobre o que existe atrás do firewall.
> ⚖️ Varredura de portas só em máquinas suas ou com **autorização formal por escrito**.

---

## 5. Encerrando uma conexão TCP

### 5.1 Encerramento elegante: FIN (four-way)

```
   A                                   B
   |  FIN          "terminei de enviar" |
   |----------------------------------->|
   |  ACK                               |
   |<-----------------------------------|
   |  FIN          "eu também terminei" |
   |<-----------------------------------|
   |  ACK                               |
   |----------------------------------->|
   [A espera um tempo em TIME_WAIT]
```

Cada lado fecha **a sua metade** da conexão separadamente (por isso 4 mensagens, às vezes resumidas em 3).

### 5.2 Encerramento abrupto: RST

O **RST (reset)** derruba a conexão **imediatamente**, sem despedida. Acontece quando:

- A porta está fechada.
- Um programa trava ou é encerrado à força.
- Um firewall/IPS decide **cortar** a conexão.

> 🔐 **Visão cyber:** muitos **IPS** e alguns firewalls de censura cortam conexões **injetando RSTs**. Muitos RSTs inesperados num log podem indicar: serviço instável, firewall bloqueando, varredura em andamento ou interferência na rede.

---

## 6. Os estados de uma conexão TCP

| Estado | Significado |
|---|---|
| `LISTEN` | Servidor esperando conexões |
| `SYN_SENT` | Cliente enviou SYN, aguardando resposta |
| `SYN_RECEIVED` (`SYN_RECV`) | Servidor recebeu SYN e respondeu SYN-ACK; espera o ACK final |
| `ESTABLISHED` | Conexão aberta, trocando dados |
| `FIN_WAIT_1` / `FIN_WAIT_2` | Quem iniciou o encerramento esperando o outro lado |
| `CLOSE_WAIT` | O outro lado fechou; a aplicação local ainda não fechou |
| `LAST_ACK` | Esperando o último ACK |
| `TIME_WAIT` | Conexão fechada, aguardando pacotes atrasados expirarem |
| `CLOSED` | Fim |

> 🔐 **Leitura de segurança dos estados:**
> - **Centenas de `SYN_RECV`** num servidor → forte indício de **SYN flood** (seção 14).
> - **Conexão `ESTABLISHED` para IP/porta estranhos** (ex.: um processo desconhecido conectado a um IP externo na porta 4444) → possível **malware / backdoor / C2** — investigar o processo dono.
> - **Muitos `CLOSE_WAIT`** → geralmente bug na aplicação (não fecha sockets), o que pode causar indisponibilidade.
> - **Portas em `LISTEN` que você não reconhece** → serviço inesperado = superfície de ataque (ou persistência de um invasor).

---

## 7. Como o TCP garante a entrega

### 7.1 Sequência e confirmação

Cada byte tem um número. O receptor confirma até onde recebeu tudo certinho.

```
A → seq=1001, 500 bytes  →  B
A ← ack=1501             ←  B   "recebi até o 1500, mande a partir do 1501"
```

### 7.2 Retransmissão

Se o ACK não vier dentro do tempo (**RTO – Retransmission Timeout**) ou chegarem **3 ACKs duplicados**, o emissor **reenvia**.

> 🛠️ **Troubleshooting:** muitas retransmissões no Wireshark = perda de pacotes (Wi-Fi ruim, cabo com defeito, link congestionado, firewall descartando).

### 7.3 Janela (controle de fluxo)

O receptor anuncia sua **window size**: "posso receber até X bytes sem confirmar". Se o receptor estiver sobrecarregado, anuncia **janela zero** e o emissor pausa.

### 7.4 Controle de congestionamento

O TCP começa devagar (*slow start*), acelera enquanto tudo vai bem e **reduz** quando detecta perda. É isso que impede a internet de colapsar com todo mundo transmitindo ao máximo.

### 7.5 MSS

**MSS (Maximum Segment Size)**: maior quantidade de dados num único segmento, negociada no handshake (tipicamente **1460 bytes** em Ethernet: 1500 de MTU − 20 IP − 20 TCP).

---

## 8. O cabeçalho TCP

Tamanho mínimo: **20 bytes**.

| Campo | Bits | Função |
|---|---|---|
| Porta de origem | 16 | Programa que enviou |
| Porta de destino | 16 | Programa que vai receber |
| Número de sequência | 32 | Posição dos dados no fluxo |
| Número de confirmação (ACK) | 32 | Próximo byte esperado |
| Data offset | 4 | Tamanho do cabeçalho |
| **Flags** | 9 | Controle da conexão (abaixo) |
| Window | 16 | Janela de recepção |
| Checksum | 16 | Detecção de erros |
| Urgent pointer | 16 | Dados urgentes (raramente usado) |
| Opções | variável | MSS, window scale, SACK, timestamps |

### As flags

| Flag | Significado | Uso |
|---|---|---|
| **SYN** | Synchronize | Abrir conexão |
| **ACK** | Acknowledgment | Confirmar recebimento |
| **FIN** | Finish | Encerrar educadamente |
| **RST** | Reset | Encerrar abruptamente / recusar |
| **PSH** | Push | Entregar já à aplicação |
| **URG** | Urgent | Dados urgentes |
| ECE / CWR | ECN | Sinalização de congestionamento |

> 🔐 **Visão cyber:** em tráfego legítimo, as flags seguem combinações previsíveis (SYN; SYN+ACK; ACK; PSH+ACK; FIN+ACK; RST). **Combinações sem sentido** (ex.: SYN+FIN juntos, ou nenhuma flag ligada) **não aparecem em comunicação normal** e são clássicas regras de detecção em IDS como Suricata e Snort — geralmente indicam varredura ou tentativa de evasão.

---

## 9. UDP: o protocolo rápido

**UDP (User Datagram Protocol)** — RFC 768, de 1980. Simples de propósito.

Características:

| Característica | O que significa |
|---|---|
| **Sem conexão** | Não tem handshake: manda e pronto |
| **Sem garantia** | Não confirma, não retransmite |
| **Sem ordem** | Datagramas podem chegar fora de ordem |
| **Sem controle de fluxo/congestionamento** | Envia na velocidade que a aplicação quiser |
| **Orientado a mensagens** | Cada datagrama é uma unidade independente |
| **Suporta broadcast e multicast** | TCP não suporta (é sempre 1 para 1) |
| **Leve** | Cabeçalho de apenas **8 bytes** |

### O cabeçalho UDP inteiro

| Campo | Bits |
|---|---|
| Porta de origem | 16 |
| Porta de destino | 16 |
| Comprimento | 16 |
| Checksum | 16 |

É só isso. Compare com os 20+ bytes do TCP.

### Se o UDP não garante nada, por que usar?

Porque em muitos casos **chegar rápido é mais importante que chegar tudo**:

- **Chamada de voz/vídeo:** retransmitir um pedaço de áudio de 200 ms atrás não adianta — ele já passou.
- **Jogos online:** a posição atual do jogador importa mais que a antiga.
- **DNS:** uma pergunta e uma resposta pequenas; fazer handshake seria mais lento que a própria consulta. Se falhar, o cliente simplesmente pergunta de novo.
- **DHCP:** o cliente nem tem IP ainda (veja o guia de DHCP).

> 💡 Quando a aplicação precisa de alguma confiabilidade sobre UDP, **ela mesma implementa** (como o QUIC, seção 12).

### E se a porta UDP estiver fechada?

Não há RST. O host normalmente responde com **ICMP Port Unreachable** — ou **nada**, se houver firewall. Por isso é **mais difícil** saber se uma porta UDP está aberta ou filtrada.

---

## 10. TCP x UDP lado a lado

| Critério | **TCP** | **UDP** |
|---|---|---|
| Conexão | Sim (handshake) | Não |
| Confiabilidade | Garante entrega | Melhor esforço |
| Ordem | Garantida | Não garantida |
| Retransmissão | Sim | Não |
| Controle de fluxo/congestionamento | Sim | Não |
| Cabeçalho | 20–60 bytes | 8 bytes |
| Velocidade/latência | Maior latência | Menor latência |
| Broadcast/multicast | Não | Sim |
| Estado no servidor | Mantém (memória por conexão) | Não mantém |
| Origem pode ser falsificada facilmente? | **Difícil** após o handshake | **Fácil** (não há handshake) |
| Uso típico | Web, e-mail, SSH, arquivos, bancos de dados | DNS, DHCP, VoIP, streaming, jogos, NTP, SNMP, syslog |

> 🔐 **As duas linhas finais da tabela são as mais importantes para segurança** — e explicam boa parte das ameaças da seção 14:
> - O TCP **guarda estado** → pode ser atacado esgotando esse estado.
> - O UDP **não confirma a origem** → pode ser usado com IP de origem falsificado.

---

## 11. Quem usa o quê

| Porta | Protocolo | Serviço | Observação de segurança |
|---|---|---|---|
| 20/21 | TCP | FTP | Credenciais em texto puro → prefira SFTP/FTPS |
| 22 | TCP | SSH / SFTP | Alvo constante de força bruta; use chave + bloqueio de tentativas |
| 23 | TCP | Telnet | Texto puro — **não use** |
| 25 / 587 | TCP | SMTP | Relay aberto = spam |
| 53 | **UDP** e TCP | DNS | UDP para consultas; TCP para respostas grandes e transferência de zona |
| 67/68 | UDP | DHCP | Veja o guia de DHCP |
| 69 | UDP | TFTP | Sem autenticação |
| 80 | TCP | HTTP | Texto puro |
| 123 | UDP | NTP | Horário certo é essencial para correlacionar logs |
| 161/162 | UDP | SNMP | Comunidade `public` = vazamento de configuração; use SNMPv3 |
| 389 / 636 | TCP | LDAP / LDAPS | Diretório (Active Directory) |
| 443 | TCP (e UDP no HTTP/3) | HTTPS | — |
| 445 | TCP | SMB | Historicamente explorado por worms; **nunca exponha à internet** |
| 514 | UDP | Syslog | Sem criptografia/garantia por padrão |
| 1194 | UDP | OpenVPN | — |
| 3306 | TCP | MySQL | Não exponha à internet |
| 3389 | TCP | RDP | Alvo frequente de força bruta e ransomware |
| 5432 | TCP | PostgreSQL | Não exponha à internet |
| 10050/10051 | TCP | Zabbix agent / server | Restrinja por IP |
| 51820 | UDP | WireGuard | — |

> 💡 **Porta não é garantia de serviço!** Qualquer programa pode escutar em qualquer porta. Malware frequentemente usa **443/TCP** justamente para se misturar ao tráfego HTTPS normal. Por isso, análise séria olha **o conteúdo e o comportamento**, não só a porta.

---

## 12. QUIC

O **QUIC** (base do **HTTP/3**) roda sobre **UDP/443**, mas implementa por conta própria:

- Entrega confiável e ordenada (como o TCP)
- Criptografia **TLS 1.3 embutida** (quase todo o cabeçalho também é criptografado)
- Conexão mais rápida (menos idas e vindas)
- Migração de conexão (trocar do Wi-Fi para o 4G sem cair)

Hoje uma fatia enorme do tráfego web (Google, YouTube, Meta, Cloudflare) usa QUIC.

> 🔐 **Visão cyber:**
> - Firewalls e proxies que inspecionam tráfego TCP/TLS **enxergam bem menos** do QUIC.
> - Muitas empresas **bloqueiam UDP/443** para forçar o navegador a voltar para HTTPS sobre TCP, onde conseguem aplicar inspeção e filtragem.
> - Regra antiga "UDP é só DNS e coisas simples" **não vale mais**: tráfego UDP alto na 443 é normal hoje.

---

## 13. Por que a camada de transporte importa em segurança

1. **Firewalls trabalham aqui.** A maioria das regras é "permitir/negar protocolo + porta + IP".
2. **Firewalls stateful** acompanham o **estado TCP**: só deixam entrar respostas de conexões que **saíram de dentro**.
3. **Superfície de ataque = portas abertas.** Inventariar portas é um dos primeiros passos de qualquer auditoria.
4. **Disponibilidade:** os próprios mecanismos do TCP (estado, handshake) e a falta deles no UDP (sem verificação de origem) podem ser abusados para negação de serviço.
5. **Detecção:** padrões anormais de flags, estados e volume por porta são sinais clássicos de varredura, DoS, exfiltração e C2.

---

## 14. Ameaças comuns (visão conceitual)

> ⚠️ Esta seção explica as ameaças em nível **conceitual**, para que você entenda o risco e saiba **reconhecer e mitigar**. Nada aqui deve ser testado fora de um lab próprio e isolado ou sem **autorização formal por escrito**.

### 14.1 Reconhecimento de portas

**Ideia:** descobrir quais serviços estão expostos observando como o alvo responde a tentativas de conexão (SYN-ACK, RST ou silêncio — seção 4).

**Como aparece para o Blue Team:**
- Um único IP tocando **muitas portas diferentes** de um host em pouco tempo.
- Ou tocando a **mesma porta** em **muitos hosts** (varredura horizontal).
- Grande quantidade de conexões que **nunca completam** o handshake.
- Flags com combinações anormais.

**Por que importa:** é normalmente a **primeira fase** de um ataque. Detectá-la cedo dá tempo de reagir.

### 14.2 SYN flood (esgotamento de estado TCP)

**Ideia:** enviar uma enxurrada de SYNs sem nunca completar o handshake. O servidor guarda cada conexão "meio aberta" em memória (`SYN_RECV`) até esgotar a fila — e clientes legítimos não conseguem mais conectar. É um ataque à **disponibilidade**.

**Sinais:** explosão de conexões em `SYN_RECV`, muitos SYN de origens variadas, servidor lento ou recusando conexões.

### 14.3 Amplificação/reflexão com UDP

**Ideia:** como o UDP não confirma a origem, um atacante pode enviar pequenas consultas a serviços UDP públicos mal configurados **com o IP de origem falsificado** como o da vítima. Os serviços respondem com respostas **muito maiores** — e todas vão para a vítima. Resultado: **DDoS** de grande volume.

Serviços historicamente abusados: DNS (resolvers abertos), NTP, SNMP, SSDP, Memcached, CLDAP.

> 💡 É o mesmo princípio do *Smurf attack* do guia de broadcasts: **IP falsificado + amplificação**.

**Lição para quem administra servidores:** não deixe serviços UDP **abertos para a internet** sem necessidade (resolver DNS aberto, SNMP com `public`, Memcached exposto). Senão seu servidor vira **arma** contra terceiros.

### 14.4 Injeção / encerramento forçado de conexões

**Ideia:** um equipamento posicionado no caminho do tráfego pode enviar RSTs forjados para derrubar conexões, ou tentar injetar dados numa sessão sem criptografia.

**Por que hoje é mais difícil:** ISNs aleatórios, validação rigorosa de números de sequência nos sistemas modernos e — principalmente — **criptografia (TLS/SSH)**, que torna inútil a injeção de conteúdo.

### 14.5 Canais de comando e controle (C2) e exfiltração

**Ideia:** malware mantém conexões de saída para o servidor do atacante, frequentemente em portas "inocentes" (443/TCP, 53/UDP) para se misturar ao tráfego normal. Dados roubados podem sair em pequenos pedaços (inclusive escondidos em consultas DNS).

**Sinais:** conexões periódicas e regulares (*beaconing*) para o mesmo IP, volume de saída incomum, consultas DNS longas e aleatórias, processos desconhecidos com conexões `ESTABLISHED`.

---

## 15. Defesas

### 15.1 Princípios

| Princípio | Na prática |
|---|---|
| **Menor superfície** | Feche/desinstale serviços que não usa |
| **Default deny** | Firewall bloqueia tudo e libera só o necessário |
| **Filtragem de saída** | Não deixe toda máquina sair para qualquer porta da internet |
| **Segmentação** | Banco de dados só aceita conexões do servidor de aplicação |
| **Criptografia** | TLS, SSH, VPN — protegem conteúdo mesmo com tráfego interceptado |

### 15.2 Firewall stateful (exemplos)

**Linux com `ufw` (simples):**

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.0.0/24 to any port 22 proto tcp   # SSH só da rede local
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

**Linux com `nftables` (conceito de stateful):**

```
table inet filtro {
  chain entrada {
    type filter hook input priority 0; policy drop;
    ct state established,related accept   # respostas de conexões já existentes
    ct state invalid drop                 # pacotes TCP sem sentido (flags estranhas etc.)
    iif lo accept
    tcp dport 22 ip saddr 192.168.0.0/24 accept
    tcp dport 443 accept
  }
}
```

**Cisco IOS (ACL estendida):**

```
ip access-list extended ENTRADA-WAN
 permit tcp any host 200.10.20.5 eq 443
 permit tcp any any established        ! retornos de conexões iniciadas de dentro
 deny   ip any any log
```

### 15.3 Contra SYN flood

- **SYN cookies** (no Linux: `net.ipv4.tcp_syncookies = 1`, ativado por padrão na maioria das distros): o servidor não guarda estado até o handshake completar.
- Limites de taxa no firewall, proteção anti-DDoS do provedor/CDN.

### 15.4 Contra amplificação UDP

- Não exponha serviços UDP sem necessidade; restrinja resolvers DNS à rede interna.
- **BCP 38 / filtragem de entrada (ingress filtering)** e **uRPF** em provedores e roteadores de borda: descartam pacotes com IP de origem impossível — atacando o problema na raiz (o IP falsificado).
- Rate limiting de respostas (ex.: RRL em servidores DNS).

### 15.5 Hardening de serviços

- SSH: desativar login de root e senha, usar chaves, **fail2ban**.
- Banco de dados escutando só em `127.0.0.1` ou na VLAN interna.
- Atualizações em dia.

---

## 16. TCP/UDP como fonte de evidência

Para o Blue Team, a camada de transporte gera muitos dados úteis:

| Fonte | O que mostra |
|---|---|
| **Logs de firewall** | Conexões permitidas/bloqueadas (5-tupla, horário, ação) |
| **NetFlow / IPFIX** | Quem falou com quem, quanto, por quanto tempo — sem o conteúdo |
| **Zeek (`conn.log`)** | Cada conexão com estado final, bytes, duração |
| **Suricata / Snort** | Alertas por assinatura (flags anormais, varreduras, padrões de C2) |
| **`ss` / `netstat` no host** | Conexões e portas abertas **agora**, com o processo dono |
| **Sysmon (Windows, evento 3)** | Conexões de rede por processo |

**Cenário típico de SOC:**

> Alerta: *"Workstation 192.168.10.57 faz conexão a cada 60 segundos para 185.x.x.x:443, sempre com ~300 bytes."*
>
> Conexões **regulares**, **pequenas** e **constantes** para um IP sem reputação = padrão de **beaconing**. Próximos passos: identificar o processo dono da conexão no host (`ss -tnp` / Sysmon), verificar reputação do IP, isolar a máquina se confirmado.

**Ideias de monitoramento (SIEM / Zabbix):**

| Métrica | Por que alertar |
|---|---|
| Nova porta em `LISTEN` num servidor | Serviço inesperado / persistência |
| Nº de conexões `SYN_RECV` | SYN flood |
| Pico de conexões bloqueadas no firewall vindas de um IP | Varredura |
| Tráfego de saída por porta incomum | Exfiltração / C2 |
| Muitas retransmissões TCP | Problema de rede (disponibilidade) |
| Serviço não responde na porta esperada | Indisponibilidade |

> 💡 **Ideia de portfólio:** no seu projeto de **Zabbix**, use os itens `net.tcp.service[...]` e `net.tcp.listen[...]` para checar se os serviços esperados estão no ar — e crie um alerta para quando uma porta **inesperada** começar a escutar.

---

## 17. Visão Red Team x Blue Team

| Tema | 🔴 Red Team pergunta… | 🔵 Blue Team pergunta… |
|---|---|---|
| Portas abertas | "Quais serviços estão expostos e em quais versões?" | "Sei exatamente quais portas deveriam estar abertas? Monitoro mudanças?" |
| Firewall | "As regras retornam RST ou descartam?" | "Estou usando *default deny* e logando bloqueios?" |
| UDP | "Há serviços UDP esquecidos (SNMP, TFTP)?" | "Existe algum serviço UDP exposto que pode ser usado em amplificação?" |
| Saída | "Consigo sair para a internet por qualquer porta?" | "Filtro tráfego de saída? Detecto beaconing?" |
| QUIC | "O tráfego via UDP/443 passa sem inspeção?" | "Preciso bloquear QUIC para manter visibilidade?" |
| Disponibilidade | "O serviço aguenta muitas conexões incompletas?" | "SYN cookies e rate limit estão ativos?" |
| Evidência | — | "Consigo dizer qual processo abriu cada conexão suspeita?" |

---

## 18. Mão na massa: comandos e filtros

Comandos de **observação da sua própria máquina** — seguros e muito usados em Help Desk e SOC.

### Ver portas abertas e conexões

```bash
# Linux
ss -tuln          # portas TCP/UDP em escuta (listen), numérico
ss -tunp          # conexões ativas + processo dono (use sudo para ver todos)
ss -s             # resumo de conexões por estado
ss -tan state syn-recv | wc -l   # quantas conexões meio abertas

# Windows
netstat -ano                     # conexões + PID
netstat -ano | findstr LISTENING
Get-NetTCPConnection | Sort-Object State     # PowerShell
tasklist /FI "PID eq 1234"       # qual programa é o PID
```

> 👀 **Exercício de Blue Team:** rode `ss -tulnp` (ou `netstat -ano`) e identifique **cada** porta em escuta. Para cada uma, responda: "que programa é esse e eu preciso dele?".

### Testar se uma porta responde (no seu próprio serviço)

```bash
nc -vz 127.0.0.1 22                       # Linux (netcat)
Test-NetConnection 127.0.0.1 -Port 3389   # Windows PowerShell
```

### Capturar com tcpdump

```bash
sudo tcpdump -i eth0 -n 'tcp[tcpflags] & tcp-syn != 0'   # pacotes com SYN
sudo tcpdump -i eth0 -n 'tcp[tcpflags] & tcp-rst != 0'   # resets
sudo tcpdump -i eth0 -n udp port 53                      # consultas DNS
sudo tcpdump -i eth0 -n port 443                         # HTTPS (TCP e QUIC)
```

### Filtros úteis no Wireshark

```
tcp.flags.syn == 1 && tcp.flags.ack == 0    # início de conexões (SYN)
tcp.flags.syn == 1 && tcp.flags.ack == 1    # SYN-ACK (porta aberta respondendo)
tcp.flags.reset == 1                        # resets
tcp.analysis.retransmission                 # retransmissões (perda de pacotes)
tcp.analysis.flags                          # todos os "problemas" TCP detectados
tcp.stream eq 5                             # uma conversa específica
udp                                         # só UDP
dns                                         # DNS
quic                                        # QUIC / HTTP3
icmp.type == 3 && icmp.code == 3            # Port Unreachable (porta UDP fechada)
```

**Recursos do Wireshark que valem ouro:**
- *Statistics → Conversations*: quem fala com quem e quanto.
- *Statistics → Protocol Hierarchy*: proporção de TCP, UDP, DNS, TLS…
- *Botão direito → Follow → TCP Stream*: reconstrói a conversa inteira (ótimo para ver por que HTTP e Telnet são inseguros!).
- *Statistics → Flow Graph*: desenha o handshake visualmente.

---

## 19. Troubleshooting

| Sintoma | Causa provável | Como verificar |
|---|---|---|
| "Connection refused" | Porta fechada (serviço parado) → RST | `ss -tuln` no servidor; serviço está rodando? |
| "Connection timed out" | Firewall descartando, host fora do ar ou rota errada | `ping`, `traceroute`, regras do firewall |
| Site carrega lento / trava | Perda de pacotes → retransmissões | Wireshark: `tcp.analysis.retransmission` |
| Serviço não aceita mais conexões | Fila de conexões cheia (carga ou SYN flood) | `ss -s`, contagem de `SYN_RECV` |
| DNS falha de vez em quando | UDP bloqueado/perdido, ou resposta grande exigindo TCP/53 bloqueado | Testar `nslookup` / `dig +tcp` |
| VoIP com cortes | Perda/atraso de UDP | Jitter e perda no Wireshark (*Telephony → RTP*) |
| Aplicação "funciona local mas não remoto" | Serviço escutando só em `127.0.0.1` | `ss -tuln`: o endereço é `127.0.0.1` ou `0.0.0.0`? |

> 🛠️ **Dica de Help Desk:** "*refused*" e "*timed out*" contam histórias diferentes. **Refused** = cheguei na máquina, mas ninguém atende naquela porta. **Timeout** = algo no caminho (firewall, rota, host desligado) impediu a resposta.

---

## 20. Exercícios para o seu lab

1. **Ver o handshake com os próprios olhos**
   Abra o Wireshark, filtre `tcp.port == 443`, acesse um site e use *Statistics → Flow Graph*. Identifique SYN, SYN-ACK, ACK e o FIN no final.

2. **TCP x UDP no Packet Tracer**
   No modo *Simulation*, acesse uma página web de um servidor e faça uma consulta DNS. Compare os PDUs: quantos pacotes cada um gerou? Onde está o handshake?

3. **Inventário de portas (Blue Team)**
   Rode `ss -tulnp` ou `netstat -ano` na sua máquina. Monte uma tabela "porta → protocolo → processo → preciso disso?". Desative o que não precisar.

4. **Refused x Timeout**
   Numa VM Linux do lab, suba um serviço (ex.: `python3 -m http.server 8080`). Teste a conexão de outra VM. Depois pare o serviço e teste de novo (refused). Por fim, bloqueie a porta com `ufw deny 8080` e teste (timeout). Capture os três casos no Wireshark.

5. **Por que texto puro é perigoso**
   No lab, acesse o `http.server` da VM e use *Follow → TCP Stream*: tudo aparece legível. Compare com uma conexão HTTPS — só dados criptografados.

6. **Firewall stateful**
   Configure `ufw` com `default deny incoming`, libere só o SSH vindo da sua rede e verifique que a navegação de saída continua funcionando (graças ao estado `established`).

7. **Monitoramento (ponte com o projeto Zabbix)**
   Crie itens que verifiquem se as portas 22 e 80 do servidor do lab respondem e um alerta para quando o serviço cair.

---

## 21. Resumo e glossário

### Resumo em 12 frases

1. TCP e UDP são protocolos da **camada 4 (transporte)**: entregam dados ao **programa** certo, identificado pela **porta**.
2. Uma conexão é identificada pela **5-tupla**: protocolo, IP e porta de origem, IP e porta de destino.
3. **TCP** é orientado à conexão, confiável, ordenado e com controle de fluxo e congestionamento.
4. O TCP abre conexões com o **three-way handshake** (SYN → SYN-ACK → ACK) e fecha com **FIN** (educado) ou **RST** (abrupto).
5. **UDP** é sem conexão, sem garantia, com cabeçalho de **8 bytes** — ideal quando velocidade importa mais que perfeição (DNS, VoIP, jogos, DHCP).
6. **QUIC/HTTP3** roda sobre **UDP/443** e traz confiabilidade e criptografia próprias.
7. Porta aberta = **superfície de ataque**; feche o que não usa.
8. As respostas **SYN-ACK / RST / silêncio** revelam se uma porta está aberta, fechada ou filtrada.
9. O **estado** que o TCP mantém pode ser esgotado (**SYN flood**) → mitigado com **SYN cookies**.
10. A **falta de verificação de origem** do UDP permite **amplificação/reflexão** → mitigada com filtragem de origem (BCP 38) e não expondo serviços UDP.
11. **Firewalls stateful** com *default deny* e filtragem de saída são a defesa base.
12. Conexões, estados e fluxos (firewall, NetFlow, Zeek, `ss`) são evidência central para o **SOC**.

### Glossário rápido

| Termo | Significado |
|---|---|
| **ACK** | Confirmação de recebimento |
| **Beaconing** | Conexões periódicas de malware ao servidor do atacante |
| **C2** | *Command and Control* — infraestrutura que controla malware |
| **Datagrama** | Unidade de dados do UDP |
| **Firewall stateful** | Firewall que acompanha o estado das conexões |
| **Handshake** | Negociação inicial do TCP (SYN, SYN-ACK, ACK) |
| **ISN** | Número de sequência inicial (aleatório) |
| **MSS** | Maior quantidade de dados por segmento TCP |
| **NetFlow** | Registro de metadados de fluxos de rede |
| **Porta efêmera** | Porta temporária usada pelo cliente |
| **QUIC** | Protocolo de transporte moderno sobre UDP (base do HTTP/3) |
| **RST** | Flag que encerra/recusa uma conexão de forma abrupta |
| **Segmento** | Unidade de dados do TCP |
| **Socket** | Combinação de IP + protocolo + porta |
| **SYN cookies** | Técnica que evita guardar estado antes do handshake terminar |
| **SYN flood** | Ataque que esgota conexões meio abertas |
| **TIME_WAIT** | Estado de espera após o fechamento da conexão |
| **Window** | Quantidade de dados que o receptor aceita sem confirmar |

---

> ⚖️ **Ética:** todo conhecimento sobre ameaças aqui serve para **entender, detectar e mitigar**. Testes só em redes e máquinas suas (lab isolado) ou com **autorização formal por escrito** e escopo definido.