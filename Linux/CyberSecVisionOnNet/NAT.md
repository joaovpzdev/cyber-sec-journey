# NAT (Network Address Translation): um guia didático com olhar de Cybersecurity

> **Para quem é este material:** quem está estudando redes (ex.: Cisco *Conceitos Básicos de Redes*) e quer entender o NAT **por dentro**: por que ele existe, como a tradução acontece, onde ele aparece no dia a dia (inclusive no **Docker** e no **WSL2**) e o que ele significa para segurança, exposição e investigação de incidentes. É continuação dos guias *Broadcasts e Roteadores*, *DHCP*, *TCP x UDP*, *Roteamento entre Redes* e *Utilitários de Teste de Rede*.

---

## Sumário

1. [O problema: os endereços IPv4 acabaram](#1-o-problema-os-endereços-ipv4-acabaram)
2. [Endereços privados x públicos](#2-endereços-privados-x-públicos)
3. [O que é NAT](#3-o-que-é-nat)
4. [Vocabulário oficial: inside/outside, local/global](#4-vocabulário-oficial)
5. [Tipos de NAT](#5-tipos-de-nat)
6. [PAT passo a passo: a tabela de tradução](#6-pat-passo-a-passo)
7. [SNAT, DNAT e port forwarding](#7-snat-dnat-e-port-forwarding)
8. [CGNAT: o NAT do provedor](#8-cgnat-o-nat-do-provedor)
9. [Quando o NAT atrapalha (e como se contorna)](#9-quando-o-nat-atrapalha)
10. [NAT no seu dia a dia: roteador de casa, Docker e WSL2](#10-nat-no-seu-dia-a-dia)
11. [NAT e IPv6](#11-nat-e-ipv6)
12. [Configurando na prática](#12-configurando-na-prática)
13. [NAT é segurança? O mito e a realidade](#13-nat-é-segurança)
14. [Riscos ligados ao NAT (visão conceitual)](#14-riscos-ligados-ao-nat-visão-conceitual)
15. [Defesas e boas práticas](#15-defesas-e-boas-práticas)
16. [NAT como fonte de evidência (SOC / forense)](#16-nat-como-fonte-de-evidência)
17. [Visão Red Team x Blue Team](#17-visão-red-team-x-blue-team)
18. [Mão na massa: comandos de verificação](#18-mão-na-massa-comandos-de-verificação)
19. [Troubleshooting](#19-troubleshooting)
20. [Exercícios para o seu lab](#20-exercícios-para-o-seu-lab)
21. [Resumo e glossário](#21-resumo-e-glossário)

---

## 1. O problema: os endereços IPv4 acabaram

O IPv4 tem 32 bits → cerca de **4,3 bilhões** de endereços. Parece muito, mas:

- Há mais de **15 bilhões** de dispositivos conectados (celulares, notebooks, TVs, câmeras, IoT…).
- Grandes blocos foram distribuídos de forma generosa nos primeiros anos da internet.
- Os registros regionais esgotaram seus estoques livres na década de 2010 — incluindo o **LACNIC**, responsável pela América Latina.

O IPv6 é a solução definitiva, mas sua adoção é gradual. Enquanto isso, o mundo funciona graças a uma "gambiarra genial": **o NAT**.

> 💡 **Analogia do prédio comercial:** um prédio tem **um único endereço na rua** (IP público), mas centenas de salas (IPs privados). Toda carta que sai leva o endereço do prédio como remetente. A **recepção (NAT)** anota quem enviou cada carta, e quando a resposta chega, sabe para qual sala entregar.

---

## 2. Endereços privados x públicos

A **RFC 1918** reservou faixas para uso **interno**, que qualquer um pode usar e que **não são roteadas na internet**:

| Faixa | Prefixo | Quantidade de endereços | Uso típico |
|---|---|---|---|
| `10.0.0.0` – `10.255.255.255` | `10.0.0.0/8` | ~16,7 milhões | Grandes empresas, nuvem, VPNs |
| `172.16.0.0` – `172.31.255.255` | `172.16.0.0/12` | ~1 milhão | Empresas, **Docker** (`172.17.0.0/16`) |
| `192.168.0.0` – `192.168.255.255` | `192.168.0.0/16` | ~65 mil | Redes domésticas |

Outras faixas especiais que você vai encontrar:

| Faixa | Uso |
|---|---|
| `100.64.0.0/10` | **CGNAT** (espaço compartilhado do provedor — seção 8) |
| `127.0.0.0/8` | Loopback (a própria máquina) |
| `169.254.0.0/16` | Link-local / APIPA (sem DHCP) |

> 🔐 **Visão cyber:**
> - Um pacote vindo **da internet** com IP de origem **privado** é, por definição, **falsificado ou mal configurado** → deve ser descartado na borda (filtro *anti-bogon*).
> - Ver seu roteador com IP WAN em `100.64.x.x` ou em outra faixa privada = você está **atrás de CGNAT**.

---

## 3. O que é NAT

**NAT (Network Address Translation)** é a técnica em que um dispositivo (roteador, firewall, servidor Linux) **reescreve os endereços IP** (e às vezes as **portas**) dos pacotes que passam por ele, mantendo uma **tabela** para traduzir as respostas de volta.

```
 Rede interna (privada)           Roteador NAT              Internet (pública)
                                                       
 192.168.0.10:51544 ──────►  [ troca origem para    ] ──────► 200.10.20.5:40001 → 142.250.79.14:443
                              [ 200.10.20.5:40001     ]
                              [ e ANOTA na tabela     ]
 192.168.0.10:51544 ◄──────  [ desfaz a troca        ] ◄────── 142.250.79.14:443 → 200.10.20.5:40001
```

O que o NAT altera:

| Campo | Alterado? |
|---|---|
| IP de origem e/ou destino | ✅ Sim |
| Porta de origem e/ou destino (PAT) | ✅ Às vezes |
| Checksums IP/TCP/UDP | ✅ Recalculados |
| Conteúdo (payload) | ❌ Normalmente não — exceto por "ajudantes" de protocolo (seção 9) |

> 💡 Repare: o NAT **quebra um princípio original da internet**, o de que cada máquina tem um endereço único e é alcançável fim a fim. Isso tem consequências para aplicações, para segurança e para investigação — como veremos.

---

## 4. Vocabulário oficial

A Cisco (e o exame CCNA) usa quatro termos. Eles parecem confusos, mas seguem uma lógica:

- **Inside / Outside** → **de qual lado** está o host (dentro ou fora da sua rede).
- **Local / Global** → **de qual ponto de vista** o endereço é visto (de dentro ou de fora).

| Termo | O que é | Exemplo |
|---|---|---|
| **Inside Local** | IP real do host interno (como a rede interna o vê) | `192.168.0.10` |
| **Inside Global** | Como o host interno aparece **para a internet** | `200.10.20.5` |
| **Outside Global** | IP real do host externo | `142.250.79.14` |
| **Outside Local** | Como o host externo aparece **para a rede interna** (geralmente igual ao global) | `142.250.79.14` |

```
  [PC 192.168.0.10]  ──── inside ────  [Roteador NAT]  ──── outside ────  [Servidor 142.250.79.14]
   Inside Local                         Inside Global = 200.10.20.5        Outside Global
```

E as interfaces do roteador são marcadas como **`ip nat inside`** (lado LAN) e **`ip nat outside`** (lado WAN).

---

## 5. Tipos de NAT

| Tipo | Mapeamento | Direção típica | Uso |
|---|---|---|---|
| **NAT estático** | 1 IP privado ↔ 1 IP público, **fixo** | Entrada e saída | Publicar um servidor (web, e-mail) |
| **NAT dinâmico** | IPs privados ↔ **pool** de IPs públicos (1 para 1, por ordem de chegada) | Saída | Raro hoje; se o pool acaba, novos hosts ficam sem acesso |
| **PAT / NAT overload** | **Muitos** IPs privados → **1** IP público, diferenciados pela **porta** | Saída | **Toda casa e quase toda empresa** |
| **Port forwarding** (NAT estático de porta / DNAT) | IP público:porta → IP privado:porta | Entrada | Expor um serviço interno específico |
| **CGNAT** | NAT feito **pelo provedor**, antes do seu roteador | Saída | Provedores com falta de IPv4 |
| **NAT64** | IPv6 ↔ IPv4 | Saída | Redes só-IPv6 acessando sites só-IPv4 |

### PAT: quantas conexões cabem num IP?

A porta tem 16 bits → até **~65 mil portas** por IP público **por protocolo e por destino**. Na prática, um único IP público atende centenas ou milhares de usuários simultâneos.

> 🔐 **Visão cyber:** o tipo de NAT determina a **exposição**:
> - **PAT** (só saída): conexões iniciadas **de fora** não têm entrada na tabela → são descartadas (por padrão).
> - **NAT estático / port forwarding**: o host interno fica **diretamente alcançável** da internet naquele IP/porta → precisa de firewall, hardening e monitoramento como qualquer servidor público.

---

## 6. PAT passo a passo

Cenário: dois PCs da sua casa acessam o mesmo site ao mesmo tempo, e por coincidência usam a **mesma porta de origem**.

```
 PC-A 192.168.0.10 ─┐
                    ├── [Roteador: LAN 192.168.0.1 | WAN 200.10.20.5] ─── Internet ─── Site 142.250.79.14:443
 PC-B 192.168.0.11 ─┘
```

**1. Saída do PC-A**

```
Antes do NAT:  192.168.0.10:51544 → 142.250.79.14:443
Depois do NAT: 200.10.20.5:51544  → 142.250.79.14:443   (porta mantida, estava livre)
```

**2. Saída do PC-B (mesma porta de origem!)**

```
Antes do NAT:  192.168.0.11:51544 → 142.250.79.14:443
Depois do NAT: 200.10.20.5:51545  → 142.250.79.14:443   (porta TROCADA para não colidir)
```

**3. A tabela de tradução fica assim:**

| Proto | Inside Local | Inside Global | Outside Global | Tempo restante |
|---|---|---|---|---|
| TCP | 192.168.0.10:51544 | 200.10.20.5:51544 | 142.250.79.14:443 | 86 400 s |
| TCP | 192.168.0.11:51544 | 200.10.20.5:51545 | 142.250.79.14:443 | 86 400 s |

**4. Volta das respostas**

```
Chega: 142.250.79.14:443 → 200.10.20.5:51545
Roteador consulta a tabela → é do PC-B
Entrega: 142.250.79.14:443 → 192.168.0.11:51544
```

**5. Chega um pacote que ninguém pediu:**

```
Chega: 45.x.x.x:1234 → 200.10.20.5:3389
Roteador consulta a tabela → nenhuma entrada, nenhum port forwarding
→ DESCARTA
```

### Tempo de vida das entradas

As traduções **expiram**. Valores típicos (variam por equipamento):

| Tipo | Timeout típico |
|---|---|
| TCP estabelecida | horas (ex.: 24 h no Cisco; ~5 dias no Linux por padrão) |
| TCP encerrada (FIN/RST) | segundos a poucos minutos |
| UDP | 30 s a 5 min |
| ICMP | ~60 s |

> **Sintoma clássico:** uma sessão SSH ou conexão de banco **cai depois de um tempo parado** → a entrada NAT expirou (ou o firewall stateful "esqueceu" a conexão). Solução: *keepalives* (ex.: `ServerAliveInterval 60` no SSH).

---

## 7. SNAT, DNAT e port forwarding

No mundo Linux/firewalls, a nomenclatura é outra — e mais intuitiva:

| Termo | O que traduz | Quando acontece | Exemplo |
|---|---|---|---|
| **SNAT** (*Source NAT*) | IP de **origem** | Na **saída** (postrouting) | LAN saindo para a internet |
| **Masquerade** | SNAT que usa automaticamente o IP da interface de saída | Na saída | Ideal quando o IP público é dinâmico |
| **DNAT** (*Destination NAT*) | IP/porta de **destino** | Na **entrada** (prerouting) | Port forwarding para um servidor interno |

### Port forwarding

```
Internet: cliente → 200.10.20.5:8443
Roteador (DNAT): troca destino para 192.168.0.50:443
Servidor interno 192.168.0.50 responde
Roteador desfaz a troca na volta
```

### Hairpin NAT (NAT loopback)

Problema comum: de **dentro** da rede, você acessa `200.10.20.5:8443` (seu próprio IP público) e **não funciona**. O roteador precisa "dar meia-volta" com o pacote — recurso chamado **hairpin NAT** ou **NAT loopback**, que nem todo roteador suporta. Alternativa: **DNS interno** apontando o nome do serviço direto para o IP privado (*split DNS*).

> 🔐 **Visão cyber:** cada port forwarding é um **buraco deliberado no perímetro**. Erros comuns:
> - Encaminhar **RDP (3389)**, **SMB (445)**, **bancos de dados** ou painéis administrativos direto para a internet.
> - Esquecer regras antigas apontando para IPs que hoje pertencem a **outra máquina** (o DHCP reaproveitou o IP!).
> - Achar que "mudar a porta" (ex.: RDP na 33890) protege — scanners de internet varrem **todas** as portas continuamente.

---

## 8. CGNAT: o NAT do provedor

Com a falta de IPv4, muitos provedores (especialmente de fibra, rádio e redes móveis) colocam **vários clientes atrás do mesmo IP público**:

```
 [Sua LAN 192.168.0.x] → [Seu roteador: WAN 100.64.12.34] → [CGNAT do provedor] → Internet (IP 177.x.x.x)
                          NAT nº 1 (o seu)                    NAT nº 2 (do provedor)
```

Isso é **NAT duplo** (às vezes chamado NAT444).

### Como saber se você está atrás de CGNAT

1. Veja o **IP WAN** no painel do seu roteador.
2. Compare com seu IP público real: `curl ifconfig.me`.
3. Se forem **diferentes**, ou se o WAN estiver em `100.64.0.0/10` (ou outra faixa privada) → há CGNAT.
4. Um `traceroute` também costuma mostrar IPs privados/`100.64.x.x` logo nos primeiros saltos.

### Consequências

| Efeito | Por quê |
|---|---|
| **Port forwarding não funciona** | Você não controla o NAT do provedor |
| Hospedar servidor em casa / acessar câmeras remotamente fica difícil | Ninguém de fora consegue iniciar conexão até você |
| Alguns jogos e P2P têm problemas | NAT "restrito" |
| **Bloqueios por IP afetam inocentes** | Se um vizinho de IP faz abuso, o IP compartilhado pode ser bloqueado por sites (CAPTCHAs, banimentos) |
| **Investigação exige porta de origem** | Um IP público = muitos clientes |

> 💡 **Soluções legítimas:** pedir IP público/fixo ao provedor (às vezes pago), usar **IPv6** (sem CGNAT), ou usar **túneis/VPN de saída** (ex.: Cloudflare Tunnel, Tailscale) que funcionam porque a conexão **sai** de dentro.

> 🔐 **Ponto forense importante (Brasil):** por causa do CGNAT, para identificar um usuário a partir de um registro de acesso é preciso **IP + porta de origem + data/hora com fuso**. O Marco Civil da Internet (Lei 12.965/2014) obriga provedores de aplicação a guardar registros de acesso, e a indústria e as autoridades passaram a exigir também o registro da **porta lógica de origem** justamente por causa do compartilhamento de IPs.

---

## 9. Quando o NAT atrapalha

O NAT foi pensado para conexões **de dentro para fora** em protocolos simples. Ele causa problemas quando:

### 9.1 O protocolo carrega o IP **dentro** dos dados

- **FTP ativo:** o cliente informa ao servidor, dentro do conteúdo, "conecte-se de volta em `192.168.0.10:porta`" — um IP privado inalcançável.
- **SIP (VoIP):** o mesmo problema com sinalização de chamadas → o famoso "áudio de um lado só".

Solução clássica: **ALGs (Application Layer Gateways)** — "ajudantes" que reescrevem o conteúdo. Funcionam, mas são fonte frequente de bugs (muitos guias de VoIP mandam **desativar o SIP ALG** do roteador).

> 🔐 Um ALG é um código que **analisa e modifica conteúdo** de protocolos complexos — portanto, mais superfície de ataque. Já houve pesquisas públicas mostrando abuso de ALGs para "abrir" portas em roteadores (técnicas como *NAT Slipstreaming*, 2020), corrigidas pelos navegadores e fabricantes. Lição: **desative ALGs que você não usa**.

### 9.2 Integridade do cabeçalho é verificada

- **IPsec AH** assina o cabeçalho IP → o NAT altera → a verificação falha.
- **IPsec ESP** esconde as portas → o PAT não consegue diferenciar.
- Solução: **NAT-T (NAT Traversal)**, que encapsula o IPsec em **UDP 4500**.

### 9.3 Alguém de fora precisa iniciar a conexão

- Chamadas de vídeo, jogos P2P, servidores caseiros.
- Soluções:
  - **STUN:** descobre "qual é meu IP/porta público".
  - **TURN:** um servidor de retransmissão quando não há outro jeito.
  - **ICE:** combina os dois (usado no WebRTC — Google Meet, Discord no navegador).
  - **UPnP / NAT-PMP / PCP:** o próprio dispositivo interno pede ao roteador para abrir uma porta (veja riscos na seção 14).

---

## 10. NAT no seu dia a dia

### 10.1 Roteador doméstico

Faz **PAT** (saída), geralmente com **UPnP ligado por padrão**, e permite **port forwarding** no painel. Muitas vezes está atrás de **CGNAT** do provedor.

### 10.2 Docker

O Docker usa NAT intensamente:

```
 Host Linux (eth0: 192.168.0.20)
   └── docker0 (bridge 172.17.0.1)
         ├── container web  172.17.0.2
         └── container db   172.17.0.3
```

- **Saída dos containers:** *masquerade* (SNAT) — o container sai para a internet com o IP do host.
- **`-p 8080:80`** (publicar porta): cria um **DNAT** — `192.168.0.20:8080` → `172.17.0.2:80`.

> 🔐 **Pegadinha de segurança muito comum:** as regras de DNAT do Docker são inseridas **antes** das regras do `ufw` / firewalld no fluxo do pacote. Resultado: uma porta publicada com `-p` pode ficar **acessível pela rede mesmo que o ufw diga que está bloqueada**.
> **Boas práticas:**
> - Publique só no loopback quando o acesso for local: `-p 127.0.0.1:5432:5432` (ex.: o **PostgreSQL** do seu projeto DashFinTrack).
> - No `docker-compose.yml`, use `"127.0.0.1:5432:5432"` em vez de `"5432:5432"`.
> - Não publique a porta do banco se só outro container precisa dele — containers na mesma rede Docker se falam pelo nome do serviço.
> - Para filtrar portas publicadas, use a cadeia `DOCKER-USER` do iptables.
> - Confira sempre "de fora" (de outra máquina) com um teste de porta.

### 10.3 WSL2

O WSL2 roda numa VM leve com rede própria, por padrão em **modo NAT**:

- A distro Linux recebe um IP privado (ex.: `172.2x.x.x`) que pode **mudar a cada reinício**.
- O Windows encaminha automaticamente `localhost` para o WSL, mas **outras máquinas da rede não alcançam** serviços do WSL sem configuração extra.
- Versões recentes do WSL oferecem o modo **mirrored** (`networkingMode=mirrored` no `.wslconfig`), em que o Linux compartilha as interfaces do Windows.


### 10.4 VirtualBox / VMware

| Modo de rede da VM | Comportamento |
|---|---|
| **NAT** | VM sai para a internet, mas ninguém de fora a alcança (precisa de port forwarding na VM) |
| **Rede NAT (NAT Network)** | Várias VMs numa rede NAT compartilhada, se enxergam entre si |
| **Bridge** | VM vira um host "real" na sua rede, com IP do seu roteador |
| **Host-only / Rede interna** | Isolada da internet |

> 🔐 **Para labs de segurança:** máquinas propositalmente vulneráveis devem ficar em **host-only / rede interna** — **nunca em bridge**, que as colocaria na sua rede doméstica real.

---

## 11. NAT e IPv6

O IPv6 tem endereços suficientes (2¹²⁸) para **cada dispositivo ter um IP global**. Por isso:

- **Não se usa NAT** no IPv6 em condições normais (existe o NPTv6, tradução de prefixo, para casos específicos).
- A conectividade volta a ser **fim a fim**.

> 🔐 **Consequência crítica de segurança:** com IPv4+NAT, muita gente se acostumou a estar "protegido" sem perceber que quem protegia era o **comportamento padrão do NAT**. No IPv6, se o roteador/firewall **permitir conexões de entrada**, os dispositivos internos ficam **diretamente alcançáveis**.
> → Por isso, roteadores domésticos sérios aplicam por padrão uma política **stateful "bloquear entrada, permitir saída"** também no IPv6. **Verifique o seu.** E em empresas, a política de firewall IPv6 precisa ser tão rígida quanto a de IPv4.

---

## 12. Configurando na prática

### 12.1 Cisco IOS — PAT (o mais comum)

```
interface GigabitEthernet0/0
 description LAN
 ip address 192.168.0.1 255.255.255.0
 ip nat inside
!
interface GigabitEthernet0/1
 description WAN
 ip address 200.10.20.5 255.255.255.248
 ip nat outside
!
access-list 1 permit 192.168.0.0 0.0.0.255
ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

### 12.2 Cisco IOS — NAT estático (servidor público)

```
ip nat inside source static 192.168.0.50 200.10.20.6
```

### 12.3 Cisco IOS — port forwarding (NAT estático de porta)

```
ip nat inside source static tcp 192.168.0.50 443 200.10.20.5 8443
```

### 12.4 Cisco IOS — NAT dinâmico com pool

```
ip nat pool POOL-PUBLICO 200.10.20.2 200.10.20.4 netmask 255.255.255.248
access-list 2 permit 192.168.10.0 0.0.0.255
ip nat inside source list 2 pool POOL-PUBLICO
```

### 12.5 Linux com nftables

```bash
# Habilitar o encaminhamento (o Linux vira roteador)
sudo sysctl -w net.ipv4.ip_forward=1
```

```
# /etc/nftables.conf (trecho)
table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    # DNAT / port forwarding: porta 8443 do roteador → servidor interno 443
    iifname "eth0" tcp dport 8443 dnat to 192.168.50.10:443
  }
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept;
    # SNAT / masquerade: LAN saindo pela eth0
    oifname "eth0" ip saddr 192.168.50.0/24 masquerade
  }
}

table inet filter {
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    iifname "eth1" oifname "eth0" accept                      # LAN → internet
    iifname "eth0" ip daddr 192.168.50.10 tcp dport 443 accept  # só o que foi encaminhado
  }
}
```

> 💡 Repare que o **NAT** (tabela `nat`) e a **filtragem** (tabela `filter`) são **coisas separadas**. Um DNAT sem a regra de `forward` correspondente não deixa nada passar — e um `forward` permissivo demais deixa passar coisas que não deviam. É a prova prática de que **NAT ≠ firewall**.

### 12.6 Equivalente com iptables (ainda muito encontrado)

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -s 192.168.50.0/24 -j MASQUERADE
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 8443 -j DNAT --to-destination 192.168.50.10:443
```

---

## 13. NAT é segurança?

### O mito

> "Estou atrás de NAT, então ninguém da internet consegue chegar nas minhas máquinas."

### A realidade

| O NAT **ajuda** porque… | O NAT **não protege** porque… |
|---|---|
| Por padrão, conexões iniciadas de fora **não têm entrada na tabela** e são descartadas | Ele **não inspeciona nem filtra** conteúdo — só traduz endereços |
| **Esconde** a estrutura interna (IPs privados, quantidade de hosts) | Tudo que **sai** de dentro é permitido: malware conecta "para fora" livremente e o NAT deixa voltar a resposta |
| | **Port forwarding** e **UPnP** criam entradas permanentes ou automáticas |
| | Não ajuda em nada contra ameaças **internas** (movimentação lateral, dispositivo comprometido na LAN) |
| | Não existe no **IPv6** — a "proteção acidental" some |
| | Phishing, downloads maliciosos e sites comprometidos chegam via conexões **iniciadas pelo próprio usuário** |

> 💡 **Frase para guardar:** *NAT é um tradutor, não um porteiro. O porteiro é o firewall.*
> A proteção que as pessoas atribuem ao NAT vem, na verdade, do **comportamento stateful** (aceitar só respostas a conexões iniciadas de dentro) — e isso deve ser configurado **explicitamente** num firewall, com regras que você conhece e controla.

---

## 14. Riscos ligados ao NAT (visão conceitual)

> ⚠️ Esta seção é **conceitual**, para você entender o risco e saber **detectar e mitigar**. Testes só em lab próprio isolado ou com **autorização formal por escrito**.

### 14.1 Port forwarding esquecido ou perigoso

Regras criadas "temporariamente" para um teste, um técnico ou um jogo, e nunca removidas. Serviços expostos (RDP, câmeras, NAS, painéis) são encontrados rapidamente por **varreduras automáticas que percorrem toda a internet** continuamente — um serviço exposto costuma receber tentativas de login em **minutos a horas**.

### 14.2 UPnP

O UPnP permite que **qualquer programa na rede interna** peça ao roteador para abrir portas, **sem autenticação**. Pensado para jogos e videochamadas, mas:

- **Malware** dentro da rede pode abrir portas para receber conexões do atacante.
- Dispositivos IoT inseguros abrem a si mesmos para a internet.
- Roteadores com UPnP **exposto no lado WAN** (falha de configuração/firmware) já foram abusados em larga escala para ataques de reflexão e para criar caminhos para a rede interna.

### 14.3 Conexões reversas (o NAT não barra saída)

Como o NAT deixa **tudo sair**, um dispositivo comprometido simplesmente **inicia a conexão para fora** (até o servidor de comando e controle do atacante), e o canal fica aberto nos dois sentidos. É por isso que **filtragem de saída** e **monitoramento de conexões** (guias de TCP x UDP e Utilitários) importam tanto.

### 14.4 Perda de visibilidade e atribuição

Do lado de fora, tudo parece vir de **um único IP**. Sem **logs de NAT**, é impossível dizer **qual máquina interna** fez uma conexão maliciosa ou recebeu uma notificação de abuso.

### 14.5 Esgotamento da tabela NAT

A tabela de traduções tem tamanho finito. Um host infectado abrindo milhares de conexões (ex.: participando de varreduras ou DDoS) pode **esgotar a tabela** ou as portas disponíveis → a internet "cai" para todos da rede. É um sintoma operacional que frequentemente **revela um host comprometido**.

### 14.6 Exposição acidental via Docker/VMs

Como visto na seção 10: portas publicadas pelo Docker contornando o firewall local, VMs vulneráveis em modo **bridge**, serviços do WSL expostos sem querer.

---

## 15. Defesas e boas práticas

### 15.1 Perímetro

| Prática | Detalhe |
|---|---|
| **Firewall stateful explícito** | Não dependa do "efeito colateral" do NAT; regras claras de entrada e saída |
| **Desativar UPnP** | Em empresas, sempre; em casa, sempre que possível |
| **Minimizar port forwarding** | Para acesso remoto, prefira **VPN** (WireGuard, OpenVPN) ou túneis com autenticação forte |
| **Revisar regras periodicamente** | Inventário de cada encaminhamento: quem pediu, para quê, até quando |
| **Reservas DHCP** para alvos de port forwarding | Evita que a regra aponte para outra máquina quando o IP mudar |
| **Filtragem de saída** | Servidores e IoT só saem para onde precisam |
| **Anti-spoofing/anti-bogon na WAN** | Descartar IPs privados vindos da internet |
| **Desativar ALGs não usados** | SIP ALG, por exemplo |
| **Gerência do roteador só pela LAN** | Painel nunca exposto na WAN |
| **Firewall IPv6 com política de entrada bloqueada** | Não existe "NAT protegendo" |

### 15.2 Serviços que precisam ficar expostos

Se algo precisa mesmo ser acessível da internet:

- Coloque-o numa **DMZ** (segmento separado, sem acesso livre à rede interna).
- **Autenticação forte** (MFA), atualizações em dia, *rate limiting*, fail2ban.
- **Reverse proxy** com TLS na frente da aplicação.
- Monitore os logs desse serviço com prioridade.

### 15.3 Hosts e containers

- Serviços locais escutando em **`127.0.0.1`** quando não precisam da rede.
- Docker: publicar em `127.0.0.1:porta` e controlar a cadeia `DOCKER-USER`.
- VMs de lab vulneráveis em **host-only**.

---

## 16. NAT como fonte de evidência

### 16.1 O problema da atribuição

> Um site externo reporta: *"O IP 200.10.20.5 tentou invadir nosso sistema em 03/10/2026 às 14:32:07 (UTC)"*.
> Atrás desse IP estão **300 funcionários**. Quem foi?

A resposta só existe se houver **log de NAT** com a tradução:

```
2026-10-03T14:32:05Z NAT TCP 192.168.10.57:51544 -> 200.10.20.5:40211 -> 203.0.113.80:443
```

→ IP interno `192.168.10.57`. Depois, com os **logs de DHCP** (quem tinha esse IP naquele horário) e a **tabela de MACs do switch**, chega-se ao equipamento e à porta física (veja os guias de DHCP e de Utilitários).

### 16.2 Requisitos para isso funcionar

| Requisito | Por quê |
|---|---|
| **Log de NAT** (ou NetFlow com campos de tradução) | Liga IP público:porta ao IP privado |
| **Relógios sincronizados (NTP)** em roteador, firewall, DHCP e servidores | Segundos de diferença tornam a correlação duvidosa |
| **Fuso horário explícito** (de preferência UTC nos logs) | Evita erros de 3 horas (UTC × Brasília) |
| **Porta de origem registrada** | Com PAT/CGNAT, o IP sozinho não identifica ninguém |
| **Retenção definida** | Investigações e solicitações legais chegam semanas depois |

### 16.3 O que monitorar (SIEM / Zabbix)

| Métrica / evento | Por que alertar |
|---|---|
| Uso da tabela NAT acima do normal | Possível host infectado, varredura ou DoS |
| Um único IP interno com número anormal de traduções | Host comprometido gerando muitas conexões |
| Nova regra de port forwarding / mapeamento UPnP | Exposição nova (legítima ou não) |
| Conexões de entrada aceitas em portas encaminhadas | Quem está acessando o serviço exposto |
| IP WAN mudou | Mudança no provedor (pode afetar regras e acessos) |


---

## 17. Visão Red Team x Blue Team

| Tema | 🔴 Red Team pergunta… (com autorização) | 🔵 Blue Team pergunta… |
|---|---|---|
| Exposição | "Quais serviços internos estão encaminhados para a internet?" | "Tenho inventário de todos os port forwardings e um dono para cada um?" |
| UPnP | "O roteador aceita mapeamentos automáticos?" | "UPnP está desativado?" |
| Saída | "Consigo conectar para fora em qualquer porta?" | "Filtro saída e alerto sobre conexões incomuns?" |
| IPv6 | "Os hosts têm IPv6 global alcançável sem o 'NAT' protegendo?" | "Meu firewall IPv6 bloqueia entrada por padrão?" |
| Containers | "Alguma porta do Docker está exposta apesar do firewall?" | "Publico portas só em 127.0.0.1 e audito de fora?" |
| Atribuição | "Minhas ações se misturam a centenas de usuários atrás do mesmo IP?" | "Tenho log de NAT com porta e NTP para responder 'quem foi'?" |

---

## 18. Mão na massa: comandos de verificação

### Descobrir seu IP privado e o público

```bash
ip -br addr                 # Linux: IP privado
ipconfig                    # Windows: IP privado
curl ifconfig.me            # IP público (como a internet te vê)
curl -4 ifconfig.me ; curl -6 ifconfig.me   # IPv4 e IPv6 públicos
```

> 👀 **Exercício:** compare o IP público com o **IP WAN** no painel do seu roteador. São iguais? Se não, você está atrás de CGNAT.

### Cisco IOS

```
show ip nat translations           ! tabela de traduções ativas
show ip nat translations verbose   ! com tempos de expiração
show ip nat statistics             ! contagem, interfaces inside/outside, hits/misses
clear ip nat translation *         ! limpa traduções dinâmicas (lab!)
debug ip nat                       ! acompanha traduções em tempo real (só em lab)
```

### Linux

```bash
sudo nft list ruleset                      # todas as regras (inclui NAT)
sudo iptables -t nat -L -n -v              # regras de NAT (iptables) com contadores
sudo conntrack -L                          # conexões rastreadas / traduções
sudo conntrack -C                          # quantidade de entradas
cat /proc/sys/net/netfilter/nf_conntrack_max   # limite da tabela
sysctl net.ipv4.ip_forward
```

### Docker

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"   # portas publicadas
#   0.0.0.0:5432->5432/tcp   ← exposto em todas as interfaces!
#   127.0.0.1:5432->5432/tcp ← só local (melhor)
docker network inspect bridge                       # sub-rede e IPs dos containers
sudo iptables -t nat -L DOCKER -n -v                # DNATs criados pelo Docker
```

### Windows / WSL2

```
netsh interface portproxy show all     # encaminhamentos de porta configurados no Windows
wsl hostname -I                        # IP da VM do WSL2
Get-NetNat                             # redes NAT do Windows (Hyper-V/containers)
```

### Wireshark: vendo a tradução

Capture **dos dois lados** do roteador NAT (LAN e WAN) no lab e compare o mesmo fluxo: o IP/porta de origem muda, o destino permanece. Filtros úteis:

```
ip.addr == 192.168.0.10        # lado LAN
tcp.port == 40211              # porta traduzida no lado WAN
```

---

## 19. Troubleshooting

| Sintoma | Causa provável | Verificação |
|---|---|---|
| LAN acessa o roteador, mas não a internet | NAT não configurado, ACL do NAT não inclui a rede, interface inside/outside trocada | `show ip nat statistics` (hits = 0?), `show run \| include nat` |
| Port forwarding não funciona de fora | **CGNAT**, firewall bloqueando, serviço escutando só em 127.0.0.1, IP interno mudou | Comparar IP WAN × `curl ifconfig.me`; `ss -tuln` no servidor; reserva DHCP |
| Port forwarding não funciona **de dentro** usando o IP público | Falta de **hairpin NAT** | Testar de fora (4G) ou usar DNS interno |
| VoIP: áudio só de um lado | SIP ALG ou NAT mal tratado | Desativar SIP ALG; usar STUN/servidor com suporte a NAT |
| VPN IPsec não conecta atrás de NAT | NAT-T bloqueado | Liberar **UDP 500 e 4500** |
| Conexões longas caem após inatividade | Timeout da tradução/estado | Keepalives (SSH `ServerAliveInterval`) |
| Internet "cai" para todos aleatoriamente | **Tabela NAT/conntrack cheia** | `conntrack -C` × `nf_conntrack_max`; procurar o host que mais gera conexões |
| Container acessível de fora apesar do `ufw deny` | DNAT do Docker contorna o ufw | Publicar em `127.0.0.1`; regras em `DOCKER-USER` |
| Outra máquina da rede não acessa serviço no WSL2 | NAT do WSL2 | `netsh interface portproxy` ou modo *mirrored* |

---

## 20. Exercícios para o seu lab

1. **Identifique seus NATs**
   Descubra seu IP privado, o IP WAN do roteador e o IP público (`curl ifconfig.me`). Desenhe quantas camadas de NAT existem entre seu PC e a internet (inclua WSL2/Docker se usar).

2. **PAT no Packet Tracer**
   Monte LAN (3 PCs) → roteador → "internet" (outro roteador + servidor web). Configure PAT, acesse o servidor dos 3 PCs e analise `show ip nat translations`. Identifique inside local, inside global e outside global.

3. **Port forwarding + "NAT não é firewall"**
   Publique um servidor web interno com NAT estático de porta. Mostre que ele fica acessível de fora. Depois adicione uma ACL na interface WAN permitindo só um IP de origem e prove a diferença.

4. **Linux como roteador NAT**
   Com duas VMs (uma "LAN" em rede interna e uma "roteador" com duas interfaces), configure `ip_forward` + masquerade com nftables. Acompanhe as traduções com `conntrack -L` enquanto a VM LAN navega.

5. **Pegadinha do Docker**
   Numa VM Linux com `ufw` ativo (`default deny incoming`), suba `docker run -d -p 8080:80 nginx`. Teste o acesso **de outra máquina** — funcionou? Refaça com `-p 127.0.0.1:8080:80` e teste novamente. Documente o resultado.


6. **Auditoria do roteador de casa**
   No painel do seu roteador: UPnP está ativo? Há port forwardings? Gerência remota pela WAN está habilitada? O firewall IPv6 bloqueia entrada? Registre o "antes e depois" (sem expor IPs reais na publicação).

7. **Forense de atribuição (simulado)**
   No lab da tarefa 4, gere conexões de duas VMs internas para o mesmo servidor. A partir só do registro "IP público + porta + horário" visto no servidor, use `conntrack`/logs para descobrir qual VM foi. Escreva o passo a passo.


---

## 21. Resumo e glossário

### Resumo em 12 frases

1. O **NAT** existe porque os endereços **IPv4 acabaram**; ele permite que muitas máquinas com **IPs privados** (RFC 1918) compartilhem poucos IPs públicos.
2. Ele **reescreve IPs (e portas)** e guarda uma **tabela de tradução** para devolver as respostas ao host certo.
3. Termos Cisco: **inside local** (IP real interno), **inside global** (como ele aparece lá fora), **outside global/local** (o host externo).
4. **PAT/overload** (muitos para um, usando portas) é o tipo mais comum; **NAT estático** e **port forwarding** expõem serviços internos.
5. No Linux: **SNAT/masquerade** na saída, **DNAT** na entrada.
6. **CGNAT** coloca vários clientes atrás do mesmo IP do provedor, impedindo port forwarding e exigindo **IP + porta + horário** para atribuição.
7. O NAT atrapalha protocolos que carregam IPs no conteúdo (FTP, SIP) e o IPsec; existem soluções como **ALGs, NAT-T, STUN/TURN/ICE**.
8. **Docker, WSL2 e VMs** usam NAT — e o **Docker pode expor portas contornando o ufw**.
9. **IPv6 não usa NAT**: sem um firewall stateful, dispositivos ficam diretamente alcançáveis.
10. **NAT não é firewall**: não filtra saída, não protege contra ameaças internas e é furado por port forwarding e UPnP.
11. Riscos principais: port forwarding esquecido, **UPnP**, conexões reversas de malware, esgotamento da tabela e perda de atribuição.
12. **Logs de NAT + NTP + porta de origem** são essenciais para responder "quem fez essa conexão?".

### Glossário rápido

| Termo | Significado |
|---|---|
| **ALG** | Ajudante que reescreve o conteúdo de protocolos para funcionarem com NAT |
| **CGNAT** | NAT feito pelo provedor, compartilhando um IP público entre vários clientes |
| **Conntrack** | Tabela do Linux que rastreia conexões e traduções |
| **DMZ** | Segmento separado para serviços expostos à internet |
| **DNAT** | Tradução do endereço de **destino** (base do port forwarding) |
| **Hairpin NAT** | Acessar, de dentro, um serviço interno pelo IP público |
| **Inside Local / Global** | IP do host interno visto de dentro / de fora |
| **Masquerade** | SNAT usando automaticamente o IP da interface de saída |
| **NAT-T** | Encapsulamento do IPsec em UDP 4500 para atravessar NAT |
| **NAT64** | Tradução entre IPv6 e IPv4 |
| **PAT / Overload** | Muitos IPs privados compartilhando um IP público via portas |
| **Port forwarding** | Encaminhar uma porta pública para um host interno |
| **RFC 1918** | Norma que define as faixas de IPs privados |
| **SNAT** | Tradução do endereço de **origem** |
| **STUN / TURN / ICE** | Técnicas para estabelecer comunicação através de NAT (WebRTC, VoIP) |
| **Tabela de tradução** | Registro das associações IP/porta interna ↔ externa |
| **UPnP** | Protocolo que permite a dispositivos internos abrir portas no roteador sem autenticação |

---

> ⚖️ **Ética:** todo conhecimento sobre riscos aqui serve para **entender, detectar e mitigar**. Testes só em redes e equipamentos seus (lab isolado) ou com **autorização formal por escrito** e escopo definido.