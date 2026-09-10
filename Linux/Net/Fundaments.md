Claro — abaixo está um `Fundamentos.md` detalhado, estruturado para servir como material de estudo e referência no seu repositório GitHub.

# Fundamentos de Redes

> Este documento apresenta os principais conceitos fundamentais de redes de computadores, com foco no funcionamento prático de redes TCP/IP e sua aplicação em sistemas Linux.

---

## Sumário

* [O que é uma rede de computadores](#o-que-é-uma-rede-de-computadores)
* [Componentes básicos de uma rede](#componentes-básicos-de-uma-rede)
* [Como os dados trafegam pela rede](#como-os-dados-trafegam-pela-rede)
* [Modelo OSI](#modelo-osi)
* [Modelo TCP/IP](#modelo-tcpip)
* [Comparação entre OSI e TCP/IP](#comparação-entre-osi-e-tcpip)
* [Encapsulamento e desencapsulamento](#encapsulamento-e-desencapsulamento)
* [Endereços MAC e IP](#endereços-mac-e-ip)
* [Portas e sockets](#portas-e-sockets)
* [Principais protocolos](#principais-protocolos)
* [Dispositivos de rede](#dispositivos-de-rede)
* [Switch, roteador e gateway](#switch-roteador-e-gateway)
* [Redes locais e Internet](#redes-locais-e-internet)
* [Fluxo de uma conexão na prática](#fluxo-de-uma-conexão-na-prática)
* [Comandos Linux fundamentais](#comandos-linux-fundamentais)
* [Conceitos importantes para troubleshooting](#conceitos-importantes-para-troubleshooting)
* [Resumo](#resumo)

---

# O que é uma rede de computadores

Uma **rede de computadores** é um conjunto de dispositivos conectados que podem trocar informações entre si.

Esses dispositivos podem incluir:

* Computadores
* Servidores
* Smartphones
* Roteadores
* Switches
* Impressoras
* Máquinas virtuais
* Containers
* Dispositivos IoT

A comunicação acontece através de regras chamadas **protocolos**.

Um protocolo define como os dispositivos devem:

* Estabelecer comunicação
* Identificar uns aos outros
* Enviar dados
* Receber dados
* Detectar erros
* Encerrar conexões

A Internet, por exemplo, é uma enorme rede formada pela interconexão de milhares de redes menores.

---

# Componentes básicos de uma rede

Uma comunicação de rede normalmente envolve os seguintes elementos:

```text
[ Aplicação ]
      |
      v
[ Sistema Operacional ]
      |
      v
[ Interface de Rede ]
      |
      |
===== REDE =====
      |
      |
      v
[ Interface de Rede ]
      |
      v
[ Sistema Operacional ]
      |
      v
[ Aplicação ]
```

Exemplo:

```text
Navegador
   |
   v
Sistema Operacional
   |
   v
Placa de Rede
   |
   v
Switch
   |
   v
Roteador
   |
   v
Internet
   |
   v
Servidor Web
```

Cada camada da comunicação possui responsabilidades específicas.

---

# Como os dados trafegam pela rede

Quando uma aplicação envia dados, essas informações não são simplesmente colocadas diretamente no cabo ou no Wi-Fi.

Os dados passam por diferentes camadas.

Por exemplo, quando você acessa:

```text
https://example.com
```

o processo pode envolver:

1. O navegador cria uma requisição.
2. O sistema resolve o nome usando DNS.
3. É criado um pacote IP.
4. Os dados são transportados usando TCP ou UDP.
5. Um frame Ethernet ou Wi-Fi é criado.
6. Os dados são enviados pela interface de rede.
7. Switches e roteadores encaminham os dados.
8. O servidor recebe e processa a requisição.
9. A resposta percorre o caminho de volta.

---

# Modelo OSI

O modelo **OSI (Open Systems Interconnection)** é um modelo conceitual utilizado para entender a comunicação em redes.

Ele possui sete camadas:

```text
+-------------------+
| 7. Aplicação      |
+-------------------+
| 6. Apresentação   |
+-------------------+
| 5. Sessão         |
+-------------------+
| 4. Transporte     |
+-------------------+
| 3. Rede           |
+-------------------+
| 2. Enlace         |
+-------------------+
| 1. Física         |
+-------------------+
```

Cada camada possui responsabilidades específicas.

---

## Camada 7 — Aplicação

A camada de aplicação é onde os programas interagem com a rede.

Exemplos:

* HTTP
* HTTPS
* FTP
* SSH
* SMTP
* DNS

Exemplo:

```text
Navegador
   |
HTTP Request
   |
Internet
```

A aplicação não precisa saber como os bits são transmitidos fisicamente.

Ela utiliza protocolos de nível superior.

---

## Camada 6 — Apresentação

Responsável pela representação dos dados.

Pode envolver:

* Criptografia
* Compressão
* Codificação
* Conversão de formatos

Exemplos:

```text
Texto
   |
UTF-8
   |
Dados transmitidos
```

Em conexões HTTPS, mecanismos de criptografia como TLS estão relacionados a essa parte conceitual do modelo.

---

## Camada 5 — Sessão

Responsável pelo gerenciamento das sessões de comunicação.

Pode envolver:

* Início da sessão
* Manutenção da sessão
* Encerramento
* Sincronização

Na prática moderna, essas responsabilidades frequentemente aparecem distribuídas entre protocolos e aplicações.

---

## Camada 4 — Transporte

Responsável pela comunicação entre processos.

Os principais protocolos são:

* TCP
* UDP

Essa camada utiliza **portas**.

Exemplo:

```text
IP: 192.168.1.10
Porta: 443
```

O endereço IP identifica o dispositivo.

A porta identifica o serviço ou processo.

---

## Camada 3 — Rede

Responsável pelo endereçamento lógico e roteamento.

O principal protocolo é:

```text
IP
```

Exemplo:

```text
Origem: 192.168.1.10
Destino: 8.8.8.8
```

Os roteadores trabalham principalmente nessa camada.

---

## Camada 2 — Enlace

Responsável pela comunicação dentro de uma rede local.

Utiliza endereços MAC.

Exemplo:

```text
MAC: AA:BB:CC:DD:EE:FF
```

Tecnologias associadas:

* Ethernet
* Wi-Fi
* VLAN

Switches trabalham principalmente nessa camada.

---

## Camada 1 — Física

Representa a transmissão física dos dados.

Exemplos:

* Cabos Ethernet
* Fibra óptica
* Sinais elétricos
* Ondas de rádio
* Conectores

Essa camada transmite bits:

```text
0
1
0
1
1
0
```

---

# Modelo TCP/IP

Na prática, a Internet utiliza principalmente o conjunto de protocolos TCP/IP.

O modelo TCP/IP geralmente é representado por quatro camadas:

```text
+------------------------+
| Aplicação              |
+------------------------+
| Transporte             |
+------------------------+
| Internet               |
+------------------------+
| Acesso à Rede          |
+------------------------+
```

---

## Camada de Aplicação

Inclui protocolos como:

* HTTP
* HTTPS
* SSH
* DNS
* SMTP
* FTP

---

## Camada de Transporte

Inclui:

* TCP
* UDP

---

## Camada de Internet

Inclui:

* IPv4
* IPv6
* ICMP

Responsável pelo roteamento entre redes.

---

## Camada de Acesso à Rede

Inclui tecnologias como:

* Ethernet
* Wi-Fi

Responsável pela comunicação dentro do meio físico e da rede local.

---

# Comparação entre OSI e TCP/IP

```text
OSI                      TCP/IP
------------------------------------------------
Aplicação       ┐
Apresentação    │       Aplicação
Sessão          ┘
------------------------------------------------
Transporte              Transporte
------------------------------------------------
Rede                    Internet
------------------------------------------------
Enlace         ┐
Física         ┘       Acesso à Rede
```

O modelo OSI é principalmente utilizado para aprendizado e diagnóstico.

O TCP/IP representa melhor o funcionamento real da Internet.

---

# Encapsulamento e desencapsulamento

Os dados enviados por uma aplicação passam por um processo chamado **encapsulamento**.

Cada camada adiciona informações próprias aos dados.

Exemplo:

```text
Dados da aplicação
        |
        v
+-------------------+
| Cabeçalho TCP     |
+-------------------+
| Dados             |
+-------------------+

        |
        v

+-------------------+
| Cabeçalho IP      |
+-------------------+
| Cabeçalho TCP     |
+-------------------+
| Dados             |
+-------------------+

        |
        v

+-------------------+
| Cabeçalho Ethernet|
+-------------------+
| Cabeçalho IP      |
+-------------------+
| Cabeçalho TCP     |
+-------------------+
| Dados             |
+-------------------+
```

No destino acontece o processo inverso.

Isso é chamado de **desencapsulamento**.

---

# Unidades de dados

Dependendo da camada, os dados recebem nomes diferentes.

```text
Camada Aplicação
    Dados

Camada Transporte
    Segmento TCP / Datagrama UDP

Camada Rede
    Pacote IP

Camada Enlace
    Frame
```

---

# Endereços MAC e IP

Existem diferentes formas de identificar dispositivos em uma rede.

As duas principais são:

* Endereço MAC
* Endereço IP

---

## Endereço MAC

Um endereço MAC identifica uma interface de rede dentro de uma rede local.

Exemplo:

```text
AA:BB:CC:DD:EE:FF
```

Ele é utilizado principalmente na camada de enlace.

---

## Endereço IP

Um endereço IP identifica um dispositivo logicamente em uma rede.

Exemplo:

```text
192.168.1.10
```

Ou em IPv6:

```text
2001:db8::10
```

O IP permite que os dados sejam roteados entre redes diferentes.

---

# Portas

Uma máquina pode executar vários serviços simultaneamente.

Exemplo:

```text
Servidor
IP: 192.168.1.10
```

Nesse mesmo IP podem existir vários serviços:

```text
192.168.1.10:22    SSH
192.168.1.10:80    HTTP
192.168.1.10:443   HTTPS
```

A porta permite identificar qual serviço deve receber os dados.

---

# Portas conhecidas

Algumas portas comuns:

| Porta | Protocolo | Serviço    |
| ----- | --------- | ---------- |
| 22    | TCP       | SSH        |
| 53    | TCP/UDP   | DNS        |
| 80    | TCP       | HTTP       |
| 123   | UDP       | NTP        |
| 443   | TCP       | HTTPS      |
| 3306  | TCP       | MySQL      |
| 5432  | TCP       | PostgreSQL |

Uma porta não é necessariamente um serviço.

Ela é apenas um número utilizado pelo sistema operacional para identificar uma comunicação ou processo.

---

# Sockets

Um socket pode ser entendido como um ponto de comunicação entre processos.

Exemplo:

```text
192.168.1.10:443
```

Uma conexão TCP normalmente pode ser identificada por:

```text
IP origem
Porta origem
IP destino
Porta destino
```

Exemplo:

```text
192.168.1.10:52341
        ->
142.250.79.46:443
```

Essa combinação permite que o sistema operacional diferencie várias conexões simultâneas.

---

# Principais protocolos

---

## TCP

TCP significa:

```text
Transmission Control Protocol
```

Características:

* Orientado à conexão
* Confiável
* Garante ordem dos dados
* Detecta perdas
* Realiza retransmissões
* Possui controle de fluxo

Antes da comunicação, normalmente ocorre o **three-way handshake**.

```text
Cliente                Servidor

SYN  ----------------->

     <----------------  SYN-ACK

ACK  ----------------->
```

Após isso, os dados podem ser transmitidos.

---

## UDP

UDP significa:

```text
User Datagram Protocol
```

Características:

* Sem conexão
* Menor overhead
* Não garante entrega
* Não garante ordem
* Mais simples que TCP

É utilizado em situações onde velocidade ou baixa latência são importantes.

Exemplos:

* DNS
* Streaming
* Jogos
* VoIP

---

## ICMP

ICMP é utilizado principalmente para mensagens de controle e diagnóstico.

Exemplo:

```bash
ping
```

O `ping` normalmente utiliza ICMP para testar conectividade.

---

## ARP

ARP é utilizado em redes IPv4 para descobrir o endereço MAC associado a um endereço IP local.

Exemplo:

```text
IP conhecido:

192.168.1.1

MAC desconhecido
```

O dispositivo pode perguntar:

```text
Quem possui 192.168.1.1?
```

O dispositivo correspondente responde com seu endereço MAC.

---

# Dispositivos de rede

---

## Hub

Um hub simplesmente replica os dados para todas as portas.

```text
      PC1
       |
PC2 -- HUB -- PC3
       |
      PC4
```

É uma tecnologia antiga e pouco utilizada atualmente.

---

## Switch

Um switch conecta dispositivos dentro de uma rede local.

Ele aprende quais endereços MAC estão associados a cada porta.

```text
PC1 ----\
PC2 ----- SWITCH ----- Servidor
PC3 ----/
```

O switch tenta encaminhar frames apenas para a porta correta.

---

## Roteador

Um roteador conecta redes diferentes.

Exemplo:

```text
192.168.1.0/24
       |
       |
    Roteador
       |
       |
10.0.0.0/24
```

O roteador toma decisões baseadas principalmente em endereços IP e tabelas de roteamento.

---

# Switch, roteador e gateway

É importante diferenciar esses conceitos.

## Switch

Conecta dispositivos na mesma rede.

Principalmente camada 2.

---

## Roteador

Conecta redes diferentes.

Principalmente camada 3.

---

## Gateway

É o ponto utilizado para alcançar outras redes.

Em uma rede doméstica:

```text
Computador
IP: 192.168.1.10

Gateway:
192.168.1.1
```

Se o destino não estiver na rede local, o computador envia os dados para o gateway.

---

# Redes locais e Internet

Uma rede local pode ser representada assim:

```text
PC1
 |
PC2 ---- Switch ---- Roteador ---- Internet
 |
PC3
```

Dispositivos da mesma rede podem se comunicar diretamente através da rede local.

Para acessar outra rede:

```text
PC
 |
v
Gateway
 |
v
Roteador
 |
v
Internet
 |
v
Servidor
```

---

# Fluxo de uma conexão na prática

Imagine que você execute:

```bash
curl https://example.com
```

O processo pode ser simplificado assim:

---

## 1. Resolução DNS

O sistema precisa descobrir o IP associado ao domínio:

```text
example.com
```

Resultado:

```text
93.184.216.34
```

---

## 2. Verificação da rota

O sistema verifica:

```text
O IP de destino está na minha rede local?
```

Se não estiver:

```text
Enviar para o gateway padrão
```

---

## 3. Descoberta do MAC

Para enviar o frame localmente, o sistema precisa conhecer o MAC do próximo salto.

Se necessário, utiliza ARP.

---

## 4. Criação da conexão TCP

O cliente inicia uma conexão:

```text
Cliente              Servidor

SYN ---------------->

     <-------------- SYN-ACK

ACK ---------------->
```

---

## 5. TLS

Em HTTPS, ocorre a negociação de criptografia utilizando TLS.

---

## 6. Requisição HTTP

O cliente envia algo semelhante a:

```text
GET / HTTP/1.1
Host: example.com
```

---

## 7. Resposta

O servidor responde com:

```text
HTTP/1.1 200 OK
```

e os dados solicitados.

---

# Comandos Linux fundamentais

---

## ip

O comando `ip` é utilizado para visualizar e configurar aspectos da rede.

Ver interfaces:

```bash
ip link
```

Ver endereços IP:

```bash
ip addr
```

Ver rotas:

```bash
ip route
```

Ver vizinhos ARP:

```bash
ip neigh
```

---

## ping

Utilizado para testar conectividade.

```bash
ping 8.8.8.8
```

Testar um domínio:

```bash
ping example.com
```

Se um IP funciona, mas um domínio não:

```text
Possível problema de DNS.
```

---

## ss

Utilizado para visualizar sockets e conexões.

```bash
ss -tulpn
```

Algumas informações exibidas:

* Portas abertas
* Processos associados
* Conexões TCP
* Conexões UDP

---

## netstat

Ferramenta tradicional para visualizar conexões.

```bash
netstat -tulpn
```

Em sistemas modernos, `ss` normalmente é preferido.

---

## traceroute

Utilizado para visualizar os saltos até um destino.

```bash
traceroute example.com
```

Exemplo conceitual:

```text
PC
 |
Roteador
 |
ISP
 |
Roteador intermediário
 |
Servidor
```

---

# Conceitos importantes para troubleshooting

Quando uma conexão falha, é importante investigar de baixo para cima.

---

## 1. A interface está ativa?

```bash
ip link
```

Verifique se a interface está:

```text
UP
```

---

## 2. Existe um endereço IP?

```bash
ip addr
```

---

## 3. Existe uma rota?

```bash
ip route
```

Normalmente deve existir uma rota padrão:

```text
default via 192.168.1.1
```

---

## 4. O gateway responde?

```bash
ping 192.168.1.1
```

---

## 5. Um IP externo responde?

```bash
ping 8.8.8.8
```

---

## 6. DNS está funcionando?

```bash
ping example.com
```

Ou:

```bash
dig example.com
```

---

## Método de troubleshooting

Uma abordagem simples:

```text
Interface
   ↓
IP
   ↓
Rota
   ↓
Gateway
   ↓
Internet por IP
   ↓
DNS
   ↓
Porta
   ↓
Aplicação
```

Isso ajuda a identificar em qual camada o problema está ocorrendo.

---

# Conceitos essenciais para memorizar

## Endereço IP

Identifica um dispositivo logicamente em uma rede.

---

## Endereço MAC

Identifica uma interface de rede localmente.

---

## Porta

Identifica um serviço ou processo.

---

## DNS

Traduz nomes em endereços IP.

```text
example.com
     ↓
IP
```

---

## ARP

Descobre o MAC associado a um IP na rede local.

---

## Switch

Encaminha frames dentro da rede local.

---

## Roteador

Encaminha pacotes entre redes.

---

## Gateway

Ponto utilizado para alcançar outras redes.

---

## TCP

Transporte confiável e orientado à conexão.

---

## UDP

Transporte simples e sem garantia de entrega.

---

# Resumo

Uma comunicação de rede pode ser resumida da seguinte forma:

```text
Aplicação
    |
    v
Protocolo de Aplicação
HTTP / SSH / DNS
    |
    v
Transporte
TCP / UDP
    |
    v
Rede
IP
    |
    v
Enlace
Ethernet / Wi-Fi
    |
    v
Meio Físico
Cabo / Fibra / Rádio
```

No destino, o processo ocorre na direção contrária:

```text
Meio Físico
    |
    v
Enlace
    |
    v
IP
    |
    v
TCP / UDP
    |
    v
Aplicação
```

Compreender esse fluxo é fundamental para aprender:

* Sub-redes
* Roteamento
* DNS
* Firewalls
* SSH
* TCP/IP
* Captura de pacotes
* Troubleshooting
* Segurança de redes

---

# Próximos tópicos

Depois de dominar estes fundamentos, os próximos arquivos recomendados são:

1. `Endereçamento.md`
2. `DNS.md`
3. `Protocolos.md`
4. `SSH.md`
5. `Firewall.md`
6. `Ferramentas.md`

> **Regra prática:** quando uma conexão não funciona, não tente adivinhar o problema. Comece pela camada mais básica possível e avance gradualmente até a aplicação.
