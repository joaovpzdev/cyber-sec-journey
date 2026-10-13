# Network Defense (Cisco) — Módulo 4: Listas de Controle de Acesso (ACLs)

> Anotações de estudo do curso **Network Defense** da Cisco Networking Academy.

**Objetivo do módulo:** entender como as **ACLs** filtram o tráfego em roteadores, como escrever máscaras curinga, quando usar ACL padrão ou estendida, e como aplicá-las para mitigar ataques em IPv4 e IPv6.

> A ordem e os nomes das seções podem ser um pouco diferentes no curso. O conteúdo está organizado por tema.

---

## O que é uma ACL

Uma **ACL** (*Access Control List*) é uma lista de regras que o roteador consulta para decidir se um pacote **passa** (*permit*) ou é **descartado** (*deny*). Cada regra da lista é uma **ACE** (*Access Control Entry*).

A ACL olha os cabeçalhos do pacote:

| Camada | Campos que a ACL pode verificar |
| --- | --- |
| **Camada 3** (rede) | IP de origem, IP de destino, protocolo (TCP, UDP, ICMP...) |
| **Camada 4** (transporte) | Porta de origem, porta de destino, flags TCP |

### Para que servem

- **Filtrar tráfego** (o uso principal neste módulo): bloquear acessos indevidos entre redes.
- Limitar quem pode acessar o roteador por **SSH/Telnet** (linhas VTY).
- Selecionar tráfego para outras funções: **NAT**, **QoS**, VPN, *route maps*.

### Como o roteador processa uma ACL

1. Compara o pacote com as ACEs **de cima para baixo**, na ordem.
2. Na **primeira ACE que bater**, executa a ação (permit ou deny) e **para de procurar**.
3. Se nenhuma ACE bater, o pacote cai no **deny implícito** (`deny any`) que existe no fim de toda ACL.

**Consequências práticas:**

- A **ordem importa**: regras mais específicas vêm antes das mais genéricas.
- Uma ACL só com `deny` bloqueia **tudo**, por causa do deny implícito. Toda ACL precisa de pelo menos um `permit`.

### Direção: entrada ou saída

| Direção | Quando é verificada | Observação |
| --- | --- | --- |
| **Inbound** (entrada) | Quando o pacote chega na interface, **antes** do roteamento | Mais eficiente: descarta o pacote antes de gastar processamento roteando |
| **Outbound** (saída) | Quando o pacote vai sair pela interface, **depois** do roteamento | Útil quando o mesmo filtro vale para tráfego vindo de várias interfaces |

---

## Máscara curinga (*wildcard mask*)

A ACL usa uma **máscara curinga** para dizer quais bits do endereço devem ser verificados.

| Bit da máscara curinga | Significado |
| --- | --- |
| **0** | O bit **precisa ser igual** ao do endereço |
| **1** | O bit **é ignorado** (pode ser qualquer valor) |

É o "inverso" da máscara de sub-rede.

### Calcular rapidamente

Subtrair a máscara de sub-rede de `255.255.255.255`:

```text
  255.255.255.255
- 255.255.255.0     (/24)
= 0.0.0.255         → máscara curinga
```

| Rede | Máscara de sub-rede | Máscara curinga |
| --- | --- | --- |
| 192.168.10.0/24 | 255.255.255.0 | 0.0.0.255 |
| 192.168.10.0/26 | 255.255.255.192 | 0.0.0.63 |
| 10.0.0.0/8 | 255.0.0.0 | 0.255.255.255 |
| 192.168.10.5/32 (um host) | 255.255.255.255 | 0.0.0.0 |

### Palavras-chave

| Palavra-chave | Equivale a | Exemplo |
| --- | --- | --- |
| **host** | máscara `0.0.0.0` (um único IP) | `host 192.168.10.5` = `192.168.10.5 0.0.0.0` |
| **any** | máscara `255.255.255.255` (qualquer IP) | `any` = `0.0.0.0 255.255.255.255` |

### Faixa de redes

Para pegar de `192.168.16.0/24` até `192.168.31.0/24` (16 redes) numa única ACE:

```text
192.168.16.0 0.0.15.255
```

---

## Diretrizes para criar ACLs

### A regra dos "3 Ps"

Só pode existir **uma ACL**:

- **por Protocolo** (uma para IPv4, outra para IPv6),
- **por Porta** (*interface*),
- **por direção** (entrada ou saída).

