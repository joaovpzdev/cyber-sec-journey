# Endereços MAC e IP: um guia didático com olhar de Cybersecurity

> **Para quem é este material:** quem está estudando redes (ex.: Cisco *Conceitos Básicos de Redes*) e quer entender de verdade os dois endereços que todo dispositivo usa: o **MAC** e o **IP**. Como são formados, para que serve cada um, como trabalham juntos e o que significam para identificação de dispositivos, controle de acesso e investigação de incidentes. Faz parte da série com os guias de *Broadcasts e Roteadores*, *DHCP*, *TCP x UDP*, *Roteamento*, *Utilitários de Teste* e *NAT*.

---

## Sumário

1. [Por que um dispositivo precisa de dois endereços](#1-por-que-um-dispositivo-precisa-de-dois-endereços)
2. [O endereço MAC](#2-o-endereço-mac)
3. [Tipos de endereço MAC](#3-tipos-de-endereço-mac)
4. [MAC aleatório e privacidade](#4-mac-aleatório-e-privacidade)
5. [O endereço IPv4](#5-o-endereço-ipv4)
6. [Máscara de sub-rede e CIDR](#6-máscara-de-sub-rede-e-cidr)
7. [Calculando sub-redes passo a passo](#7-calculando-sub-redes-passo-a-passo)
8. [Endereços IPv4 especiais](#8-endereços-ipv4-especiais)
9. [O endereço IPv6](#9-o-endereço-ipv6)
10. [MAC e IP trabalhando juntos](#10-mac-e-ip-trabalhando-juntos)
11. [MAC x IP lado a lado](#11-mac-x-ip-lado-a-lado)
12. [Por que isso importa em segurança](#12-por-que-isso-importa-em-segurança)
13. [Identidade de dispositivo: o que dá e o que não dá para confiar](#13-identidade-de-dispositivo)
14. [Controles de acesso baseados em endereço](#14-controles-de-acesso-baseados-em-endereço)
15. [MAC e IP como fonte de evidência (SOC / forense)](#15-mac-e-ip-como-fonte-de-evidência)
16. [Visão Red Team x Blue Team](#16-visão-red-team-x-blue-team)
17. [Mão na massa: comandos](#17-mão-na-massa-comandos)
18. [Troubleshooting](#18-troubleshooting)
19. [Exercícios para o seu lab](#19-exercícios-para-o-seu-lab)
20. [Resumo e glossário](#20-resumo-e-glossário)

---

## 1. Por que um dispositivo precisa de dois endereços

Cada dispositivo numa rede tem (pelo menos) dois endereços, e cada um resolve um problema diferente:

| Endereço | Camada OSI | Pergunta que responde | Alcance |
|---|---|---|---|
| **MAC** | 2 - Enlace | "Qual **placa de rede**, aqui neste segmento local?" | Só a rede local |
| **IP** | 3 - Rede | "Qual **dispositivo**, em qual **rede** do mundo?" | Fim a fim, atravessa roteadores |

**Analogia da correspondência:**

- O **IP** é o **endereço postal completo** (país, cidade, rua, número). Ele diz **para onde** a carta vai, do começo ao fim da viagem.
- O **MAC** é a **instrução para o carteiro do trecho atual**: "entregue para a próxima agência" ou "entregue na portaria do prédio X". A cada trecho, essa instrução muda.

Por que não usar só um? Porque:

- O **MAC** não tem hierarquia: ele não diz **onde** o dispositivo está, só **qual** placa ele é. Um roteador não conseguiria decidir caminhos com ele.
- O **IP** é lógico e hierárquico (rede + host), perfeito para roteamento, mas a placa Ethernet/Wi-Fi não entende IP: ela entrega quadros com base no MAC.

> **Dica:** *IP leva o pacote até a rede certa. MAC entrega o quadro na placa certa dentro dessa rede.*

---

## 2. O endereço MAC

**MAC (Media Access Control)** é o endereço físico de uma interface de rede (placa Ethernet, Wi-Fi, Bluetooth).

### 2.1 Formato

- **48 bits** (6 bytes), escritos em **hexadecimal**.
- Várias notações para o mesmo endereço:

| Notação | Exemplo | Onde aparece |
|---|---|---|
| Dois-pontos | `3C:52:82:1A:2B:3C` | Linux, macOS |
| Hífen | `3C-52-82-1A-2B-3C` | Windows |
| Pontos (grupos de 4) | `3c52.821a.2b3c` | Cisco IOS |

### 2.2 Estrutura: OUI + identificador

```
   3C : 52 : 82   :   1A : 2B : 3C
   └─────┬────┘       └─────┬────┘
        OUI            Específico da placa
  (fabricante,         (o fabricante atribui
   24 bits)             sequencialmente, 24 bits)
```

- **OUI (Organizationally Unique Identifier):** os 3 primeiros bytes, comprados pelo fabricante junto ao **IEEE**. Identificam quem fabricou a placa (Intel, Cisco, Apple, Samsung, Raspberry Pi, TP-Link...).
- **Os 3 últimos bytes:** atribuídos pelo fabricante, um para cada placa.

Com 24 bits por fabricante, cada OUI permite cerca de **16,7 milhões** de placas. Fabricantes grandes têm vários OUIs.

> **Visão cyber:** pelo OUI dá para inferir o **tipo de dispositivo** sem acessá-lo. Uma lista de MACs da rede já mostra "isso é uma câmera Hikvision", "isso é um Raspberry Pi", "isso é uma impressora HP". É útil para **inventário** (Blue Team) e também para **reconhecimento**. Um OUI de Raspberry Pi aparecendo numa rede corporativa onde ninguém usa Raspberry Pi merece investigação.

### 2.3 Gravado na placa... mas não imutável

O fabricante grava um MAC na placa (o *burned-in address*). Porém o **sistema operacional pode usar outro MAC** por software. Isso tem usos legítimos (privacidade, virtualização, clusters de alta disponibilidade) e é o motivo de o MAC **não servir como prova de identidade** (seção 13).

---

## 3. Tipos de endereço MAC

Dois bits do **primeiro byte** carregam significado:

```
Primeiro byte: 3C = 0011 1100
                         ││
                         │└─ bit I/G (menos significativo): 0 = unicast, 1 = multicast
                         └── bit U/L (segundo menos significativo): 0 = global (do fabricante), 1 = local (administrado por software)
```

| Tipo | Como reconhecer | Exemplo | Uso |
|---|---|---|---|
| **Unicast global** | Bits I/G=0 e U/L=0 | `3C:52:82:...` | MAC de fábrica de uma placa |
| **Unicast local** | U/L=1 → 2º dígito hexa é **2, 6, A ou E** | `DA:A1:19:...` | MAC aleatório, VMs, containers |
| **Multicast** | I/G=1 → 2º dígito hexa ímpar | `01:00:5E:...` (IPv4), `33:33:...` (IPv6) | Grupos (streaming, protocolos de roteamento) |
| **Broadcast** | Todos os bits 1 | `FF:FF:FF:FF:FF:FF` | Todos da rede local |

> **Dica rápida para reconhecer MAC aleatório:** olhe o **segundo caractere**. Se for **2, 6, A ou E**, é um endereço administrado localmente: quase sempre um MAC aleatório de celular/notebook, uma VM ou um container.

Prefixos que você vai ver muito em labs:

| Prefixo | Origem |
|---|---|
| `08:00:27` | VirtualBox |
| `00:0C:29`, `00:50:56` | VMware |
| `00:15:5D` | Hyper-V (inclui WSL2) |
| `02:42` | Docker (padrão em várias versões) |

---

## 4. MAC aleatório e privacidade

Problema: o MAC de fábrica é **único e permanente**. Lojas, shoppings e aeroportos podiam rastrear um celular de uma rede Wi-Fi para outra só pelo MAC que ele anunciava ao procurar redes.

Solução moderna: **MAC aleatório (privado)**.

| Sistema | Comportamento padrão (geral) |
|---|---|
| **iOS / iPadOS** | "Endereço privado" diferente para cada rede Wi-Fi |
| **Android** | MAC aleatório por rede Wi-Fi |
| **Windows 10/11** | Opção de "endereços de hardware aleatórios" (por rede) |
| **Linux (NetworkManager)** | Aleatório durante a busca de redes; configurável por conexão |

> **Visão cyber - dois lados da mesma moeda:**
> - **Privacidade:** dificulta o rastreamento de pessoas. Ótimo para o usuário.
> - **Operação e segurança corporativa:** atrapalha **reservas de DHCP**, **filtros por MAC**, **inventário** e **investigações** ("qual aparelho era esse MAC?"). Por isso empresas preferem identificar dispositivos por **autenticação (802.1X / certificados)**, e não por MAC.

---

## 5. O endereço IPv4

**IP (Internet Protocol)** é o endereço **lógico** de um dispositivo, atribuído por configuração manual ou por DHCP.

### 5.1 Formato

- **32 bits**, escritos em **notação decimal pontuada**: quatro octetos de 0 a 255.

```
   192    .   168    .    1     .    10
11000000 . 10101000 . 00000001 . 00001010
```

Total possível: 2³² = cerca de **4,3 bilhões** de endereços (insuficiente, por isso existem NAT e IPv6 - veja o guia de NAT).

### 5.2 Parte de rede + parte de host

Todo IP tem duas partes. Quem diz onde uma termina e a outra começa é a **máscara**:

```
IP:      192.168.1.10
Máscara: 255.255.255.0   (/24)

         192.168.1   .   10
         └───┬───┘       └┬┘
          REDE          HOST
```

- **Parte de rede:** igual para todos os dispositivos da mesma sub-rede. É o que os roteadores usam.
- **Parte de host:** identifica o dispositivo dentro da sub-rede.

### 5.3 As antigas classes (contexto histórico)

| Classe | Primeiro octeto | Máscara padrão | Observação |
|---|---|---|---|
| A | 1 - 126 | /8 | Redes enormes |
| B | 128 - 191 | /16 | Redes médias |
| C | 192 - 223 | /24 | Redes pequenas |
| D | 224 - 239 | - | Multicast |
| E | 240 - 255 | - | Reservado |

Hoje a internet usa **CIDR** (sem classes), mas as provas e a nomenclatura ainda citam as classes.

---

## 6. Máscara de sub-rede e CIDR

A máscara é uma sequência de bits **1** (parte de rede) seguida de bits **0** (parte de host). A notação **CIDR** (`/24`) só diz **quantos bits 1** existem.

| CIDR | Máscara | Endereços no bloco | Hosts utilizáveis |
|---|---|---|---|
| /8 | 255.0.0.0 | 16.777.216 | 16.777.214 |
| /16 | 255.255.0.0 | 65.536 | 65.534 |
| /24 | 255.255.255.0 | 256 | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 (links entre roteadores) |
| /32 | 255.255.255.255 | 1 | 1 (um host específico) |

**Fórmulas:**

```
Endereços no bloco  = 2^(32 - prefixo)
Hosts utilizáveis   = 2^(32 - prefixo) - 2      (menos o endereço de rede e o de broadcast)
```

### Como o host usa a máscara

O dispositivo faz um **AND binário** entre o IP de destino e a sua máscara para decidir se o destino é **local** (entrega direto) ou **remoto** (manda para o gateway). Isso está detalhado no guia de *Roteamento*.

> **Visão cyber:** em pentest e em auditoria, **escopo é definido em CIDR** ("autorizado: 10.20.30.0/24"). Errar o cálculo significa testar fora do escopo autorizado (problema legal e contratual) ou deixar parte do ambiente sem análise.

---

## 7. Calculando sub-redes passo a passo

**Exemplo:** `192.168.10.77/27`

**Passo 1 - tamanho do bloco**

```
/27 → 32 - 27 = 5 bits de host → 2^5 = 32 endereços por sub-rede
Máscara: 255.255.255.224   (256 - 224 = 32, o "número mágico")
```

**Passo 2 - limites das sub-redes (múltiplos de 32 no último octeto)**

```
.0   .32   .64   .96   .128   .160   .192   .224
```

**Passo 3 - em qual bloco o .77 cai?** Entre .64 e .95.

| Item | Valor |
|---|---|
| Endereço de rede | `192.168.10.64` |
| Primeiro host | `192.168.10.65` |
| Último host | `192.168.10.94` |
| Broadcast | `192.168.10.95` |
| Hosts utilizáveis | 30 |

**Exercício mental:** `10.0.5.200/26`. Bloco de 64 → limites .0, .64, .128, .192. O .200 está em .192-.255. Rede `10.0.5.192`, broadcast `10.0.5.255`, hosts `.193` a `.254`.

> **Dica de prova e de trabalho:** treine até fazer de cabeça para /24 a /30. É uma das habilidades mais cobradas em entrevistas de redes, suporte e SOC.

---

## 8. Endereços IPv4 especiais

| Faixa | Nome | Significado |
|---|---|---|
| `0.0.0.0` | "Este host" / qualquer | Origem de quem ainda não tem IP (DHCP); em servidores, "escutar em todas as interfaces" |
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | Privados (RFC 1918) | Redes internas, não roteados na internet |
| `100.64.0.0/10` | Espaço compartilhado | CGNAT de provedores |
| `127.0.0.0/8` | Loopback | A própria máquina (`127.0.0.1` = localhost) |
| `169.254.0.0/16` | Link-local (APIPA) | Sem resposta do DHCP |
| `224.0.0.0/4` | Multicast | Grupos |
| `255.255.255.255` | Broadcast limitado | Todos da rede local |
| `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | Documentação | Só para exemplos (use em tutoriais e relatórios) |

> **Visão cyber:**
> - Um serviço escutando em `0.0.0.0` está acessível **por todas as interfaces**; em `127.0.0.1`, só pela própria máquina (veja o README sobre Docker).
> - Pacotes vindos da internet com origem privada, loopback ou de documentação são **"bogons"**: falsificados ou mal configurados, devem ser descartados na borda.
> - Em relatórios e posts públicos, use as faixas de **documentação** em vez dos seus IPs reais.

---

## 9. O endereço IPv6

### 9.1 Formato

- **128 bits**, em **8 grupos de 4 dígitos hexadecimais**:

```
2001:0db8:0000:0000:0000:ff00:0042:8329
```

**Regras de abreviação:**

1. Zeros à esquerda de cada grupo podem ser omitidos: `0db8` → `db8`, `0042` → `42`.
2. **Uma única** sequência de grupos só de zeros pode virar `::`.

```
2001:0db8:0000:0000:0000:ff00:0042:8329
→ 2001:db8::ff00:42:8329
```

### 9.2 Estrutura típica

```
2001:db8:acad:0001 : 0000:0000:0000:0010
└─────── 64 bits ──┘ └──── 64 bits ─────┘
   Prefixo de rede      Identificador da interface
   (do provedor/        (gerado pelo host)
    sub-rede)
```

Na maioria das redes, a sub-rede é **/64**.

### 9.3 Tipos principais

| Tipo | Prefixo | Uso |
|---|---|---|
| **Global unicast** | `2000::/3` | Endereço público, roteável na internet |
| **Link-local** | `fe80::/10` | Só no enlace local; todo host IPv6 tem um, sempre |
| **Unique local** | `fc00::/7` (na prática `fd00::/8`) | Equivalente aos privados do IPv4 |
| **Loopback** | `::1` | A própria máquina |
| **Multicast** | `ff00::/8` | Grupos (o IPv6 **não tem broadcast**) |

### 9.4 IPv6 e o MAC

Antigamente, o identificador de interface era derivado do MAC (método **EUI-64**: o MAC é dividido ao meio, recebe `FF:FE` no centro e tem o bit U/L invertido). Isso fazia o **MAC aparecer dentro do IPv6 público**, permitindo rastrear o aparelho em qualquer rede.

Hoje os sistemas usam por padrão **identificadores aleatórios / temporários** (extensões de privacidade), que mudam com o tempo.

> **Visão cyber:** um IPv6 com `ff:fe` no meio do identificador de interface provavelmente expõe o MAC do dispositivo. E lembre: com IPv6 não há NAT, então cada dispositivo pode ter um endereço **globalmente alcançável**; quem protege é o **firewall** (veja o guia de NAT).

---

## 10. MAC e IP trabalhando juntos

### 10.1 Encapsulamento

Quando você envia dados, cada camada adiciona seu cabeçalho:

```
┌──────────────────────────────────────────────────────────────────────┐
│ Cabeçalho Ethernet │ Cabeçalho IP          │ TCP/UDP │ Dados │ FCS   │
│ MAC dest | MAC orig│ IP orig | IP dest|TTL │ portas  │       │       │
└──────────────────────────────────────────────────────────────────────┘
   Camada 2             Camada 3               Camada 4
```

### 10.2 O que muda e o que não muda no caminho

Seu PC (`192.168.1.10`) acessa um servidor (`203.0.113.80`) passando por dois roteadores:

| Trecho | IP origem | IP destino | MAC origem | MAC destino |
|---|---|---|---|---|
| PC → Roteador 1 | 192.168.1.10 | 203.0.113.80 | PC | Roteador 1 (LAN) |
| Roteador 1 → Roteador 2 | 192.168.1.10* | 203.0.113.80 | Roteador 1 (WAN) | Roteador 2 |
| Roteador 2 → Servidor | 192.168.1.10* | 203.0.113.80 | Roteador 2 | Servidor |

\* Se houver NAT no Roteador 1, o IP de origem passa a ser o IP público dele (veja o guia de NAT).

**Regra de ouro:**

- **IP:** identifica origem e destino **finais** e se mantém (exceto com NAT).
- **MAC:** identifica apenas o **salto atual** e é trocado em cada roteador.

### 10.3 Como o host descobre o MAC certo

O host precisa do MAC do **próximo salto**:

- Destino **na mesma rede** → precisa do MAC do **próprio destino**.
- Destino **em outra rede** → precisa do MAC do **gateway padrão** (nunca do destino final, que está longe).

No IPv4 essa resolução de IP para MAC é feita pelo protocolo **ARP**; no IPv6, pelo **NDP** (Neighbor Discovery). O resultado fica guardado numa tabela local (cache de vizinhos), que você pode ver com `ip neigh` ou `arp -a`.

### 10.4 Quem usa qual endereço

| Dispositivo | Olha principalmente para... | Tabela que mantém |
|---|---|---|
| **Switch** (camada 2) | **MAC** de destino | Tabela de MACs (MAC → porta) |
| **Roteador** (camada 3) | **IP** de destino | Tabela de roteamento (rede → próximo salto) |
| **Host** | Os dois | Configuração IP + cache de vizinhos |

**Como o switch aprende:** ao receber um quadro, ele anota "o MAC de origem X está na porta Y". Para entregar, procura o MAC de destino na tabela; se não conhece, **inunda** o quadro para todas as portas da VLAN.

---

## 11. MAC x IP lado a lado

| Critério | MAC | IPv4 | IPv6 |
|---|---|---|---|
| Camada | 2 | 3 | 3 |
| Tamanho | 48 bits | 32 bits | 128 bits |
| Notação | Hexadecimal | Decimal pontuado | Hexadecimal com `:` |
| Exemplo | `3C:52:82:1A:2B:3C` | `192.168.1.10` | `2001:db8::10` |
| Quem atribui | Fabricante (ou SO) | Admin / DHCP | Admin / SLAAC / DHCPv6 |
| Hierárquico? | Não (só fabricante) | Sim (rede + host) | Sim (prefixo + interface) |
| Alcance | Segmento local | Fim a fim | Fim a fim |
| Muda no caminho? | Sim, a cada salto | Não (salvo NAT) | Não |
| Usado por | Switches | Roteadores | Roteadores |
| Pode ser alterado por software? | **Sim** | **Sim** | **Sim** |

> A última linha é a mais importante para segurança: **nenhum dos dois é uma identidade confiável por si só.**

---

## 12. Por que isso importa em segurança

1. **Identificação de dispositivos:** inventário, NAC e monitoramento começam por "quais MACs e IPs existem na minha rede?".
2. **Controle de acesso:** muitas regras (firewall, ACL, Wi-Fi) usam IP ou MAC como critério, e é preciso saber **o quanto** se pode confiar nelas.
3. **Segmentação:** redes e sub-redes (IP) e VLANs (camada 2) definem quem alcança quem.
4. **Investigação:** quase todo alerta de segurança chega como um **IP**. Transformar esse IP em **"qual máquina, de quem, em qual mesa"** passa pelo MAC.
5. **Privacidade:** MAC fixo e IPv6 derivado do MAC permitem rastrear pessoas.

---

## 13. Identidade de dispositivo

### 13.1 O que **não** dá para confiar

| Atributo | Por que não é prova de identidade |
|---|---|
| **MAC** | Qualquer sistema operacional permite alterá-lo por configuração; dispositivos modernos ainda o randomizam sozinhos |
| **IP** | Pode ser configurado manualmente por qualquer um; muda com o DHCP; com NAT, vários dispositivos compartilham o mesmo |
| **Hostname** | Definido livremente pelo usuário/dispositivo |

Ou seja: **"este MAC está na lista permitida" não significa "este é o dispositivo autorizado"**. Significa só que *algo* na rede está usando aquele MAC.

### 13.2 O que dá mais confiança

| Mecanismo | Como identifica |
|---|---|
| **802.1X** (com RADIUS) | O dispositivo/usuário se **autentica** antes de a porta do switch ou o Wi-Fi liberar acesso |
| **Certificados de máquina (EAP-TLS)** | Identidade criptográfica, difícil de copiar |
| **WPA2/WPA3-Enterprise** | Credenciais individuais no Wi-Fi, em vez de uma senha compartilhada |
| **NAC (Network Access Control)** | Combina autenticação + verificação de postura (antivírus, atualizações) |
| **Autenticação na aplicação (MFA)** | A identidade é provada no serviço, não pela origem de rede |

> **Frase para guardar:** *endereços dizem **de onde** veio o tráfego, não **quem** é o dispositivo. Identidade se prova com autenticação.*

---

## 14. Controles de acesso baseados em endereço

Mesmo sem serem identidade forte, controles por endereço são úteis **como camada**, desde que você conheça os limites.

### 14.1 Filtro de MAC no Wi-Fi

- **O que faz:** só aceita dispositivos com MAC numa lista.
- **Limite:** os MACs de clientes legítimos trafegam visíveis no ar; um MAC permitido pode ser reutilizado por outro dispositivo. E o MAC aleatório dos celulares quebra a lista.
- **Veredito:** não é controle de segurança real. Use **WPA3** (ou WPA2-AES) com senha forte, ou **WPA2/WPA3-Enterprise**.

### 14.2 Port Security no switch (Cisco)

Limita **quantos** MACs podem aparecer numa porta e/ou **quais**:

```
interface FastEthernet0/5
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky      ! aprende o 1º MAC e fixa
 switchport port-security violation restrict      ! descarta e registra log
!
show port-security interface FastEthernet0/5
show port-security address
```

| Modo de violação | Efeito |
|---|---|
| `protect` | Descarta o tráfego do MAC não autorizado, sem log |
| `restrict` | Descarta e **gera log/contador** |
| `shutdown` (padrão) | **Desativa a porta** (err-disabled) |

- **Ajuda contra:** alguém ligar um switch/roteador pessoal na tomada; enxurrada de MACs falsos tentando lotar a tabela do switch.
- **Limite:** não impede quem copia o MAC autorizado depois que o dispositivo legítimo é desconectado.

### 14.3 ACLs e firewall por IP

- **Muito úteis** para segmentação (ex.: "só a VLAN de TI acessa o SSH dos servidores").
- **Limites:** IP pode ser configurado manualmente; por isso combine com **IP Source Guard** / DHCP Snooping no switch (o switch só aceita na porta o IP que o DHCP entregou a ela) e com **anti-spoofing** na borda (uRPF / BCP 38).

### 14.4 Resumo

| Controle | Valor real | Use como |
|---|---|---|
| Filtro de MAC no Wi-Fi | Baixo | Não conte com ele |
| Port Security | Médio | Camada extra em portas de acesso |
| ACL por IP + anti-spoofing | Alto para segmentação | Base da segmentação |
| 802.1X / certificados | Alto | Controle de acesso de verdade |

---

## 15. MAC e IP como fonte de evidência

### 15.1 Do alerta à mesa: a trilha de investigação

**Cenário:** o firewall alerta: *"192.168.10.57 conectou em um domínio de malware às 14:32"*.

| Passo | Pergunta | Fonte |
|---|---|---|
| 1 | Se houver NAT: qual IP interno estava atrás do IP público nesse horário? | Logs de NAT |
| 2 | Qual **MAC** tinha o IP `192.168.10.57` às 14:32? | **Logs do DHCP** (lease) ou cache de vizinhos do gateway |
| 3 | Qual o **hostname** e o **fabricante** (OUI) desse MAC? | DHCP (opção 12), inventário, consulta de OUI |
| 4 | Em qual **switch e porta** esse MAC estava? | `show mac address-table`, opção 82 do DHCP, NAC |
| 5 | Qual **usuário** estava logado? | 802.1X/RADIUS, logs do AD, EDR |

```
IP 192.168.10.57 (14:32)
   → DHCP: MAC aa:bb:cc:12:34:56, hostname NOTE-FIN-023
   → Switch SW-ANDAR3, porta Gi1/0/14
   → Usuário autenticado: fulano.silva
```

### 15.2 Cuidados

- **MAC aleatório** pode impedir a correlação com o inventário. Por isso redes corporativas costumam exigir MAC fixo ou 802.1X nos dispositivos da empresa.
- **Relógios sincronizados (NTP)** em todos os equipamentos. Leases de DHCP mudam: o IP de hoje pode ter sido de outra máquina ontem.
- O MAC visto num log de firewall depois de um roteador é o **do roteador**, não o do dispositivo original (o MAC muda a cada salto).
- **Guarde os logs** (DHCP, NAT, switch) por tempo suficiente; investigações chegam dias ou semanas depois.

### 15.3 O que monitorar

| Evento | Por que alertar |
|---|---|
| MAC novo/desconhecido na rede | Dispositivo não autorizado |
| OUI inesperado (ex.: Raspberry Pi, adaptador USB) na rede corporativa | Possível equipamento plantado |
| Mesmo MAC aparecendo em duas portas/switches ao mesmo tempo | Possível clonagem de MAC |
| Violação de Port Security | Tentativa de conexão não autorizada |
| Muitos MACs diferentes numa única porta | Switch/roteador não autorizado ou ataque à tabela de MACs |
| Conflito de IP | Erro de configuração ou uso indevido de IP |


---

## 16. Visão Red Team x Blue Team

| Tema | Red Team pergunta... (com autorização) | Blue Team pergunta... |
|---|---|---|
| Inventário | "Que tipos de dispositivo existem aqui, pelo OUI?" | "Sei quais MACs/IPs são esperados e alerto sobre novos?" |
| Acesso físico | "Um dispositivo ligado numa tomada qualquer ganha acesso?" | "Tenho 802.1X ou ao menos Port Security nas portas de acesso?" |
| Wi-Fi | "O controle é só filtro de MAC?" | "Uso WPA3/Enterprise em vez de filtro de MAC?" |
| Confiança por IP | "Alguma regra confia num IP de origem sem outra verificação?" | "Combino ACL por IP com anti-spoofing e autenticação?" |
| IPv6 | "Os hosts têm IPv6 global alcançável?" | "Meu firewall cobre IPv6 também?" |
| Rastreabilidade | "Minhas ações ficam atribuíveis a um dispositivo?" | "Consigo ir do IP do alerta até a porta do switch e o usuário?" |

---

## 17. Mão na massa: comandos

Comandos de **observação da sua própria máquina e do seu lab**.

### Ver seus próprios endereços

```bash
# Linux
ip link                  # MACs ("link/ether")
ip -br addr              # IPs, resumido
ip -6 addr               # IPv6 (repare no fe80:: link-local e nos temporários)

# Windows
ipconfig /all            # "Endereço Físico" (MAC), IPv4, IPv6
getmac /v                # MACs de todas as interfaces
Get-NetAdapter | Select Name, MacAddress, Status    # PowerShell
```

### Ver vizinhos e tabelas

```bash
ip neigh                 # Linux: IP → MAC dos vizinhos conhecidos
arp -a                   # Windows/Linux
ip route                 # gateway padrão
```

### No switch / roteador Cisco (Packet Tracer)

```
show mac address-table                    ! MAC → porta → VLAN
show mac address-table address 3c52.821a.2b3c
show interfaces FastEthernet0/1           ! MAC da própria interface
show ip interface brief                   ! IPs das interfaces
show port-security
show arp                                  ! vizinhos do roteador
```

### Descobrir o fabricante pelo OUI

- Pesquise os 6 primeiros dígitos (ex.: `3C5282`) num site de consulta de OUI ou na lista pública do IEEE.
- O Wireshark já mostra o fabricante automaticamente (ex.: `IntelCor_1a:2b:3c`).

### Calcular sub-redes no terminal

```bash
ipcalc 192.168.10.77/27      # Linux (pacote ipcalc)
sipcalc 2001:db8::/64        # útil também para IPv6
```

### Filtros no Wireshark

```
eth.addr == 3c:52:82:1a:2b:3c      # tudo de/para um MAC
eth.dst == ff:ff:ff:ff:ff:ff       # broadcasts
eth.dst[0] & 1                     # multicast/broadcast (bit I/G)
ip.addr == 192.168.1.10            # tudo de/para um IP
ip.src == 192.168.1.0/24           # origem numa sub-rede
ipv6.addr == fe80::/10             # tráfego link-local IPv6
```

---

## 18. Troubleshooting

| Sintoma | Causa provável | Verificação |
|---|---|---|
| "Conflito de endereço IP" | Dois dispositivos com o mesmo IP (estático dentro do pool DHCP) | `ipconfig /all`, logs do DHCP, `show ip dhcp conflict` |
| Rede funciona para uns e não para outros na mesma sala | Máscara errada em alguns hosts | Comparar máscara/gateway com `ipconfig` |
| Pinga IPs locais, mas não sai da rede | Gateway errado ou fora da sub-rede | `ip route` / `ipconfig` |
| Reserva DHCP não funciona no celular | **MAC aleatório** | Desativar endereço privado só para aquela rede ou usar outro método |
| Porta do switch desativou sozinha (err-disabled) | Violação de Port Security | `show port-security`, `show interfaces status err-disabled` |
| Dispositivo some e volta da rede, com IPs diferentes | Lease curto, MAC aleatório trocando | Logs do DHCP |
| VM não acessa a rede em modo bridge | MAC da VM bloqueado (Port Security / Wi-Fi não aceita bridge) | Testar em NAT ou cabo |
| Serviço acessível só localmente | Escutando em `127.0.0.1` | `ss -tuln` / `netstat -ano` |

---

## 19. Exercícios para o seu lab

1. **Leia seus endereços**
   Anote o MAC, o IPv4, a máscara, o gateway e os IPv6 (link-local e global) da sua máquina. Descubra o fabricante pelo OUI. Seu Wi-Fi está usando MAC aleatório? (Dica: veja o 2º caractere.)

2. **Treino de sub-redes**
   Para cada endereço, encontre rede, primeiro e último host e broadcast: `172.16.4.130/25`, `10.10.10.45/28`, `192.168.0.200/29`, `192.168.50.1/30`. Confira com `ipcalc`.

3. **Plano de endereçamento**
   Divida `192.168.100.0/24` para: 100 usuários, 50 IoT, 20 servidores e 2 links ponto a ponto. Use VLSM (sub-redes de tamanhos diferentes) e monte a tabela.

4. **MAC muda, IP não (Packet Tracer)**
   Monte PC → R1 → R2 → Servidor. No modo *Simulation*, clique no pacote em cada trecho e anote IPs e MACs. Confirme a regra de ouro da seção 10.

5. **Tabela de MACs do switch**
   Ligue 4 PCs num switch, faça pings entre eles e rode `show mac address-table`. Depois desligue um PC, espere e veja a entrada expirar (padrão: 300 s).

6. **Port Security**
   Configure `maximum 1` + `sticky` + `violation restrict` numa porta. Troque o PC daquela porta por outro e observe os contadores de violação. Repita com `shutdown` e reabilite a porta (`shutdown` / `no shutdown`).

7. **Trilha de investigação (simulado)**
   No lab com DHCP, escolha um IP e documente o caminho até a porta física: lease do DHCP → MAC → `show mac address-table` → porta. Escreva como um mini-relatório de SOC.

8. **Inventário com Zabbix**
   Configure a descoberta de rede do Zabbix para a sub-rede do lab e crie uma ação para quando um host novo aparecer.


---

## 20. Resumo e glossário

### Resumo em 12 frases

1. Todo dispositivo tem um **MAC** (camada 2, entrega local) e um **IP** (camada 3, entrega fim a fim).
2. O **MAC** tem 48 bits em hexadecimal; os 3 primeiros bytes (**OUI**) identificam o fabricante.
3. O 2º caractere **2, 6, A ou E** indica MAC **administrado localmente** (aleatório, VM, container).
4. **MAC aleatório** protege a privacidade, mas dificulta inventário, reservas e investigações.
5. O **IPv4** tem 32 bits divididos em **rede + host** pela **máscara** (notação CIDR).
6. Hosts utilizáveis = **2^(bits de host) - 2**; saber calcular sub-redes define escopo e segmentação.
7. Faixas especiais: privadas (RFC 1918), loopback, APIPA, CGNAT, documentação.
8. O **IPv6** tem 128 bits, sub-redes /64, sempre um endereço **link-local** e não tem broadcast.
9. No caminho, o **IP se mantém** (salvo NAT) e o **MAC muda a cada salto**; switches usam MAC, roteadores usam IP.
10. **MAC e IP podem ser alterados por software**: não são prova de identidade.
11. Filtro de MAC no Wi-Fi é fraco; Port Security ajuda; **802.1X, certificados e autenticação** são o controle real.
12. A trilha **IP → lease DHCP → MAC → porta do switch → usuário** é a base de muitas investigações de SOC, e depende de logs e NTP.

### Glossário rápido

| Termo | Significado |
|---|---|
| **802.1X** | Autenticação do dispositivo antes de liberar a porta/Wi-Fi |
| **APIPA** | IP automático `169.254.x.x` quando não há DHCP |
| **Bogon** | Endereço que não deveria aparecer como origem vindo da internet |
| **CIDR** | Notação `/n` que indica quantos bits formam a parte de rede |
| **Encapsulamento** | Cada camada adiciona seu cabeçalho aos dados |
| **EUI-64** | Método antigo de gerar o identificador IPv6 a partir do MAC |
| **Link-local** | Endereço válido só no enlace local (`fe80::/10` no IPv6) |
| **Loopback** | Endereço da própria máquina (`127.0.0.1`, `::1`) |
| **MAC** | Endereço físico de 48 bits da interface de rede |
| **Máscara** | Define a divisão entre parte de rede e parte de host |
| **NAC** | Controle de acesso à rede com autenticação e verificação de postura |
| **OUI** | Prefixo de 24 bits do MAC que identifica o fabricante |
| **Port Security** | Recurso do switch que limita/fixa MACs por porta |
| **Sub-rede** | Divisão de uma rede maior em blocos menores |
| **Tabela de MACs** | Tabela do switch que associa MAC a porta |
| **VLSM** | Sub-redes de tamanhos diferentes dentro do mesmo bloco |

---

> **Ética:** pratique na **sua** máquina e no **seu** lab. Em redes de terceiros, qualquer teste exige **autorização formal por escrito** e escopo definido.