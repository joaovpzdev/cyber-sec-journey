# Utilitários de Teste de Rede: um guia didático com olhar de Cybersecurity

> **Para quem é este material:** quem está estudando redes (ex.: Cisco *Conceitos Básicos de Redes*) e quer dominar as **ferramentas de linha de comando** que todo profissional de Help Desk, SOC e Pentest usa no dia a dia: o que cada uma faz, como ler o resultado e o que ela revela do ponto de vista da segurança. É continuação dos guias *Broadcasts e Roteadores*, *DHCP*, *TCP x UDP* e *Roteamento entre Redes*.

---

## Sumário

1. [Por que dominar utilitários de rede](#1-por-que-dominar-utilitários-de-rede)
2. [Método: testar de baixo para cima](#2-método-testar-de-baixo-para-cima)
3. [ipconfig / ip: "quem sou eu na rede?"](#3-ipconfig--ip)
4. [ping: "o destino está vivo?"](#4-ping)
5. [traceroute / tracert / mtr / pathping: "por onde passo?"](#5-traceroute--tracert--mtr--pathping)
6. [nslookup / dig: "o nome resolve?"](#6-nslookup--dig)
7. [netstat / ss: "o que está aberto e conectado?"](#7-netstat--ss)
8. [Testando portas: nc, Test-NetConnection, telnet](#8-testando-portas)
9. [curl e openssl: testando HTTP e TLS](#9-curl-e-openssl)
10. [Tabela de vizinhos e rotas](#10-tabela-de-vizinhos-e-rotas)
11. [tcpdump e Wireshark: "o que está passando no fio?"](#11-tcpdump-e-wireshark)
12. [iperf3: medindo desempenho](#12-iperf3)
13. [whois e consultas de reputação](#13-whois-e-consultas-de-reputação)
14. [Scanners de rede: uso responsável](#14-scanners-de-rede-uso-responsável)
15. [Utilitários no Cisco IOS (Packet Tracer)](#15-utilitários-no-cisco-ios)
16. [O outro lado: quando o atacante usa as mesmas ferramentas](#16-o-outro-lado)
17. [Visão Red Team x Blue Team](#17-visão-red-team-x-blue-team)
18. [Cheat sheet: Windows x Linux x Cisco](#18-cheat-sheet)
19. [Cenários de troubleshooting](#19-cenários-de-troubleshooting)
20. [Exercícios para o seu lab](#20-exercícios-para-o-seu-lab)
21. [Resumo e glossário](#21-resumo-e-glossário)

---

## 1. Por que dominar utilitários de rede

Essas ferramentas são as mesmas em três profissões diferentes — o que muda é a **pergunta**:

| Profissional | Pergunta típica | Exemplo |
|---|---|---|
| 🛠️ **Help Desk / N1** | "Por que **não funciona**?" | "O usuário não acessa o sistema" → `ipconfig`, `ping`, `nslookup` |
| 🔵 **Blue Team / SOC** | "O que está **acontecendo** e é **normal**?" | "Que processo abriu essa conexão para fora?" → `ss -tnp`, `netstat -ano`, Wireshark |
| 🔴 **Red Team / Pentest** | "O que **existe** e está **exposto**?" (com autorização) | Mapear rotas, serviços e nomes dentro do escopo |

> 💡 **Analogia:** os utilitários são o **estetoscópio, termômetro e raio-X** da rede. Nenhum deles cura nada sozinho, mas sem eles você trabalha no escuro.

> ⚖️ **Regra de ouro para toda esta apostila:** comandos de **observação da sua própria máquina** são sempre seguros. Testes contra **máquinas e redes de terceiros** só com **autorização formal por escrito** e escopo definido.

---

## 2. Método: testar de baixo para cima

Testar aleatoriamente desperdiça tempo. Siga o modelo OSI **de baixo para cima** (ou "de dentro para fora"):

| Passo | Camada | Pergunta | Ferramenta |
|---|---|---|---|
| 1 | Física / Enlace | O cabo/Wi-Fi está conectado? Link ativo? | LED da placa, `ip link`, `ipconfig` |
| 2 | Rede (local) | Tenho IP, máscara e gateway corretos? | `ipconfig /all`, `ip addr` |
| 3 | Pilha local | Meu TCP/IP funciona? | `ping 127.0.0.1` |
| 4 | Rede local | Chego no gateway? | `ping <gateway>` |
| 5 | Roteamento | Chego em um IP fora da rede? | `ping 8.8.8.8`, `traceroute` |
| 6 | DNS | O nome resolve? | `nslookup`, `dig` |
| 7 | Transporte | A porta do serviço responde? | `Test-NetConnection`, `nc` |
| 8 | Aplicação | O serviço responde certo? | `curl`, navegador, `openssl s_client` |

> 🛠️ **Dica de ouro:** se `ping 8.8.8.8` funciona e `ping google.com` não, **o problema é DNS** — não "a internet". Esse único raciocínio resolve uma enorme fatia dos chamados de Help Desk.

---

## 3. ipconfig / ip

**Para que serve:** mostrar a configuração de rede **do próprio host**.

### Windows

```
ipconfig                 # resumo: IP, máscara, gateway
ipconfig /all            # completo: MAC, DHCP, DNS, lease
ipconfig /release        # devolve o IP ao DHCP
ipconfig /renew          # pede um IP novo
ipconfig /displaydns     # cache DNS local
ipconfig /flushdns       # limpa o cache DNS
```

### Linux

```bash
ip addr                  # IPs e máscaras (substitui o antigo ifconfig)
ip -br addr              # versão resumida, uma linha por interface
ip link                  # estado das interfaces (UP/DOWN) e MACs
ip route                 # tabela de roteamento e gateway
resolvectl status        # servidores DNS em uso (systemd-resolved)
cat /etc/resolv.conf     # DNS configurado
```

### Como ler o resultado

| Você vê… | Significa… |
|---|---|
| IP `169.254.x.x` | Não recebeu IP do DHCP (APIPA) — veja o guia de DHCP |
| IP de outra faixa que o esperado | Possível **servidor DHCP não autorizado** na rede |
| Gateway em branco | Não sai da rede local |
| DNS estranho (IP que você não reconhece) | Configuração errada ou **DNS alterado** (investigar!) |
| Interface `DOWN` / "Mídia desconectada" | Problema físico ou Wi-Fi desconectado |

> 🔐 **Visão cyber:** `ipconfig /all` é um dos primeiros comandos numa **triagem de incidente**: confirma gateway e DNS. Um **DNS alterado** sem explicação é um sinal clássico de malware ou de roteador comprometido (veja o guia de roteadores).
> 🔐 `ipconfig /displaydns` mostra quais domínios a máquina resolveu recentemente — útil como **evidência** (cuidado: `/flushdns` apaga essa evidência; numa investigação, colete antes de limpar).

---

## 4. ping

**Para que serve:** testar se um host responde e medir a **latência** (tempo de ida e volta). Usa **ICMP Echo Request (tipo 8)** e **Echo Reply (tipo 0)**.

```bash
ping 8.8.8.8                    # Linux: contínuo (Ctrl+C para parar)
ping -c 4 8.8.8.8               # Linux: 4 pacotes
ping -n 4 8.8.8.8               # Windows: 4 pacotes (padrão já é 4)
ping -t 8.8.8.8                 # Windows: contínuo
ping -s 1472 -M do 8.8.8.8      # Linux: testa MTU (pacote grande, sem fragmentar)
ping -f -l 1472 8.8.8.8         # Windows: idem
ping6 / ping -6 google.com      # IPv6
```

### Lendo a saída

```
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=12.4 ms
--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss
rtt min/avg/max/mdev = 11.9/12.3/12.8/0.3 ms
```

| Campo | O que diz |
|---|---|
| `time` | Latência (RTT). LAN: < 1–2 ms; mesma cidade: ~5–20 ms; outro continente: 100+ ms |
| `ttl` | Dá pistas do SO e da distância (veja o guia de roteamento: 64 Linux, 128 Windows, 255 rede) |
| `packet loss` | Perda — 0% é o ideal; perdas constantes indicam problema de link |
| `mdev` / variação | **Jitter** — oscilação alta prejudica voz e vídeo |

### Mensagens de erro e o que significam

| Mensagem | Significado |
|---|---|
| `Request timed out` / sem resposta | Host desligado **ou** firewall bloqueando ICMP |
| `Destination host unreachable` | Sem caminho; frequentemente o host não existe na rede local |
| `Destination net unreachable` | Um roteador não tem rota para a rede |
| `TTL expired in transit` | Loop de roteamento |
| `Packet needs to be fragmented but DF set` | Problema de **MTU** |

> ⚠️ **"Não pinga" ≠ "está fora do ar".** O **Firewall do Windows bloqueia ping por padrão** em redes públicas, e muitos servidores bloqueiam ICMP. Confirme com um teste de porta (seção 8).
> 🔐 **Visão cyber:** ping é a forma mais simples de **descoberta de hosts**. Por isso muitas redes limitam ICMP vindo de fora. Mas bloquear **todo** ICMP prejudica o diagnóstico e a descoberta de MTU — o equilíbrio usual é permitir ICMP essencial e limitar a taxa.

---

## 5. traceroute / tracert / mtr / pathping

**Para que serve:** descobrir **o caminho** (os saltos) até um destino e **onde** ele falha ou fica lento. Funciona aumentando o TTL de 1 em 1 e coletando as respostas *ICMP Time Exceeded* (veja o guia de roteamento).

```bash
traceroute 8.8.8.8          # Linux (UDP por padrão)
traceroute -I 8.8.8.8       # Linux usando ICMP
traceroute -T -p 443 site   # Linux usando TCP na porta 443 (atravessa melhor firewalls)
tracepath 8.8.8.8           # Linux, sem root, mostra MTU do caminho
tracert 8.8.8.8             # Windows (ICMP)
tracert -d 8.8.8.8          # Windows sem resolver nomes (mais rápido)

mtr 8.8.8.8                 # Linux: traceroute contínuo com estatística por salto
pathping 8.8.8.8            # Windows: traceroute + estatística de perda (demora ~5 min)
```

### Lendo a saída

```
 1  192.168.0.1      1.2 ms   1.0 ms   1.1 ms     ← seu roteador
 2  10.20.0.1        8.5 ms   8.1 ms   8.9 ms     ← provedor (IP privado = CGNAT/rede interna do ISP)
 3  * * *                                          ← não responde (filtro) — normal
 4  200.230.x.x     11.2 ms  10.9 ms  11.5 ms
 ...
 9  8.8.8.8         12.3 ms  12.1 ms  12.4 ms     ← destino
```

| Padrão | Interpretação |
|---|---|
| `* * *` num salto, mas os seguintes respondem | Roteador apenas não responde ICMP — **não é falha** |
| `* * *` do salto N até o fim | O problema (ou o bloqueio) está **a partir do salto N** |
| Latência salta muito num salto e **continua alta** depois | Gargalo/congestionamento a partir dali |
| Latência alta num salto, mas os seguintes normais | Roteador só prioriza pouco o ICMP — geralmente ignorável |
| IPs se repetindo em ciclo | **Loop de roteamento** |

> 🛠️ **Use o `mtr`/`pathping` para problemas intermitentes:** um único traceroute é uma foto; o mtr é um **filme** com perda e latência acumuladas por salto.
> 🔐 **Visão cyber:** traceroute revela **topologia** (IPs de roteadores internos, provedores, número de saltos). Por isso empresas costumam limitar *ICMP Time Exceeded* na borda. Para o Blue Team, é uma ferramenta essencial para provar **onde** um tráfego está sendo bloqueado ou desviado.

---

## 6. nslookup / dig

**Para que serve:** testar **resolução de nomes (DNS)**.

```bash
nslookup google.com                 # Windows e Linux
nslookup google.com 1.1.1.1         # pergunta a um servidor DNS específico
nslookup -type=MX gmail.com         # registros de e-mail

dig google.com                      # Linux (mais detalhado)
dig +short google.com               # só o IP
dig google.com MX                   # servidores de e-mail
dig google.com TXT                  # textos (SPF, verificações)
dig -x 8.8.8.8                      # DNS reverso (IP → nome)
dig @1.1.1.1 google.com             # usando um resolvedor específico
dig +trace google.com               # mostra a resolução desde os servidores raiz

Resolve-DnsName google.com          # PowerShell
```

### Tipos de registro importantes

| Registro | Função | Relevância em segurança |
|---|---|---|
| **A / AAAA** | Nome → IPv4 / IPv6 | Base de tudo |
| **CNAME** | Apelido para outro nome | CNAMEs apontando para serviços desativados podem permitir *subdomain takeover* |
| **MX** | Servidor de e-mail | — |
| **TXT** | Texto livre | Contém **SPF, DKIM, DMARC** (proteção contra falsificação de e-mail) |
| **PTR** | IP → nome (reverso) | Ajuda a identificar quem é um IP em logs |
| **NS** | Servidores autoritativos do domínio | — |

### Teste-chave de diagnóstico

```
Comparar o resultado do DNS da rede com um DNS público:
  nslookup banco.com.br           → resposta A
  nslookup banco.com.br 1.1.1.1   → resposta B
Se A ≠ B → algo no DNS local está diferente (cache, configuração... ou adulteração)
```

> 🔐 **Visão cyber:**
> - **Blue Team:** verificar **SPF/DKIM/DMARC** (`dig dominio.com TXT`, `dig _dmarc.dominio.com TXT`) faz parte da análise de **phishing**. DNS reverso (`dig -x`) ajuda a dar contexto a IPs em alertas.
> - **Resolução divergente** do esperado para domínios sensíveis (bancos, e-mail corporativo) é sinal de alerta: DNS alterado no host ou no roteador.
> - DNS também é canal de **exfiltração** de dados por malware (consultas longas e aleatórias) — por isso logs de DNS são tão valiosos no SOC.

---

## 7. netstat / ss

**Para que serve:** listar **portas em escuta** e **conexões ativas** do próprio host — e, crucialmente, **qual processo** é dono de cada uma.

### Linux (`ss` substituiu o `netstat`)

```bash
ss -tuln              # portas TCP/UDP em escuta (numérico)
sudo ss -tulnp        # + processo dono
sudo ss -tnp          # conexões TCP ativas + processo
ss -s                 # resumo por estado
ss -tan state established
sudo lsof -i :443     # quem está usando a porta 443
```

### Windows

```
netstat -ano                          # conexões + PID
netstat -ano | findstr LISTENING      # só portas em escuta
netstat -ab                           # + nome do executável (como admin)
tasklist /FI "PID eq 4321"            # qual programa é o PID
Get-NetTCPConnection -State Established | Select LocalPort,RemoteAddress,RemotePort,OwningProcess
Get-Process -Id 4321 | Select Name,Path
```

### Lendo a saída

```
Proto  Local Address        Foreign Address        State         PID
TCP    0.0.0.0:3389         0.0.0.0:0              LISTENING     1124
TCP    127.0.0.1:5432       0.0.0.0:0              LISTENING     2210
TCP    192.168.0.10:51544   142.250.79.14:443      ESTABLISHED   8812
```

| Endereço local | Significa |
|---|---|
| `0.0.0.0:porta` / `[::]:porta` | Escutando em **todas** as interfaces → acessível pela rede |
| `127.0.0.1:porta` | Só acessível **pela própria máquina** (mais seguro) |
| `IP-da-rede:porta` | Só naquela interface |

> 🔐 **Visão cyber — um dos comandos mais importantes do Blue Team:**
> - **Inventário de superfície:** cada linha `LISTENING` em `0.0.0.0` é uma porta exposta. Você sabe o que é cada uma?
> - **Triagem de host suspeito:** conexões `ESTABLISHED` para IPs externos desconhecidos, de processos estranhos (ex.: um executável em `AppData\Temp`), são um forte indício de **malware/C2**.
> - **Exemplo prático:** banco de dados (5432) em `0.0.0.0` numa máquina de desenvolvimento = exposto à rede inteira. Corrigir para `127.0.0.1` é hardening simples e eficaz.

---

## 8. Testando portas

`ping` testa o **host**. Para saber se um **serviço específico** responde, teste a **porta**.

```bash
# Linux - netcat
nc -vz 192.168.0.20 22               # testa TCP/22
nc -vz -w 3 192.168.0.20 443         # com timeout de 3 s
nc -vzu 192.168.0.20 53              # UDP (resultado menos confiável — UDP não confirma)

# Linux - sem instalar nada (bash)
timeout 3 bash -c '</dev/tcp/192.168.0.20/22' && echo aberta || echo fechada/filtrada

# Windows - PowerShell
Test-NetConnection 192.168.0.20 -Port 3389
Test-NetConnection google.com -Port 443 -InformationLevel Detailed

# Telnet (antigo; útil só como teste de porta)
telnet 192.168.0.20 25
```

### Interpretando (relembrando o guia de TCP x UDP)

| Resultado | Significado | Causa provável |
|---|---|---|
| `succeeded` / `TcpTestSucceeded: True` | Porta **aberta** (handshake completou) | Serviço rodando e acessível |
| `Connection refused` | Porta **fechada** (RST) | Serviço parado ou escutando só em `127.0.0.1` |
| Timeout | Porta **filtrada** | Firewall descartando, rota inexistente, host desligado |

> 🛠️ **Clássico de Help Desk:** "o sistema não abre". `ping servidor` funciona, mas `Test-NetConnection servidor -Port 443` dá timeout → **firewall** bloqueando a porta, não o servidor fora do ar.
> 🔐 Testar **uma porta específica** num servidor que você administra é diagnóstico. Varrer **muitas portas** de hosts de terceiros é reconhecimento — exige autorização (seção 14).

---

## 9. curl e openssl

### 9.1 curl — testando a camada de aplicação (HTTP)

```bash
curl -I https://exemplo.com              # só os cabeçalhos da resposta
curl -v https://exemplo.com              # detalhado: DNS, conexão, TLS, cabeçalhos
curl -o /dev/null -s -w "%{http_code} %{time_total}s\n" https://exemplo.com   # código + tempo
curl -L http://exemplo.com               # segue redirecionamentos
curl --resolve exemplo.com:443:10.0.0.5 https://exemplo.com   # força um IP (testar servidor específico)
curl ifconfig.me                         # descobre seu IP público
```

(No Windows 10/11, `curl.exe` já vem instalado; no PowerShell também há `Invoke-WebRequest`.)

**Códigos HTTP essenciais:**

| Código | Significado |
|---|---|
| 200 | OK |
| 301 / 302 | Redirecionamento |
| 401 / 403 | Não autenticado / proibido |
| 404 | Não encontrado |
| 500 / 502 / 503 / 504 | Erro no servidor / gateway / indisponível / timeout do proxy |

> 🔐 **Visão cyber — cabeçalhos de segurança:** com `curl -I` você verifica rapidamente se um site **seu** está com os cabeçalhos de proteção:
> `Strict-Transport-Security` (HSTS), `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`. E se ele **vaza informação** desnecessária, como `Server: Apache/2.4.29 (Ubuntu)` ou `X-Powered-By: PHP/7.2` (versão exata ajuda atacantes a buscar vulnerabilidades conhecidas).
> 💡 Isso conecta direto com seus projetos de **Node/Express**: o middleware `helmet` adiciona esses cabeçalhos e remove o `X-Powered-By: Express`.

### 9.2 openssl — inspecionando certificados TLS

```bash
openssl s_client -connect exemplo.com:443 -servername exemplo.com
# ver validade do certificado:
echo | openssl s_client -connect exemplo.com:443 -servername exemplo.com 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates
```

**O que checar:** emissor, para quais nomes vale, **data de expiração**, versão do TLS negociada.

> 🔐 Certificado **expirado** derruba serviços (disponibilidade); certificado **emitido por quem não deveria** ou com nome errado pode indicar **interceptação**. Monitorar validade de certificados é um item clássico de **Zabbix**.

---

## 10. Tabela de vizinhos e rotas

Dois comandos de **leitura** do estado do próprio host, úteis em troubleshooting:

```bash
# Tabela de rotas (já vista no guia de roteamento)
ip route                 # Linux
route print              # Windows

# Cache de vizinhos (IP ↔ MAC que o host conhece na rede local)
ip neigh                 # Linux
arp -a                   # Windows / Linux
```

> 🛠️ **Uso típico:** se o gateway **não aparece** na tabela de vizinhos (ou aparece como `INCOMPLETE`/`FAILED`), o host não está conseguindo falar com ele na camada 2 → verifique cabo, Wi-Fi e VLAN.
> 🔐 **Blue Team:** registrar o MAC do gateway como referência ajuda a perceber mudanças inesperadas na rede local.

---

## 11. tcpdump e Wireshark

**Para que serve:** capturar e analisar os **pacotes reais** — a "verdade" do que passa na rede. Quando todas as outras ferramentas deixam dúvida, a captura responde.

### tcpdump (linha de comando)

```bash
sudo tcpdump -D                              # lista interfaces
sudo tcpdump -i eth0 -n                      # captura tudo, sem resolver nomes
sudo tcpdump -i eth0 -n host 192.168.0.20    # só um host
sudo tcpdump -i eth0 -n port 53              # só DNS
sudo tcpdump -i eth0 -n icmp                 # só ICMP (ping/traceroute)
sudo tcpdump -i eth0 -w captura.pcap         # salva para abrir no Wireshark
sudo tcpdump -r captura.pcap                 # lê um arquivo salvo
```

### Wireshark (interface gráfica)

| Recurso | Para quê |
|---|---|
| **Filtros de exibição** (`dns`, `tcp.port == 443`, `ip.addr == x`) | Focar no que importa |
| *Statistics → Conversations* | Quem fala com quem, quanto |
| *Statistics → Protocol Hierarchy* | Quais protocolos dominam a captura |
| *Follow → TCP Stream* | Reconstruir uma conversa inteira |
| *Analyze → Expert Information* | Lista retransmissões, resets, erros |
| *File → Export Objects → HTTP* | Extrair arquivos transferidos (análise de malware em lab) |

**Filtros úteis (resumo da série):**

```
icmp                                  # ping e traceroute
dns                                   # resoluções
dhcp                                  # endereçamento
tcp.flags.syn == 1 && tcp.flags.ack == 0   # inícios de conexão
tcp.flags.reset == 1                  # conexões recusadas/cortadas
tcp.analysis.retransmission           # perda de pacotes
http.request                          # requisições HTTP em texto puro
tls.handshake.type == 1               # Client Hello (mostra o domínio no SNI)
```

> 🔐 **Visão cyber:**
> - Captura é a base da **análise de tráfego e de incidentes** (arquivos `.pcap` são evidência).
> - *Follow TCP Stream* em HTTP, FTP ou Telnet mostra **senhas em texto puro** — a melhor demonstração prática de por que usar criptografia.
> - ⚖️ Capturar tráfego **de outras pessoas** sem autorização pode ser crime (interceptação). Capture **só a sua máquina ou o seu lab**.

---

## 12. iperf3

**Para que serve:** medir a **vazão real** (bandwidth) entre dois pontos que você controla — ótimo para separar "a rede está lenta" de "o servidor está lento".

```bash
# Na máquina A (servidor)
iperf3 -s

# Na máquina B (cliente)
iperf3 -c <IP-da-A>              # teste TCP de 10 s
iperf3 -c <IP-da-A> -R           # sentido inverso (download)
iperf3 -c <IP-da-A> -u -b 50M    # UDP a 50 Mbit/s (mostra perda e jitter)
iperf3 -c <IP-da-A> -P 4         # 4 fluxos paralelos
```

| Resultado | Interpretação |
|---|---|
| Vazão muito abaixo do link (ex.: 90 Mbit/s num link gigabit) | Negociação em 100 Mbit/s (cabo/porta), duplex errado, Wi-Fi fraco |
| UDP com muita perda/jitter | Link instável — afeta VoIP e vídeo |
| Vazão boa no iperf, aplicação lenta | Gargalo está na **aplicação/servidor**, não na rede |

> 🔐 Disponibilidade também é segurança (tríade CIA). Ter uma **linha de base** de desempenho ajuda a perceber anomalias — como uma estação de repente enviando muito mais dados que o normal.

---

## 13. whois e consultas de reputação

**Para que serve:** descobrir **a quem pertence** um domínio ou bloco de IP — essencial para dar contexto a alertas.

```bash
whois exemplo.com            # dono/registrador do domínio, datas de criação/expiração
whois 8.8.8.8                # organização dona do bloco de IP, país, ASN
```

**Fontes de reputação usadas no SOC (consulta passiva, via navegador):**

| Serviço | Para quê |
|---|---|
| **VirusTotal** | Reputação de IPs, domínios, URLs e hashes de arquivos |
| **AbuseIPDB** | Denúncias de abuso associadas a um IP |
| **Shodan / Censys** | O que um IP expõe publicamente (útil para checar **a sua própria** exposição) |
| **Registro.br** | WHOIS de domínios `.br` |

> 🔐 **Exemplo de triagem no SOC:** alerta de conexão para `185.x.x.x`. `whois` mostra um provedor de hospedagem barato num país sem relação com a empresa; AbuseIPDB mostra centenas de denúncias; o domínio associado foi criado **há 3 dias**. Combinado com o processo visto no `netstat`, isso eleva muito a suspeita.
> 💡 **Domínio recém-criado** é um indicador forte em análise de phishing.

---

## 14. Scanners de rede: uso responsável

Ferramentas como o **Nmap** fazem descoberta de hosts e serviços em escala. Elas são padrão da indústria para:

- **Blue Team / administração:** inventário de ativos, verificar se só as portas esperadas estão abertas, validar regras de firewall após mudanças.
- **Red Team / pentest:** fase de reconhecimento, **dentro do escopo contratado**.

**Uso seguro para começar — na sua própria máquina:**

```bash
nmap localhost               # quais portas sua máquina expõe
```

Compare o resultado com o `ss -tuln` / `netstat -ano`: as duas visões ("de dentro" e "de fora") devem bater.

> ⚖️ **Atenção legal:** varrer redes ou servidores de terceiros **sem autorização** pode configurar crime no Brasil (Lei 12.737/2012 – "Lei Carolina Dieckmann", que trata de invasão de dispositivo informático) e viola os termos de uso de provedores. Pratique **só** no seu lab (VMs, Packet Tracer) ou em plataformas de treino feitas para isso (TryHackMe, Hack The Box), e em trabalhos profissionais **sempre com contrato e escopo por escrito**.

---

## 15. Utilitários no Cisco IOS

No Packet Tracer (e em equipamentos reais):

```
ping 192.168.1.10                       ! "!" = sucesso, "." = timeout, "U" = unreachable
ping 192.168.1.10 source 10.0.0.1       ! ping a partir de uma interface específica
traceroute 172.16.0.20

show ip interface brief                 ! status e IP de todas as interfaces
show interfaces Gi0/0                   ! erros, colisões, CRC, velocidade/duplex
show ip route                           ! tabela de roteamento
show arp                                ! tabela de vizinhos do roteador
show mac address-table                  ! (switch) qual MAC está em qual porta
show vlan brief                         ! (switch) VLANs e portas
show cdp neighbors                      ! equipamentos Cisco vizinhos
show running-config                     ! configuração atual
show logging                            ! logs do equipamento
```

| Símbolo do ping Cisco | Significado |
|---|---|
| `!` | Resposta recebida |
| `.` | Timeout |
| `U` | Destination unreachable |
| `Q` | Source quench (congestionamento) |
| `?` | Tipo de pacote desconhecido |

> 💡 Em pings Cisco, é comum o **primeiro pacote falhar** (`.!!!!`): o roteador ainda estava resolvendo o MAC do próximo salto. Não é erro.
> 🔐 `show mac address-table` + logs de DHCP + `show arp` = a trilha que leva de um **IP suspeito** até a **porta física** do switch onde o equipamento está ligado.

---

## 16. O outro lado

As ferramentas desta apostila **não são maliciosas** — mas atacantes que já estão dentro de uma rede também as usam, justamente porque **já vêm instaladas** e não chamam atenção. Isso se chama ***Living off the Land*** (usar os recursos do próprio sistema).

Comandos como `ipconfig /all`, `netstat -ano`, `route print`, `nslookup`, `arp -a`, `whoami`, `net view` executados em sequência, por um usuário comum, num horário estranho, podem indicar **reconhecimento pós-invasão**.

**Como o Blue Team enxerga isso:**

| Fonte | O que registrar |
|---|---|
| **Sysmon (Evento 1)** | Criação de processos com linha de comando completa |
| **Windows Event 4688** | Criação de processos (com auditoria de linha de comando ativada) |
| **PowerShell Script Block Logging** | Comandos PowerShell executados |
| **auditd / histórico de shell (Linux)** | Comandos executados |
| **EDR** | Correlação automática de comportamentos suspeitos |

**Regra de detecção conceitual:** *"vários utilitários de reconhecimento de rede executados pelo mesmo usuário em menos de X minutos, a partir de um processo pai incomum (ex.: Word → cmd.exe)"*. Esse tipo de lógica aparece no **MITRE ATT&CK** nas táticas de *Discovery* (ex.: T1016 – System Network Configuration Discovery, T1049 – System Network Connections Discovery).

> 💡 O contexto é tudo: o mesmo `ipconfig /all` é rotina quando o técnico de TI roda durante um chamado — e é suspeito quando roda às 3h da manhã a partir de um anexo de e-mail.

---

## 17. Visão Red Team x Blue Team

| Ferramenta | 🔴 Red Team (com autorização) usa para… | 🔵 Blue Team usa para… |
|---|---|---|
| `ipconfig` / `ip` | Entender em qual rede caiu | Confirmar gateway/DNS na triagem |
| `ping` | Ver quais hosts respondem | Disponibilidade, linha de base de latência |
| `traceroute` | Mapear topologia | Provar onde o tráfego é bloqueado/desviado |
| `nslookup` / `dig` | Descobrir nomes e serviços | Verificar SPF/DMARC, resolução adulterada |
| `netstat` / `ss` | Ver serviços locais e conexões | **Achar processos com conexões suspeitas** |
| Teste de porta | Confirmar serviço acessível | Validar regras de firewall |
| `curl` | Identificar tecnologia do servidor | Verificar cabeçalhos de segurança e certificados |
| Wireshark | Analisar protocolos em texto puro | Análise de incidentes, evidência em `.pcap` |
| `whois` / reputação | Reconhecimento de infraestrutura | Contexto de IPs/domínios em alertas |
| Scanner (Nmap) | Reconhecimento dentro do escopo | Inventário e auditoria de exposição |

---

## 18. Cheat sheet

| Objetivo | Windows | Linux | Cisco IOS |
|---|---|---|---|
| Ver IP / configuração | `ipconfig /all` | `ip addr` | `show ip interface brief` |
| Renovar IP | `ipconfig /release` + `/renew` | `nmcli con down/up …` / `dhclient` | — |
| Testar host | `ping -n 4 x` | `ping -c 4 x` | `ping x` |
| Ver caminho | `tracert x` | `traceroute x` / `mtr x` | `traceroute x` |
| Caminho + perda | `pathping x` | `mtr x` | — |
| Resolver nome | `nslookup x` / `Resolve-DnsName x` | `dig x` / `nslookup x` | — |
| Limpar cache DNS | `ipconfig /flushdns` | `resolvectl flush-caches` | — |
| Portas/conexões | `netstat -ano` | `ss -tulnp` | `show control-plane host open-ports` |
| Testar porta | `Test-NetConnection x -Port p` | `nc -vz x p` | `telnet x p` |
| Tabela de rotas | `route print` | `ip route` | `show ip route` |
| Tabela de vizinhos | `arp -a` | `ip neigh` | `show arp` |
| Testar HTTP | `curl.exe -I url` | `curl -I url` | — |
| Capturar pacotes | Wireshark | `tcpdump` / Wireshark | `monitor capture` (equip. reais) |
| Dono de IP/domínio | navegador (whois online) | `whois x` | — |

---

## 19. Cenários de troubleshooting

**Cenário 1 — "Estou sem internet"**
```
ipconfig /all → IP 169.254.10.20
→ Não recebeu DHCP. Verificar cabo/Wi-Fi, VLAN da porta, servidor DHCP.
```

**Cenário 2 — "A internet funciona, mas só alguns sites"**
```
ping 8.8.8.8 → OK      ping google.com → OK
nslookup sistema.empresa.local → "Non-existent domain"
→ DNS: o host está usando DNS público em vez do DNS interno. Verificar DHCP/configuração.
```

**Cenário 3 — "O sistema interno não abre"**
```
ping servidor → OK
Test-NetConnection servidor -Port 443 → TcpTestSucceeded: False (timeout)
→ Servidor vivo, porta filtrada → firewall. Se der "refused" → serviço parado.
```

**Cenário 4 — "A internet está lenta"**
```
ping 192.168.0.1 → 1 ms, 0% perda (rede local ok)
mtr 8.8.8.8 → perda de 15% a partir do salto 2 (provedor)
→ Problema no provedor. Guardar a saída do mtr como evidência para abrir chamado.
```

**Cenário 5 — "Máquina estranha, lenta e com tráfego alto" (SOC)**
```
netstat -ano → ESTABLISHED para 185.x.x.x:4444, PID 6620
tasklist /FI "PID eq 6620" → svchost32.exe (nome falso, caminho em AppData)
whois / AbuseIPDB → IP com histórico de abuso
→ Suspeita de malware: isolar a máquina da rede, preservar evidências, escalar.
```

---

## 20. Exercícios para o seu lab

1. **Roteiro de baixo para cima**
   Na sua máquina, execute os 8 passos da seção 2 e anote o resultado de cada um. Depois desconecte o cabo/Wi-Fi e veja em qual passo o teste começa a falhar.

2. **DNS quebrado de propósito**
   Numa VM, configure um DNS inexistente (ex.: `10.99.99.99`). Mostre que `ping 8.8.8.8` funciona e `ping google.com` não. Corrija e documente.

3. **Inventário da sua superfície**
   Rode `netstat -ano` (ou `ss -tulnp`) e `nmap localhost`. Monte a tabela "porta → processo → escuta em 0.0.0.0 ou 127.0.0.1 → preciso?". Feche o que não precisar.

4. **Aberta × fechada × filtrada**
   Numa VM Linux: suba `python3 -m http.server 8080`, teste com `nc`/`Test-NetConnection`; pare o serviço e teste; bloqueie com `ufw deny 8080` e teste. Capture os três casos no Wireshark.

5. **Senha em texto puro**
   No lab, faça login num serviço HTTP ou FTP sem criptografia e use *Follow TCP Stream* para encontrar a senha. Repita com HTTPS/SFTP e compare.

6. **Cabeçalhos do seu projeto**
   Rode `curl -I` no deploy do seu **Task Manager** (Vercel) ou na sua API **DashFinTrack** local. Quais cabeçalhos de segurança existem? Há `X-Powered-By`? Corrija com `helmet` na API e compare o antes/depois.

7. **Investigação de IP**
   Escolha um IP que aparece no seu `netstat` (ex.: de um site que você acessou). Use `whois`, `dig -x` e o VirusTotal para descobrir a quem pertence. Documente como faria num alerta de SOC.

8. **Monitoramento (ponte com o projeto Zabbix)**
   Crie itens no Zabbix para: ping (ICMP) a um host do lab, checagem de porta TCP de um serviço e **dias até expirar** um certificado TLS — com alertas.

---

## 21. Resumo e glossário

### Resumo em 12 frases

1. Os mesmos utilitários servem ao **Help Desk** (o que quebrou?), ao **Blue Team** (o que está acontecendo?) e ao **Red Team** (o que está exposto?).
2. Teste **de baixo para cima**: link → IP → gateway → roteamento → DNS → porta → aplicação.
3. `ipconfig`/`ip` mostram a configuração; IP `169.254.x.x` = sem DHCP; DNS estranho = investigar.
4. `ping` testa o host, mas **"não pinga" não significa "fora do ar"** (firewalls bloqueiam ICMP).
5. `traceroute`/`mtr`/`pathping` mostram o caminho e **onde** há perda ou bloqueio; `* * *` isolado é normal.
6. `nslookup`/`dig` testam DNS; se o IP funciona e o nome não, **é DNS**.
7. `netstat`/`ss` mostram portas e conexões **com o processo dono** — ferramenta central de triagem.
8. Teste de porta distingue **aberta (sucesso)**, **fechada (refused)** e **filtrada (timeout)**.
9. `curl` e `openssl` testam a aplicação, cabeçalhos de segurança e certificados.
10. `tcpdump`/Wireshark mostram a verdade do tráfego — só capture o que você está autorizado.
11. `whois` e serviços de reputação dão **contexto** a IPs e domínios em alertas.
12. Atacantes também usam esses utilitários (*Living off the Land*) — por isso registrar a **linha de comando** dos processos é essencial para a detecção.

### Glossário rápido

| Termo | Significado |
|---|---|
| **APIPA** | IP automático `169.254.x.x` quando não há DHCP |
| **Baseline** | Linha de base do comportamento normal (latência, tráfego, portas) |
| **C2** | Infraestrutura de comando e controle de malware |
| **ICMP** | Protocolo de mensagens de controle (ping, traceroute) |
| **Jitter** | Variação da latência |
| **Latência / RTT** | Tempo de ida e volta de um pacote |
| **Living off the Land** | Atacante usando ferramentas nativas do sistema |
| **MITRE ATT&CK** | Base de conhecimento de táticas e técnicas de atacantes |
| **MTU** | Maior tamanho de pacote que um link transporta sem fragmentar |
| **PCAP** | Formato de arquivo de captura de pacotes |
| **Perda de pacotes** | Pacotes que não chegam ao destino |
| **Runbook** | Roteiro passo a passo para diagnosticar/resolver um problema |
| **SNI** | Campo do TLS que mostra o domínio acessado |
| **SPF / DKIM / DMARC** | Registros DNS que protegem contra falsificação de e-mail |
| **Sysmon** | Ferramenta da Microsoft que registra atividade detalhada do sistema |
| **Vazão (throughput)** | Quantidade de dados transferidos por segundo |

---

> ⚖️ **Ética:** use estas ferramentas livremente na **sua** máquina e no **seu** lab. Em redes, sistemas ou tráfego de terceiros, só com **autorização formal por escrito** e escopo definido.