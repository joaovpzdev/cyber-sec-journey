# Broadcasts e Roteadores: um guia didático com olhar de Cybersecurity

> **Para quem é este material:** quem está estudando redes (ex.: Cisco *Conceitos Básicos de Redes*) e quer entender **por que** esses conceitos importam para Red Team (ataque/pentest) e Blue Team (defesa/monitoramento).

---

## Sumário

1. [Antes de tudo: como os dados "andam" numa rede](#1-antes-de-tudo-como-os-dados-andam-numa-rede)
2. [Os três tipos de comunicação: unicast, broadcast e multicast](#2-os-três-tipos-de-comunicação)
3. [Broadcast em detalhe](#3-broadcast-em-detalhe)
4. [Domínio de broadcast](#4-domínio-de-broadcast)
5. [Roteadores: o que são e o que fazem](#5-roteadores-o-que-são-e-o-que-fazem)
6. [Por que o roteador "corta" o broadcast](#6-por-que-o-roteador-corta-o-broadcast)
7. [Protocolos que vivem de broadcast (e seus riscos)](#7-protocolos-que-vivem-de-broadcast-e-seus-riscos)
8. [Roteadores como alvo e como defesa](#8-roteadores-como-alvo-e-como-defesa)
9. [Visão Red Team x Blue Team](#9-visão-red-team-x-blue-team)
10. [Mão na massa: comandos para observar tudo isso](#10-mão-na-massa-comandos-para-observar)
11. [Exercícios para o seu lab](#11-exercícios-para-o-seu-lab)
12. [Resumo e glossário](#12-resumo-e-glossário)

---

## 1. Antes de tudo: como os dados "andam" numa rede

Pense numa rede como um **condomínio**:

| Rede | Condomínio |
|---|---|
| Endereço **MAC** (camada 2) | Número do apartamento — identifica *quem* é o morador dentro do prédio |
| Endereço **IP** (camada 3) | Endereço completo (rua + número + apto) — permite chegar de *outro bairro* |
| **Switch** | Porteiro que entrega correspondência *dentro* do prédio |
| **Roteador** | Correios — leva a carta *de um prédio para outro* |

Dois pontos-chave do modelo OSI que vamos usar o tempo todo:

- **Camada 2 (Enlace):** comunicação dentro da mesma rede local, usando MAC. Quem trabalha aqui: **switches**.
- **Camada 3 (Rede):** comunicação entre redes diferentes, usando IP. Quem trabalha aqui: **roteadores**.

> 💡 **Guarde isto:** *Switch conecta dispositivos. Roteador conecta redes.*

---

## 2. Os três tipos de comunicação

| Tipo | Quem recebe | Analogia | Exemplo |
|---|---|---|---|
| **Unicast** | Um destinatário específico | Ligar para uma pessoa | Seu navegador falando com um servidor web |
| **Broadcast** | **Todos** da rede local | Gritar no corredor do prédio | ARP Request, DHCP Discover |
| **Multicast** | Um grupo que "se inscreveu" | Grupo de WhatsApp | Streaming IPTV, OSPF, mDNS |

> Obs.: o **IPv6 não tem broadcast**. Ele usa **multicast** (ex.: `ff02::1` = "todos os nós do link"). Isso muda a superfície de ataque, como veremos.

---

## 3. Broadcast em detalhe

### 3.1 O que é

Broadcast é uma mensagem enviada para **todos os dispositivos de um mesmo segmento de rede**, sem que o remetente saiba quem eles são.

Ele existe por um motivo simples: **às vezes você não sabe com quem precisa falar.**

- "Quem tem o IP 192.168.0.1? Me diga seu MAC." → **ARP**
- "Acabei de chegar, alguém me dá um IP?" → **DHCP**

### 3.2 Endereços de broadcast

**Na camada 2 (MAC):**
```
FF:FF:FF:FF:FF:FF
```
Todo quadro com esse destino é entregue pelo switch a **todas as portas** (exceto a de origem).

**Na camada 3 (IP):**

| Tipo | Exemplo | Significado |
|---|---|---|
| Broadcast limitado | `255.255.255.255` | "Todos na *minha* rede local" — **nunca** é roteado |
| Broadcast direcionado | `192.168.10.255` (em uma /24) | "Todos na rede 192.168.10.0/24" — pode, em tese, vir de fora |

### 3.3 Calculando o broadcast de uma rede

O endereço de broadcast é o **último endereço** da sub-rede (todos os bits de host = 1).

Exemplo: `192.168.1.0/26`

```
Máscara /26 = 255.255.255.192 → blocos de 64 endereços
Redes:   .0   .64   .128   .192
Rede 1:  192.168.1.0    (endereço de rede)
         192.168.1.1  a 192.168.1.62  (hosts)
         192.168.1.63   (broadcast)
```

> 🔐 **Por que isso importa em cyber?** Em pentest, a primeira coisa é entender o *escopo*: qual a rede, quantos hosts cabem nela, qual o broadcast. Errar o cálculo de sub-rede = escanear fora do escopo autorizado (problema legal!) ou deixar hosts de fora.

### 3.4 O lado ruim do broadcast

1. **Consome recursos:** todo host precisa "abrir a carta" e verificar se é para ele.
2. **Vaza informação:** qualquer um na rede ouve. Um atacante conectado passivamente já descobre IPs, MACs, nomes de máquinas e serviços.
3. **Não tem autenticação:** quem responde primeiro "ganha". Base de vários ataques.
4. **Pode virar tempestade:** os famosos **broadcast storms**.

#### Broadcast storm

Acontece quando broadcasts circulam em **loop** entre switches (ex.: dois cabos ligando os mesmos switches sem STP). Cada switch reencaminha o quadro, que volta, é reencaminhado de novo… em segundos a rede para.

- **Causa comum:** erro de cabeamento, STP desativado.
- **Proteção:** **STP (Spanning Tree Protocol)**, *storm control* nas portas do switch, **BPDU Guard**.
- **Visão cyber:** é um problema de **disponibilidade** (o "A" da tríade CIA). Um insider mal-intencionado (ou só desastrado) pode derrubar uma rede inteira com um cabo.

---

## 4. Domínio de broadcast

**Domínio de broadcast** = o conjunto de dispositivos que recebem o broadcast uns dos outros.

```
            [ Roteador ]
            /          \
     [Switch A]      [Switch B]
     /   |   \        /   |   \
    PC1 PC2 PC3     PC4  PC5  PC6

  Domínio 1: PC1, PC2, PC3     Domínio 2: PC4, PC5, PC6
```

- **Switches** (sem VLANs) **ampliam** o domínio de broadcast.
- **Roteadores** **separam** domínios de broadcast.
- **VLANs** dividem logicamente um switch em vários domínios de broadcast.

> 🔐 **Conceito de segurança fundamental:** cada domínio de broadcast é, na prática, uma **zona de confiança**. Tudo que está nele consegue "ouvir" e "falar" diretamente com o resto. Por isso:
> - Rede de visitantes **separada** da rede corporativa.
> - Câmeras/IoT em VLAN **própria**.
> - Servidores críticos isolados.
>
> Isso se chama **segmentação de rede** e é uma das defesas mais eficazes contra **movimentação lateral** de um atacante.

---

## 5. Roteadores: o que são e o que fazem

### 5.1 Definição

O **roteador** é um dispositivo de **camada 3** que encaminha pacotes **entre redes diferentes**, decidindo o melhor caminho com base no **IP de destino**.

### 5.2 A tabela de roteamento

É o "GPS" do roteador. Cada linha diz: *para chegar na rede X, mande para Y, pela interface Z*.

```
Destino           Próximo salto     Interface   Origem
192.168.1.0/24    diretamente       Gi0/0       C (conectada)
10.0.0.0/8        192.168.1.254     Gi0/0       S (estática)
0.0.0.0/0         200.10.20.1       Gi0/1       S (rota padrão)
```

- **Rotas conectadas (C):** redes ligadas diretamente às interfaces.
- **Rotas estáticas (S):** configuradas manualmente.
- **Rotas dinâmicas:** aprendidas por protocolos (OSPF, EIGRP, RIP, BGP).
- **Rota padrão (0.0.0.0/0):** "se não sei para onde vai, mando para cá" — geralmente a internet.

O roteador sempre escolhe a rota **mais específica** (maior prefixo, *longest prefix match*).

### 5.3 O passo a passo de um pacote

Seu PC (`192.168.0.10`) acessa `8.8.8.8`:

1. O PC compara: `8.8.8.8` está na minha rede? **Não.**
2. Então manda para o **gateway padrão** (`192.168.0.1` – o roteador).
3. Para isso precisa do MAC do roteador → faz um **ARP (broadcast!)**.
4. Envia o pacote: IP destino `8.8.8.8`, MAC destino = **MAC do roteador**.
5. O roteador recebe, consulta a tabela, decrementa o **TTL**, faz **NAT** e envia para o próximo salto.
6. O processo se repete roteador a roteador até chegar ao destino.

> Repare: **o IP de destino não muda no caminho (exceto por NAT), mas o MAC muda a cada salto.**

### 5.4 Outras funções do roteador doméstico/corporativo

| Função | O que faz | Relevância em cyber |
|---|---|---|
| **NAT** | Traduz IPs privados para o IP público | Esconde a rede interna, mas *não é firewall* |
| **DHCP Server** | Distribui IPs | Alvo de ataques de spoofing/starvation |
| **DNS forwarder** | Repassa consultas DNS | Pode ser sequestrado (DNS hijacking) |
| **Firewall / ACL** | Filtra tráfego | Primeira linha de defesa de perímetro |
| **Port forwarding / UPnP** | Abre portas para a internet | Expõe serviços internos sem querer |
| **Painel web de admin** | Configuração | Alvo nº 1 se tiver senha padrão |

### 5.5 TTL: o "contador de vida"

Cada roteador subtrai 1 do **TTL**. Se chegar a 0, o pacote é descartado e o roteador envia um **ICMP Time Exceeded** de volta. Isso:

- **Evita loops infinitos** de roteamento.
- É a base do **`traceroute`/`tracert`** — usado em reconhecimento para mapear o caminho até um alvo.
- Permite **fingerprinting** de SO: Linux costuma começar com TTL 64, Windows com 128, equipamentos de rede com 255.

---

## 6. Por que o roteador "corta" o broadcast

Por padrão, **roteadores não encaminham broadcasts**. Isso é proposital:

- Se encaminhassem, um único ARP iria para a internet inteira. 🌍💥
- Isolar broadcast = **conter o barulho e conter o risco**.

### Exceções controladas

- **DHCP Relay (`ip helper-address`):** o roteador converte o broadcast DHCP em **unicast** para um servidor DHCP em outra rede. Útil, mas deve ser configurado com cuidado.
- **Broadcast direcionado (`ip directed-broadcast`):** **desativado por padrão** em roteadores modernos — e deve continuar assim (veja o *Smurf attack* abaixo).

> 🔐 **Lição para o Blue Team:** o roteador é uma **fronteira natural de segurança**. Ataques baseados em broadcast (ARP spoofing, DHCP rogue, LLMNR poisoning) **ficam presos ao segmento local**. Quanto menores os segmentos, menor o raio de impacto.

---

## 7. Protocolos que vivem de broadcast (e seus riscos)

Aqui está o coração da relação entre broadcast e cybersecurity. Todos estes protocolos **confiam cegamente** em quem responde.

> ⚠️ Os ataques abaixo são descritos em nível **conceitual**, para que você entenda o risco e saiba **detectar e mitigar**. Testes só em ambiente próprio (lab) ou com autorização formal por escrito.

### 7.1 ARP (Address Resolution Protocol)

**Como funciona:**
```
PC1 (broadcast): "Quem tem 192.168.0.1? Responda para 192.168.0.10"
Roteador (unicast): "192.168.0.1 está no MAC AA:BB:CC:11:22:33"
```

**Problema:** o ARP não tem autenticação. Hosts aceitam até respostas que **não pediram** (*gratuitous ARP*).

**Ataque — ARP Spoofing / ARP Poisoning:**
O atacante anuncia: *"192.168.0.1 sou eu!"*. As vítimas passam a enviar o tráfego destinado ao roteador para o atacante → **Man-in-the-Middle (MitM)**: interceptação, captura de credenciais em protocolos sem criptografia, manipulação de tráfego.

**Detecção (Blue Team):**
- Mesmo IP associado a **dois MACs diferentes** na tabela ARP.
- Volume anormal de *gratuitous ARP*.
- Ferramentas: `arpwatch`, alertas no IDS (Suricata/Zeek/Snort), monitoramento SNMP.

**Mitigação:**
- **Dynamic ARP Inspection (DAI)** no switch.
- Entradas ARP **estáticas** para ativos críticos (gateway).
- Criptografia ponta a ponta (HTTPS, SSH, VPN) — mesmo interceptado, o conteúdo fica protegido.
- Segmentação em VLANs.

### 7.2 DHCP (Dynamic Host Configuration Protocol)

**Como funciona (DORA):**
```
Discover  (broadcast)  Cliente: "Alguém me dá um IP?"
Offer     (servidor)   "Toma o 192.168.0.50"
Request   (broadcast)  "Aceito o .50"
Ack       (servidor)   "Confirmado. Gateway: .1, DNS: .1"
```

**Ataques conceituais:**
- **Rogue DHCP:** um servidor DHCP falso responde mais rápido e entrega **seu próprio IP como gateway/DNS** → MitM ou redirecionamento para sites falsos.
- **DHCP Starvation:** o atacante pede IPs com milhares de MACs falsos até esgotar o pool → **negação de serviço** (e abre espaço para o rogue DHCP).

**Mitigação:**
- **DHCP Snooping** (o switch só aceita *Offers* vindos de portas confiáveis).
- **Port Security** (limita MACs por porta).
- Monitorar logs de "pool exhausted" e servidores DHCP desconhecidos.

### 7.3 LLMNR / NBT-NS / mDNS (resolução de nomes local)

Quando o DNS falha (ex.: usuário digita `\\fileserverr` errado), o Windows **pergunta para a rede inteira** via multicast/broadcast: *"Alguém aqui é o fileserverr?"*

**Risco:** um atacante responde *"sou eu!"* e a vítima tenta se autenticar nele, enviando **hashes NTLM**. Esse é um dos vetores mais clássicos em pentests internos de ambientes Windows/Active Directory.

**Mitigação:**
- **Desativar LLMNR e NBT-NS** via GPO quando não forem necessários.
- Exigir **SMB Signing**.
- Detectar respostas LLMNR/NBT-NS vindas de hosts que não são servidores.

### 7.4 Smurf Attack (broadcast direcionado + ICMP)

**Conceito histórico:** o atacante envia `ping` para o **endereço de broadcast** de uma rede, falsificando o IP de origem como o da vítima. Todos os hosts respondem **para a vítima** → amplificação → **DDoS**.

**Por que hoje é raro?** Porque roteadores modernos vêm com `no ip directed-broadcast` por padrão. É um ótimo exemplo de **configuração segura por padrão** resolvendo uma classe inteira de ataques.

> 💡 O mesmo princípio (*amplificação + IP falsificado*) aparece em ataques modernos com DNS, NTP e Memcached. Entender o Smurf ajuda a entender todos eles.

### 7.5 Reconhecimento passivo

Só de **ouvir** os broadcasts de uma rede (sem enviar nada), dá para descobrir:

- IPs e MACs ativos (ARP)
- Fabricante dos dispositivos (os 3 primeiros bytes do MAC = **OUI**)
- Nomes de host e domínio (DHCP, NetBIOS, mDNS)
- Serviços anunciados (SSDP/UPnP, mDNS: impressoras, Chromecasts etc.)

> 🔐 **Red Team:** reconhecimento passivo é **silencioso** — difícil de detectar.
> **Blue Team:** reduza o que é anunciado: desative serviços de descoberta desnecessários, segmente a rede.

---

## 8. Roteadores como alvo e como defesa

### 8.1 Por que roteadores são alvos valiosos

Quem controla o roteador controla **todo o tráfego** que passa por ele. Ele é o "ponto único de passagem".

**Vetores comuns de comprometimento:**

| Vetor | Exemplo | Defesa |
|---|---|---|
| Credenciais padrão | `admin/admin` no painel | Trocar senha na instalação |
| Painel de admin exposto à internet | Gerência remota habilitada na WAN | Desativar gerência pela WAN |
| Firmware desatualizado | CVEs públicas não corrigidas | Atualizar firmware regularmente |
| UPnP habilitado | Malware abre portas sozinho | Desativar UPnP |
| WPS habilitado | PIN fraco no Wi-Fi | Desativar WPS |
| Telnet / HTTP para gerência | Credenciais em texto puro | Usar SSH / HTTPS |
| SNMP com comunidade `public` | Vazamento da configuração | SNMPv3 ou comunidade forte + ACL |

**Consequências de um roteador comprometido:**
- **DNS hijacking:** troca o DNS para mandar vítimas a sites falsos.
- **Botnets:** roteadores domésticos são recrutados em massa (ex.: o caso *Mirai*, em 2016, que usou dispositivos IoT com senha padrão).
- **Pivô** para a rede interna.

### 8.2 Roteador como ferramenta de defesa

| Recurso | Para que serve |
|---|---|
| **ACLs (Access Control Lists)** | Permitir/negar tráfego por IP, porta e protocolo |
| **Anti-spoofing (uRPF / ingress filtering)** | Descartar pacotes com IP de origem impossível naquela interface |
| **Segmentação / roteamento entre VLANs** | Controlar quem fala com quem |
| **Logs e NetFlow** | Visibilidade: quem falou com quem, quanto e quando |
| **Hardening** | Desativar serviços desnecessários, banner de aviso, AAA |

**Exemplo de ACL (sintaxe Cisco IOS)** — bloquear que a rede de visitantes acesse a rede corporativa:

```
access-list 110 deny   ip 192.168.50.0 0.0.0.255 192.168.10.0 0.0.0.255
access-list 110 permit ip 192.168.50.0 0.0.0.255 any
!
interface GigabitEthernet0/1
 ip access-group 110 in
```

**Hardening básico (Cisco IOS):**
```
no ip directed-broadcast        ! evita amplificação tipo Smurf
no ip http server               ! desativa painel HTTP sem criptografia
no cdp run                      ! evita vazar info do equipamento (se não usado)
service password-encryption
ip ssh version 2
line vty 0 4
 transport input ssh            ! só SSH, nada de Telnet
 login local
```

---

## 9. Visão Red Team x Blue Team

| Conceito | 🔴 Red Team pergunta… | 🔵 Blue Team pergunta… |
|---|---|---|
| Domínio de broadcast | "Em qual segmento estou? O que consigo ouvir daqui?" | "Esse segmento está pequeno e isolado o suficiente?" |
| ARP | "O switch tem DAI? Consigo me posicionar no meio?" | "Estou alertando sobre IP com MAC duplicado?" |
| DHCP | "Existe DHCP Snooping?" | "Algum servidor DHCP não autorizado apareceu?" |
| LLMNR/NBT-NS | "Os hosts ainda fazem resolução por broadcast?" | "Desativei via GPO? Estou monitorando?" |
| Roteador | "Painel exposto? Senha padrão? Firmware antigo?" | "Hardening aplicado? Logs indo para o SIEM/Zabbix?" |
| Tabela de roteamento | "Daqui eu alcanço quais redes? Dá para pivotar?" | "As ACLs impedem movimentação lateral?" |
| TTL / traceroute | "Quantos saltos até o alvo? Qual o SO?" | "Devo filtrar ICMP Time Exceeded na borda?" |

> 💡 **Um bom profissional de segurança pensa dos dois lados.** Entender o ataque é o que permite construir a detecção.

---

## 10. Mão na massa: comandos para observar

Todos são **comandos de observação** da sua própria máquina/rede — seguros para usar no seu lab.

### Ver sua configuração de rede
```bash
# Linux
ip addr                 # IPs, máscaras e broadcast de cada interface
ip route                # tabela de roteamento (procure "default via")

# Windows
ipconfig /all
route print
```

### Ver a tabela ARP (IP ↔ MAC)
```bash
ip neigh                # Linux
arp -a                  # Windows / Linux
```
> 👀 Exercício de Blue Team: confira se o IP do gateway aparece com **um único MAC**.

### Ver o caminho até um destino
```bash
traceroute 8.8.8.8      # Linux
tracert 8.8.8.8         # Windows
```

### Capturar broadcasts com tcpdump
```bash
# Todo tráfego de broadcast
sudo tcpdump -i eth0 -n broadcast

# Só ARP
sudo tcpdump -i eth0 -n arp

# Só DHCP
sudo tcpdump -i eth0 -n port 67 or port 68
```

### Filtros úteis no Wireshark
```
eth.dst == ff:ff:ff:ff:ff:ff     # todo broadcast de camada 2
arp                              # tráfego ARP
arp.duplicate-address-detected   # possível ARP spoofing!
dhcp                             # tráfego DHCP (bootp em versões antigas)
llmnr || nbns                    # resolução de nomes por broadcast/multicast
icmp.type == 11                  # Time Exceeded (traceroute)
```

---

## 11. Exercícios para o seu lab

Use o **Cisco Packet Tracer** (ou VMs com Linux) para fixar:

1. **Domínios de broadcast**
   Monte 2 switches com 3 PCs cada, ligados a um roteador. No modo *Simulation*, envie um ping de um PC e observe: o ARP chega nos PCs do outro switch? Por quê?

2. **Cálculo de sub-redes**
   Divida `192.168.100.0/24` em 4 sub-redes (Corporativo, Visitantes, IoT, Servidores). Anote rede, primeiro/último host e broadcast de cada uma.

3. **Segmentação com ACL**
   Crie uma ACL que impeça a rede de Visitantes de acessar a rede de Servidores, mas permita internet. Teste com ping.

4. **DHCP Relay**
   Coloque o servidor DHCP em uma rede diferente e configure `ip helper-address` no roteador. Observe o broadcast virando unicast.

5. **Hardening**
   Aplique o checklist da seção 8.2 no roteador do lab e documente o *antes e depois*.

6. **Monitoramento (ponte com Blue Team)**
   No Wireshark, capture 5 minutos de tráfego da sua rede de casa e responda: quantos dispositivos você descobriu só pelos broadcasts? Quais serviços eles anunciam?

> 📁 **Dica de portfólio:** documente esses exercícios num repositório no GitHub com prints, topologia e conclusões de segurança. Isso demonstra conhecimento prático para vagas de SOC, Help Desk e Pentest.

---

## 12. Resumo e glossário

### Resumo em 10 frases

1. **Broadcast** = mensagem para todos de um segmento; existe porque às vezes não se sabe o destinatário.
2. Endereços: `FF:FF:FF:FF:FF:FF` (L2), `255.255.255.255` e o último IP da sub-rede (L3).
3. **Domínio de broadcast** = quem ouve o broadcast de quem; na prática, uma **zona de confiança**.
4. **Switches** ampliam domínios; **roteadores e VLANs** os separam.
5. **Roteadores** encaminham pacotes entre redes usando a **tabela de roteamento**.
6. Roteadores **não repassam broadcasts** — isso é uma barreira de segurança natural.
7. ARP, DHCP, LLMNR e NBT-NS dependem de broadcast/multicast e **não autenticam respostas** → base para MitM e roubo de credenciais.
8. Defesas de camada 2: **DAI, DHCP Snooping, Port Security, STP/BPDU Guard, storm control**.
9. Roteadores são **alvos valiosos** (controlam o tráfego) e **ferramentas de defesa** (ACLs, anti-spoofing, logs).
10. **Segmentação de rede** reduz o raio de impacto de qualquer ataque baseado em broadcast.

### Glossário rápido

| Termo | Significado |
|---|---|
| **ACL** | Lista de regras que permite ou nega tráfego |
| **ARP** | Descobre o MAC a partir de um IP |
| **DAI** | Dynamic ARP Inspection — valida respostas ARP no switch |
| **DHCP** | Distribui IPs automaticamente |
| **DHCP Snooping** | Bloqueia servidores DHCP não autorizados |
| **Gateway padrão** | Roteador para onde vão os pacotes de fora da rede local |
| **LLMNR / NBT-NS** | Resolução de nomes local do Windows, via multicast/broadcast |
| **MitM** | *Man-in-the-Middle* — atacante intercepta a comunicação |
| **Movimentação lateral** | Atacante pulando de um host comprometido para outros |
| **NAT** | Tradução de IPs privados para públicos |
| **OUI** | Primeiros 3 bytes do MAC; identificam o fabricante |
| **STP** | Spanning Tree — evita loops entre switches |
| **TTL** | Contador de saltos de um pacote |
| **uRPF** | Verificação anti-spoofing de IP de origem |
| **VLAN** | Rede virtual que divide um switch em vários domínios de broadcast |

---

> ⚖️ **Ética:** todo conhecimento ofensivo aqui serve para **entender, detectar e mitigar**. Testes só em redes suas (lab) ou com **autorização formal por escrito** e escopo definido.