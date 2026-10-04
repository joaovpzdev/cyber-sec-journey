# Endereçamento Dinâmico com DHCP: um guia didático com olhar de Cybersecurity

> **Para quem é este material:** quem está estudando redes (ex.: Cisco *Conceitos Básicos de Redes*) e quer dominar o DHCP **por dentro**: como funciona, como configurar, como ele é atacado e como defender e monitorar. É continuação do guia *Broadcasts e Roteadores*.

---

## Sumário

1. [O problema que o DHCP resolve](#1-o-problema-que-o-dhcp-resolve)
2. [Endereçamento estático x dinâmico](#2-endereçamento-estático-x-dinâmico)
3. [Peças do DHCP: cliente, servidor, relay, pool e lease](#3-peças-do-dhcp)
4. [O processo DORA, passo a passo](#4-o-processo-dora-passo-a-passo)
5. [Dentro do pacote DHCP](#5-dentro-do-pacote-dhcp)
6. [O ciclo de vida do lease: renovação, T1, T2 e liberação](#6-o-ciclo-de-vida-do-lease)
7. [Todas as mensagens DHCP](#7-todas-as-mensagens-dhcp)
8. [Opções DHCP: muito além do IP](#8-opções-dhcp-muito-além-do-ip)
9. [Reservas, exclusões e APIPA](#9-reservas-exclusões-e-apipa)
10. [DHCP Relay: atravessando roteadores](#10-dhcp-relay-atravessando-roteadores)
11. [E no IPv6? DHCPv6 e SLAAC](#11-e-no-ipv6-dhcpv6-e-slaac)
12. [Configurando na prática](#12-configurando-na-prática)
13. [Por que o DHCP é sensível em segurança](#13-por-que-o-dhcp-é-sensível-em-segurança)
14. [Ataques ao DHCP (visão conceitual)](#14-ataques-ao-dhcp-visão-conceitual)
15. [Defesas: hardening de camada 2 e do servidor](#15-defesas)
16. [DHCP como fonte de evidência (Blue Team / forense)](#16-dhcp-como-fonte-de-evidência)
17. [Visão Red Team x Blue Team](#17-visão-red-team-x-blue-team)
18. [Mão na massa: comandos e filtros](#18-mão-na-massa-comandos-e-filtros)
19. [Troubleshooting: quando o DHCP não funciona](#19-troubleshooting)
20. [Exercícios para o seu lab](#20-exercícios-para-o-seu-lab)
21. [Resumo e glossário](#21-resumo-e-glossário)

---

## 1. O problema que o DHCP resolve

Para um dispositivo conversar numa rede IPv4, ele precisa de **pelo menos quatro informações**:

| Informação | Exemplo | Para que serve |
|---|---|---|
| Endereço IP | `192.168.0.50` | Identidade na rede |
| Máscara de sub-rede | `255.255.255.0` | Saber o que é "local" e o que é "remoto" |
| Gateway padrão | `192.168.0.1` | Sair da rede local (roteador) |
| Servidor DNS | `192.168.0.1` ou `1.1.1.1` | Traduzir nomes em IPs |

Agora imagine configurar isso **na mão** em 500 notebooks, 200 celulares, 80 impressoras e 300 câmeras… e ainda garantir que **nenhum IP se repita**. Impossível de manter.

O **DHCP (Dynamic Host Configuration Protocol)** resolve isso: um servidor **empresta** essas configurações automaticamente para quem entra na rede.

> 💡 **Analogia:** o DHCP é a **recepção de um hotel**. Você chega, se identifica (MAC), recebe um quarto (IP) por um período (lease), junto com as informações da casa (gateway, DNS, Wi-Fi…). Quando vai embora, o quarto volta para a recepção.

---

## 2. Endereçamento estático x dinâmico

| | **Estático** (manual) | **Dinâmico** (DHCP) |
|---|---|---|
| Configuração | Feita à mão em cada host | Automática |
| Escala | Ruim | Excelente |
| Risco de IP duplicado | Alto (erro humano) | Baixo (servidor controla) |
| Mudanças (ex.: trocar DNS) | Host por host | Altera no servidor, todos recebem |
| Previsibilidade do IP | Total | Variável (exceto com reserva) |
| Uso típico | Servidores, roteadores, switches, firewalls | Estações, notebooks, celulares, visitantes |

> 🔐 **Visão cyber:** infraestrutura crítica (gateway, DNS, servidor DHCP, controlador de domínio, SIEM) deve ter **IP fixo** — se dependesse do DHCP e ele caísse ou fosse falsificado, a rede inteira ficaria vulnerável. Já o endereçamento dinâmico, quando bem registrado em log, ajuda o Blue Team a **rastrear quem estava com qual IP e quando**.

---

## 3. Peças do DHCP

| Peça | O que é |
|---|---|
| **Cliente DHCP** | Qualquer dispositivo que pede configuração (PC, celular, IoT) |
| **Servidor DHCP** | Quem distribui (roteador doméstico, Windows Server, Linux com Kea/dnsmasq, firewall) |
| **DHCP Relay Agent** | Roteador/switch L3 que repassa pedidos entre redes diferentes |
| **Escopo / Pool** | Faixa de IPs disponível para empréstimo (ex.: `.100` a `.200`) |
| **Lease (concessão)** | O "contrato de aluguel" do IP, com tempo de validade |
| **Exclusão** | IPs dentro da rede que o servidor **não** deve entregar |
| **Reserva** | IP sempre entregue ao mesmo MAC |

**Portas e transporte:**

- Protocolo de transporte: **UDP** (não há conexão — o cliente ainda nem tem IP!)
- **Servidor escuta na porta 67**
- **Cliente escuta na porta 68**

> 💡 Por que UDP? Porque TCP exige um *handshake* entre dois IPs. No início, o cliente **não tem IP** — ele usa `0.0.0.0` como origem e `255.255.255.255` como destino. Só um protocolo sem conexão e baseado em broadcast resolve isso.

---

## 4. O processo DORA, passo a passo

DORA = **D**iscover, **O**ffer, **R**equest, **A**cknowledge.

```
  Cliente (sem IP)                                   Servidor DHCP (192.168.0.1)
       |                                                        |
       | 1) DHCPDISCOVER  (broadcast)                           |
       |   "Tem algum servidor DHCP aí?"                        |
       |------------------------------------------------------->|
       |                                                        |
       | 2) DHCPOFFER                                           |
       |   "Posso te dar o 192.168.0.50, por 24h"               |
       |<-------------------------------------------------------|
       |                                                        |
       | 3) DHCPREQUEST  (broadcast)                            |
       |   "Quero o .50 do servidor 192.168.0.1"                |
       |------------------------------------------------------->|
       |                                                        |
       | 4) DHCPACK                                             |
       |   "Fechado! IP .50, máscara /24, GW .1, DNS .1, 24h"   |
       |<-------------------------------------------------------|
       |                                                        |
   [Cliente configura a interface e faz um ARP de checagem]
```

### 4.1 Discover

| Campo | Valor |
|---|---|
| MAC origem | MAC do cliente |
| MAC destino | `FF:FF:FF:FF:FF:FF` |
| IP origem | `0.0.0.0` |
| IP destino | `255.255.255.255` |
| Portas | UDP 68 → 67 |

O cliente grita para toda a rede local. Ele pode incluir o **último IP que usou** (opção 50) pedindo para recebê-lo de novo.

### 4.2 Offer

O(s) servidor(es) respondem oferecendo um IP livre do pool. Antes de oferecer, muitos servidores fazem um **ping de verificação** para ter certeza de que o IP não está em uso.

> ⚠️ **Se houver dois servidores na rede, o cliente recebe duas ofertas** — e normalmente aceita **a primeira que chegar**. Guarde isso: é exatamente o que um **servidor DHCP falso (rogue)** explora.

### 4.3 Request

Por que o cliente manda o Request em **broadcast** se já sabe quem é o servidor? Para avisar **todos** os servidores ao mesmo tempo:

- Ao escolhido: "aceito sua oferta".
- Aos outros: "recusei, podem devolver o IP que reservaram para mim ao pool".

O Request carrega a **opção 54 (Server Identifier)**, dizendo qual servidor foi escolhido.

### 4.4 Acknowledge

O servidor confirma e grava o lease no seu banco. Se algo deu errado (ex.: o IP foi tomado nesse meio-tempo), ele responde **DHCPNAK** e o cliente recomeça o DORA.

Após o ACK, o cliente geralmente envia um **ARP para o próprio IP** (*ARP probe / gratuitous ARP*). Se alguém responder, há **conflito**: o cliente envia **DHCPDECLINE** e pede outro IP.

> 💡 Em alguns casos o ACK/Offer é enviado em **unicast** em vez de broadcast — depende do **flag de broadcast** que o cliente marca no pacote (alguns sistemas não aceitam unicast antes de terem IP configurado).

---

## 5. Dentro do pacote DHCP

O DHCP é uma evolução do antigo **BOOTP**, por isso no Wireshark versões antigas mostram o filtro `bootp`. Campos principais:

| Campo | Significado |
|---|---|
| `op` | 1 = pedido (cliente), 2 = resposta (servidor) |
| `xid` | *Transaction ID* — número aleatório que liga pedido e resposta |
| `secs` | Segundos desde que o cliente começou o processo |
| `flags` | Bit de broadcast |
| `ciaddr` | IP atual do cliente (preenchido em renovações) |
| `yiaddr` | **"Your IP"** — o IP que o servidor está oferecendo |
| `siaddr` | IP do próximo servidor (ex.: servidor TFTP para boot) |
| `giaddr` | **IP do relay agent** (gateway) — essencial no DHCP Relay |
| `chaddr` | **MAC do cliente** (*client hardware address*) |
| `options` | Onde mora quase tudo: tipo de mensagem, máscara, gateway, DNS, lease… |

> 🔐 **Visão cyber:** repare que o servidor identifica o cliente pelo **`chaddr`** — um valor que o próprio cliente informa e que **pode ser forjado livremente**. O DHCP clássico (RFC 2131) **não tem autenticação**. Isso é a raiz de praticamente todos os ataques ao protocolo.

---

## 6. O ciclo de vida do lease

O IP é **emprestado**, não dado. O lease tem duração (ex.: 8h, 24h, 7 dias) e dois temporizadores importantes:

```
 0%            50% (T1)                 87,5% (T2)          100%
 |---------------|------------------------|-------------------|
 ACK recebido    Tenta RENOVAR            Tenta REVINCULAR     Lease expira
                 (unicast ao servidor     (broadcast para      → para de usar o IP
                  original)                qualquer servidor)  → recomeça DORA
```

| Fase | O que acontece |
|---|---|
| **Bound** | Cliente usando o IP normalmente |
| **Renewing (T1 = 50%)** | Envia `DHCPREQUEST` **unicast** ao servidor que concedeu. Se receber ACK, o tempo reinicia |
| **Rebinding (T2 = 87,5%)** | O servidor original não respondeu → envia `DHCPREQUEST` em **broadcast** para qualquer servidor |
| **Expirado** | Nenhuma resposta → remove o IP e volta ao Discover |
| **Release** | O cliente sai voluntariamente e devolve o IP (`DHCPRELEASE`) |

**Como escolher o tempo de lease?**

| Ambiente | Lease sugerido | Motivo |
|---|---|---|
| Wi-Fi de visitantes / cafeteria | 1–4 horas | Muita rotatividade, pool se esgota rápido |
| Escritório | 8 horas a 1 dia | Equilíbrio |
| Rede estável (desktops fixos) | 3–8 dias | Menos tráfego DHCP |

> 🔐 **Visão cyber:** leases **longos** + pool **pequeno** = pool esgotado com facilidade (ótimo para um ataque de *starvation*). Leases **curtos** geram mais logs e mais tráfego, mas tornam o mapeamento IP↔dispositivo mais dinâmico — o que exige **logs bem guardados** na investigação de incidentes.

---

## 7. Todas as mensagens DHCP

| Mensagem | Quem envia | Para quê |
|---|---|---|
| **DISCOVER** | Cliente | Procurar servidores |
| **OFFER** | Servidor | Oferecer um IP |
| **REQUEST** | Cliente | Aceitar oferta / renovar |
| **ACK** | Servidor | Confirmar |
| **NAK** | Servidor | Negar (IP inválido ou rede errada) |
| **DECLINE** | Cliente | "Esse IP já está em uso (conflito)" |
| **RELEASE** | Cliente | Devolver o IP |
| **INFORM** | Cliente | Já tem IP fixo, só quer as outras opções (DNS etc.) |

> 🔐 Repare: o **RELEASE** e o **DECLINE** também não são autenticados. Em teoria, alguém pode forjar um RELEASE em nome de outro cliente ou um DECLINE para "queimar" IPs do pool — mais um motivo para as defesas de camada 2 da seção 15.

---

## 8. Opções DHCP: muito além do IP

As **opções** são o verdadeiro poder do DHCP — e também o verdadeiro risco, porque o servidor diz ao cliente **para onde mandar o tráfego**.

| Nº | Opção | Exemplo | Por que importa em segurança |
|---|---|---|---|
| 1 | Máscara de sub-rede | `255.255.255.0` | Define o que é "local" |
| 3 | **Router (gateway)** | `192.168.0.1` | **Quem controla isso controla a saída do tráfego** |
| 6 | **DNS** | `192.168.0.1` | **Quem controla isso controla a resolução de nomes** |
| 12 | Hostname | `NOTE-JOAO` | Vaza nome do dispositivo (reconhecimento) |
| 15 | Nome de domínio | `empresa.local` | Revela o domínio interno |
| 42 | NTP | `192.168.0.10` | Horário correto é vital para logs e Kerberos |
| 43 | Vendor specific | — | Usado por APs/telefones IP |
| 50 | IP solicitado | `192.168.0.50` | Cliente pede IP anterior |
| 51 | Tempo de lease | `86400` (24h) | |
| 53 | Tipo de mensagem | 1=Discover … 8=Inform | |
| 54 | Server Identifier | `192.168.0.1` | Qual servidor respondeu — **ótimo para detectar rogue** |
| 55 | Lista de parâmetros pedidos | — | Sequência típica de cada SO → **fingerprinting** |
| 60 | Vendor Class ID | `MSFT 5.0`, `android-dhcp-14` | Identifica o tipo de sistema |
| 61 | Client Identifier | — | Identidade do cliente |
| 66 / 67 | Servidor TFTP / arquivo de boot | — | Boot por rede (PXE): se falsificado, entrega um SO malicioso |
| 82 | Relay Agent Information | switch + porta | Identifica **em qual porta física** o cliente está |
| 121 | Rotas estáticas classless | — | Injeta rotas no cliente (pode **desviar tráfego, inclusive de VPN**) |
| 252 | WPAD | URL de proxy | Configuração automática de proxy — vetor clássico de MitM |

> 🔐 **Dois destaques:**
> - **Fingerprinting por DHCP:** as opções 55 e 60 funcionam como uma "assinatura" do sistema. Ferramentas de NAC e de inventário (e também atacantes passivos) sabem dizer "isso é um iPhone", "isso é um Windows 11", "isso é uma câmera" só olhando o Discover.
> - **Opção 121:** já foi usada em pesquisas públicas (técnica conhecida como *TunnelVision*, 2024) para mostrar que um DHCP malicioso na mesma rede pode fazer o tráfego "escapar" de algumas VPNs. Lição: **confiar no DHCP de uma rede pública é confiar em quem a controla.**

---

## 9. Reservas, exclusões e APIPA

### 9.1 Exclusões

Faixas que o servidor **nunca** distribui — normalmente para equipamentos com IP estático.

```
Rede:       192.168.10.0/24
Excluídos:  192.168.10.1   – 192.168.10.20   (roteador, switches, servidores, impressoras)
Pool:       192.168.10.21  – 192.168.10.254
```

> ⚠️ Esquecer a exclusão é a causa nº 1 de **conflito de IP** em labs: o DHCP entrega o mesmo IP que você configurou à mão no servidor.

### 9.2 Reservas

O servidor associa **um MAC a um IP fixo**. O dispositivo continua usando DHCP, mas sempre recebe o mesmo endereço. Ótimo para impressoras, câmeras e o host do **Zabbix** que você quer monitorar com IP previsível.

> 🔐 Reserva **não é controle de acesso**: como o MAC é forjável, um atacante que clona o MAC de uma impressora recebe o IP dela. Para autenticar dispositivos de verdade, use **802.1X / NAC**.

### 9.3 APIPA (Automatic Private IP Addressing)

Se o cliente **não recebe resposta** de nenhum servidor, Windows e outros sistemas se autoatribuem um IP na faixa:

```
169.254.0.0/16   (link-local)
```

Esse IP só funciona dentro do segmento local, **sem gateway e sem internet**.

> 🛠️ **Help Desk:** viu `169.254.x.x` no `ipconfig`? O cliente **não conseguiu falar com o DHCP**. Verifique cabo, Wi-Fi, VLAN, relay ou se o servidor caiu/esgotou o pool.
> 🔐 **SOC:** muitos hosts com APIPA de repente pode indicar **DHCP fora do ar** — ou um ataque de **starvation** em andamento.

---

## 10. DHCP Relay: atravessando roteadores

O Discover é **broadcast**, e roteadores **não encaminham broadcast**. Então como um único servidor DHCP atende várias redes/VLANs?

Resposta: **DHCP Relay Agent** (`ip helper-address` no Cisco).

```
 VLAN 10 (192.168.10.0/24)                         VLAN 99 (Servidores)
  [PC] --Discover (broadcast)--> [Roteador/Switch L3] --unicast--> [Servidor DHCP 10.0.99.5]
                                  giaddr = 192.168.10.1
                                                    <--Offer------
  [PC] <------- Offer ---------- [Roteador]
```

1. O PC envia o Discover em broadcast.
2. O roteador (relay) recebe na interface `192.168.10.1`, **preenche o campo `giaddr`** com esse IP e reenvia em **unicast** para o servidor.
3. O servidor olha o `giaddr` e pensa: "esse pedido vem da rede `192.168.10.0/24` → vou usar o escopo dessa rede".
4. A resposta volta ao relay, que entrega ao cliente.

> **Vantagem de segurança:** centralizar o DHCP num servidor dentro de uma VLAN protegida (em vez de um DHCP em cada roteador) facilita **hardening, backup e coleta de logs**. Combine com a **opção 82** para saber *exatamente* em qual switch e porta cada cliente está.

---

## 11. E no IPv6? DHCPv6 e SLAAC

No IPv6 **não existe broadcast**, então o processo muda:

| Mecanismo | Como funciona |
|---|---|
| **SLAAC** | O roteador envia *Router Advertisements* (RA, ICMPv6) com o prefixo da rede; o host monta o próprio endereço sozinho |
| **DHCPv6 stateless** | SLAAC para o endereço + DHCPv6 só para opções (DNS) |
| **DHCPv6 stateful** | Servidor DHCPv6 entrega o endereço, como no IPv4 |

- DHCPv6 usa **UDP 546 (cliente)** e **547 (servidor)**.
- O cliente procura servidores no **multicast `ff02::1:2`**.
- O processo equivalente ao DORA é **SARR**: *Solicit, Advertise, Request, Reply*.

> **Ponto cego clássico:** muitas redes "só usam IPv4", mas os sistemas operacionais **têm IPv6 ativo por padrão**. Um atacante pode anunciar RAs ou responder DHCPv6 e se tornar o **DNS/gateway IPv6** das vítimas, mesmo numa rede "sem IPv6". Defesas: **RA Guard**, **DHCPv6 Guard**, e desativar IPv6 onde ele realmente não é usado (ou, melhor ainda, gerenciá-lo de verdade).

---

## 12. Configurando na prática

### 12.1 Cisco IOS (roteador como servidor DHCP) — ótimo para o Packet Tracer

```
! 1. Excluir IPs reservados para infraestrutura
ip dhcp excluded-address 192.168.10.1 192.168.10.20

! 2. Criar o pool
ip dhcp pool VLAN10-USUARIOS
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 192.168.10.10 8.8.8.8
 domain-name lab.local
 lease 1                      ! 1 dia
!
! 3. Verificar
show ip dhcp binding           ! quem recebeu qual IP
show ip dhcp pool              ! uso do pool
show ip dhcp conflict          ! conflitos detectados
show ip dhcp server statistics
```

### 12.2 Cisco IOS — relay para servidor em outra rede

```
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 ip helper-address 10.0.99.5
```

### 12.3 Linux com dnsmasq (simples, ótimo para lab)

```ini
# /etc/dnsmasq.conf
interface=eth1
dhcp-range=192.168.50.100,192.168.50.200,255.255.255.0,12h
dhcp-option=option:router,192.168.50.1
dhcp-option=option:dns-server,192.168.50.1
dhcp-host=AA:BB:CC:DD:EE:FF,192.168.50.20,zabbix-server   # reserva
log-dhcp                                                  # log detalhado
```

### 12.4 Linux com ISC Kea (servidor moderno, sucessor do ISC DHCP)

```json
{
  "Dhcp4": {
    "interfaces-config": { "interfaces": [ "eth1" ] },
    "valid-lifetime": 28800,
    "subnet4": [
      {
        "id": 1,
        "subnet": "192.168.50.0/24",
        "pools": [ { "pool": "192.168.50.100 - 192.168.50.200" } ],
        "option-data": [
          { "name": "routers", "data": "192.168.50.1" },
          { "name": "domain-name-servers", "data": "192.168.50.1" }
        ],
        "reservations": [
          { "hw-address": "aa:bb:cc:dd:ee:ff", "ip-address": "192.168.50.20" }
        ]
      }
    ]
  }
}
```

### 12.5 Do lado do cliente

```bash
# Windows
ipconfig /all          # mostra servidor DHCP, lease obtido e expiração
ipconfig /release      # devolve o IP (DHCPRELEASE)
ipconfig /renew        # pede de novo (DORA)

# Linux (NetworkManager)
nmcli device show eth0
sudo nmcli connection down "Wired connection 1" && sudo nmcli connection up "Wired connection 1"

# Linux (dhclient, em distros que usam)
sudo dhclient -r eth0  # release
sudo dhclient -v eth0  # renew com saída detalhada (mostra o DORA!)
```

---

## 13. Por que o DHCP é sensível em segurança

Resumindo tudo o que vimos, o DHCP tem uma combinação perigosa:

1. **Funciona por broadcast** → qualquer um no segmento ouve e pode responder.
2. **Não tem autenticação** → o cliente confia no **primeiro** servidor que responder.
3. **Identifica clientes pelo MAC** → que pode ser forjado.
4. **Entrega configurações críticas** → gateway, DNS, proxy (WPAD), rotas, servidor de boot.
5. **É a primeira coisa que um dispositivo faz** ao entrar na rede → acontece antes de qualquer outra proteção do host entrar em ação.

> 💡 **Frase para guardar:** *quem controla o DHCP controla para onde o tráfego da rede vai.*

---

## 14. Ataques ao DHCP (visão conceitual)

> ⚠️ Os ataques abaixo são descritos em nível **conceitual**, para você entender o risco e saber **detectar e mitigar**. Testes só em ambiente próprio (lab isolado) ou com **autorização formal por escrito** e escopo definido.

### 14.1 DHCP Starvation (esgotamento)

**Ideia:** enviar uma enxurrada de `DISCOVER`/`REQUEST`, cada um com um **MAC falso diferente**, até que o servidor entregue todos os IPs do pool.

**Impacto:**
- **Negação de serviço (DoS):** clientes legítimos não recebem IP (e caem em APIPA).
- Prepara o terreno para o **rogue DHCP**: com o servidor legítimo "sem estoque", o falso é o único que responde.

**Indicadores (IoCs):**
- Pico súbito de Discovers por segundo.
- Centenas de MACs novos vindos de **uma única porta** do switch.
- Log do servidor: *"no free leases"* / pool 100% utilizado.
- MACs aleatórios com OUIs inexistentes ou de fabricantes estranhos.

### 14.2 Rogue DHCP Server (servidor falso)

**Ideia:** um servidor não autorizado responde aos Discovers mais rápido que o legítimo e entrega:
- **Gateway = atacante** → todo tráfego passa por ele (**Man-in-the-Middle**).
- **DNS = atacante** → redirecionamento para páginas falsas (phishing, roubo de credenciais).
- **WPAD / proxy = atacante** → tráfego web passa por um proxy malicioso.
- **Opção 121** → rotas que desviam tráfego específico.

> 💡 **Nem todo rogue DHCP é malicioso!** O caso mais comum no dia a dia é um funcionário ligar um **roteador doméstico** na tomada da empresa, ou uma VM no modo "bridge" com DHCP ativo. Resultado: metade da rede recebe `192.168.0.x` e "a internet cai". É um clássico de **Help Desk**.

**Indicadores (IoCs):**
- Mais de um valor distinto na **opção 54 (Server Identifier)** na mesma rede.
- `DHCPOFFER`/`DHCPACK` vindo de uma porta do switch que não é a do servidor/uplink.
- Clientes com gateway ou DNS diferente do padrão.

### 14.3 Spoofing de mensagens (RELEASE / DECLINE)

**Ideia:** forjar um `RELEASE` em nome de outro cliente (o servidor libera o IP dele) ou mandar `DECLINE` em massa para marcar IPs como "em conflito" e tirá-los do pool.

**Impacto:** instabilidade, conflitos de IP, DoS seletivo.

### 14.4 Reconhecimento passivo via DHCP

Sem enviar nada, só ouvindo os broadcasts, é possível levantar:

- Hostnames (opção 12) → padrão de nomes da empresa (`NOTE-FIN-023`)
- Domínio interno (opção 15)
- Tipo de SO e fabricante (opções 55, 60 e OUI do MAC)
- IP do servidor DHCP, gateway e DNS

>  **Red Team:** reconhecimento passivo é silencioso.
> **Blue Team:** reduza o que vaza (padronize hostnames sem informação sensível, segmente a rede, controle quem pode se conectar fisicamente).

---

## 15. Defesas

### 15.1 Defesas no switch (camada 2)

| Recurso | O que faz | Protege contra |
|---|---|---|
| **DHCP Snooping** | Define portas **confiáveis** (uplink/servidor) e **não confiáveis** (usuários). Respostas DHCP (Offer/Ack) vindas de porta não confiável são **descartadas** | Rogue DHCP |
| **Rate limit de DHCP** | Limita pacotes DHCP por segundo em cada porta | Starvation |
| **Verificação de MAC** | Confere se o `chaddr` bate com o MAC de origem do quadro | Starvation com MAC forjado no payload |
| **Port Security** | Limita a quantidade de MACs por porta | Starvation |
| **Binding table** | O snooping grava IP + MAC + VLAN + porta + lease | Base para DAI e IP Source Guard |
| **DAI (Dynamic ARP Inspection)** | Usa a binding table para validar ARP | ARP spoofing |
| **IP Source Guard** | Só permite tráfego com o IP que o DHCP realmente entregou àquela porta | IP spoofing |
| **802.1X / NAC** | Autentica o dispositivo **antes** de liberar a porta | Dispositivo não autorizado na rede |

**Exemplo (Cisco IOS):**

```
! Ativa o DHCP Snooping globalmente e na VLAN 10
ip dhcp snooping
ip dhcp snooping vlan 10
ip dhcp snooping verify mac-address
!
! Porta do uplink/servidor: confiável
interface GigabitEthernet0/1
 ip dhcp snooping trust
!
! Portas de usuários: não confiáveis + limite de taxa + port security
interface range FastEthernet0/1 - 24
 ip dhcp snooping limit rate 10
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
!
! Usa a binding table para proteger contra ARP spoofing e IP spoofing
ip arp inspection vlan 10
interface range FastEthernet0/1 - 24
 ip verify source
!
! Verificação
show ip dhcp snooping
show ip dhcp snooping binding
show ip dhcp snooping statistics
```

> 💡 **Ordem lógica:** DHCP Snooping é a **fundação**. DAI e IP Source Guard **dependem** da tabela que ele constrói.

### 15.2 Defesas no servidor DHCP

- **IP estático** para o próprio servidor, em VLAN de infraestrutura protegida.
- **Exclusões** corretas para toda a infraestrutura.
- **Pools dimensionados** com folga e leases adequados ao ambiente.
- **Alta disponibilidade** (failover ou dois servidores com divisão de escopo).
- **Logs centralizados** (syslog → SIEM / Wazuh / Graylog) com retenção definida.
- Em ambiente Windows/AD: **autorizar o servidor DHCP no Active Directory** (servidores Windows não autorizados não sobem o serviço).
- Desativar opções desnecessárias (ex.: não distribuir WPAD se não usa).
- Atualizar o software do servidor (Kea, Windows Server etc.) — servidores DHCP já tiveram vulnerabilidades críticas publicadas.

### 15.3 Defesas no cliente / usuário

- Em redes públicas, usar **VPN** bem configurada (e preferir clientes que bloqueiam rotas injetadas por DHCP).
- **HTTPS/HSTS, SSH, DNS criptografado** → mesmo com MitM, o conteúdo continua protegido.
- Desativar **WPAD** automático onde não é necessário.

---

## 16. DHCP como fonte de evidência

Para o Blue Team, os **logs do DHCP são ouro** em investigação de incidentes.

**Cenário típico de SOC:**

> O firewall alertou: *"192.168.10.57 acessou um domínio de malware às 14:32 de terça."*
> Pergunta: **quem é o 192.168.10.57?**

Como o IP é dinâmico, ele pode ter sido de outro dispositivo ontem. A resposta vem dos logs do DHCP:

```
2026-09-29 13:05:12 DHCPACK on 192.168.10.57 to aa:bb:cc:12:34:56 (NOTE-FIN-023) via eth1
```

→ IP `.57` estava com o MAC `aa:bb:cc:12:34:56`, hostname `NOTE-FIN-023`, desde 13:05. Combinando com a **opção 82** (switch/porta) ou com a tabela de MACs do switch, chega-se até a **mesa** do equipamento.

**O que monitorar (ideias de alertas para SIEM / Zabbix):**

| Métrica / evento | Por que alertar |
|---|---|
| Uso do pool > 80% / 95% | Esgotamento iminente (natural ou starvation) |
| Taxa de DISCOVER acima do normal | Possível starvation ou loop |
| Novo Server Identifier (opção 54) na rede | Rogue DHCP |
| Violações de DHCP Snooping / Port Security nos logs do switch | Tentativa de ataque ou equipamento não autorizado |
| MAC desconhecido recebendo lease fora do horário | Dispositivo estranho na rede |
| Muitos `DECLINE` / `NAK` | Conflitos de IP ou spoofing |
| Serviço DHCP parado | Disponibilidade |


---

## 17. Visão Red Team x Blue Team

| Tema | 🔴 Red Team pergunta… | 🔵 Blue Team pergunta… |
|---|---|---|
| Reconhecimento | "O que os Discovers revelam sobre hostnames, domínio e SOs?" | "Nossos hostnames vazam informação sensível?" |
| Rogue DHCP | "O switch tem DHCP Snooping? Portas de usuário estão como não confiáveis?" | "Estou alertando quando surge um novo servidor DHCP?" |
| Starvation | "Existe rate limit e port security?" | "Monitoro uso do pool e taxa de Discover?" |
| IPv6 | "Os hosts aceitam RA/DHCPv6 mesmo numa rede 'só IPv4'?" | "RA Guard e DHCPv6 Guard estão ativos?" |
| Opções perigosas | "WPAD e opção 121 são aceitos pelos clientes?" | "Distribuímos só as opções necessárias?" |
| Evidência | — | "Consigo responder 'quem tinha o IP X no horário Y'?" |
| Acesso físico | "Consigo ligar um dispositivo numa tomada qualquer e receber IP?" | "Temos 802.1X/NAC?" |

---

## 18. Mão na massa: comandos e filtros

Comandos de **observação** — seguros para usar na sua própria máquina/rede.

### Ver o DORA acontecendo

```bash
# Terminal 1: captura
sudo tcpdump -i eth0 -n -vv port 67 or port 68

# Terminal 2: força uma renovação
sudo dhclient -r eth0 && sudo dhclient -v eth0      # Linux
ipconfig /release && ipconfig /renew                # Windows (em outro PC)
```

### Filtros no Wireshark

```
dhcp                                   # todo DHCP (use "bootp" em versões antigas)
dhcp.option.dhcp == 1                  # só DISCOVER
dhcp.option.dhcp == 2                  # só OFFER
dhcp.option.dhcp == 3                  # só REQUEST
dhcp.option.dhcp == 5                  # só ACK
dhcp.option.dhcp == 6                  # só NAK
dhcp.option.dhcp_server_id             # mostra os servidores que estão respondendo
dhcp.option.hostname                   # hostnames vazando
dhcp.option.vendor_class_id            # tipo de SO / fabricante
dhcpv6                                 # DHCP no IPv6
icmpv6.type == 134                     # Router Advertisements (IPv6)
```

>  **Exercício de Blue Team:** abra *Statistics → Conversations* ou aplique `dhcp.option.dhcp == 2` e confira **quantos IPs diferentes** estão enviando OFFER. Se for mais de um (e você não tem failover), investigue.

### Onde ficam os leases e logs

| Sistema | Local |
|---|---|
| Cliente Linux (dhclient) | `/var/lib/dhcp/dhclient.leases` |
| Cliente Linux (NetworkManager) | `/var/lib/NetworkManager/*.lease` |
| Servidor dnsmasq | `/var/lib/misc/dnsmasq.leases` + `journalctl -u dnsmasq` |
| Servidor Kea | arquivo *memfile* (CSV) ou banco de dados configurado |
| Windows Server | `C:\Windows\System32\dhcp\DhcpSrvLog-*.log` |
| Cisco IOS | `show ip dhcp binding` |

---

## 19. Troubleshooting

Roteiro de **Help Desk / N1** quando "não pega IP":

| Sintoma | Causa provável | Verificação |
|---|---|---|
| IP `169.254.x.x` | Sem resposta do DHCP | Cabo/Wi-Fi, VLAN da porta, servidor ativo, relay configurado |
| IP de outra faixa (ex.: `192.168.0.x` em vez de `10.x`) | **Rogue DHCP** (ex.: roteador doméstico ligado na rede) | `ipconfig /all` → campo "Servidor DHCP" |
| "Conflito de endereço IP" | IP estático dentro do pool sem exclusão | `show ip dhcp conflict`, revisar exclusões |
| Alguns pegam IP, outros não | **Pool esgotado** | Uso do pool, tamanho do lease, possível starvation |
| Pega IP mas não navega | Gateway/DNS errados na configuração do pool | `ipconfig /all`, `nslookup`, `ping` no gateway |
| Funciona numa VLAN, não em outra | Falta `ip helper-address` na interface daquela VLAN | Configuração do relay |
| Pega IP, mas porta do switch bloqueia | DHCP Snooping / Port Security disparou | Logs do switch, `show port-security` |

---

## 20. Exercícios para o seu lab

Use o **Cisco Packet Tracer** (ou VMs Linux em rede isolada):

1. **DORA no modo Simulation**
   Monte 1 roteador + 1 switch + 3 PCs. Configure o roteador como servidor DHCP. No modo *Simulation*, filtre só DHCP e clique em cada pacote: identifique Discover, Offer, Request e Ack, e os campos `yiaddr` e `chaddr`.

2. **Exclusões e reservas**
   Exclua `.1` a `.20`, coloque um "servidor" fixo em `.10` e confirme que nenhum PC recebe esse IP. Depois, faça uma reserva por MAC (no Packet Tracer, use um servidor com serviço DHCP, ou faça no dnsmasq/Kea).

3. **APIPA de propósito**
   Desligue o serviço DHCP e renove o IP de um PC. Observe o `169.254.x.x`. Ligue de novo e renove.

4. **DHCP Relay entre VLANs**
   Crie VLAN 10 e VLAN 20, um servidor DHCP central em uma VLAN de servidores e configure `ip helper-address`. Verifique no servidor qual escopo atendeu cada pedido (graças ao `giaddr`).

5. **Simulando um rogue DHCP "acidental"**
   Adicione um segundo roteador na rede com DHCP entregando outra faixa. Veja os PCs recebendo configurações erradas. Em seguida, ative **DHCP Snooping** no switch, marque só a porta do servidor legítimo como `trust` e repita. O que mudou?

6. **Documentação de evidência**
   Monte uma tabela "IP ↔ MAC ↔ hostname ↔ porta do switch" usando `show ip dhcp binding` e `show mac address-table`. É exatamente o que um analista de SOC faz para localizar um host suspeito.

7. **Monitoramento (ponte com o projeto Zabbix)**
   Monitore o serviço DHCP de uma VM Linux do lab e crie um alerta para quando o serviço parar ou o pool passar de 80%.


---

## 21. Resumo e glossário

### Resumo em 12 frases

1. O **DHCP** distribui automaticamente IP, máscara, gateway, DNS e outras opções.
2. Usa **UDP 67 (servidor)** e **68 (cliente)**; no IPv6, **546/547**.
3. O processo é o **DORA**: Discover → Offer → Request → Ack.
4. O Discover é **broadcast** porque o cliente ainda não tem IP nem sabe quem é o servidor.
5. O IP é **emprestado** (lease), com renovação em **T1 (50%)** e revinculação em **T2 (87,5%)**.
6. **Exclusões** protegem IPs fixos; **reservas** fixam IP por MAC (mas não autenticam).
7. **APIPA (169.254.x.x)** indica que o cliente não conseguiu falar com nenhum DHCP.
8. **DHCP Relay** (`ip helper-address`) leva os pedidos através de roteadores, usando o campo `giaddr`.
9. O DHCP **não tem autenticação**: o cliente confia no primeiro servidor que responder.
10. Principais ataques: **starvation**, **rogue DHCP** (MitM via gateway/DNS falsos), spoofing de mensagens e reconhecimento passivo.
11. A defesa base é o **DHCP Snooping**, completada por rate limit, Port Security, DAI, IP Source Guard e 802.1X.
12. **Logs de DHCP** são essenciais para responder "quem tinha esse IP naquele momento?" numa investigação.

### Glossário rápido

| Termo | Significado |
|---|---|
| **APIPA** | Autoatribuição de IP `169.254.x.x` quando não há DHCP |
| **Binding** | Registro IP ↔ MAC ↔ porta ↔ lease |
| **chaddr** | Campo com o MAC do cliente no pacote DHCP |
| **DHCP Relay** | Repassa pedidos DHCP entre redes |
| **DHCP Snooping** | Recurso do switch que bloqueia servidores DHCP não autorizados |
| **DORA** | Discover, Offer, Request, Acknowledge |
| **Exclusão** | IP que o servidor não distribui |
| **giaddr** | IP do relay agent; indica de qual rede veio o pedido |
| **Lease** | Tempo de empréstimo do IP |
| **Opção 82** | Informação do relay (switch/porta do cliente) |
| **Pool / Escopo** | Faixa de IPs disponível para distribuição |
| **RA Guard** | Bloqueia Router Advertisements IPv6 não autorizados |
| **Reserva** | IP fixo associado a um MAC |
| **Rogue DHCP** | Servidor DHCP não autorizado na rede |
| **SARR** | Solicit, Advertise, Request, Reply (DHCPv6) |
| **SLAAC** | Autoconfiguração de endereço IPv6 sem servidor |
| **Starvation** | Esgotamento proposital do pool de IPs |
| **T1 / T2** | Momentos de renovação (50%) e revinculação (87,5%) do lease |
| **yiaddr** | "Your IP" — o endereço oferecido ao cliente |

---

> ⚖️ **Ética:** todo conhecimento ofensivo aqui serve para **entender, detectar e mitigar**. Testes só em redes suas (lab isolado) ou com **autorização formal por escrito** e escopo definido.