Ou seja, uma interface pode ter no máximo 4 ACLs: IPv4 entrada, IPv4 saída, IPv6 entrada e IPv6 saída.

### Boas práticas

- Planejar a ACL com base na **política de segurança** da organização.
- Escrever em um editor de texto antes de colar no roteador, e guardar uma cópia.
- **Documentar** com `remark` (comentário dentro da ACL).
- Colocar as regras **mais específicas no topo**.
- **Testar** em ambiente de desenvolvimento antes de aplicar em produção.

### Onde aplicar

| Tipo | Onde colocar | Por quê |
| --- | --- | --- |
| **Estendida** | **Perto da origem** do tráfego | Filtra com precisão (origem, destino, porta), então descarta cedo sem bloquear nada além do pretendido |
| **Padrão** | **Perto do destino** | Só olha o IP de origem; se ficar perto da origem, pode bloquear o acesso dessa rede a **todos** os destinos |

Fatores que também influenciam: quem controla cada roteador, largura de banda dos links e facilidade de configuração.

---

## Tipos de ACL IPv4

| | **Padrão** (*standard*) | **Estendida** (*extended*) |
| --- | --- | --- |
| Filtra por | Só **IP de origem** | IP de origem e destino, protocolo, portas, flags TCP |
| Numeração | 1–99 e 1300–1999 | 100–199 e 2000–2699 |
| Precisão | Baixa | Alta |
| Posição | Perto do destino | Perto da origem |

### Numerada x nomeada

| | Numerada | Nomeada |
| --- | --- | --- |
| Identificação | Um número (ex.: `10`, `110`) | Um nome (ex.: `BLOQUEIA-WEB`) |
| Edição | Mais difícil | Fácil: pode inserir e remover linhas pelo número de sequência |
| Recomendação | — | **Preferida**: o nome já explica a função |

---

## Configurar ACL padrão

### Numerada

```text
R1(config)# access-list 10 remark Permite a LAN 192.168.10.0
R1(config)# access-list 10 permit 192.168.10.0 0.0.0.255
R1(config)# interface g0/0/1
R1(config-if)# ip access-group 10 out
```

### Nomeada

```text
R1(config)# ip access-list standard PERMITE-LAN10
R1(config-std-nacl)# remark Permite a LAN 192.168.10.0
R1(config-std-nacl)# permit 192.168.10.0 0.0.0.255
R1(config-std-nacl)# deny any log
R1(config-std-nacl)# exit
R1(config)# interface g0/0/1
R1(config-if)# ip access-group PERMITE-LAN10 out
```

> O `deny any log` explícito não muda o comportamento (o deny implícito já existe), mas **registra** e **conta** os pacotes bloqueados. Isso ajuda a monitorar tentativas de acesso.

---

## Modificar uma ACL

Duas formas:

1. **Editor de texto:** copiar a ACL, editar, apagar a antiga (`no access-list 10`) e colar a nova.
2. **Números de sequência** (funciona em ACLs nomeadas e numeradas, pelo modo `ip access-list`):

```text
R1# show access-lists
Standard IP access list 10
    10 permit 192.168.10.0, wildcard bits 0.0.0.255
    20 deny   192.168.10.99

R1(config)# ip access-list standard 10
R1(config-std-nacl)# no 20
R1(config-std-nacl)# 5 deny host 192.168.10.99
```

A linha `5` fica **antes** da linha `10`. Por padrão, as ACEs são numeradas de 10 em 10, deixando espaço para inserções.

**Atenção:** nesse exemplo original, o `deny 192.168.10.99` na linha 20 nunca seria usado, porque o host já bate no `permit` da linha 10. Por isso a ordem é tão importante.

### Zerar os contadores

```text
R1# clear access-list counters 10
```

---

## Proteger o acesso VTY (SSH) com ACL padrão

Para restringir **quem** pode acessar o roteador remotamente, a ACL é aplicada nas linhas VTY com **`access-class`** (e não `ip access-group`):

```text
R1(config)# ip access-list standard ADMIN-ACCESS
R1(config-std-nacl)# remark Somente o PC do administrador
R1(config-std-nacl)# permit host 192.168.10.10
R1(config-std-nacl)# deny any log
R1(config-std-nacl)# exit
R1(config)# line vty 0 4
R1(config-line)# transport input ssh
R1(config-line)# access-class ADMIN-ACCESS in
```

