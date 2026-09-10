# Protocolos de Rede

> Este documento apresenta os principais protocolos envolvidos na comunicação em redes IP, com foco em **TCP, UDP, ICMP e ARP**. O objetivo é entender não apenas o que cada protocolo faz, mas também como os pacotes são construídos, transmitidos, recebidos e diagnosticados no Linux.

---

# Sumário

* [1. O que é um protocolo](#1-o-que-é-um-protocolo)
* [2. Onde os protocolos ficam no modelo TCP/IP](#2-onde-os-protocolos-ficam-no-modelo-tcpip)
* [3. Encapsulamento](#3-encapsulamento)
* [4. TCP](#4-tcp)
* [5. Como o TCP estabelece uma conexão](#5-como-o-tcp-estabelece-uma-conexão)
* [6. Three-Way Handshake](#6-three-way-handshake)
* [7. Flags TCP](#7-flags-tcp)
* [8. Número de sequência](#8-número-de-sequência)
* [9. ACK](#9-ack)
* [10. Retransmissão](#10-retransmissão)
* [11. Controle de fluxo](#11-controle-de-fluxo)
* [12. Controle de congestionamento](#12-controle-de-congestionamento)
* [13. MSS](#13-mss)
* [14. Estados TCP](#14-estados-tcp)
* [15. Encerramento de uma conexão TCP](#15-encerramento-de-uma-conexão-tcp)
* [16. RST](#16-rst)
* [17. UDP](#17-udp)
* [18. Estrutura do UDP](#18-estrutura-do-udp)
* [19. TCP vs UDP](#19-tcp-vs-udp)
* [20. ICMP](#20-icmp)
* [21. ICMP Echo Request e Echo Reply](#21-icmp-echo-request-e-echo-reply)
* [22. ICMP e troubleshooting](#22-icmp-e-troubleshooting)
* [23. ARP](#23-arp)
* [24. Como funciona o ARP](#24-como-funciona-o-arp)
* [25. ARP Request e ARP Reply](#25-arp-request-e-arp-reply)
* [26. Cache ARP](#26-cache-arp)
* [27. ARP no Linux](#27-arp-no-linux)
* [28. Broadcast](#28-broadcast)
* [29. Unicast, Broadcast e Multicast](#29-unicast-broadcast-e-multicast)
* [30. MTU](#30-mtu)
* [31. Fragmentação](#31-fragmentação)
* [32. Portas](#32-portas)
* [33. IP + Porta](#33-ip--porta)
* [34. Socket](#34-socket)
* [35. Como uma requisição realmente acontece](#35-como-uma-requisição-realmente-acontece)
* [36. Exemplo com HTTP](#36-exemplo-com-http)
* [37. Exemplo com SSH](#37-exemplo-com-ssh)
* [38. Exemplo com DNS](#38-exemplo-com-dns)
* [39. Capturando pacotes com tcpdump](#39-capturando-pacotes-com-tcpdump)
* [40. Analisando um handshake TCP](#40-analisando-um-handshake-tcp)
* [41. Analisando ICMP](#41-analisando-icmp)
* [42. Analisando ARP](#42-analisando-arp)
* [43. Diagnóstico de problemas TCP](#43-diagnóstico-de-problemas-tcp)
* [44. Diagnóstico de problemas UDP](#44-diagnóstico-de-problemas-udp)
* [45. Diagnóstico de problemas ARP](#45-diagnóstico-de-problemas-arp)
* [46. Diagnóstico de problemas ICMP](#46-diagnóstico-de-problemas-icmp)
* [47. Ferramentas Linux](#47-ferramentas-linux)
* [48. Exercícios](#48-exercícios)
* [49. Resumo](#49-resumo)

---

# 1. O que é um protocolo

Um **protocolo de rede** é um conjunto de regras que define como dispositivos devem trocar informações.

Um protocolo pode definir:

* Formato das mensagens.
* Ordem dos campos.
* Como uma comunicação começa.
* Como uma comunicação termina.
* Como erros são tratados.
* Como os dados são identificados.
* Como os dispositivos respondem uns aos outros.

Uma comunicação real utiliza vários protocolos ao mesmo tempo.

Por exemplo:

```text
HTTPS
  |
TCP
  |
IP
  |
Ethernet
```

Cada protocolo resolve um problema diferente.

---

# 2. Onde os protocolos ficam no modelo TCP/IP

Podemos visualizar:

```text
+--------------------------+
| Aplicação                |
| HTTP, HTTPS, DNS, SSH    |
+--------------------------+
| Transporte               |
| TCP, UDP                 |
+--------------------------+
| Internet                 |
| IP, ICMP                 |
+--------------------------+
| Acesso à rede            |
| Ethernet, Wi-Fi, ARP*    |
+--------------------------+
```

> ARP é frequentemente associado à camada de enlace/à interação entre camada de rede e enlace em redes IPv4. O importante é entender sua função prática: descobrir o endereço MAC correspondente a um IPv4 local.

---

# 3. Encapsulamento

Imagine que um navegador deseja enviar uma requisição HTTPS.

A aplicação produz:

```text
Dados HTTP
```

O TCP adiciona seu cabeçalho:

```text
+------------------+
| Cabeçalho TCP    |
+------------------+
| Dados HTTP       |
+------------------+
```

O IP adiciona seu cabeçalho:

```text
+------------------+
| Cabeçalho IP     |
+------------------+
| Cabeçalho TCP    |
+------------------+
| Dados HTTP       |
+------------------+
```

Ethernet adiciona seu cabeçalho e trailer:

```text
+------------------+
| Cabeçalho Ethernet|
+------------------+
| Cabeçalho IP     |
+------------------+
| Cabeçalho TCP    |
+------------------+
| Dados HTTP       |
+------------------+
| FCS              |
+------------------+
```

No destino, acontece o processo inverso.

---

# 4. TCP

TCP significa:

```text
Transmission Control Protocol
```

É um protocolo de transporte orientado à conexão.

Ele fornece mecanismos para:

* Entrega confiável.
* Ordenação.
* Detecção de perda.
* Retransmissão.
* Controle de fluxo.
* Controle de congestionamento.
* Identificação de conexões através de portas.

Exemplos de aplicações que frequentemente utilizam TCP:

```text
HTTP
HTTPS
SSH
FTP
SMTP
IMAP
```

---

# 5. Como o TCP estabelece uma conexão

Antes de transportar dados, TCP normalmente estabelece uma conexão.

O cliente envia:

```text
SYN
```

O servidor responde:

```text
SYN + ACK
```

O cliente responde:

```text
ACK
```

Depois disso:

```text
CONEXÃO ESTABELECIDA
```

---

# 6. Three-Way Handshake

O processo:

```text
Cliente                         Servidor

   |                                |
   | -------- SYN ----------------> |
   |                                |
   | <------ SYN + ACK ------------ |
   |                                |
   | -------- ACK ----------------> |
   |                                |
   |         CONECTADO              |
```

Vamos detalhar.

---

## Primeiro passo — SYN

O cliente envia:

```text
SYN
```

Isso significa:

```text
Quero iniciar uma conexão TCP.
```

Também contém um número inicial de sequência.

Exemplo:

```text
SEQ = 1000
```

---

## Segundo passo — SYN-ACK

O servidor responde:

```text
SYN + ACK
```

Isso significa:

```text
Recebi seu pedido.
Também quero estabelecer uma conexão.
```

Exemplo:

```text
SEQ = 5000
ACK = 1001
```

O `ACK = 1001` indica que o servidor recebeu o `SEQ = 1000` e espera o próximo número de sequência.

---

## Terceiro passo — ACK

O cliente responde:

```text
ACK
```

Exemplo:

```text
ACK = 5001
```

Agora ambos possuem informações suficientes para começar a transmissão.

---

# 7. Flags TCP

O cabeçalho TCP possui diversas flags.

As mais importantes:

| Flag | Significado                           |
| ---- | ------------------------------------- |
| SYN  | Inicia/sincroniza conexão             |
| ACK  | Confirma recebimento                  |
| FIN  | Solicita encerramento normal          |
| RST  | Reinicia/rejeita uma conexão          |
| PSH  | Solicita entrega imediata à aplicação |
| URG  | Indica dados urgentes                 |

Para estudar troubleshooting, as principais são:

```text
SYN
ACK
FIN
RST
```

---

# SYN

Utilizado para iniciar uma conexão.

```text
SYN
```

---

# ACK

Confirma o recebimento de dados.

```text
ACK
```

---

# FIN

Indica que o remetente não possui mais dados a enviar e deseja encerrar seu lado da conexão.

```text
FIN
```

---

# RST

Indica uma reinicialização imediata da conexão.

Pode aparecer quando:

* Uma porta não possui serviço escutando.
* Uma aplicação rejeita uma conexão.
* Existe uma condição inesperada de conexão.

Exemplo conceitual:

```text
Cliente                 Servidor

SYN -------------------->

     <------------------ RST
```

---

# 8. Número de sequência

TCP precisa garantir que os dados possam ser colocados na ordem correta.

Para isso, utiliza números de sequência.

Imagine:

```text
Dados A
Dados B
Dados C
```

Podemos visualizar:

```text
SEQ 1000 -> Dados A
SEQ 1100 -> Dados B
SEQ 1200 -> Dados C
```

Se B chegar antes de A, o receptor pode identificar a posição correta usando os números de sequência.

---

# 9. ACK

O receptor utiliza ACKs para indicar até onde recebeu os dados.

Imagine:

```text
SEQ = 1000
Quantidade = 100
```

O próximo byte esperado pode ser:

```text
ACK = 1100
```

Isso significa:

```text
Recebi até antes do byte 1100.
Agora espero o 1100.
```

Essa lógica permite detectar perda e retransmissão.

---

# 10. Retransmissão

Imagine:

```text
Cliente                    Servidor

Segmento 1 ----------------->

Segmento 2 -------X         

Segmento 3 ----------------->
```

O servidor pode perceber que o segmento esperado não chegou.

Dependendo do mecanismo usado, o TCP pode retransmitir os dados.

Simplificando:

```text
Perda
  |
  v
Detecção
  |
  v
Retransmissão
```

É uma das características que tornam TCP confiável.

---

# 11. Controle de fluxo

TCP precisa evitar que um transmissor envie mais dados do que o receptor consegue processar.

Para isso existe a **janela de recepção**.

Simplificando:

```text
Receptor:

"Consigo receber X bytes."
```

O transmissor limita a quantidade de dados não confirmados de acordo com as informações recebidas.

---

# 12. Controle de congestionamento

Controle de fluxo protege principalmente o receptor.

Controle de congestionamento considera as condições da rede.

O TCP possui mecanismos para ajustar a quantidade de dados transmitidos conforme detecta sinais de congestionamento.

Conceitualmente:

```text
Mais capacidade disponível
        |
        v
Pode aumentar transmissão

Congestionamento
        |
        v
Reduz transmissão
```

Esse comportamento é uma das razões pelas quais TCP consegue operar sobre redes compartilhadas sem simplesmente saturá-las de forma indiscriminada.

---

# 13. MSS

MSS significa:

```text
Maximum Segment Size
```

É a quantidade máxima de dados de aplicação que um segmento TCP pode transportar, sem considerar o cabeçalho IP e TCP.

Em uma rede IPv4 Ethernet com MTU de 1500 bytes, um valor comum de MSS é:

```text
1500 - 20 - 20 = 1460
```

Onde:

```text
1500 = MTU
20   = cabeçalho IPv4
20   = cabeçalho TCP
```

Em cenários com opções de cabeçalho ou IPv6, os valores efetivos podem mudar.

---

# 14. Estados TCP

Uma conexão TCP passa por diferentes estados.

Alguns importantes:

```text
LISTEN
SYN-SENT
SYN-RECEIVED
ESTABLISHED
FIN-WAIT-1
FIN-WAIT-2
CLOSE-WAIT
LAST-ACK
TIME-WAIT
CLOSED
```

---

## LISTEN

O servidor está esperando conexões.

Exemplo:

```text
Servidor
   |
   +-- :22
   |
   +-- :80
   |
   +-- :443
```

---

## SYN-SENT

O cliente enviou SYN e espera resposta.

---

## SYN-RECEIVED

O servidor recebeu SYN e está no processo de estabelecimento da conexão.

---

## ESTABLISHED

A conexão foi estabelecida.

```text
Cliente <==== dados ====> Servidor
```

---

## TIME-WAIT

Após o encerramento, determinado endpoint pode permanecer temporariamente em `TIME-WAIT` para lidar corretamente com segmentos atrasados e garantir que a conexão anterior não seja confundida com uma nova conexão.

---

# 15. Encerramento de uma conexão TCP

O encerramento normalmente utiliza FIN e ACK.

Um caso típico:

```text
Cliente                         Servidor

   | -------- FIN ------------> |
   | <-------- ACK ------------ |
   |                            |
   | <-------- FIN ------------ |
   | -------- ACK ------------> |
```

Diferente do handshake de abertura, o encerramento pode envolver mais mensagens porque os dois lados precisam fechar seus fluxos independentemente.

---

# 16. RST

RST significa:

```text
Reset
```

É diferente de um encerramento normal com FIN.

Exemplo:

```text
Cliente                 Servidor

SYN -------------------->

<----------------------- RST
```

Uma interpretação comum é:

```text
Não existe um serviço aceitando essa conexão nessa porta.
```

Por exemplo:

```bash
curl http://192.168.1.10:9999
```

Se nenhuma aplicação estiver escutando a porta, o comportamento observado pode envolver um RST, dependendo da configuração e do caminho da rede.

---

# 17. UDP

UDP significa:

```text
User Datagram Protocol
```

É um protocolo de transporte muito mais simples que TCP.

Características:

* Sem conexão.
* Sem handshake TCP.
* Sem retransmissão própria.
* Não garante entrega.
* Não garante ordenação.
* Possui baixo overhead.

Exemplos de uso:

```text
DNS
DHCP
NTP
VoIP
Jogos online
Streaming
QUIC
```

> O fato de UDP não garantir entrega não significa que uma aplicação baseada em UDP não possa implementar confiabilidade por conta própria. Alguns protocolos de aplicação fazem isso.

---

# 18. Estrutura do UDP

O cabeçalho UDP possui quatro campos principais:

```text
+------------------------+
| Source Port            |
+------------------------+
| Destination Port       |
+------------------------+
| Length                 |
+------------------------+
| Checksum               |
+------------------------+
| Dados                   |
+------------------------+
```

É muito menor e mais simples que o cabeçalho TCP.

---

# 19. TCP vs UDP

| Característica               | TCP     | UDP            |
| ---------------------------- | ------- | -------------- |
| Conexão                      | Sim     | Não            |
| Handshake                    | Sim     | Não            |
| Ordem                        | Sim     | Não            |
| Retransmissão                | Sim     | Não            |
| Controle de fluxo            | Sim     | Não            |
| Controle de congestionamento | Sim     | Não como TCP   |
| Overhead                     | Maior   | Menor          |
| Latência inicial             | Maior   | Menor          |
| Uso típico                   | Web/SSH | DNS/VoIP/Jogos |

Resumo:

```text
TCP
=
Confiabilidade + controle

UDP
=
Simplicidade + baixa sobrecarga
```

---

# 20. ICMP

ICMP significa:

```text
Internet Control Message Protocol
```

É utilizado para mensagens de controle, diagnóstico e comunicação de erros relacionados ao IP.

Ele não é um protocolo de transporte como TCP ou UDP.

ICMP fica associado à camada de Internet.

---

# 21. ICMP Echo Request e Echo Reply

O comando:

```bash
ping 8.8.8.8
```

normalmente utiliza:

```text
ICMP Echo Request
```

O destino responde com:

```text
ICMP Echo Reply
```

Visualmente:

```text
Cliente                     Destino

Echo Request  ------------->

Echo Reply   <-------------
```

O resultado permite verificar aspectos da conectividade IP e medir o tempo de ida e volta.

---

# 22. ICMP e troubleshooting

ICMP é muito útil para diagnóstico.

Exemplos de mensagens ICMP incluem mensagens relacionadas a:

* Destino inalcançável.
* Time Exceeded.
* Echo Request.
* Echo Reply.

O `traceroute` tradicional pode aproveitar mensagens ICMP para identificar quando um pacote excede seu TTL.

Importante:

```text
Ping falhar
≠
O host necessariamente está offline.
```

Um firewall pode bloquear respostas ICMP mesmo que o serviço esteja funcionando.

Da mesma forma:

```text
Ping funcionar
≠
A porta TCP/UDP desejada está aberta.
```

---

# 23. ARP

ARP significa:

```text
Address Resolution Protocol
```

Em redes IPv4 Ethernet, ele permite descobrir:

```text
IPv4 -> MAC
```

Imagine:

```text
IP:

192.168.1.1
```

O computador conhece o IP, mas precisa descobrir:

```text
Qual MAC possui esse IP?
```

ARP resolve essa associação.

---

# 24. Como funciona o ARP

Imagine:

```text
PC A:

192.168.1.10
```

Precisa enviar para:

```text
192.168.1.1
```

Primeiro consulta sua tabela local:

```text
Tenho o MAC de 192.168.1.1?
```

Se não tiver:

```text
ARP Request
```

é enviado para a rede local.

---

# 25. ARP Request e ARP Reply

Fluxo:

```text
PC A                                  PC B

"Quem tem 192.168.1.1?"

          ARP Request
        ------------------------------>

<-------------------------------

"192.168.1.1 é meu.
Meu MAC é AA:BB:CC:DD:EE:FF"

          ARP Reply
```

O computador armazena a informação em cache.

---

# 26. Cache ARP

Não seria eficiente perguntar constantemente:

```text
Quem possui 192.168.1.1?
```

Por isso, a associação pode ser armazenada temporariamente.

Exemplo conceitual:

```text
192.168.1.1 -> AA:BB:CC:DD:EE:FF
```

No Linux:

```bash
ip neigh
```

Exemplo:

```text
192.168.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE
```

---

# 27. ARP no Linux

Visualizar vizinhos:

```bash
ip neigh
```

Limpar uma entrada específica:

```bash
sudo ip neigh del 192.168.1.1 dev eth0
```

Consultar novamente:

```bash
ip neigh
```

Ao tentar acessar o host novamente, o sistema pode precisar descobrir o MAC outra vez.

---

# 28. Broadcast

Broadcast significa enviar para todos os dispositivos de um domínio de broadcast local.

No IPv4:

```text
255.255.255.255
```

é o broadcast limitado.

Em uma rede:

```text
192.168.1.0/24
```

o broadcast dirigido tradicional é:

```text
192.168.1.255
```

ARP Request é um exemplo clássico de mensagem enviada em broadcast Ethernet.

---

# 29. Unicast, Broadcast e Multicast

## Unicast

Um remetente:

```text
A
|
+----> B
```

Comunicação ponto a ponto.

---

## Broadcast

Um remetente:

```text
        B
        ^
        |
A ----> + ----> C
        |
        v
        D
```

Todos os dispositivos do domínio recebem a mensagem.

---

## Multicast

Um remetente envia para um grupo específico:

```text
        B
       ^
      /
A ---+
      \
       v
        D
```

Apenas os membros do grupo recebem.

---

# 30. MTU

MTU significa:

```text
Maximum Transmission Unit
```

É o maior tamanho de pacote IP que pode ser transportado por determinada interface/enlace sem fragmentação naquele enlace.

Um valor bastante comum em Ethernet é:

```text
1500 bytes
```

Isso inclui o cabeçalho IP e os dados IP, mas não o cabeçalho Ethernet e o FCS.

---

# 31. Fragmentação

Se um pacote IPv4 for maior que o que determinado enlace suporta e a fragmentação for permitida, ele pode ser dividido em fragmentos.

Exemplo conceitual:

```text
Pacote grande
       |
       v
+------+------+
| Frag 1      |
+-------------+
| Frag 2      |
+-------------+
| Frag 3      |
+-------------+
```

O destino precisa remontar os fragmentos.

A fragmentação pode gerar overhead e problemas de desempenho.

Em muitos ambientes modernos, busca-se evitar fragmentação utilizando mecanismos como Path MTU Discovery.

---

# 32. Portas

TCP e UDP utilizam portas para identificar serviços e fluxos.

Exemplo:

```text
22
80
443
53
```

Um servidor pode estar:

```text
LISTEN
```

em uma porta.

Exemplo:

```text
0.0.0.0:22
```

Isso significa que um serviço está escutando na porta TCP 22 em todos os endereços IPv4 locais associados àquele socket, conforme o bind realizado.

---

# 33. IP + Porta

Um IP identifica um host/interface logicamente.

A porta ajuda a identificar o serviço ou endpoint de transporte naquele host.

Exemplo:

```text
192.168.1.10:22
```

significa:

```text
IP:
192.168.1.10

Porta:
22
```

Outro:

```text
192.168.1.10:443
```

---

# 34. Socket

Um socket representa um endpoint de comunicação utilizado pelo sistema operacional.

Uma conexão TCP pode ser identificada pelo conjunto:

```text
IP origem
Porta origem
IP destino
Porta destino
```

Exemplo:

```text
192.168.1.10:51234
        |
        v
142.250.x.x:443
```

Outro cliente pode utilizar:

```text
192.168.1.10:51235
        |
        v
142.250.x.x:443
```

Mesmo destino:

```text
142.250.x.x:443
```

mas portas de origem diferentes.

Isso permite ao sistema diferenciar as conexões.

---

# 35. Como uma requisição realmente acontece

Imagine:

```text
Cliente:

192.168.1.10
```

Quer acessar:

```text
https://example.com
```

Uma versão simplificada é:

```text
1. DNS
   |
   v
2. Descobrir IP
   |
   v
3. Descobrir próximo MAC via ARP, se necessário
   |
   v
4. TCP handshake
   |
   v
5. TLS
   |
   v
6. HTTP
   |
   v
7. Resposta
```

---

# 36. Exemplo com HTTP

Imagine:

```bash
curl http://192.168.1.50
```

O processo pode ser:

```text
curl
 |
 v
TCP SYN
 |
 v
TCP SYN-ACK
 |
 v
TCP ACK
 |
 v
HTTP GET
 |
 v
HTTP Response
```

Visualmente:

```text
Cliente                         Servidor

SYN ---------------------------->

    <---------------------------- SYN-ACK

ACK ---------------------------->

GET / -------------------------->

    <---------------------------- HTTP Response
```

---

# 37. Exemplo com SSH

Imagine:

```bash
ssh usuario@192.168.1.50
```

O primeiro passo de transporte será normalmente:

```text
TCP/22
```

O fluxo simplificado:

```text
SSH Client
    |
    v
TCP handshake
    |
    v
SSH protocol negotiation
    |
    v
Autenticação
    |
    v
Sessão SSH
```

---

# 38. Exemplo com DNS

Imagine:

```bash
dig example.com
```

Uma consulta tradicional pode utilizar:

```text
UDP/53
```

Fluxo:

```text
Cliente
   |
   | DNS Query
   v
Servidor DNS
   |
   | DNS Response
   v
Cliente
```

Em situações apropriadas, DNS também pode utilizar TCP.

---

# 39. Capturando pacotes com tcpdump

`tcpdump` permite visualizar o tráfego que passa por uma interface.

Exemplo:

```bash
sudo tcpdump -i eth0
```

Capturar somente TCP:

```bash
sudo tcpdump -i eth0 tcp
```

Somente UDP:

```bash
sudo tcpdump -i eth0 udp
```

Somente ICMP:

```bash
sudo tcpdump -i eth0 icmp
```

---

# 40. Analisando um handshake TCP

Execute:

```bash
sudo tcpdump -i eth0 -n 'tcp port 80'
```

Ao acessar um servidor HTTP, podemos encontrar algo conceitualmente semelhante a:

```text
IP 192.168.1.10.50000 > 192.168.1.20.80: Flags [S]

IP 192.168.1.20.80 > 192.168.1.10.50000: Flags [S.]

IP 192.168.1.10.50000 > 192.168.1.20.80: Flags [.]
```

Interpretando:

```text
[S]
```

SYN

```text
[S.]
```

SYN + ACK

```text
[.]
```

ACK

Portanto:

```text
SYN
 ↓
SYN-ACK
 ↓
ACK
```

---

# 41. Analisando ICMP

Execute:

```bash
sudo tcpdump -i eth0 -n icmp
```

Depois:

```bash
ping 8.8.8.8
```

Você pode observar:

```text
Echo Request
Echo Reply
```

Fluxo:

```text
Cliente
    |
    | Echo Request
    v
Servidor
    |
    | Echo Reply
    v
Cliente
```

---

# 42. Analisando ARP

Execute:

```bash
sudo tcpdump -i eth0 -n arp
```

Depois tente acessar um host local cuja entrada ARP não esteja em cache.

Você pode observar algo semelhante a:

```text
ARP, Request who-has 192.168.1.1 tell 192.168.1.10
```

seguido por:

```text
ARP, Reply 192.168.1.1 is-at aa:bb:cc:dd:ee:ff
```

---

# 43. Diagnóstico de problemas TCP

Se uma conexão TCP não funciona, observe o handshake.

Caso:

```text
SYN
```

seja enviado e:

```text
SYN-ACK
```

nunca apareça, investigue:

* Rota.
* Firewall.
* Servidor.
* Porta.
* Filtragem.
* Problemas intermediários.

---

## Caso 1 — SYN sem resposta

```text
Cliente                 Servidor

SYN -------------------->
SYN -------------------->
SYN -------------------->
```

Possíveis causas:

```text
Servidor inacessível
Firewall DROP
Problema de rota
Porta filtrada
```

---

## Caso 2 — RST

```text
SYN -------------------->

<----------------------- RST
```

Pode indicar:

```text
Porta sem serviço escutando
```

ou outro motivo para rejeição imediata.

---

## Caso 3 — handshake funciona

```text
SYN
SYN-ACK
ACK
```

Então:

```text
Transporte funcionando.
```

O problema pode estar acima:

```text
TLS
HTTP
Autenticação
Aplicação
```

---

# 44. Diagnóstico de problemas UDP

UDP não possui handshake como TCP.

Portanto, pode ser mais difícil determinar onde está o problema.

Exemplo:

```text
Cliente
    |
    | UDP
    v
Servidor
```

Pode ocorrer:

```text
Cliente envia
        |
        v
Nenhuma resposta
```

Isso não significa automaticamente:

```text
Servidor offline
```

Pode ser:

* Serviço não está respondendo.
* Firewall bloqueando.
* Pacote perdido.
* Aplicação esperando uma mensagem específica.
* Serviço simplesmente não possui resposta para aquela entrada.

Por isso, análise com `tcpdump` ou Wireshark pode ser extremamente útil.

---

# 45. Diagnóstico de problemas ARP

Imagine:

```text
192.168.1.10
```

não consegue acessar:

```text
192.168.1.1
```

Verifique:

```bash
ip neigh
```

Talvez apareça:

```text
192.168.1.1 dev eth0 INCOMPLETE
```

Isso significa que o sistema ainda não conseguiu resolver corretamente o vizinho.

Capturar ARP:

```bash
sudo tcpdump -i eth0 -n arp
```

Se houver:

```text
ARP Request
```

mas nunca:

```text
ARP Reply
```

investigue:

* Conectividade de camada 2.
* VLAN.
* Switch.
* Cabo.
* Wi-Fi.
* Endereço IP incorreto.
* Host de destino.

---

# 46. Diagnóstico de problemas ICMP

Um teste:

```bash
ping 8.8.8.8
```

falhou.

Não conclua imediatamente:

```text
Internet está fora.
```

Verifique:

```text
1. Interface
2. IP
3. Gateway
4. Rota
5. Firewall
6. ICMP sendo bloqueado
```

É possível que:

```text
ICMP esteja bloqueado
```

enquanto:

```text
TCP/443
```

continua funcionando.

---

# 47. Ferramentas Linux

## `ip`

Interfaces:

```bash
ip link
```

Endereços:

```bash
ip addr
```

Rotas:

```bash
ip route
```

Vizinhos:

```bash
ip neigh
```

---

## `ss`

Ver sockets TCP:

```bash
ss -t
```

Ver escutas:

```bash
ss -l
```

Ver TCP/UDP:

```bash
ss -tu
```

Ver processos:

```bash
sudo ss -tulpn
```

---

## `ping`

```bash
ping 8.8.8.8
```

---

## `tcpdump`

TCP:

```bash
sudo tcpdump -i eth0 tcp
```

UDP:

```bash
sudo tcpdump -i eth0 udp
```

ICMP:

```bash
sudo tcpdump -i eth0 icmp
```

ARP:

```bash
sudo tcpdump -i eth0 arp
```

---

## `nc`

Netcat pode ser útil para testar portas.

No servidor:

```bash
nc -l 8080
```

No cliente:

```bash
nc 192.168.1.50 8080
```

Isso pode ajudar a verificar se existe conectividade TCP até determinada porta.

---

# 48. Exercícios

## Exercício 1 — TCP

Explique:

```text
SYN
SYN-ACK
ACK
```

O que cada pacote representa?

---

## Exercício 2 — TCP

Você captura:

```text
SYN
SYN-ACK
ACK
```

Mas nenhum dado HTTP aparece.

O que pode estar acontecendo?

Investigue:

```text
TLS
Aplicação
Firewall
Servidor
```

---

## Exercício 3 — TCP

Você captura:

```text
SYN
RST
```

Qual é uma hipótese provável?

---

## Exercício 4 — UDP

Explique por que:

```text
UDP
```

pode ser mais difícil de diagnosticar do que:

```text
TCP
```

---

## Exercício 5 — ICMP

Execute:

```bash
ping 127.0.0.1
```

Depois:

```bash
ping 8.8.8.8
```

Explique a diferença entre os dois testes.

---

## Exercício 6 — ARP

Execute:

```bash
ip neigh
```

Identifique:

```text
IP
MAC
Estado
Interface
```

---

## Exercício 7 — Captura TCP

Execute:

```bash
sudo tcpdump -i any -n 'tcp port 80'
```

Em outro terminal:

```bash
curl http://example.com
```

Observe o handshake.

---

## Exercício 8 — Captura ICMP

Execute:

```bash
sudo tcpdump -i any -n icmp
```

Depois:

```bash
ping -c 4 8.8.8.8
```

Identifique:

```text
Echo Request
Echo Reply
```

---

## Exercício 9 — Captura ARP

Execute:

```bash
sudo tcpdump -i any -n arp
```

Limpe uma entrada de neighbor:

```bash
sudo ip neigh del 192.168.1.1 dev eth0
```

Depois tente acessar o gateway.

Observe:

```text
ARP Request
ARP Reply
```

---

# 49. Resumo

Os quatro protocolos principais deste documento possuem funções muito diferentes:

```text
TCP
 |
 +-- Transporte confiável
 +-- Conexão
 +-- Ordem
 +-- Retransmissão
```

```text
UDP
 |
 +-- Transporte simples
 +-- Sem conexão
 +-- Sem retransmissão própria
 +-- Baixo overhead
```

```text
ICMP
 |
 +-- Controle
 +-- Diagnóstico
 +-- Mensagens de erro
 +-- Ping
 +-- Traceroute
```

```text
ARP
 |
 +-- IPv4 -> MAC
 +-- Rede local
 +-- Descoberta de vizinhos
```

---

# Fluxo completo

Uma comunicação típica pode envolver todos esses conceitos:

```text
                    APLICAÇÃO
                        |
                        v
                HTTP / HTTPS / SSH
                        |
                        v
                TCP / UDP
                        |
                        v
                  IP / ICMP
                        |
                        v
              Ethernet / Wi-Fi
                        |
                        v
                       ARP
                        |
                        v
                 MAC / Meio físico
```

Por exemplo:

```text
Navegador
   |
   v
HTTPS
   |
   v
TCP/443
   |
   v
IP
   |
   v
Gateway
   |
   v
Ethernet
   |
   v
Internet
```

---

# O que você deve dominar

Antes de avançar para firewall e ferramentas de análise, procure dominar:

* Diferença entre TCP e UDP.
* Three-Way Handshake.
* Flags SYN, ACK, FIN e RST.
* Números de sequência.
* ACK.
* Retransmissão.
* Controle de fluxo.
* Controle de congestionamento.
* Estados TCP.
* Encerramento TCP.
* Estrutura básica do UDP.
* Funcionamento do ICMP.
* Echo Request e Echo Reply.
* Funcionamento do ARP.
* ARP Request e Reply.
* Cache ARP.
* Broadcast.
* Unicast e multicast.
* MTU.
* MSS.
* Relação entre IP e porta.
* Conceito de socket.
* Leitura básica do `tcpdump`.
* Identificação de handshake TCP.
* Identificação de tráfego ICMP.
* Identificação de tráfego ARP.

---

# Mapa mental

```text
PROTOCOLOS
│
├── TRANSPORTE
│   │
│   ├── TCP
│   │   ├── SYN
│   │   ├── ACK
│   │   ├── FIN
│   │   ├── RST
│   │   ├── Sequência
│   │   ├── Retransmissão
│   │   ├── Controle de fluxo
│   │   └── Congestionamento
│   │
│   └── UDP
│       ├── Sem conexão
│       ├── Sem garantia
│       └── Baixo overhead
│
├── INTERNET
│   │
│   ├── IP
│   │
│   └── ICMP
│       ├── Ping
│       ├── Erros
│       └── Diagnóstico
│
├── REDE LOCAL
│   │
│   └── ARP
│       ├── IPv4 -> MAC
│       ├── Request
│       ├── Reply
│       └── Cache
│
└── DIAGNÓSTICO
    ├── ip
    ├── ss
    ├── ping
    ├── tcpdump
    └── nc
```

---

# Regra prática de troubleshooting

Quando uma aplicação não consegue se comunicar, pense em camadas:

```text
Aplicação
    ↓
Porta
    ↓
TCP / UDP
    ↓
IP
    ↓
Rota
    ↓
Gateway
    ↓
ARP
    ↓
Ethernet / Wi-Fi
```

E utilize as ferramentas correspondentes:

```text
ip route     -> rota
ip neigh     -> ARP / vizinhos
ss           -> sockets / portas
ping         -> ICMP
tcpdump      -> pacotes
nc           -> teste de porta
```

> **Regra de ouro:** não tente diagnosticar uma aplicação olhando apenas para a aplicação. Observe o tráfego. Descubra se o pacote foi enviado, se chegou ao destino, se houve resposta e em qual camada a comunicação parou.
