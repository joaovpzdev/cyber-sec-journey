# Unicast, Broadcast e Multicast no IPv4

> Este documento explica detalhadamente as três principais formas de entrega de pacotes em redes IPv4: **Unicast**, **Broadcast** e **Multicast**. O objetivo é compreender para quem um pacote é enviado, como os dispositivos da rede recebem esse tráfego e em quais situações cada tipo de transmissão é utilizado.

---

# Sumário

- [1. Introdução](#1-introdução)
- [2. O que significa transmitir um pacote](#2-o-que-significa-transmitir-um-pacote)
- [3. Os tipos de transmissão no IPv4](#3-os-tipos-de-transmissão-no-ipv4)
- [4. Unicast](#4-unicast)
- [5. Como funciona o Unicast](#5-como-funciona-o-unicast)
- [6. Unicast e endereços IP](#6-unicast-e-endereços-ip)
- [7. Unicast e endereços MAC](#7-unicast-e-endereços-mac)
- [8. Broadcast](#8-broadcast)
- [9. Como funciona o Broadcast](#9-como-funciona-o-broadcast)
- [10. Endereço de Broadcast](#10-endereço-de-broadcast)
- [11. Broadcast limitado](#11-broadcast-limitado)
- [12. Broadcast direcionado](#12-broadcast-direcionado)
- [13. Broadcast e roteadores](#13-broadcast-e-roteadores)
- [14. Protocolos que utilizam Broadcast](#14-protocolos-que-utilizam-broadcast)
- [15. Multicast](#15-multicast)
- [16. Como funciona o Multicast](#16-como-funciona-o-multicast)
- [17. Endereços IPv4 Multicast](#17-endereços-ipv4-multicast)
- [18. Grupos Multicast](#18-grupos-multicast)
- [19. Multicast e IGMP](#19-multicast-e-igmp)
- [20. Multicast e endereços MAC](#20-multicast-e-endereços-mac)
- [21. Comparação entre Unicast, Broadcast e Multicast](#21-comparação-entre-unicast-broadcast-e-multicast)
- [22. Broadcast Domain](#22-broadcast-domain)
- [23. Switches e Broadcast](#23-switches-e-broadcast)
- [24. Roteadores e Broadcast Domains](#24-roteadores-e-broadcast-domains)
- [25. VLANs e Broadcast](#25-vlans-e-broadcast)
- [26. Exemplos práticos](#26-exemplos-práticos)
- [27. Capturando tráfego](#27-capturando-tráfego)
- [28. Relação com ARP](#28-relação-com-arp)
- [29. Relação com DHCP](#29-relação-com-dhcp)
- [30. Relação com DNS](#30-relação-com-dns)
- [31. Problemas relacionados ao Broadcast](#31-problemas-relacionados-ao-broadcast)
- [32. Broadcast Storm](#32-broadcast-storm)
- [33. Boas práticas](#33-boas-práticas)
- [34. Exercícios](#34-exercícios)
- [35. Resumo](#35-resumo)

---

# 1. Introdução

Quando um dispositivo envia um pacote pela rede, uma pergunta importante precisa ser respondida:

> **Para quem esse pacote deve ser enviado?**

Dependendo da resposta, o tráfego pode ser classificado como:

```text
Unicast
Broadcast
Multicast
```

Esses três conceitos descrevem diferentes formas de comunicação.

```text
UNCAST
Um -> Um

BROADCAST
Um -> Todos

MULTICAST
Um -> Grupo
```

Representação:

```text
                EMISSOR
                   |
         +---------+---------+
         |         |         |
      Unicast   Broadcast  Multicast
         |         |         |
       Um        Todos     Grupo
```

---

# 2. O que significa transmitir um pacote

Imagine uma rede:

```text
        +--------+
        |   PC   |
        +--------+
             |
             |
        +----+----+
        | Switch  |
        +----+----+
         |   |   |
         |   |   |
        PC  PC  Server
```

O primeiro PC pode enviar dados:

```text
Para um dispositivo específico
```

Ou:

```text
Para todos os dispositivos
```

Ou:

```text
Para um grupo específico
```

Essas três situações representam:

```text
Unicast
Broadcast
Multicast
```

---

# 3. Os tipos de transmissão no IPv4

## Unicast

```text
Um emissor
     |
     v
Um destinatário
```

---

## Broadcast

```text
Um emissor
     |
     v
Todos os dispositivos da rede
```

---

## Multicast

```text
Um emissor
     |
     v
Grupo específico de dispositivos
```

Comparação visual:

```text
UNICAST

A -----> B


BROADCAST

          B
          ^
          |
A --------+-------> C
          |
          v
          D


MULTICAST

          B
          ^
          |
A --------+-------> C

D não participa
```

---

# 4. Unicast

Unicast é a forma mais comum de comunicação em redes.

Um dispositivo envia informações para outro dispositivo específico.

```text
Cliente
   |
   | Dados
   v
Servidor
```

Exemplo:

```text
PC
192.168.1.10

Servidor
192.168.1.20
```

O PC envia um pacote para:

```text
192.168.1.20
```

A comunicação é:

```text
Um emissor
      |
      v
Um destinatário
```

---

# 5. Como funciona o Unicast

Imagine:

```text
PC A
192.168.1.10
     |
     |
     v
Switch
     |
     |
     v
PC B
192.168.1.20
```

O pacote possui um endereço de destino específico.

Exemplo conceitual:

```text
IP Origem:
192.168.1.10

IP Destino:
192.168.1.20
```

O objetivo é entregar o pacote apenas ao dispositivo correspondente ao endereço de destino.

---

# 6. Unicast e endereços IP

A maior parte dos endereços IPv4 utilizados por hosts representa comunicação unicast.

Exemplos:

```text
192.168.1.10
10.0.0.5
172.16.20.10
```

Esses endereços normalmente identificam uma interface específica.

Exemplo:

```text
192.168.1.0/24

192.168.1.1   Gateway
192.168.1.10  PC
192.168.1.20  Notebook
192.168.1.30  Servidor
```

Se o PC:

```text
192.168.1.10
```

enviar um pacote para:

```text
192.168.1.30
```

temos:

```text
UNICAST
```

---

# 7. Unicast e endereços MAC

Em uma rede Ethernet, o pacote IP é transportado dentro de um frame.

Representação simplificada:

```text
FRAME ETHERNET
+------------------------+
| MAC Destino            |
| MAC Origem             |
+------------------------+
| PACOTE IP              |
|                        |
| IP Origem              |
| IP Destino             |
+------------------------+
```

Em um tráfego unicast:

```text
IP Destino
      |
      v
Dispositivo específico
      |
      v
MAC correspondente
```

O endereço MAC de destino normalmente é obtido utilizando mecanismos como ARP em redes IPv4 Ethernet.

---

# 8. Broadcast

Broadcast é uma transmissão destinada a todos os dispositivos dentro de um domínio de broadcast.

Representação:

```text
            A
            |
            v

        +--------+
        | Switch |
        +--------+
        /   |    \
       /    |     \
      v     v      v

      B     C      D
```

O dispositivo A envia uma mensagem.

Todos os dispositivos do domínio de broadcast recebem o frame.

---

# 9. Como funciona o Broadcast

Imagine a rede:

```text
192.168.1.0/24
```

Com os dispositivos:

```text
192.168.1.1   Gateway
192.168.1.10  PC
192.168.1.20  Notebook
192.168.1.30  Servidor
```

O endereço de broadcast da rede é:

```text
192.168.1.255
```

Quando um pacote é enviado para esse endereço, ele é destinado a todos os hosts daquela rede IPv4.

Conceitualmente:

```text
PC
 |
 | 192.168.1.255
 |
 v

+--------+
| Switch |
+--------+
 |   |   |
 |   |   |
 v   v   v

PC  PC  Server
```

---

# 10. Endereço de Broadcast

O endereço de broadcast depende da máscara ou prefixo da rede.

Exemplo:

```text
Rede:
192.168.1.0/24
```

Máscara:

```text
255.255.255.0
```

Endereço de broadcast:

```text
192.168.1.255
```

Outro exemplo:

```text
Rede:
192.168.10.0/24

Broadcast:
192.168.10.255
```

---

## Como identificar o broadcast

Em uma rede IPv4, o endereço de broadcast possui todos os bits da parte de host definidos como:

```text
1
```

Exemplo:

```text
Rede:

192.168.1.0/24
```

Parte da rede:

```text
192.168.1
```

Parte de host:

```text
8 bits
```

Broadcast:

```text
11111111
```

Resultado:

```text
192.168.1.255
```

---

# 11. Broadcast limitado

O endereço:

```text
255.255.255.255
```

é conhecido como broadcast limitado.

Ele representa:

```text
Broadcast para a rede local
```

Exemplo:

```text
Host
 |
 | 255.255.255.255
 |
 v
Rede local
```

Esse tipo de broadcast não é encaminhado por roteadores.

---

# 12. Broadcast direcionado

Também existe o conceito de broadcast direcionado.

Exemplo:

```text
Rede:

192.168.10.0/24
```

Broadcast:

```text
192.168.10.255
```

Esse endereço representa o broadcast daquela rede específica.

Conceitualmente:

```text
192.168.10.0/24

Host A
    |
    | Broadcast
    v

192.168.10.255
```

Por motivos de segurança e para evitar abusos, o encaminhamento de broadcasts direcionados por roteadores geralmente é restringido ou desabilitado.

---

# 13. Broadcast e roteadores

Roteadores separam redes.

Exemplo:

```text
Rede A

192.168.1.0/24
        |
        |
     Roteador
        |
        |
Rede B

192.168.2.0/24
```

Um broadcast normalmente pertence apenas ao domínio local.

```text
PC
 |
 | Broadcast
 v
Switch
 |
 +---- PC
 +---- PC
 +---- PC

ROTEADOR
 |
 X
 |
Outra rede
```

O roteador atua como uma fronteira entre domínios de broadcast.

---

# 14. Protocolos que utilizam Broadcast

Alguns protocolos e mecanismos utilizam broadcast.

Exemplos:

```text
ARP
DHCP
```

---

## ARP

Quando um dispositivo conhece o IP, mas precisa descobrir o MAC correspondente, ele pode enviar uma solicitação ARP.

Exemplo:

```text
Quem possui
192.168.1.20?
```

Representação:

```text
PC
 |
 | ARP Request
 | Broadcast
 v

+--------+
| Switch |
+--------+
 |   |   |
 v   v   v

PC  PC  Server
```

O dispositivo dono do IP responde.

---

## DHCP

Um dispositivo que acabou de entrar na rede pode ainda não possuir um endereço IP.

Ele pode enviar mensagens DHCP utilizando broadcast.

Fluxo simplificado:

```text
Cliente
   |
   | DHCP Discover
   | Broadcast
   v

Rede
```

O servidor DHCP responde com uma configuração.

---

# 15. Multicast

Multicast permite enviar dados para um grupo de dispositivos interessados.

Não é:

```text
Um -> Um
```

Nem:

```text
Um -> Todos
```

É:

```text
Um -> Grupo
```

Representação:

```text
                Emissor
                   |
                   v
                Rede
             /    |    \
            v     v     v

        Grupo A  Grupo A  Não participa
```

Somente os membros interessados recebem o tráfego multicast.

---

# 16. Como funciona o Multicast

Imagine:

```text
        +---------+
        | Emissor |
        +---------+
             |
             v

        Grupo Multicast

          /       \
         v         v

     Host A      Host B


Host C
não participa
```

O emissor envia os dados para um endereço multicast.

Os hosts interessados participam daquele grupo.

---

# 17. Endereços IPv4 Multicast

Os endereços IPv4 multicast pertencem ao intervalo:

```text
224.0.0.0
até
239.255.255.255
```

Em CIDR:

```text
224.0.0.0/4
```

Representação binária:

```text
1110xxxx.xxxxxxxx.xxxxxxxx.xxxxxxxx
```

Os primeiros quatro bits:

```text
1110
```

identificam o espaço de endereços multicast IPv4.

---

# 18. Grupos Multicast

Um endereço multicast representa um grupo.

Exemplo conceitual:

```text
239.1.1.1
```

Os dispositivos interessados podem entrar nesse grupo.

```text
Host A
   |
JOIN
   |
239.1.1.1


Host B
   |
JOIN
   |
239.1.1.1
```

O emissor envia:

```text
Destino:

239.1.1.1
```

Os membros recebem o tráfego.

---

# 19. Multicast e IGMP

Em redes IPv4, um protocolo importante para gerenciamento de grupos multicast é:

```text
IGMP
```

Significa:

```text
Internet Group Management Protocol
```

Ele permite que hosts comuniquem sua participação em grupos multicast.

Exemplo:

```text
Host
 |
 | Quero participar
 v
Grupo Multicast
```

Conceitualmente:

```text
Host A
 |
 | IGMP Join
 v

Roteador / Switch Multicast-aware
```

---

# 20. Multicast e endereços MAC

Em redes Ethernet, o tráfego multicast IP precisa ser transportado utilizando um endereço MAC multicast.

Existe um mapeamento entre:

```text
IP Multicast
```

e:

```text
MAC Multicast
```

Exemplo de prefixo MAC associado a multicast IPv4:

```text
01:00:5E
```

Representação conceitual:

```text
IP Multicast
     |
     v
Mapeamento
     |
     v
MAC Multicast
```

Isso permite que o tráfego seja identificado como multicast na camada Ethernet.

---

# 21. Comparação entre Unicast, Broadcast e Multicast

| Tipo | Comunicação | Destinatários |
|---|---|---|
| Unicast | Um para um | Um dispositivo |
| Broadcast | Um para todos | Todos no domínio de broadcast |
| Multicast | Um para grupo | Membros do grupo |

Visualmente:

```text
UNICAST

A ---> B
```

```text
BROADCAST

        B
        ^
        |
A ------+------> C
        |
        v
        D
```

```text
MULTICAST

        B
        ^
        |
A ------+------> C

D não pertence ao grupo
```

---

# 22. Broadcast Domain

Um broadcast domain é o conjunto de dispositivos que recebem um broadcast.

Exemplo:

```text
             SWITCH

       +--------+--------+
       |        |        |
       v        v        v

      PC       PC      Server
```

Todos pertencem ao mesmo domínio de broadcast.

Se um dispositivo enviar:

```text
Broadcast
```

os demais dispositivos daquele domínio recebem o tráfego.

---

# 23. Switches e Broadcast

Um switch aprende quais dispositivos estão conectados às suas portas utilizando endereços MAC.

Para tráfego unicast conhecido:

```text
PC A
 |
 v
Switch
 |
 v
Porta específica
 |
 v
PC B
```

Para broadcast:

```text
PC A
 |
 v
Switch
 |
 +----> Porta 2
 |
 +----> Porta 3
 |
 +----> Porta 4
```

O switch normalmente replica o tráfego de broadcast para as demais portas pertencentes ao mesmo domínio de broadcast.

---

# 24. Roteadores e Broadcast Domains

Roteadores conectam redes diferentes.

```text
Rede A
    |
    v
Roteador
    |
    v
Rede B
```

Cada interface de roteamento representa uma fronteira entre domínios de broadcast.

Exemplo:

```text
192.168.1.0/24
        |
     Switch
        |
     Roteador
        |
     Switch
        |
192.168.2.0/24
```

Temos dois domínios de broadcast.

---

# 25. VLANs e Broadcast

VLANs também podem separar domínios de broadcast.

Exemplo:

```text
                Switch

        +---------+---------+
        |                   |
        v                   v

      VLAN 10             VLAN 20

      PC A                PC C
      PC B                PC D
```

Mesmo utilizando o mesmo switch físico:

```text
VLAN 10
```

e:

```text
VLAN 20
```

possuem domínios de broadcast separados.

Um broadcast da VLAN 10 não deve ser entregue aos dispositivos da VLAN 20.

---

# 26. Exemplos práticos

## Exemplo 1 — Acessando um servidor Web

```text
PC
192.168.1.10
      |
      | HTTP
      v
Servidor
192.168.1.20
```

Tipo:

```text
UNICAST
```

---

## Exemplo 2 — Descobrindo um endereço MAC

```text
PC
 |
 | Quem possui 192.168.1.20?
 | ARP Request
 | Broadcast
 v
Rede
```

Tipo:

```text
BROADCAST
```

---

## Exemplo 3 — Grupo de vídeo

Imagine vários dispositivos interessados em um fluxo de vídeo.

```text
Servidor
   |
   | Multicast
   v

Grupo

+-------+-------+
|       |       |
v       v       v

TV A   TV B   TV C
```

Tipo:

```text
MULTICAST
```

---

# 27. Capturando tráfego

Ferramentas como `tcpdump` podem ajudar a observar o tráfego.

Listar interfaces:

```bash
ip link
```

Capturar tráfego:

```bash
sudo tcpdump -i any
```

Capturar ARP:

```bash
sudo tcpdump -i any arp
```

Capturar ICMP:

```bash
sudo tcpdump -i any icmp
```

Capturar tráfego multicast:

```bash
sudo tcpdump -i any multicast
```

Uma captura pode ajudar a visualizar:

```text
IP origem
IP destino
MAC origem
MAC destino
Protocolo
Portas
```

---

# 28. Relação com ARP

ARP é um excelente exemplo para compreender broadcast.

Imagine:

```text
PC A

IP:
192.168.1.10
```

Ele deseja comunicar com:

```text
192.168.1.20
```

Primeiro precisa descobrir o MAC correspondente.

Ele envia:

```text
ARP Request

Quem possui:

192.168.1.20?
```

A solicitação é enviada em broadcast.

```text
PC A
 |
 v
Switch
 |
 +---- PC B
 |
 +---- PC C
 |
 +---- Servidor
```

O dispositivo que possui o IP responde.

```text
Servidor
192.168.1.20
 |
 | ARP Reply
 v
PC A
```

Normalmente, a resposta é enviada diretamente ao solicitante.

---

# 29. Relação com DHCP

DHCP também ajuda a entender broadcast.

Quando um dispositivo entra em uma rede, ele pode não saber:

```text
Seu IP
Gateway
Servidor DHCP
```

Então envia uma mensagem inicial.

```text
Cliente
   |
   | DHCP Discover
   | Broadcast
   v
Rede
```

O servidor DHCP pode responder oferecendo uma configuração.

Fluxo simplificado:

```text
DHCP Discover
      |
      v

DHCP Offer
      |
      v

DHCP Request
      |
      v

DHCP ACK
```

---

# 30. Relação com DNS

DNS normalmente utiliza comunicação unicast.

Exemplo:

```text
Cliente
   |
   | DNS Query
   v
Servidor DNS
```

Tipo:

```text
UNICAST
```

Porém, dependendo da tecnologia utilizada, existem mecanismos de resolução local que podem utilizar multicast.

Um exemplo importante em redes locais é o conceito de resolução multicast de nomes, utilizado por determinados mecanismos e protocolos de descoberta.

Portanto:

```text
DNS tradicional
=
Normalmente Unicast
```

Enquanto determinados mecanismos de descoberta local podem utilizar:

```text
Multicast
```

---

# 31. Problemas relacionados ao Broadcast

Broadcast é útil, mas gera tráfego para todos os dispositivos do domínio.

Imagine:

```text
1000 dispositivos
```

Se muitos dispositivos gerarem broadcasts constantemente:

```text
Muitos broadcasts
      |
      v
Mais processamento
      |
      v
Mais tráfego
```

Por isso, redes muito grandes normalmente são segmentadas.

---

# 32. Broadcast Storm

Uma broadcast storm ocorre quando uma quantidade excessiva de tráfego broadcast circula pela rede.

Exemplo conceitual:

```text
Broadcast
   |
   v
Switch A
   |
   v
Switch B
   |
   v
Switch C
   |
   +--------+
            |
            +----> Volta para a rede
```

Se existirem loops de camada 2 e mecanismos de proteção não estiverem funcionando corretamente, os frames podem ser replicados repetidamente.

Resultado:

```text
Mais tráfego
   |
   v
Mais cópias
   |
   v
Mais tráfego
   |
   v
Saturação
```

Uma rede pode se tornar inutilizável.

Mecanismos como protocolos de prevenção de loops ajudam a evitar esse tipo de problema em redes com múltiplos switches.

---

# 33. Boas práticas

## Manter domínios de broadcast controlados

```text
Rede pequena
   |
Pouco Broadcast
```

```text
Rede grande
   |
Segmentação
   |
VLANs
   |
Múltiplas sub-redes
```

---

## Utilizar multicast quando apropriado

Se vários dispositivos precisam receber o mesmo conteúdo:

```text
Unicast para cada dispositivo
```

pode gerar várias transmissões.

Conceitualmente:

```text
Servidor
 |
 +---- Stream -> A
 |
 +---- Stream -> B
 |
 +---- Stream -> C
```

Multicast pode permitir:

```text
Servidor
 |
 +---- Um fluxo
        |
        +---- A
        +---- B
        +---- C
```

A implementação correta depende da aplicação e da infraestrutura da rede.

---

## Segmentar redes

Exemplo:

```text
VLAN 10
Usuários

VLAN 20
Servidores

VLAN 30
IoT

VLAN 40
Visitantes
```

Benefícios:

```text
Menos Broadcast
Maior organização
Maior isolamento
Maior controle
```

---

# 34. Exercícios

## Exercício 1 — Identificar Unicast

Observe:

```text
PC
192.168.1.10

Servidor
192.168.1.20
```

O PC envia um pacote para:

```text
192.168.1.20
```

Pergunta:

```text
Qual tipo de transmissão?
```

Resposta:

```text
Unicast
```

---

## Exercício 2 — Calcular Broadcast

Para:

```text
192.168.10.0/24
```

Determine:

```text
Endereço de Broadcast
```

Resposta:

```text
192.168.10.255
```

---

## Exercício 3 — Outro Broadcast

Para:

```text
10.0.5.0/24
```

Determine:

```text
Broadcast
```

Resposta:

```text
10.0.5.255
```

---

## Exercício 4 — Identificar Multicast

O endereço:

```text
239.10.10.10
```

pertence a qual tipo?

Resposta:

```text
Multicast
```

Pois está dentro do intervalo:

```text
224.0.0.0/4
```

---

## Exercício 5 — Observar ARP

Execute:

```bash
ip neigh
```

Observe os endereços IP e MAC conhecidos.

Depois capture:

```bash
sudo tcpdump -i any arp
```

Tente gerar comunicação com outro dispositivo da rede.

Observe:

```text
ARP Request
ARP Reply
```

---

## Exercício 6 — Broadcast Domain

Considere:

```text
PC
 |
Switch
 |
+---+---+
|       |
PC      Server
```

Pergunta:

```text
Quantos domínios de broadcast existem?
```

Resposta:

```text
1
```

Agora:

```text
Rede A
   |
Switch
   |
Roteador
   |
Switch
   |
Rede B
```

Pergunta:

```text
Quantos domínios de broadcast?
```

Resposta:

```text
2
```

---

# 35. Resumo

Os três principais tipos de transmissão IPv4 são:

```text
UNICAST
Um -> Um
```

```text
BROADCAST
Um -> Todos no domínio de broadcast
```

```text
MULTICAST
Um -> Grupo específico
```

Comparação:

```text
UNICAST

PC A
  |
  v
PC B
```

```text
BROADCAST

       PC B
        ^
        |
PC A ---+----> PC C
        |
        v
      Server
```

```text
MULTICAST

        Host A
           ^
           |
Servidor --+----> Host B

Host C não participa
```

Faixas importantes:

```text
Multicast IPv4:

224.0.0.0
até
239.255.255.255

CIDR:

224.0.0.0/4
```

Broadcast limitado:

```text
255.255.255.255
```

Broadcast depende da rede:

```text
192.168.1.0/24
       |
       v
192.168.1.255
```

Conceito fundamental:

```text
Switch
=
Normalmente mantém o domínio de broadcast

Roteador
=
Separa domínios de broadcast

VLAN
=
Pode criar domínios de broadcast separados
```

> Entender Unicast, Broadcast e Multicast é fundamental para compreender como os dispositivos recebem tráfego em uma rede IPv4. Esses conceitos aparecem diretamente no funcionamento de protocolos como ARP, DHCP, mecanismos de descoberta, streaming, roteamento e segmentação de redes.