- Aplicar a **mesma** restrição em **todas** as linhas VTY, porque o usuário pode cair em qualquer uma.

---

## Configurar ACL estendida

Sintaxe geral:

```text
access-list <100-199> {permit|deny} <protocolo> <origem> <curinga> <destino> <curinga> [operador porta] [established] [log]
```

Operadores de porta: `eq` (igual), `gt` (maior), `lt` (menor), `neq` (diferente), `range` (faixa).

### Exemplo: LAN só pode navegar na web

```text
R1(config)# ip access-list extended NAVEGACAO-LAN10
R1(config-ext-nacl)# remark Permite HTTP e HTTPS para a LAN 10
R1(config-ext-nacl)# permit tcp 192.168.10.0 0.0.0.255 any eq 80
R1(config-ext-nacl)# permit tcp 192.168.10.0 0.0.0.255 any eq 443
R1(config-ext-nacl)# permit udp 192.168.10.0 0.0.0.255 any eq 53
R1(config-ext-nacl)# exit
R1(config)# interface g0/0/0
R1(config-if)# ip access-group NAVEGACAO-LAN10 in
```

> A ACL é aplicada na entrada da interface da LAN (perto da origem). Sem a linha do DNS (UDP 53), os usuários não conseguiriam resolver nomes de sites.

### TCP *established*

Permite a **volta** só de conexões que a rede interna iniciou. O roteador deixa passar segmentos TCP com a flag **ACK** ou **RST** ligada:

```text
R1(config)# ip access-list extended RESPOSTAS-WEB
R1(config-ext-nacl)# permit tcp any 192.168.10.0 0.0.0.255 established
R1(config-ext-nacl)# exit
R1(config)# interface g0/0/0
R1(config-if)# ip access-group RESPOSTAS-WEB out
```

- Bloqueia conexões **iniciadas de fora** (o primeiro SYN não tem ACK).
- É uma forma **simples** de filtragem com estado. O firewall *stateful* de verdade (próximos módulos) faz isso muito melhor, porque acompanha a sessão inteira.

---

## Mitigação de ataques com ACLs

### Anti-spoofing (falsificação de IP)

Na interface que recebe tráfego da **internet**, bloquear pacotes com IP de origem que **nunca** deveria vir de fora:

| Faixa | Por que bloquear |
| --- | --- |
| `0.0.0.0/8` | Endereços "esta rede", inválidos como origem |
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | Endereços privados (RFC 1918), não roteáveis na internet |
| `127.0.0.0/8` | Loopback |
| `224.0.0.0/4` | Multicast, inválido como origem |
| A própria rede interna da empresa | Alguém de fora fingindo ser de dentro |

```text
R1(config)# ip access-list extended ANTI-SPOOF
R1(config-ext-nacl)# deny ip 0.0.0.0 0.255.255.255 any
R1(config-ext-nacl)# deny ip 10.0.0.0 0.255.255.255 any
R1(config-ext-nacl)# deny ip 172.16.0.0 0.15.255.255 any
R1(config-ext-nacl)# deny ip 192.168.0.0 0.0.255.255 any
R1(config-ext-nacl)# deny ip 127.0.0.0 0.255.255.255 any
R1(config-ext-nacl)# deny ip 224.0.0.0 15.255.255.255 any
R1(config-ext-nacl)# permit ip any any
R1(config-ext-nacl)# exit
R1(config)# interface s0/0/0
R1(config-if)# ip access-group ANTI-SPOOF in
```

No sentido contrário, na saída para a internet, só deixar sair pacotes com origem na **própria rede interna**.

### Permitir só os serviços necessários

Quando a rede interna tem servidores acessados de fora, liberar **apenas** as portas deles (por exemplo DNS 53, SMTP 25, HTTP/HTTPS 80/443 para o servidor certo) e negar o resto.

### Filtrar ICMP

O ICMP ajuda o atacante a **mapear a rede** (ping sweep, traceroute), mas algumas mensagens são necessárias para a rede funcionar.

| Direção | Mensagens ICMP normalmente permitidas |
| --- | --- |
| **Entrando** (de fora para dentro) | `echo-reply` (resposta aos pings internos), `unreachable` (destino inalcançável), `source-quench` |
| **Saindo** (de dentro para fora) | `echo` (ping), `parameter-problem`, `packet-too-big`, `source-quench` |

