# Roteamento entre Redes: um guia didático com olhar de Cybersecurity

> **Para quem é este material:** quem está estudando redes (ex.: Cisco *Conceitos Básicos de Redes*) e quer entender **como um pacote atravessa várias redes até o destino** — e por que o roteamento é, ao mesmo tempo, peça-chave da **segmentação defensiva** e um alvo valioso. É continuação dos guias *Broadcasts e Roteadores*, *DHCP* e *TCP x UDP*.

---

## Sumário

1. [O que é roteamento](#1-o-que-é-roteamento)
2. [A primeira decisão: local ou remoto?](#2-a-primeira-decisão-local-ou-remoto)
3. [O gateway padrão](#3-o-gateway-padrão)
4. [A jornada de um pacote, salto a salto](#4-a-jornada-de-um-pacote-salto-a-salto)
5. [A tabela de roteamento em detalhe](#5-a-tabela-de-roteamento-em-detalhe)
6. [Como o roteador escolhe a rota](#6-como-o-roteador-escolhe-a-rota)
7. [Roteamento estático](#7-roteamento-estático)
8. [Roteamento dinâmico](#8-roteamento-dinâmico)
9. [Roteamento entre VLANs](#9-roteamento-entre-vlans)
10. [NAT e PAT: roteando para a internet](#10-nat-e-pat)
11. [TTL, ICMP e traceroute](#11-ttl-icmp-e-traceroute)
12. [Roteamento no IPv6](#12-roteamento-no-ipv6)
13. [Linux como roteador](#13-linux-como-roteador)
14. [Por que roteamento é assunto de segurança](#14-por-que-roteamento-é-assunto-de-segurança)
15. [Ameaças ao roteamento (visão conceitual)](#15-ameaças-ao-roteamento-visão-conceitual)
16. [Defesas e hardening](#16-defesas-e-hardening)
17. [Roteamento como fonte de evidência (SOC)](#17-roteamento-como-fonte-de-evidência)
18. [Visão Red Team x Blue Team](#18-visão-red-team-x-blue-team)
19. [Mão na massa: comandos](#19-mão-na-massa-comandos)
20. [Troubleshooting](#20-troubleshooting)
21. [Exercícios para o seu lab](#21-exercícios-para-o-seu-lab)
22. [Resumo e glossário](#22-resumo-e-glossário)

---

## 1. O que é roteamento

**Roteamento** é o processo de **escolher o caminho** que um pacote deve seguir para ir de uma rede até outra.

- Dentro da **mesma rede** (mesmo domínio de broadcast), quem entrega é o **switch**, usando MAC → isso é **comutação (switching)**.
- Entre **redes diferentes**, quem entrega é o **roteador**, usando IP → isso é **roteamento (routing)**.

> 💡 **Analogia dos Correios:** sua carta sai de São Paulo para Recife. Nenhuma agência conhece o caminho inteiro. Cada centro de distribuição só sabe "**para onde mandar a seguir**" (o próximo salto). Etapa por etapa, a carta chega. Roteadores funcionam exatamente assim: **decisão salto a salto (hop-by-hop)**.

Na internet, um pacote passa tipicamente por **10 a 20 roteadores** até o destino — e cada um decide **sozinho**, olhando apenas a própria tabela.

---

## 2. A primeira decisão: local ou remoto?

Antes de enviar qualquer pacote, **o próprio host** responde a uma pergunta:

> *"O destino está na minha rede ou em outra?"*

Ele descobre fazendo um **AND binário** entre os IPs e a **máscara de sub-rede**.

**Exemplo:** meu PC é `192.168.1.10/24`.

```
Destino A: 192.168.1.50
  Meu IP   AND máscara → 192.168.1.0
  Destino  AND máscara → 192.168.1.0    → MESMA rede → entrega direta (local)

Destino B: 8.8.8.8
  Meu IP   AND máscara → 192.168.1.0
  Destino  AND máscara → 8.8.8.0        → OUTRA rede → manda para o gateway
```

> ⚠️ **Máscara errada = roteamento errado.** Se um PC tiver máscara `/16` numa rede `/24`, ele vai achar que IPs de outras sub-redes são "locais" e nunca vai mandá-los ao gateway. É um erro clássico de Help Desk.

---

## 3. O gateway padrão

O **gateway padrão (default gateway)** é o IP do roteador da sua rede local — a "porta de saída" para qualquer destino remoto.

Regras importantes:

- O gateway **precisa estar na mesma sub-rede** do host.
- Normalmente é o primeiro (`.1`) ou o último (`.254`) IP utilizável — é só convenção.
- Normalmente o host o recebe via **DHCP** (opção 3 — veja o guia de DHCP).

> 🔐 **Visão cyber:** o gateway é o **ponto por onde passa todo o tráfego que sai da rede**. Por isso:
> - Quem **se passa pelo gateway** (via DHCP falso ou outras técnicas de camada 2) consegue se posicionar **no meio** da comunicação.
> - O gateway é o **melhor ponto para filtrar e registrar** tráfego (firewall, logs, IDS).

---

## 4. A jornada de um pacote, salto a salto

Topologia:

```
 [PC-A]──────[R1]──────────[R2]──────[Servidor]
 192.168.1.10  .1 | 10.0.0.1  10.0.0.2 | .1   172.16.0.20
 Rede 192.168.1.0/24   Rede 10.0.0.0/30   Rede 172.16.0.0/24
```

PC-A envia um pacote para o Servidor (`172.16.0.20`):

| Trecho | IP origem | IP destino | MAC origem | MAC destino | TTL |
|---|---|---|---|---|---|
| PC-A → R1 | 192.168.1.10 | 172.16.0.20 | PC-A | R1 (Gi0/0) | 64 |
| R1 → R2 | 192.168.1.10 | 172.16.0.20 | R1 (Gi0/1) | R2 (Gi0/0) | 63 |
| R2 → Servidor | 192.168.1.10 | 172.16.0.20 | R2 (Gi0/1) | Servidor | 62 |

**O que cada roteador faz ao receber o pacote:**

1. Recebe o quadro, confere o MAC de destino (é para mim?) e remove o cabeçalho de camada 2.
2. Lê o **IP de destino**.
3. Consulta a **tabela de roteamento** e escolhe a melhor rota.
4. **Decrementa o TTL** (se chegar a 0, descarta e avisa a origem com ICMP).
5. Recalcula o checksum do cabeçalho IP.
6. Monta um **novo quadro** com o MAC da sua interface de saída e o MAC do próximo salto.
7. Envia pela interface de saída.

> 💡 **Regra de ouro:**
> - **IPs (origem e destino) permanecem iguais** do início ao fim (exceto quando há NAT).
> - **MACs mudam a cada salto**, porque cada trecho é uma rede local diferente.
>
> 🔐 **Consequência para forense:** o MAC que aparece num log de firewall é o do **último salto** (normalmente um roteador), não o da máquina original. Para identificar o host real atrás de um IP, você precisa dos registros **daquela rede local** (tabela ARP do gateway, logs de DHCP, tabela de MACs do switch).

---

## 5. A tabela de roteamento em detalhe

Exemplo de `show ip route` num roteador Cisco:

```
Codes: C - connected, L - local, S - static, O - OSPF, D - EIGRP, R - RIP, * - candidate default

Gateway of last resort is 200.10.20.1 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 200.10.20.1
      10.0.0.0/8 is variably subnetted
C        10.0.0.0/30 is directly connected, GigabitEthernet0/1
L        10.0.0.1/32 is directly connected, GigabitEthernet0/1
O     172.16.0.0/24 [110/2] via 10.0.0.2, 00:12:31, GigabitEthernet0/1
C     192.168.1.0/24 is directly connected, GigabitEthernet0/0
L     192.168.1.1/32 is directly connected, GigabitEthernet0/0
```

Lendo a linha do OSPF:

```
O     172.16.0.0/24   [110/2]    via 10.0.0.2   00:12:31   GigabitEthernet0/1
│     │               │   │      │              │          │
│     │               │   │      │              │          └ interface de saída
│     │               │   │      │              └ há quanto tempo a rota existe
│     │               │   │      └ próximo salto (next hop)
│     │               │   └ métrica (custo)
│     │               └ distância administrativa (confiabilidade da fonte)
│     └ rede de destino / prefixo
└ origem da rota (O = OSPF)
```

**Tipos de rota:**

| Código | Tipo | Como surge |
|---|---|---|
| **C** | Conectada | Automaticamente, ao configurar IP numa interface ativa |
| **L** | Local | O próprio IP da interface (/32) |
| **S** | Estática | Configurada manualmente |
| **S\*** | Rota padrão | `0.0.0.0/0` — "qualquer outro destino" |
| **O / D / R / B** | Dinâmica | Aprendida por OSPF / EIGRP / RIP / BGP |

> Se não houver rota para o destino **e** não houver rota padrão, o roteador **descarta** o pacote e envia **ICMP Destination Unreachable** à origem.

---

## 6. Como o roteador escolhe a rota

O roteador aplica três critérios, **nesta ordem**:

### 6.1 Prefixo mais longo (Longest Prefix Match) — sempre vence

A rota **mais específica** ganha, independentemente da origem.

Destino: `10.1.1.50`

| Rota na tabela | Casa com 10.1.1.50? | Bits iguais |
|---|---|---|
| `0.0.0.0/0` | Sim | 0 |
| `10.0.0.0/8` | Sim | 8 |
| `10.1.0.0/16` | Sim | 16 |
| **`10.1.1.0/24`** | **Sim** | **24 ← vencedora** |
| `10.1.2.0/24` | Não | — |

### 6.2 Distância administrativa (AD) — para o **mesmo** prefixo vindo de fontes diferentes

Mede **o quanto o roteador confia na fonte** da rota. **Menor é melhor.**

| Origem | AD (Cisco) |
|---|---|
| Conectada | 0 |
| Estática | 1 |
| eBGP | 20 |
| EIGRP (interno) | 90 |
| OSPF | 110 |
| IS-IS | 115 |
| RIP | 120 |
| iBGP | 200 |
| Desconhecida | 255 (nunca usada) |

### 6.3 Métrica — para o mesmo prefixo vindo do **mesmo** protocolo

Cada protocolo mede "custo" de um jeito:

| Protocolo | Métrica |
|---|---|
| RIP | Número de saltos (máx. 15) |
| OSPF | Custo baseado na largura de banda |
| EIGRP | Banda + atraso (por padrão) |
| BGP | Atributos/políticas (AS_PATH, local preference…) |

> 🔐 **Visão cyber:** o *longest prefix match* é uma **regra poderosa**: quem conseguir anunciar um prefixo **mais específico** que o legítimo "rouba" o tráfego, mesmo com rotas legítimas presentes. Esse é o princípio por trás de incidentes de **sequestro de rotas BGP** na internet (seção 15).

---

## 7. Roteamento estático

O administrador escreve as rotas à mão.

```
! Sintaxe: ip route <rede destino> <máscara> <próximo salto | interface>
ip route 172.16.0.0 255.255.255.0 10.0.0.2

! Rota padrão (para a internet)
ip route 0.0.0.0 0.0.0.0 200.10.20.1

! Rota estática flutuante (backup): AD 5, só entra se a principal cair
ip route 0.0.0.0 0.0.0.0 201.30.40.1 5

! Rota "null" (buraco negro): descarta tráfego para uma rede
ip route 192.0.2.0 255.255.255.0 Null0
```

| Vantagens | Desvantagens |
|---|---|
| Simples e previsível | Não escala em redes grandes |
| Zero tráfego de protocolo | Não se adapta sozinha a falhas |
| **Mais seguro:** não há anúncios para falsificar | Erro humano = rede fora do ar |
| Controle total do caminho | Muita manutenção |

**Quando usar:** redes pequenas, redes "stub" (com uma única saída), rota padrão para a internet, rotas de backup.

> 🔐 A rota para **Null0** também é usada em segurança: **blackhole routing** (ou RTBH, *Remotely Triggered Black Hole*) descarta tráfego destinado a um IP sob ataque DDoS ou tráfego para destinos maliciosos conhecidos.

---

## 8. Roteamento dinâmico

Os roteadores **conversam entre si** e trocam informações sobre as redes que conhecem. Se um link cai, eles **recalculam** sozinhos (convergência).

### 8.1 Famílias de protocolos

| Categoria | Ideia | Exemplos |
|---|---|---|
| **Vetor de distância** | "Ouvi do meu vizinho que a rede X está a N saltos" — conhece só a direção e a distância | RIP, (EIGRP é um "vetor de distância avançado") |
| **Estado de enlace (link-state)** | Cada roteador tem o **mapa completo** da área e calcula o melhor caminho (algoritmo de Dijkstra) | OSPF, IS-IS |
| **Vetor de caminho** | Escolhe rotas por **políticas** entre organizações | BGP |

| Escopo | Nome | Exemplos |
|---|---|---|
| Dentro de uma organização | **IGP** (Interior Gateway Protocol) | OSPF, EIGRP, RIP, IS-IS |
| Entre organizações (internet) | **EGP** (Exterior Gateway Protocol) | **BGP** |

### 8.2 Protocolos em uma frase

- **RIP:** antigo, simples, métrica = saltos (máx. 15). Bom para estudar, ruim para produção.
- **OSPF:** padrão aberto, link-state, organizado em **áreas** (área 0 = backbone). O mais comum em empresas.
- **EIGRP:** criado pela Cisco, convergência rápida.
- **BGP:** o protocolo que **mantém a internet unida**. Cada organização (provedor, big tech, banco) é um **AS (Autonomous System)** com número próprio, e anuncia seus prefixos aos vizinhos.

### 8.3 Exemplo: OSPF básico (Cisco IOS)

```
router ospf 1
 router-id 1.1.1.1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.3 area 0
 passive-interface GigabitEthernet0/0     ! não fala OSPF na rede dos usuários
!
show ip ospf neighbor
show ip route ospf
```

> 🔐 Repare no **`passive-interface`**: a rede `192.168.1.0/24` continua sendo **anunciada**, mas o roteador **não envia nem aceita** mensagens OSPF na interface dos usuários. Sem isso, qualquer host da rede de usuários poderia **ouvir** os anúncios (revelando a topologia interna) e, se não houver autenticação, tentar **participar** do protocolo.

### 8.4 Estático x dinâmico

| Critério | Estático | Dinâmico |
|---|---|---|
| Escala | Pequena | Grande |
| Adaptação a falhas | Manual | Automática |
| Uso de CPU/banda | Nenhum | Algum |
| Superfície de ataque | Mínima | Maior (anúncios podem ser falsificados se não autenticados) |
| Previsibilidade | Total | Depende da convergência |

---

## 9. Roteamento entre VLANs

**VLANs** separam um switch em vários domínios de broadcast (veja o guia de broadcasts). Mas e quando a VLAN de RH precisa acessar a VLAN de servidores? Precisa de **roteamento**.

### 9.1 Router-on-a-stick (roteador com subinterfaces)

Um único link **trunk** entre switch e roteador, com uma **subinterface por VLAN**:

```
                   trunk (802.1Q)
 [Switch]═══════════════════════[Roteador]
  VLAN 10 (RH)                   Gi0/0.10 → 192.168.10.1
  VLAN 20 (TI)                   Gi0/0.20 → 192.168.20.1
  VLAN 99 (Servidores)           Gi0/0.99 → 192.168.99.1
```

```
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
!
interface GigabitEthernet0/0.99
 encapsulation dot1Q 99
 ip address 192.168.99.1 255.255.255.0
```

### 9.2 Switch camada 3 (SVIs)

Mais rápido e comum em empresas: o próprio switch roteia, com uma **interface virtual (SVI)** por VLAN.

```
ip routing
!
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
interface Vlan20
 ip address 192.168.20.1 255.255.255.0
```

> 🔐 **O ponto de segurança mais importante deste guia:**
> **Ligar o roteamento entre VLANs, sem filtros, desfaz grande parte da segmentação.** VLANs separam o *broadcast*, mas se o roteador encaminha **tudo** entre elas, a VLAN de visitantes alcança a de servidores normalmente.
> A segmentação real exige **ACLs ou um firewall** no ponto de roteamento, definindo **quem pode falar com quem e em quais portas**:

```
! VLAN de visitantes (30) só pode sair para a internet; nada interno
ip access-list extended VISITANTES-IN
 deny   ip 192.168.30.0 0.0.0.255 10.0.0.0 0.255.255.255
 deny   ip 192.168.30.0 0.0.0.255 172.16.0.0 0.15.255.255
 deny   ip 192.168.30.0 0.0.0.255 192.168.0.0 0.0.255.255
 permit ip 192.168.30.0 0.0.0.255 any
!
interface Vlan30
 ip access-group VISITANTES-IN in
```

---

## 10. NAT e PAT

IPs privados (RFC 1918) **não são roteados na internet**:

| Faixa | Prefixo |
|---|---|
| `10.0.0.0` – `10.255.255.255` | `/8` |
| `172.16.0.0` – `172.31.255.255` | `/12` |
| `192.168.0.0` – `192.168.255.255` | `/16` |

Para sair, o roteador de borda **traduz** o IP privado para um IP público:

| Tipo | Como funciona | Uso |
|---|---|---|
| **NAT estático** | 1 IP privado ↔ 1 IP público fixo | Publicar um servidor |
| **NAT dinâmico** | Pool de IPs públicos | Pouco usado hoje |
| **PAT / NAT overload** | **Muitos** IPs privados → **1** IP público, diferenciados pela **porta** | Toda casa e quase toda empresa |
| **Port forwarding** | Porta pública → IP:porta interno | Expor serviço interno |

**Tabela de tradução PAT (exemplo):**

```
IP interno:porta         IP público:porta          Destino
192.168.1.10:51544  →    200.10.20.5:40001    →    142.250.79.14:443
192.168.1.11:51544  →    200.10.20.5:40002    →    142.250.79.14:443
```

```
! Cisco IOS - PAT
interface GigabitEthernet0/0
 ip nat inside
interface GigabitEthernet0/1
 ip nat outside
!
access-list 1 permit 192.168.1.0 0.0.0.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload
!
show ip nat translations
```

> 🔐 **Visão cyber:**
> - **NAT não é firewall.** Ele dificulta conexões de fora para dentro como efeito colateral, mas a proteção de verdade vem das regras de firewall.
> - **Port forwarding** e **UPnP** abrem buracos no perímetro — revise-os sempre.
> - **Forense com NAT/CGNAT:** um IP público pode representar **milhares** de usuários (em provedores com CGNAT). Para identificar quem fez uma conexão, é preciso **IP + porta de origem + horário exato** — por isso logs de NAT e **relógios sincronizados (NTP)** são essenciais.

---

## 11. TTL, ICMP e traceroute

### 11.1 TTL

Cada roteador subtrai 1 do **TTL** (*Time To Live*). Em 0, o pacote é descartado. Isso evita que pacotes circulem para sempre em **loops de roteamento**.

| Sistema | TTL inicial típico |
|---|---|
| Linux / macOS / Android | 64 |
| Windows | 128 |
| Equipamentos de rede (Cisco etc.) | 255 |

> 🔐 Um ping que volta com **TTL 118** provavelmente veio de um **Windows** a ~10 saltos (128 − 10). É uma forma simples de *fingerprinting* — usada tanto em reconhecimento quanto em troubleshooting.

### 11.2 Mensagens ICMP ligadas ao roteamento

| Tipo | Nome | Quando aparece |
|---|---|---|
| 0 / 8 | Echo Reply / Request | `ping` |
| 3 | **Destination Unreachable** | Sem rota (código 0), host inalcançável (1), porta fechada (3), proibido por filtro (13) |
| 5 | **Redirect** | Roteador avisa: "existe um caminho melhor, use outro gateway" |
| 11 | **Time Exceeded** | TTL chegou a 0 (base do traceroute) |

### 11.3 Como o traceroute funciona

```
Envia pacote com TTL=1 → 1º roteador descarta → responde "Time Exceeded" → revela salto 1
Envia pacote com TTL=2 → 2º roteador descarta → responde "Time Exceeded" → revela salto 2
... até chegar ao destino
```

- Linux `traceroute`: usa UDP por padrão. Windows `tracert`: usa ICMP.
- Linhas com `* * *` = roteador que não responde (filtro ou política), não necessariamente falha.

> 🔐 **Visão cyber:** traceroute revela a **topologia** (quantos saltos, IPs internos de roteadores, provedores). Muitas organizações **limitam ICMP Time Exceeded** na borda para não expor a estrutura interna — mas cuidado: bloquear **todo** ICMP quebra coisas importantes (como a descoberta de MTU do caminho).

---

## 12. Roteamento no IPv6

A lógica é a mesma (longest prefix match, AD, protocolos), com diferenças:

| Aspecto | IPv4 | IPv6 |
|---|---|---|
| Ativar roteamento (Cisco) | Ativo por padrão | `ipv6 unicast-routing` |
| Rota padrão | `0.0.0.0/0` | `::/0` |
| Descoberta do gateway | DHCP / manual | **Router Advertisements (RA)** + endereço *link-local* (`fe80::`) |
| Protocolos | OSPFv2, RIPv2, EIGRP | **OSPFv3**, RIPng, EIGRP for IPv6 |
| NAT | Comum | Normalmente **não** é usado — cada host tem IP global |
| Próximo salto | IP do vizinho | Normalmente o **link-local** do vizinho |

```
ipv6 unicast-routing
ipv6 route ::/0 2001:db8:acad:1::1
show ipv6 route
```

> 🔐 **Visão cyber:**
> - Sem NAT, **cada host IPv6 pode ser alcançável da internet** se o firewall permitir → a política de firewall IPv6 precisa ser tão rígida quanto a de IPv4.
> - "Rede só IPv4" muitas vezes tem **IPv6 ativo nos hosts**. Um RA falso pode tornar um dispositivo não autorizado o **gateway IPv6** da rede → use **RA Guard** e monitore.

---

## 13. Linux como roteador

Qualquer Linux com duas interfaces pode rotear — ótimo para lab.

```bash
# Ver a tabela de roteamento
ip route
ip route get 8.8.8.8          # qual rota seria usada para esse destino

# Adicionar/remover rotas (temporário)
sudo ip route add 172.16.0.0/24 via 10.0.0.2
sudo ip route del 172.16.0.0/24
sudo ip route add default via 192.168.1.1

# Habilitar o encaminhamento de pacotes (vira roteador)
sudo sysctl -w net.ipv4.ip_forward=1
# permanente: em /etc/sysctl.d/99-router.conf → net.ipv4.ip_forward = 1

# NAT (masquerade) com nftables, saindo pela eth0
sudo nft add table ip nat
sudo nft add chain ip nat postrouting '{ type nat hook postrouting priority 100 ; }'
sudo nft add rule ip nat postrouting oifname "eth0" masquerade
```

> 🔐 **Visão cyber:** `net.ipv4.ip_forward = 1` numa máquina que **não deveria** ser roteador é um **sinal de alerta**. Um host comprometido pode ser transformado em **ponte entre redes** que deveriam estar isoladas (ex.: um notebook ligado ao Wi-Fi de visitantes e à rede cabeada ao mesmo tempo). Auditar esse parâmetro em servidores e estações é uma boa prática de hardening.

---

## 14. Por que roteamento é assunto de segurança

1. **O roteador decide quem alcança quem.** Rotas + ACLs **são** a política de segmentação da rede.
2. **Segmentação limita a movimentação lateral:** se um PC de usuário for comprometido, as regras de roteamento/filtragem determinam até onde o atacante consegue chegar.
3. **Protocolos de roteamento confiam nos vizinhos:** sem autenticação, anúncios falsos podem desviar tráfego.
4. **O ponto de roteamento é o melhor lugar para enxergar o tráfego** entre segmentos (logs, NetFlow, IDS).
5. **Roteadores são infraestrutura crítica:** comprometer um roteador = controlar o tráfego que passa por ele.

> 💡 **Frase para guardar:** *rota é permissão de alcance. Toda rota que existe sem necessidade é um caminho a mais para um atacante.*

---

## 15. Ameaças ao roteamento (visão conceitual)

> ⚠️ Esta seção é **conceitual**, para você entender o risco e saber **detectar e mitigar**. Testes só em lab próprio isolado ou com **autorização formal por escrito**.

### 15.1 Movimentação lateral e pivoteamento

**Ideia:** depois de comprometer uma máquina, o atacante a usa como **ponto de apoio** para alcançar outras redes que ela consegue rotear — por exemplo, um servidor web na DMZ que tem rota para o banco de dados interno.

**Por que importa:** a maioria dos incidentes graves envolve essa fase. **A segmentação bem feita é o que transforma "uma máquina comprometida" em "um incidente contido" em vez de "a empresa inteira comprometida".**

**Sinais:** um host de usuário iniciando conexões para muitas sub-redes internas; servidores da DMZ abrindo conexões para a rede interna; tráfego entre segmentos que normalmente não conversam.

### 15.2 Injeção de rotas em protocolos dinâmicos

**Ideia:** um dispositivo não autorizado que consiga participar de um protocolo de roteamento sem autenticação (ex.: OSPF ativo na rede de usuários) pode anunciar rotas falsas — desviando tráfego para si (**man-in-the-middle**) ou para lugar nenhum (**negação de serviço**).

**Mitigação:** autenticação nos protocolos, `passive-interface`, filtros de rotas.

### 15.3 Sequestro de rotas BGP (BGP hijacking)

**Ideia:** na internet, um AS anuncia — por erro ou má-fé — prefixos que **não lhe pertencem** (ou prefixos mais específicos). Pelo *longest prefix match*, parte da internet passa a enviar o tráfego para o lugar errado.

**Casos públicos conhecidos:** em 2008, um anúncio indevido tirou o YouTube do ar globalmente por algumas horas; em 2018, um sequestro de rotas de um serviço DNS da Amazon foi usado para redirecionar usuários de uma carteira de criptomoedas para um site falso.

**Mitigação:** **RPKI** (assinatura criptográfica que diz qual AS pode anunciar cada prefixo), filtros de prefixos entre provedores, monitoramento de anúncios do seu prefixo. Para quem não é provedor: **TLS com validação de certificado** impede que um desvio de rota vire roubo de dados silencioso.

### 15.4 ICMP Redirect malicioso

**Ideia:** mensagens ICMP Redirect forjadas podem tentar convencer um host a usar outro "gateway".

**Mitigação:** desativar o envio e a aceitação de redirects onde não são necessários (seção 16).

### 15.5 IP spoofing

**Ideia:** pacotes com **IP de origem falsificado** — base de ataques de amplificação (veja o guia de TCP x UDP) e tentativas de contornar regras baseadas em IP.

**Mitigação:** **uRPF** e filtros anti-spoofing na borda (BCP 38): "um pacote que entra pela interface da internet **não pode** ter IP de origem da minha rede interna".

### 15.6 Comprometimento do próprio roteador

Senha padrão, gerência exposta à internet, firmware vulnerável, Telnet/HTTP, SNMP com comunidade `public` (veja o guia de broadcasts e roteadores). Consequências: alteração de rotas, DNS ou NAT; captura de tráfego; uso como pivô ou em botnets.

---

## 16. Defesas e hardening

### 16.1 Arquitetura

| Prática | Efeito |
|---|---|
| **Segmentação por função** (usuários, servidores, gerência, IoT, visitantes, DMZ) | Limita movimentação lateral |
| **ACLs/firewall entre segmentos** com *default deny* | "Rota existe" ≠ "acesso permitido" |
| **Rede de gerência separada** (out-of-band) | Painel de roteadores e switches inacessível aos usuários |
| **Filtragem de saída** | Servidores só saem para onde precisam |
| **Zero Trust** | Não confiar em algo só por estar "dentro" da rede |

### 16.2 Protocolos de roteamento

```
! OSPF com autenticação (exemplo com chave MD5 — em equipamentos novos, prefira SHA)
interface GigabitEthernet0/1
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 <senha-forte>
!
router ospf 1
 passive-interface default                     ! passivo em tudo...
 no passive-interface GigabitEthernet0/1       ! ...menos nos links entre roteadores
```

- Autenticar **todos** os protocolos dinâmicos (OSPF, EIGRP, BGP).
- `passive-interface` nas redes de usuários.
- Filtrar quais prefixos podem ser aprendidos/anunciados.
- Para BGP: RPKI, filtros de prefixo, limite máximo de prefixos.

### 16.3 Plano de dados (tráfego que passa)

```
! Anti-spoofing: descarta pacotes com IP de origem que não deveria vir por essa interface
interface GigabitEthernet0/1
 ip verify unicast source reachable-via rx
 no ip redirects
 no ip unreachables          ! (avalie: reduz informação exposta)
 no ip proxy-arp
 no ip directed-broadcast
!
no ip source-route           ! desativa "source routing" (origem escolhe o caminho)
```

**No Linux (hosts que não são roteadores):**

```
# /etc/sysctl.d/99-hardening.conf
net.ipv4.ip_forward = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.rp_filter = 1           # anti-spoofing (reverse path filter)
net.ipv6.conf.all.accept_redirects = 0
```

### 16.4 Plano de gerência (acesso ao roteador)

```
ip ssh version 2
no ip http server
ip http secure-server                  ! se precisar de interface web, só HTTPS
!
access-list 10 permit 192.168.99.0 0.0.0.255   ! só a rede de gerência
line vty 0 4
 transport input ssh
 access-class 10 in
 login local
 exec-timeout 10 0
!
logging host 192.168.99.50             ! logs para o servidor central (SIEM)
ntp server 192.168.99.10               ! horário correto nos logs
service timestamps log datetime msec
```

---

## 17. Roteamento como fonte de evidência

| Fonte | O que revela |
|---|---|
| **Logs de ACL/firewall entre segmentos** | Tentativas de acesso entre redes que não deveriam conversar |
| **NetFlow/IPFIX** dos roteadores | Fluxos entre segmentos: volume, portas, horários |
| **Logs de NAT** | Qual IP interno estava atrás do IP público num horário |
| **Mudanças na tabela de roteamento** | Rotas novas inesperadas, vizinhos OSPF/BGP que caíram ou surgiram |
| **Logs de configuração** (quem mudou o quê) | Alterações não autorizadas no roteador |
| **Monitoramento externo do seu prefixo** | Sequestro de rotas BGP |

**Ideias de alertas (SIEM / Zabbix):**

| Evento | Por que alertar |
|---|---|
| Novo vizinho OSPF/EIGRP/BGP | Dispositivo não autorizado no protocolo |
| Rota padrão mudou | Desvio de tráfego ou falha |
| Bloqueios repetidos de ACL entre VLANs vindos do mesmo host | Possível varredura / movimentação lateral |
| Host de usuário falando com sub-rede de gerência | Violação de segmentação |
| Mudança de configuração fora da janela de manutenção | Alteração não autorizada |
| Link/interface de roteador caiu | Disponibilidade |
| `ip_forward=1` em servidor que não é roteador | Possível ponte entre redes |

---

## 18. Visão Red Team x Blue Team

| Tema | 🔴 Red Team pergunta… | 🔵 Blue Team pergunta… |
|---|---|---|
| Rotas do host | "Quais redes eu alcanço a partir desta máquina?" | "Esse host precisa mesmo alcançar todas essas redes?" |
| Inter-VLAN | "O roteamento entre VLANs tem filtros?" | "Minhas ACLs seguem *default deny* entre segmentos?" |
| Protocolos dinâmicos | "O OSPF fala na rede de usuários? Tem autenticação?" | "`passive-interface` e autenticação estão configurados?" |
| Gerência | "Consigo alcançar o SSH/web dos roteadores da rede de usuários?" | "A gerência está isolada e restrita por ACL?" |
| Pivô | "Algum host tem duas interfaces ou `ip_forward` ligado?" | "Audito hosts com duas redes e encaminhamento ativo?" |
| Topologia | "O traceroute revela a estrutura interna?" | "Quanto da topologia estou expondo?" |
| Evidência | — | "Tenho NetFlow e logs de ACL entre segmentos e de NAT?" |

---

## 19. Mão na massa: comandos

### No host (observação)

```bash
# Linux
ip addr                 # IP e máscara
ip route                # tabela de roteamento do host
ip route get 1.1.1.1    # qual rota/gateway será usado
traceroute 8.8.8.8
tracepath 8.8.8.8       # alternativa sem root, mostra MTU
mtr 8.8.8.8             # traceroute contínuo com perda por salto
sysctl net.ipv4.ip_forward

# Windows
ipconfig /all
route print
tracert 8.8.8.8
pathping 8.8.8.8        # traceroute + estatística de perda
Get-NetRoute            # PowerShell
Find-NetRoute -RemoteIPAddress 8.8.8.8
```

> 👀 **Exercício rápido:** rode `ip route` (ou `route print`) e identifique: rota padrão, gateway, redes conectadas. Depois rode `traceroute 8.8.8.8` e conte quantos saltos estão dentro da sua casa, do seu provedor e fora dele.

### No roteador Cisco (Packet Tracer)

```
show ip route
show ip route 172.16.0.20        ! qual rota casa com esse destino
show ip interface brief
show ip protocols
show ip ospf neighbor
show ip nat translations
show access-lists                ! contadores de "matches" de cada regra
show running-config | section router
debug ip routing                 ! (só em lab!)
```

### Filtros no Wireshark

```
icmp.type == 11                  # Time Exceeded (traceroute / loops)
icmp.type == 3                   # Destination Unreachable
icmp.type == 5                   # Redirect (suspeito se não esperado)
ospf                             # tráfego OSPF (não deveria aparecer na rede de usuários!)
ip.ttl < 5                       # TTL baixo: possível loop ou traceroute
```

---

## 20. Troubleshooting

Método de **dentro para fora**:

```
1. ipconfig / ip addr      → tenho IP, máscara e gateway corretos?
2. ping 127.0.0.1          → a pilha TCP/IP local funciona?
3. ping <meu IP>           → a interface funciona?
4. ping <gateway>          → chego no roteador local?
5. ping <IP remoto>        → o roteamento funciona?  (ex.: 8.8.8.8)
6. nslookup google.com     → o DNS funciona?
7. traceroute <destino>    → onde exatamente o caminho para?
```

| Sintoma | Causa provável | Verificação |
|---|---|---|
| Pinga o gateway, mas não sai da rede | Rota padrão ausente no roteador ou NAT quebrado | `show ip route`, `show ip nat translations` |
| Pinga IPs, mas não abre sites | DNS | `nslookup` |
| Não pinga o gateway | Gateway errado, VLAN errada, cabo, máscara | `ipconfig`, porta do switch |
| Ida funciona, volta não | **Falta rota de retorno** no roteador do outro lado | Tabelas de roteamento dos **dois** lados |
| Traceroute fica em loop entre dois IPs | **Loop de roteamento** (rotas apontando uma para a outra) | Rotas estáticas dos dois roteadores |
| Uma VLAN acessa a outra, mas não o contrário | ACL aplicada só num sentido / errada | `show access-lists` (contadores) |
| `* * *` no meio do traceroute, mas o destino responde | Roteador intermediário não responde ICMP — **normal** | — |

> 🛠️ **Dica de ouro:** *"ida funciona, volta não"* é o erro mais comum em labs de roteamento estático. **Todo caminho precisa de rota de ida E de volta.**

---

## 21. Exercícios para o seu lab

1. **Local x remoto na mão**
   Para o host `172.20.5.130/26`, diga se cada destino é local ou remoto: `172.20.5.150`, `172.20.5.200`, `172.20.4.10`. (Dica: calcule a rede de cada um.)

2. **Roteamento estático com 3 redes (Packet Tracer)**
   Monte 2 roteadores e 3 redes (como na seção 4). Configure rotas estáticas, faça o ping funcionar e, no modo *Simulation*, observe o **MAC mudando** e o **TTL diminuindo** a cada salto.

3. **Provoque o erro "ida sem volta"**
   Remova a rota de retorno em R2 e veja o ping falhar. Explique por quê.

4. **OSPF**
   Substitua as rotas estáticas por OSPF na área 0. Derrube um link redundante e observe a convergência. Depois configure `passive-interface` e autenticação.

5. **Router-on-a-stick + segmentação**
   Crie VLANs RH, TI, Servidores e Visitantes. Configure o roteamento entre elas e confirme que **todas se falam**. Depois aplique ACLs para que Visitantes **só** acessem a internet e RH só acesse os Servidores na porta 443. Teste e verifique os contadores com `show access-lists`.

6. **NAT/PAT**
   Configure PAT no roteador de borda e veja a tabela `show ip nat translations` enquanto vários PCs acessam um "servidor da internet".

7. **Hardening do roteador**
   Aplique o checklist da seção 16.4 (SSH, ACL de gerência, logs, NTP) e documente o antes/depois.

8. **Monitoramento (ponte com o projeto Zabbix)**
   Monitore via SNMP as interfaces de um roteador (ou do seu roteador doméstico, se suportar) e crie alertas de link caído.

---

## 22. Resumo e glossário

### Resumo em 12 frases

1. **Roteamento** é escolher o caminho de um pacote entre redes diferentes, **salto a salto**.
2. O host usa a **máscara** para decidir se o destino é local ou remoto; remoto vai para o **gateway padrão**.
3. Ao longo do caminho, os **IPs se mantêm** (sem NAT) e os **MACs mudam a cada salto**.
4. A **tabela de roteamento** lista redes, próximo salto, interface, distância administrativa e métrica.
5. A escolha segue: **prefixo mais longo → distância administrativa → métrica**.
6. **Rotas estáticas** são simples e seguras, mas não escalam; **protocolos dinâmicos** (OSPF, EIGRP, BGP) se adaptam, mas precisam de autenticação.
7. **Roteamento entre VLANs** sem filtros desfaz a segmentação; use **ACLs/firewall** com *default deny*.
8. **NAT/PAT** permite sair para a internet com IPs privados — mas **NAT não é firewall**.
9. **TTL** evita loops e é a base do **traceroute**, que também revela topologia.
10. Principais riscos: **movimentação lateral**, injeção de rotas, **sequestro BGP**, redirects, IP spoofing e roteador comprometido.
11. Defesas: segmentação, autenticação de protocolos, `passive-interface`, uRPF, desativar redirects/source routing, gerência isolada e logs.
12. Logs de ACL, **NetFlow**, NAT e mudanças de rota são evidências centrais para o **SOC**.

### Glossário rápido

| Termo | Significado |
|---|---|
| **AD (Distância Administrativa)** | Confiabilidade da origem de uma rota (menor = melhor) |
| **AS (Autonomous System)** | Rede sob uma única administração na internet, com número próprio |
| **BGP** | Protocolo de roteamento entre organizações na internet |
| **Convergência** | Tempo até todos os roteadores concordarem sobre as rotas após uma mudança |
| **Gateway padrão** | Roteador para onde vão os pacotes destinados a outras redes |
| **Hop (salto)** | Passagem por um roteador |
| **Inter-VLAN routing** | Roteamento entre VLANs |
| **Longest prefix match** | Regra de escolher a rota mais específica |
| **Métrica** | Custo de uma rota dentro de um protocolo |
| **Movimentação lateral** | Atacante avançando de um host comprometido para outros |
| **NAT / PAT** | Tradução de endereços (PAT usa portas para compartilhar um IP) |
| **NetFlow** | Registro de metadados dos fluxos de tráfego |
| **Next hop** | Próximo roteador no caminho |
| **OSPF** | Protocolo de roteamento link-state, padrão aberto |
| **Passive-interface** | Interface que não envia nem recebe mensagens do protocolo de roteamento |
| **Rota padrão** | `0.0.0.0/0` — usada quando nenhuma outra rota casa |
| **RPKI** | Validação criptográfica de quem pode anunciar cada prefixo no BGP |
| **SVI** | Interface virtual de VLAN num switch camada 3 |
| **TTL** | Contador de saltos de um pacote |
| **uRPF** | Verificação anti-spoofing pelo caminho reverso |

---

> ⚖️ **Ética:** todo conhecimento sobre ameaças aqui serve para **entender, detectar e mitigar**. Testes só em redes suas (lab isolado) ou com **autorização formal por escrito** e escopo definido.