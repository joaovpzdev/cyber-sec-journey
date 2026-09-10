# Endereçamento IP e Sub-redes

> Este documento apresenta os fundamentos do endereçamento IP, máscaras de rede, CIDR, sub-redes, gateways, endereços públicos e privados, além de NAT. O objetivo é compreender como dispositivos são identificados e como os pacotes encontram seu caminho entre diferentes redes.

---

# Sumário

* [O que é endereçamento IP](#o-que-é-endereçamento-ip)
* [IPv4](#ipv4)
* [Estrutura de um endereço IPv4](#estrutura-de-um-endereço-ipv4)
* [Binário e decimal](#binário-e-decimal)
* [Endereço de rede e endereço de host](#endereço-de-rede-e-endereço-de-host)
* [Máscara de sub-rede](#máscara-de-sub-rede)
* [CIDR](#cidr)
* [Como calcular redes](#como-calcular-redes)
* [Endereço de rede](#endereço-de-rede)
* [Broadcast](#broadcast)
* [Hosts utilizáveis](#hosts-utilizáveis)
* [Sub-redes](#sub-redes)
* [Classes de endereço](#classes-de-endereço)
* [Endereços privados e públicos](#endereços-privados-e-públicos)
* [Loopback](#loopback)
* [APIPA](#apipa)
* [Gateway padrão](#gateway-padrão)
* [Tabela de roteamento](#tabela-de-roteamento)
* [NAT](#nat)
* [PAT](#pat)
* [IPv6](#ipv6)
* [Ferramentas Linux](#ferramentas-linux)
* [Exercícios](#exercícios)
* [Resumo](#resumo)

---

# O que é endereçamento IP

Para que dispositivos possam se comunicar em uma rede, eles precisam de identificadores.

No nível da rede, esse identificador é o **endereço IP**.

Exemplo:

```text
192.168.1.10
```

Um endereço IP permite identificar:

1. A rede à qual o dispositivo pertence.
2. O dispositivo dentro dessa rede.

Um endereço IP sozinho, porém, não é suficiente para determinar completamente a rede.

Também precisamos conhecer a:

```text
Máscara de rede
```

ou:

```text
Prefixo CIDR
```

Por exemplo:

```text
IP:       192.168.1.10
Máscara:  255.255.255.0
```

ou:

```text
192.168.1.10/24
```

---

# IPv4

IPv4 significa:

```text
Internet Protocol version 4
```

Um endereço IPv4 possui:

```text
32 bits
```

Esses 32 bits são divididos em quatro grupos de 8 bits.

Exemplo:

```text
192.168.1.10
```

Em binário:

```text
11000000.10101000.00000001.00001010
```

Cada grupo de 8 bits é chamado de:

```text
Octeto
```

Portanto:

```text
192 . 168 . 1 . 10
 |     |    |    |
 8     8    8    8 bits
```

Total:

```text
8 + 8 + 8 + 8 = 32 bits
```

---

# Estrutura de um endereço IPv4

Um endereço IPv4 possui duas partes conceituais:

```text
+----------------------+----------------------+
|        REDE          |         HOST         |
+----------------------+----------------------+
```

A divisão entre rede e host depende da máscara ou prefixo CIDR.

Exemplo:

```text
192.168.1.10/24
```

Os primeiros 24 bits representam a rede.

Os últimos 8 bits representam os hosts.

```text
192.168.1 | 10
<---24---> <8>
   REDE    HOST
```

---

# Binário e decimal

Computadores trabalham com bits.

Um bit possui dois valores possíveis:

```text
0
1
```

Cada octeto possui 8 bits:

```text
00000000
```

Até:

```text
11111111
```

Os valores possíveis são:

```text
0 até 255
```

Isso acontece porque:

```text
2^8 = 256 valores
```

Os pesos de cada posição são:

```text
128 64 32 16 8 4 2 1
```

Exemplo:

```text
11000000
```

Significa:

```text
128 + 64 = 192
```

Outro exemplo:

```text
10101000
```

Significa:

```text
128 + 32 + 8 = 168
```

Portanto:

```text
11000000.10101000
```

É equivalente a:

```text
192.168
```

---

# Endereço de rede e endereço de host

Considere:

```text
192.168.1.10/24
```

Com `/24`, temos:

```text
192.168.1 | 10
```

A parte da rede é:

```text
192.168.1.0
```

A parte do host é:

```text
10
```

Portanto, o dispositivo pertence à rede:

```text
192.168.1.0/24
```

---

# Máscara de sub-rede

A máscara define quais bits representam a rede e quais representam os hosts.

Exemplo:

```text
255.255.255.0
```

Em binário:

```text
11111111.11111111.11111111.00000000
```

Os bits com valor:

```text
1
```

Representam a parte da rede.

Os bits com valor:

```text
0
```

Representam a parte dos hosts.

---

## Exemplo

```text
IP:

192.168.1.10

Máscara:

255.255.255.0
```

Representação:

```text
IP:

11000000.10101000.00000001.00001010

Máscara:

11111111.11111111.11111111.00000000
```

Os primeiros 24 bits representam a rede.

Os últimos 8 representam hosts.

---

# CIDR

CIDR significa:

```text
Classless Inter-Domain Routing
```

CIDR utiliza uma notação com:

```text
/
```

seguida pela quantidade de bits da rede.

Exemplo:

```text
192.168.1.10/24
```

Significa:

```text
24 bits para rede
8 bits para hosts
```

Porque:

```text
32 - 24 = 8
```

---

# Tabela CIDR

| CIDR | Máscara         | Total de endereços | Hosts utilizáveis* |
| ---- | --------------- | -----------------: | -----------------: |
| /8   | 255.0.0.0       |         16.777.216 |         16.777.214 |
| /16  | 255.255.0.0     |             65.536 |             65.534 |
| /24  | 255.255.255.0   |                256 |                254 |
| /25  | 255.255.255.128 |                128 |                126 |
| /26  | 255.255.255.192 |                 64 |                 62 |
| /27  | 255.255.255.224 |                 32 |                 30 |
| /28  | 255.255.255.240 |                 16 |                 14 |
| /29  | 255.255.255.248 |                  8 |                  6 |
| /30  | 255.255.255.252 |                  4 |                  2 |

> *A regra tradicional de hosts utilizáveis considera que um endereço é reservado para a rede e outro para broadcast. Existem exceções, como `/31`, utilizado em determinados enlaces ponto a ponto.

---

# Fórmula para calcular endereços

Um endereço IPv4 possui:

```text
32 bits
```

Se uma rede possui prefixo:

```text
/24
```

Sobram:

```text
32 - 24 = 8 bits
```

Quantidade total de endereços:

```text
2^8 = 256
```

Hosts tradicionais utilizáveis:

```text
256 - 2 = 254
```

---

# Endereço de rede

O endereço de rede identifica a própria rede.

Considere:

```text
192.168.1.10/24
```

A rede é:

```text
192.168.1.0
```

O endereço de rede não é normalmente atribuído a um host.

---

# Broadcast

O broadcast representa todos os hosts de uma rede IPv4.

Para:

```text
192.168.1.0/24
```

Temos:

```text
Endereço de rede:

192.168.1.0
```

Hosts:

```text
192.168.1.1
até
192.168.1.254
```

Broadcast:

```text
192.168.1.255
```

Visualmente:

```text
192.168.1.0
    |
    |---- Endereço de rede
    |
192.168.1.1
    |
    |---- Primeiro host
    |
...
    |
192.168.1.254
    |
    |---- Último host
    |
192.168.1.255
    |
    |---- Broadcast
```

---

# Hosts utilizáveis

Na regra tradicional:

```text
Total de hosts = 2^(bits de host) - 2
```

Exemplo:

```text
/24
```

Bits de host:

```text
32 - 24 = 8
```

Total:

```text
2^8 = 256
```

Hosts utilizáveis:

```text
256 - 2 = 254
```

---

# Sub-redes

Subnetting é o processo de dividir uma rede maior em redes menores.

Considere:

```text
192.168.1.0/24
```

Essa rede possui:

```text
256 endereços
```

Podemos dividi-la em duas redes `/25`.

```text
192.168.1.0/25
192.168.1.128/25
```

---

## Primeira sub-rede

```text
Rede:

192.168.1.0/25
```

Endereços:

```text
192.168.1.0
até
192.168.1.127
```

Hosts:

```text
192.168.1.1
até
192.168.1.126
```

Broadcast:

```text
192.168.1.127
```

---

## Segunda sub-rede

```text
Rede:

192.168.1.128/25
```

Endereços:

```text
192.168.1.128
até
192.168.1.255
```

Hosts:

```text
192.168.1.129
até
192.168.1.254
```

Broadcast:

```text
192.168.1.255
```

---

# Como calcular sub-redes

Uma forma prática é observar o tamanho do bloco.

Exemplo:

```text
/26
```

A máscara é:

```text
255.255.255.192
```

O tamanho do bloco é:

```text
256 - 192 = 64
```

Portanto, as redes começam em:

```text
192.168.1.0
192.168.1.64
192.168.1.128
192.168.1.192
```

As redes são:

```text
192.168.1.0/26
192.168.1.64/26
192.168.1.128/26
192.168.1.192/26
```

---

# Exemplo de cálculo

Considere:

```text
IP:

192.168.10.70/26
```

A máscara é:

```text
255.255.255.192
```

Tamanho do bloco:

```text
256 - 192 = 64
```

Redes possíveis:

```text
0
64
128
192
```

O número:

```text
70
```

Está entre:

```text
64 e 127
```

Portanto:

```text
Rede:

192.168.10.64/26
```

Broadcast:

```text
192.168.10.127
```

Hosts:

```text
192.168.10.65
até
192.168.10.126
```

---

# Classes de endereço

Historicamente, IPv4 utilizava classes.

---

## Classe A

```text
1.0.0.0
até
126.255.255.255
```

Máscara histórica:

```text
255.0.0.0
```

Ou:

```text
/8
```

---

## Classe B

```text
128.0.0.0
até
191.255.255.255
```

Máscara histórica:

```text
255.255.0.0
```

Ou:

```text
/16
```

---

## Classe C

```text
192.0.0.0
até
223.255.255.255
```

Máscara histórica:

```text
255.255.255.0
```

Ou:

```text
/24
```

---

## Classes D e E

Classe D:

```text
224.0.0.0 até 239.255.255.255
```

Utilizada para:

```text
Multicast
```

Classe E:

```text
240.0.0.0 até 255.255.255.255
```

Reservada para usos especiais.

---

> Atualmente, o roteamento moderno utiliza CIDR. As classes são principalmente um conceito histórico e didático.

---

# Endereços privados e públicos

Existem faixas de IPv4 reservadas para redes privadas.

Esses endereços não são roteados diretamente pela Internet pública.

---

## Faixa 10.0.0.0/8

```text
10.0.0.0
até
10.255.255.255
```

---

## Faixa 172.16.0.0/12

```text
172.16.0.0
até
172.31.255.255
```

---

## Faixa 192.168.0.0/16

```text
192.168.0.0
até
192.168.255.255
```

---

# Endereço público

Um endereço público pode ser roteado pela Internet.

Exemplo conceitual:

```text
Servidor
IP público

203.x.x.x
```

Endereços públicos normalmente são fornecidos por:

* Provedores de Internet
* Data centers
* Provedores de cloud

---

# Loopback

A faixa de loopback é:

```text
127.0.0.0/8
```

O endereço mais conhecido é:

```text
127.0.0.1
```

Também chamado de:

```text
localhost
```

Ele representa o próprio computador.

Exemplo:

```bash
ping 127.0.0.1
```

A comunicação não sai fisicamente pela interface de rede.

---

# APIPA

Quando um dispositivo configurado para receber IP automaticamente não consegue obter um endereço DHCP, alguns sistemas podem utilizar uma faixa automática.

Exemplo:

```text
169.254.0.0/16
```

Esse comportamento é conhecido como:

```text
APIPA
```

ou:

```text
Link-Local Addressing
```

Em uma rede local, encontrar um endereço `169.254.x.x` frequentemente indica que houve falha na obtenção de um endereço configurado por DHCP.

---

# Gateway padrão

O gateway padrão é utilizado quando o destino está fora da rede local.

Considere:

```text
Computador:

192.168.1.10/24
```

Gateway:

```text
192.168.1.1
```

O computador deseja acessar:

```text
8.8.8.8
```

Esse endereço não pertence à rede:

```text
192.168.1.0/24
```

Portanto:

```text
Computador
     |
     v
Gateway
192.168.1.1
     |
     v
Internet
```

---

# Como saber se um destino está na rede local

Considere:

```text
Host:

192.168.1.10/24
```

Destino:

```text
192.168.1.50
```

Ambos pertencem à rede:

```text
192.168.1.0/24
```

Portanto, podem se comunicar diretamente pela rede local.

Agora:

```text
Host:

192.168.1.10/24
```

Destino:

```text
192.168.2.10
```

As redes são diferentes:

```text
192.168.1.0/24

192.168.2.0/24
```

Logo, é necessário um roteador.

---

# Tabela de roteamento

O sistema operacional mantém uma tabela de roteamento.

No Linux:

```bash
ip route
```

Exemplo:

```text
default via 192.168.1.1 dev eth0
192.168.1.0/24 dev eth0
```

Isso significa:

```text
Rede local:

192.168.1.0/24
```

Qualquer destino fora dessa rede:

```text
Enviar para:

192.168.1.1
```

---

# Rota padrão

A rota:

```text
0.0.0.0/0
```

Representa:

```text
Qualquer rede
```

Ela normalmente é chamada de:

```text
Default Route
```

Exemplo:

```text
default via 192.168.1.1
```

---

# NAT

NAT significa:

```text
Network Address Translation
```

NAT permite modificar endereços IP durante o tráfego entre redes.

Um uso comum é permitir que dispositivos privados acessem a Internet utilizando um endereço público.

Exemplo:

```text
Rede interna

192.168.1.10
192.168.1.20
192.168.1.30

        |
        v

Roteador

        |
        v

IP Público

203.x.x.x
```

Os dispositivos privados não aparecem diretamente na Internet com seus IPs privados.

O roteador realiza a tradução.

---

# PAT

PAT significa:

```text
Port Address Translation
```

Também é frequentemente chamado de:

```text
NAT Overload
```

Ele permite que vários dispositivos compartilhem um único endereço IP público.

Exemplo:

```text
PC1:

192.168.1.10:50000

PC2:

192.168.1.20:50001

PC3:

192.168.1.30:50002
```

Todos podem acessar a Internet através de:

```text
203.0.113.x
```

O roteador diferencia as conexões utilizando portas.

---

# NAT na prática

Antes do NAT:

```text
Origem:

192.168.1.10:50000
```

Após o NAT:

```text
Origem pública:

203.0.113.10:40000
```

Quando a resposta retorna:

```text
203.0.113.10:40000
```

O roteador consulta sua tabela de traduções e encaminha os dados para:

```text
192.168.1.10:50000
```

---

# Tipos comuns de NAT

## SNAT

Modifica o endereço de origem.

Muito utilizado para permitir que redes privadas acessem outras redes.

---

## DNAT

Modifica o endereço de destino.

Muito utilizado para redirecionamento de portas.

Exemplo:

```text
IP Público:

203.0.113.10:443
```

Pode ser encaminhado para:

```text
192.168.1.10:443
```

---

## Masquerade

Uma forma comum de SNAT utilizada quando o IP externo pode mudar dinamicamente.

Muito utilizada em:

```text
Roteadores
Firewalls Linux
Ambientes domésticos
```

---

# IPv6

IPv6 foi criado para resolver, entre outros problemas, a limitação de endereços do IPv4.

IPv4 possui:

```text
32 bits
```

IPv6 possui:

```text
128 bits
```

Exemplo:

```text
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

---

# Simplificação de IPv6

Zeros à esquerda podem ser removidos.

Exemplo:

```text
2001:0db8:0000:0000:0000:0000:0000:0001
```

Pode ser escrito como:

```text
2001:db8::1
```

A sequência de grupos com zeros pode ser representada por:

```text
::
```

Essa compressão pode ser utilizada uma vez em um endereço.

---

# Prefixos IPv6

Assim como IPv4, IPv6 utiliza CIDR.

Exemplo:

```text
2001:db8:abcd:1234::/64
```

O prefixo `/64` é muito comum em redes IPv6.

---

# Loopback IPv6

O equivalente a:

```text
127.0.0.1
```

No IPv6 é:

```text
::1
```

---

# IPv6 Link-Local

Interfaces IPv6 normalmente possuem um endereço link-local.

A faixa começa com:

```text
fe80::
```

Exemplo:

```text
fe80::1
```

Esses endereços são utilizados para comunicação local no enlace.

---

# Ferramentas Linux

---

## Ver endereços IP

```bash
ip addr
```

Forma curta:

```bash
ip a
```

---

## Ver interfaces

```bash
ip link
```

---

## Ver rotas

```bash
ip route
```

Para IPv6:

```bash
ip -6 route
```

---

## Ver o gateway padrão

```bash
ip route | grep default
```

Exemplo:

```text
default via 192.168.1.1 dev eth0
```

---

## Testar conectividade

```bash
ping 8.8.8.8
```

---

## Testar IPv6

```bash
ping -6 2606:4700:4700::1111
```

---

## Ver tabela ARP/neighbors

```bash
ip neigh
```

---

## Adicionar endereço IP temporariamente

```bash
sudo ip addr add 192.168.1.50/24 dev eth0
```

---

## Remover endereço IP

```bash
sudo ip addr del 192.168.1.50/24 dev eth0
```

---

## Adicionar rota

```bash
sudo ip route add 10.10.0.0/16 via 192.168.1.1
```

---

## Adicionar rota padrão

```bash
sudo ip route add default via 192.168.1.1
```

> Alterações realizadas com `ip addr` e `ip route` geralmente são temporárias e podem desaparecer após reiniciar o sistema ou reiniciar a interface. A persistência depende da distribuição e do gerenciador de rede utilizado.

---

# Exercícios

## Exercício 1

Determine a rede:

```text
192.168.10.25/24
```

Resposta:

```text
Rede:

192.168.10.0/24
```

Broadcast:

```text
192.168.10.255
```

Hosts:

```text
192.168.10.1
até
192.168.10.254
```

---

## Exercício 2

Determine a rede:

```text
192.168.10.70/26
```

Blocos:

```text
0
64
128
192
```

O endereço `70` está no bloco:

```text
64 até 127
```

Resposta:

```text
Rede:

192.168.10.64/26
```

Broadcast:

```text
192.168.10.127
```

Hosts:

```text
192.168.10.65
até
192.168.10.126
```

---

## Exercício 3

Quantos hosts uma rede `/27` possui?

Bits de host:

```text
32 - 27 = 5
```

Total de endereços:

```text
2^5 = 32
```

Hosts tradicionais utilizáveis:

```text
32 - 2 = 30
```

---

## Exercício 4

Determine se os hosts estão na mesma rede:

```text
Host A:

10.0.1.10/24
```

```text
Host B:

10.0.1.200/24
```

Sim.

Ambos pertencem à rede:

```text
10.0.1.0/24
```

---

## Exercício 5

Determine se os hosts estão na mesma rede:

```text
Host A:

192.168.1.10/24
```

```text
Host B:

192.168.2.10/24
```

Não.

As redes são:

```text
192.168.1.0/24
```

e:

```text
192.168.2.0/24
```

A comunicação precisa passar por um roteador.

---

# Resumo

Um endereço IPv4 possui:

```text
32 bits
```

Uma máscara ou prefixo CIDR define:

```text
Parte da rede
+
Parte do host
```

Exemplo:

```text
192.168.1.10/24
```

Representa:

```text
Rede:

192.168.1.0/24
```

Hosts tradicionais:

```text
192.168.1.1
até
192.168.1.254
```

Broadcast:

```text
192.168.1.255
```

Para destinos fora da rede local:

```text
Host
  |
  v
Gateway
  |
  v
Roteador
  |
  v
Outra rede / Internet
```

NAT permite traduzir endereços entre redes:

```text
IP Privado
     |
     v
NAT
     |
     v
IP Público
```

---

# Próximos tópicos

Após compreender endereçamento IP e sub-redes, os próximos tópicos recomendados são:

1. `DNS.md`
2. `Protocolos.md`
3. `SSH.md`
4. `Firewall.md`
5. `Ferramentas.md`

> **Regra prática:** antes de diagnosticar um problema de aplicação, confirme sempre: interface → endereço IP → máscara → rota → gateway → DNS → serviço.