### Proteger o gerenciamento

- Liberar SSH, SNMP e Syslog **só** a partir dos IPs dos administradores ou da rede de gerência.
- Bloquear SNMP vindo da internet.

---

## ACLs IPv6

As ACLs IPv6 funcionam de forma parecida com as estendidas IPv4, mas com diferenças importantes:

| Característica | ACL IPv6 |
| --- | --- |
| Tipo | Só existe **nomeada** e só um tipo (equivale à estendida) |
| Aplicação na interface | `ipv6 traffic-filter` (no IPv4 é `ip access-group`) |
| Máscara | Usa **comprimento de prefixo** (`/64`), não máscara curinga |
| Regras implícitas no fim | `permit icmp any any nd-na`, `permit icmp any any nd-ns` e depois `deny ipv6 any any` |

**Por que o permit implícito de ND?** O IPv6 não tem ARP. Ele usa o **Neighbor Discovery** (mensagens ICMPv6 *neighbor solicitation* e *neighbor advertisement*) para descobrir endereços MAC. Se o ND fosse bloqueado, a rede pararia de funcionar.

**Cuidado:** se você escrever um `deny ipv6 any any` explícito (por exemplo, para usar `log`), ele vem **antes** das regras implícitas de ND. Então é preciso permitir o ND manualmente antes dele.

```text
R1(config)# ipv6 access-list BLOQUEIA-FTP
R1(config-ipv6-acl)# deny tcp any any eq ftp
R1(config-ipv6-acl)# deny tcp any any eq ftp-data
R1(config-ipv6-acl)# permit ipv6 any any
R1(config-ipv6-acl)# exit
R1(config)# interface g0/0/0
R1(config-if)# ipv6 traffic-filter BLOQUEIA-FTP in
```

---

## Comandos de verificação

| Comando | Mostra |
| --- | --- |
| `show access-lists` | Todas as ACLs, com as ACEs e **contadores** de pacotes que bateram em cada uma |
| `show ip access-lists` / `show ipv6 access-list` | Só as ACLs IPv4 / IPv6 |
| `show ip interface g0/0/0` | Quais ACLs estão aplicadas na interface e em que direção |
| `show running-config \| section access-list` | As ACLs na configuração |
| `clear access-list counters` | Zera os contadores |

---

## Resumo rápido

- A ACL é lida **de cima para baixo**; vale a **primeira** regra que bater.
- Toda ACL termina com um **deny implícito**: precisa ter pelo menos um `permit`.
- **Máscara curinga:** `0` confere, `1` ignora; `host` = um IP, `any` = qualquer IP.
- **3 Ps:** uma ACL por protocolo, por interface, por direção.
- **Padrão** (1–99): só origem, colocar **perto do destino**.
- **Estendida** (100–199): origem, destino, protocolo e porta, colocar **perto da origem**.
- **Nomeadas** são mais fáceis de entender e editar.
- VTY usa **`access-class`**; interface usa **`ip access-group`** (IPv6: `ipv6 traffic-filter`).
- **Anti-spoofing:** bloquear na entrada da internet os IPs privados, loopback e multicast como origem.
- **IPv6:** só nomeadas, prefixo no lugar da curinga e ND liberado implicitamente.

## Relação com os labs de Packet Tracer

| Tema do módulo | Lab |
| --- | --- |
| ACL padrão e estendida, máscara curinga, posicionamento | Lab 4 — ACLs |
| `access-class` nas linhas VTY com SSH | Lab 1 — Acesso seguro |
| Filtro de tráfego entre zonas (evolução das ACLs) | Lab 6 — Zone-Based Firewall |

## Vocabulário (inglês → português)

| Inglês | Português |
| --- | --- |
| access control list (ACL) | lista de controle de acesso |
| access control entry (ACE) | entrada (regra) da lista |
| wildcard mask | máscara curinga |
| implicit deny | negação implícita |
| inbound / outbound | entrada / saída |
| standard / extended | padrão / estendida |
| named / numbered | nomeada / numerada |
| sequence number | número de sequência |
| spoofing | falsificação (de endereço) |
| established | conexão já estabelecida |
| neighbor discovery (ND) | descoberta de vizinhos |
| traffic filter | filtro de tráfego |
