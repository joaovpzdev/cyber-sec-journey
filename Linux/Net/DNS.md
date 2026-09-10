# DNS — Domain Name System

> O DNS (Domain Name System) é o sistema responsável por associar nomes de domínio a informações utilizadas na rede, principalmente endereços IP. Ele permite que pessoas utilizem nomes como `google.com` em vez de precisar memorizar endereços IP.

---

# Sumário

* [1. O que é DNS?](#1-o-que-é-dns)
* [2. Por que o DNS existe?](#2-por-que-o-dns-existe)
* [3. Como o DNS funciona?](#3-como-o-dns-funciona)
* [4. Nome de domínio](#4-nome-de-domínio)
* [5. Estrutura hierárquica do DNS](#5-estrutura-hierárquica-do-dns)
* [6. A hierarquia na prática](#6-a-hierarquia-na-prática)
* [7. Servidores DNS](#7-servidores-dns)
* [8. Resolver DNS](#8-resolver-dns)
* [9. Resolução recursiva](#9-resolução-recursiva)
* [10. Resolução iterativa](#10-resolução-iterativa)
* [11. Exemplo completo de resolução](#11-exemplo-completo-de-resolução)
* [12. Cache DNS](#12-cache-dns)
* [13. TTL](#13-ttl)
* [14. Registros DNS](#14-registros-dns)
* [15. Registro A](#15-registro-a)
* [16. Registro AAAA](#16-registro-aaaa)
* [17. Registro CNAME](#17-registro-cname)
* [18. Registro MX](#18-registro-mx)
* [19. Registro NS](#19-registro-ns)
* [20. Registro TXT](#20-registro-txt)
* [21. Registro SOA](#21-registro-soa)
* [22. Registro PTR](#22-registro-ptr)
* [23. Registro SRV](#23-registro-srv)
* [24. Registro CAA](#24-registro-caa)
* [25. Zona DNS](#25-zona-dns)
* [26. Nameserver](#26-nameserver)
* [27. DNS autoritativo](#27-dns-autoritativo)
* [28. DNS recursivo](#28-dns-recursivo)
* [29. DNS público e DNS privado](#29-dns-público-e-dns-privado)
* [30. DNS no Linux](#30-dns-no-linux)
* [31. `/etc/hosts`](#31-etchosts)
* [32. `/etc/resolv.conf`](#32-etcresolvconf)
* [33. `resolvectl`](#33-resolvectl)
* [34. `dig`](#34-dig)
* [35. `nslookup`](#35-nslookup)
* [36. `host`](#36-host)
* [37. Consultando registros específicos](#37-consultando-registros-específicos)
* [38. Consulta reversa](#38-consulta-reversa)
* [39. `dig +trace`](#39-dig-trace)
* [40. TCP e UDP no DNS](#40-tcp-e-udp-no-dns)
* [41. DNS e portas](#41-dns-e-portas)
* [42. DNSSEC](#42-dnssec)
* [43. DoT e DoH](#43-dot-e-doh)
* [44. Problemas comuns de DNS](#44-problemas-comuns-de-dns)
* [45. Diagnóstico de problemas](#45-diagnóstico-de-problemas)
* [46. Exemplos práticos](#46-exemplos-práticos)
* [47. Exercícios](#47-exercícios)
* [48. Resumo](#48-resumo)

---

# 1. O que é DNS?

DNS significa:

```text
Domain Name System
```

Ele é um sistema distribuído e hierárquico utilizado para armazenar e consultar informações relacionadas a nomes de domínio.

Uma das funções mais conhecidas é transformar:

```text
google.com
```

em um endereço IP, por exemplo:

```text
142.250.x.x
```

A ideia pode ser simplificada como:

```text
Nome
  |
  v
DNS
  |
  v
IP
```

Por exemplo:

```text
example.com
     |
     v
93.184.216.34
```

Mas o DNS não serve apenas para descobrir IPs.

Ele também pode informar:

* Quais servidores recebem e-mails.
* Quais servidores são autoritativos por um domínio.
* Qual nome está associado a determinado IP.
* Informações utilizadas por diversos serviços.
* Políticas e verificações por meio de registros TXT.
* Serviços específicos utilizando registros SRV.

---

# 2. Por que o DNS existe?

Computadores trabalham muito bem com endereços IP, mas humanos preferem nomes.

Imagine acessar um serviço utilizando:

```text
142.250.190.14
```

em vez de:

```text
google.com
```

Além de difícil de memorizar, o endereço IP de um serviço pode mudar.

O DNS cria uma camada de abstração:

```text
Usuário
   |
   v
google.com
   |
   v
DNS
   |
   v
IP atual
   |
   v
Servidor
```

Assim, o usuário pode continuar utilizando o mesmo nome mesmo quando a infraestrutura por trás dele muda.

---

# 3. Como o DNS funciona?

Uma forma simplificada de visualizar o processo:

```text
Aplicação
    |
    v
Sistema operacional
    |
    v
Resolver DNS
    |
    v
Servidor DNS recursivo
    |
    v
Hierarquia DNS
    |
    v
Servidor autoritativo
    |
    v
Resposta
```

Por exemplo:

```text
Qual é o IP de example.com?
```

O resolver pergunta a um servidor DNS recursivo.

O servidor recursivo pode consultar a hierarquia:

```text
Root
  |
  v
.com
  |
  v
example.com
```

Até encontrar um servidor que possua a resposta autoritativa.

---

# 4. Nome de domínio

Um nome DNS pode ser formado por várias partes.

Exemplo:

```text
www.example.com
```

Podemos separar:

```text
www
 |
 +--- host/subdomínio

example
 |
 +--- domínio

com
 |
 +--- domínio de topo
```

Outro exemplo:

```text
api.dev.example.com
```

Temos:

```text
api
dev
example
com
```

Cada parte é chamada de **label**.

---

# 5. Estrutura hierárquica do DNS

O DNS possui uma estrutura em árvore.

No topo existe a raiz:

```text
.
```

Depois temos os chamados TLDs:

```text
.com
.org
.net
.br
.dev
```

Depois vêm os domínios:

```text
example.com
empresa.com.br
```

E depois os subdomínios:

```text
www.example.com
api.example.com
mail.example.com
```

Visualmente:

```text
.
├── com
│   └── example
│       ├── www
│       ├── api
│       └── mail
│
└── br
    └── empresa
        └── www
```

---

# 6. A hierarquia na prática

Considere:

```text
www.example.com.
```

O ponto final representa a raiz:

```text
.
```

A estrutura é lida da direita para a esquerda:

```text
.
└── com
    └── example
        └── www
```

Portanto:

```text
.
 |
 +-- com
       |
       +-- example
                |
                +-- www
```

O nome completo é chamado de:

```text
FQDN
```

ou:

```text
Fully Qualified Domain Name
```

Exemplo:

```text
www.example.com.
```

O último ponto pode ser omitido em muitos contextos:

```text
www.example.com
```

---

# 7. Servidores DNS

Existem diferentes tipos de servidores envolvidos na resolução de nomes.

Os principais conceitos são:

```text
Stub resolver
Recursive resolver
Root server
TLD server
Authoritative server
```

---

# 8. Resolver DNS

O **resolver** é o componente responsável por iniciar uma consulta DNS em nome de uma aplicação ou sistema.

No Linux, aplicações normalmente não consultam diretamente toda a hierarquia DNS.

Elas entregam a consulta ao mecanismo de resolução configurado no sistema.

Fluxo simplificado:

```text
Aplicação
   |
   v
Stub resolver
   |
   v
DNS recursivo
```

---

# 9. Resolução recursiva

Na resolução recursiva, o cliente solicita ao resolver:

```text
Descubra o IP de example.com para mim.
```

O resolver assume a responsabilidade de encontrar a resposta.

Exemplo:

```text
Cliente
   |
   | "Qual IP de example.com?"
   v
Resolver DNS
   |
   | consulta servidores necessários
   v
Internet / Hierarquia DNS
   |
   v
Resposta
   |
   v
Resolver
   |
   v
Cliente
```

O cliente não precisa conhecer cada etapa da hierarquia.

---

# 10. Resolução iterativa

Em uma consulta iterativa, um servidor DNS pode responder:

```text
Eu não sei a resposta,
mas você pode perguntar para este servidor.
```

Por exemplo:

```text
Resolver
   |
   v
Root
   |
   +---- "Pergunte ao TLD .com"
                |
                v
              .com
                |
                +---- "Pergunte ao autoritativo"
                              |
                              v
                        example.com
```

Assim, cada etapa direciona a próxima.

---

# 11. Exemplo completo de resolução

Imagine que o computador execute:

```bash
curl https://www.example.com
```

Antes de estabelecer a comunicação HTTPS, é necessário descobrir o endereço IP de `www.example.com`.

Um fluxo simplificado é:

```text
1. Aplicação solicita resolução
          |
          v
2. Resolver local verifica cache
          |
          v
3. Caso necessário, consulta servidor recursivo
          |
          v
4. Resolver consulta a hierarquia DNS
          |
          v
5. Root indica servidor do TLD
          |
          v
6. TLD indica nameserver autoritativo
          |
          v
7. Autoritativo responde
          |
          v
8. Resolver retorna o resultado
          |
          v
9. Aplicação conecta ao IP
```

Visualmente:

```text
Cliente
   |
   v
DNS Resolver
   |
   v
Root
   |
   v
.com
   |
   v
Autoritativo de example.com
   |
   v
Resposta
```

---

# 12. Cache DNS

Consultar toda a hierarquia para cada requisição seria ineficiente.

Por isso, respostas DNS podem ser armazenadas em cache.

Exemplo:

```text
Cliente
   |
   v
DNS Resolver
   |
   v
Cache
```

Se a resposta estiver disponível:

```text
Cache HIT
```

O resolver pode responder imediatamente.

Caso contrário:

```text
Cache MISS
```

e será necessário consultar outros servidores.

---

# 13. TTL

TTL significa:

```text
Time To Live
```

No DNS, o TTL indica por quanto tempo uma resposta pode permanecer em cache antes de precisar ser consultada novamente.

Exemplo:

```text
example.com.  300  IN  A  93.184.216.34
```

O valor:

```text
300
```

significa:

```text
300 segundos
```

ou:

```text
5 minutos
```

Valores maiores podem reduzir consultas ao DNS.

Valores menores permitem que alterações sejam percebidas mais rapidamente.

Existe um trade-off entre:

```text
Cache eficiente
        x
Atualização rápida
```

---

# 14. Registros DNS

O DNS armazena informações em registros.

Alguns dos principais:

| Registro | Função                                |
| -------- | ------------------------------------- |
| A        | Nome → IPv4                           |
| AAAA     | Nome → IPv6                           |
| CNAME    | Alias para outro nome                 |
| MX       | Servidores de e-mail                  |
| NS       | Nameservers autoritativos             |
| TXT      | Texto e políticas                     |
| SOA      | Informações principais da zona        |
| PTR      | IP → nome                             |
| SRV      | Descoberta de serviços                |
| CAA      | Autoridades certificadoras permitidas |

---

# 15. Registro A

O registro `A` associa um nome a um endereço IPv4.

Exemplo:

```text
example.com.    IN    A    93.184.216.34
```

Significa:

```text
example.com
      |
      v
93.184.216.34
```

Consulta:

```bash
dig A example.com
```

---

# 16. Registro AAAA

O registro `AAAA` associa um nome a um endereço IPv6.

Exemplo:

```text
example.com.    IN    AAAA    2001:db8::10
```

Consulta:

```bash
dig AAAA example.com
```

Diferença:

```text
A
 |
 +-- IPv4

AAAA
 |
 +-- IPv6
```

---

# 17. Registro CNAME

CNAME significa:

```text
Canonical Name
```

Ele cria um alias para outro nome.

Exemplo:

```text
www.example.com.    IN    CNAME    example.com.
```

Podemos interpretar como:

```text
www.example.com
        |
        v
example.com
```

O CNAME aponta para outro **nome**, não diretamente para um endereço IP.

Depois da resolução do CNAME, o resolver precisa encontrar os registros aplicáveis ao nome de destino.

---

# 18. Registro MX

MX significa:

```text
Mail Exchange
```

Ele informa quais servidores recebem e-mail por um domínio.

Exemplo conceitual:

```text
example.com.    IN    MX    10    mail.example.com.
```

O número:

```text
10
```

representa a preferência/prioridade.

Quanto menor o valor, maior a preferência.

Pode existir mais de um:

```text
example.com. IN MX 10 mail1.example.com.
example.com. IN MX 20 mail2.example.com.
```

Nesse exemplo:

```text
mail1
```

tem prioridade maior.

---

# 19. Registro NS

NS significa:

```text
Name Server
```

Ele informa quais servidores DNS são autoritativos para uma zona.

Exemplo:

```text
example.com.    IN    NS    ns1.example.net.
example.com.    IN    NS    ns2.example.net.
```

Esses servidores são responsáveis por responder autoritativamente pelas informações da zona.

---

# 20. Registro TXT

O registro TXT armazena informações textuais.

É muito utilizado para:

* Verificação de domínio.
* SPF.
* DKIM.
* DMARC.
* Integrações com serviços.
* Políticas e validações.

Exemplo:

```text
example.com. IN TXT "alguma informação"
```

Uma consulta:

```bash
dig TXT example.com
```

---

# 21. Registro SOA

SOA significa:

```text
Start of Authority
```

Ele contém informações importantes sobre uma zona DNS.

Pode incluir:

* Servidor autoritativo principal.
* E-mail administrativo.
* Número de série.
* Temporizadores usados na operação da zona.

Exemplo conceitual:

```text
example.com. IN SOA ns1.example.com. admin.example.com. (
    2026091001
    3600
    600
    86400
    300
)
```

O registro SOA é importante para o funcionamento e gerenciamento de uma zona autoritativa.

---

# 22. Registro PTR

PTR é utilizado principalmente para resolução reversa.

Enquanto:

```text
A
```

faz:

```text
nome -> IPv4
```

PTR faz:

```text
IPv4 -> nome
```

Exemplo:

```text
93.184.216.34
       |
       v
example.com
```

Consulta:

```bash
dig -x 93.184.216.34
```

---

# 23. Registro SRV

SRV significa:

```text
Service
```

Ele permite descobrir onde determinado serviço está disponível.

Pode informar:

* Prioridade
* Peso
* Porta
* Host de destino

É utilizado por diversos sistemas que precisam descobrir serviços automaticamente.

Um formato típico é:

```text
_service._proto.example.com
```

Exemplo:

```text
_sip._tcp.example.com
```

---

# 24. Registro CAA

CAA significa:

```text
Certification Authority Authorization
```

É utilizado para indicar quais autoridades certificadoras podem emitir certificados para um domínio.

Exemplo conceitual:

```text
example.com. IN CAA 0 issue "ca.example"
```

Isso pode ajudar a controlar quais CAs estão autorizadas a emitir certificados para o domínio.

---

# 25. Zona DNS

Uma **zona DNS** é uma parte do namespace DNS administrada como uma unidade.

Por exemplo:

```text
example.com
```

pode possuir registros:

```text
example.com
www.example.com
api.example.com
mail.example.com
```

Visualmente:

```text
example.com
|
+-- A
+-- AAAA
+-- MX
+-- NS
+-- TXT
+-- SOA
|
+-- www
+-- api
+-- mail
```

A zona é administrada por servidores autoritativos.

---

# 26. Nameserver

Nameserver é um servidor responsável por responder consultas referentes a determinada zona.

Exemplo:

```text
example.com
       |
       +---- ns1.example.net
       |
       +---- ns2.example.net
```

É comum possuir mais de um nameserver para aumentar disponibilidade.

---

# 27. DNS autoritativo

Um servidor DNS autoritativo possui a informação oficial de uma zona.

Por exemplo:

```text
example.com
```

O servidor autoritativo possui os registros reais configurados para o domínio.

Quando responde autoritativamente:

```text
93.184.216.34
```

está afirmando:

```text
Essa é a informação que consta na zona que eu administro.
```

---

# 28. DNS recursivo

Um DNS recursivo recebe perguntas dos clientes e busca respostas em nome deles.

Fluxo:

```text
Cliente
   |
   | pergunta
   v
DNS Recursivo
   |
   | busca
   v
Root / TLD / Autoritativo
   |
   v
DNS Recursivo
   |
   v
Cliente
```

É o modelo normalmente utilizado por máquinas clientes.

---

# 29. DNS público e DNS privado

## DNS público

São servidores acessíveis publicamente na Internet.

Exemplos conhecidos incluem:

```text
Google Public DNS
Cloudflare DNS
Quad9
```

---

## DNS privado

É utilizado em redes internas.

Exemplo:

```text
servidor01.intranet.local
```

Esses nomes podem existir apenas dentro da infraestrutura interna.

Um ambiente corporativo pode ter:

```text
Clientes
   |
   v
DNS interno
   |
   +---- nomes internos
   |
   +---- consultas externas
```

O DNS interno também pode encaminhar consultas externas para outros resolvers.

---

# 30. DNS no Linux

No Linux, a configuração e o comportamento do DNS dependem da distribuição e do serviço de gerenciamento de rede.

Arquivos e ferramentas importantes incluem:

```text
/etc/hosts
/etc/resolv.conf
resolvectl
systemd-resolved
NetworkManager
dnsmasq
BIND
Unbound
```

---

# 31. `/etc/hosts`

O arquivo:

```text
/etc/hosts
```

permite associar manualmente nomes a endereços IP.

Exemplo:

```text
127.0.0.1       localhost
192.168.1.10    servidor01
192.168.1.20    banco01
```

Quando um programa tenta resolver:

```text
servidor01
```

o sistema pode consultar essa fonte antes de realizar uma consulta DNS externa, dependendo da configuração de resolução do sistema.

---

## Uso prático

Imagine um servidor de testes:

```text
192.168.1.50
```

Você pode adicionar:

```text
192.168.1.50    app.local
```

Agora:

```bash
ping app.local
```

pode resolver para:

```text
192.168.1.50
```

Isso é útil para:

* Laboratórios.
* Ambientes de desenvolvimento.
* Testes locais.
* Simulação de domínios.

---

# 32. `/etc/resolv.conf`

Esse arquivo tradicionalmente contém informações sobre quais servidores DNS utilizar.

Exemplo:

```text
nameserver 192.168.1.1
nameserver 1.1.1.1
```

O termo:

```text
nameserver
```

indica um servidor DNS que o sistema pode consultar.

Entretanto, em distribuições modernas, `/etc/resolv.conf` pode ser gerenciado automaticamente por outro serviço e até ser um link simbólico.

Por isso, editar o arquivo manualmente pode não ser uma configuração persistente.

---

# 33. `resolvectl`

Em sistemas que utilizam `systemd-resolved`, o comando:

```bash
resolvectl
```

pode ser utilizado para consultar o estado da resolução DNS.

Ver informações gerais:

```bash
resolvectl status
```

Consultar um domínio:

```bash
resolvectl query example.com
```

Isso pode revelar:

* Servidores DNS utilizados.
* Interfaces.
* Domínios de busca.
* Resultados de consultas.

---

# 34. `dig`

`dig` significa:

```text
Domain Information Groper
```

É uma das ferramentas mais importantes para diagnosticar DNS.

Consulta simples:

```bash
dig example.com
```

O resultado geralmente possui seções como:

```text
QUESTION
ANSWER
AUTHORITY
ADDITIONAL
```

---

# 35. `nslookup`

Outra ferramenta tradicional:

```bash
nslookup example.com
```

Também permite consultar tipos específicos.

Exemplo:

```bash
nslookup -type=MX example.com
```

Embora seja útil, `dig` costuma fornecer informações mais detalhadas e é muito utilizado em troubleshooting.

---

# 36. `host`

Uma alternativa simples:

```bash
host example.com
```

Exemplo:

```text
example.com has address 93.184.216.34
```

Para MX:

```bash
host -t MX example.com
```

---

# 37. Consultando registros específicos

## A

```bash
dig A example.com
```

---

## AAAA

```bash
dig AAAA example.com
```

---

## MX

```bash
dig MX example.com
```

---

## NS

```bash
dig NS example.com
```

---

## TXT

```bash
dig TXT example.com
```

---

## SOA

```bash
dig SOA example.com
```

---

## CNAME

```bash
dig CNAME www.example.com
```

---

# 38. Consulta reversa

Para descobrir um nome associado a um IP:

```bash
dig -x 8.8.8.8
```

A consulta utiliza a infraestrutura de DNS reverso.

No IPv4, consultas reversas utilizam a zona:

```text
in-addr.arpa
```

Por exemplo:

```text
8.8.8.8
```

é representado conceitualmente como:

```text
8.8.8.8.in-addr.arpa
```

com os octetos invertidos na representação reversa.

---

# 39. `dig +trace`

Uma das ferramentas mais interessantes para estudar DNS:

```bash
dig +trace example.com
```

Ele mostra, de forma iterativa, a caminhada pela hierarquia DNS.

Conceitualmente:

```text
Root
  |
  v
.com
  |
  v
example.com
```

Isso é excelente para compreender:

* Root servers.
* TLD servers.
* Delegações.
* Nameservers.
* Respostas autoritativas.

---

# 40. TCP e UDP no DNS

O DNS tradicionalmente utiliza:

```text
UDP/53
```

para muitas consultas.

Porém, DNS também pode utilizar:

```text
TCP/53
```

O TCP pode ser necessário em determinadas situações, como respostas que exigem uma conexão TCP ou transferências de zona.

Portanto:

```text
DNS ≠ somente UDP
```

É importante lembrar:

```text
UDP 53
TCP 53
```

---

# 41. DNS e portas

A porta tradicional do DNS é:

```text
53
```

Portanto:

```text
UDP/53
TCP/53
```

Exemplo de comunicação:

```text
Cliente
192.168.1.10:50000
      |
      | UDP
      v
DNS Server
192.168.1.1:53
```

---

# 42. DNSSEC

DNSSEC significa:

```text
Domain Name System Security Extensions
```

Ele adiciona mecanismos criptográficos para permitir a validação da autenticidade dos dados DNS.

O objetivo principal é ajudar a detectar respostas DNS manipuladas.

Sem validação adequada, um atacante poderia tentar fazer um cliente acreditar que:

```text
banco.example
```

aponta para um servidor malicioso.

DNSSEC permite validar criptograficamente determinadas respostas.

---

# 43. DoT e DoH

Existem mecanismos modernos para transportar consultas DNS de forma criptografada.

## DNS over TLS

Conhecido como:

```text
DoT
```

DNS over TLS utiliza TLS para proteger a comunicação DNS.

---

## DNS over HTTPS

Conhecido como:

```text
DoH
```

DNS over HTTPS transporta consultas DNS através de HTTPS.

---

## Comparação simplificada

```text
DNS tradicional
UDP/TCP 53

DoT
TLS

DoH
HTTPS
```

A criptografia do transporte ajuda a proteger a consulta contra observação ou manipulação no caminho, mas não significa que o DNS tradicional ou criptografado substitua mecanismos como DNSSEC; são problemas diferentes.

---

# 44. Problemas comuns de DNS

Quando um usuário diz:

```text
"A Internet não funciona."
```

o problema pode não estar na conexão IP.

Por exemplo:

```text
ping 8.8.8.8
```

funciona.

Mas:

```text
ping example.com
```

falha.

Isso sugere investigar DNS.

---

# Problema 1 — servidor DNS inacessível

Exemplo:

```text
nameserver 192.168.1.1
```

mas o servidor:

```text
192.168.1.1
```

não está acessível.

Teste:

```bash
ping 192.168.1.1
```

---

# Problema 2 — nome não existe

Ao consultar:

```bash
dig exemplo-inexistente.com
```

podemos receber:

```text
NXDOMAIN
```

Isso significa que o nome não existe no namespace consultado.

---

# Problema 3 — DNS lento

Pode ocorrer quando:

* O resolver está sobrecarregado.
* Existe perda de pacotes.
* O caminho até o DNS está com problemas.
* Há falhas de configuração.
* O servidor autoritativo está lento.

Pode ser investigado com:

```bash
dig example.com
```

Observando:

```text
Query time:
```

---

# Problema 4 — registro incorreto

Exemplo:

```text
example.com
```

aponta para:

```text
10.0.0.10
```

quando deveria apontar para:

```text
10.0.0.20
```

Nesse caso:

```text
DNS está funcionando.
```

O problema é que:

```text
DNS possui informação incorreta.
```

---

# Problema 5 — cache desatualizado

Imagine:

```text
IP antigo:
203.0.113.10
```

Foi alterado para:

```text
203.0.113.20
```

Se ainda existir cache válido, alguns clientes podem continuar recebendo o endereço antigo até que o TTL expire.

Isso pode causar um comportamento temporariamente inconsistente entre diferentes clientes.

---

# 45. Diagnóstico de problemas

Uma sequência útil para troubleshooting:

```text
1. Existe conectividade IP?
       |
       v
2. O servidor DNS está configurado?
       |
       v
3. O servidor DNS está acessível?
       |
       v
4. A consulta retorna resposta?
       |
       v
5. O registro está correto?
       |
       v
6. O TTL/cache está influenciando?
       |
       v
7. O problema está na aplicação?
```

---

# Diagnóstico passo a passo

## Passo 1 — verificar configuração

```bash
cat /etc/resolv.conf
```

---

## Passo 2 — verificar conectividade

```bash
ping 1.1.1.1
```

---

## Passo 3 — consultar DNS diretamente

```bash
dig example.com
```

---

## Passo 4 — consultar um servidor específico

```bash
dig @1.1.1.1 example.com
```

A sintaxe:

```text
dig @servidor nome
```

permite escolher explicitamente qual servidor DNS será consultado.

---

## Passo 5 — verificar registro específico

```bash
dig A example.com
dig AAAA example.com
dig MX example.com
dig NS example.com
dig TXT example.com
```

---

## Passo 6 — investigar a hierarquia

```bash
dig +trace example.com
```

---

## Passo 7 — verificar resolução reversa

```bash
dig -x 8.8.8.8
```

---

# 46. Exemplos práticos

## Descobrir o IPv4 de um domínio

```bash
dig A example.com
```

Fluxo:

```text
example.com
     |
     v
A
     |
     v
IPv4
```

---

## Descobrir o IPv6

```bash
dig AAAA example.com
```

---

## Descobrir servidores de e-mail

```bash
dig MX example.com
```

---

## Descobrir nameservers

```bash
dig NS example.com
```

---

## Descobrir registros TXT

```bash
dig TXT example.com
```

---

## Consultar DNS diretamente

```bash
dig @8.8.8.8 example.com
```

ou:

```bash
dig @1.1.1.1 example.com
```

---

## Consultar apenas a resposta

Uma opção bastante útil:

```bash
dig +short A example.com
```

Pode retornar algo semelhante a:

```text
93.184.216.34
```

---

## Consultar reverso

```bash
dig -x 8.8.8.8 +short
```

---

# 47. Exercícios

## Exercício 1

O que acontece quando executamos:

```bash
ping google.com
```

Pense nas seguintes etapas:

```text
google.com
    |
    v
DNS
    |
    v
IP
    |
    v
Conectividade IP
```

---

## Exercício 2

Qual registro deve ser usado para associar:

```text
www.example.com
```

a:

```text
192.168.1.10
```

Resposta:

```text
A
```

---

## Exercício 3

Qual registro deve ser usado para IPv6?

Resposta:

```text
AAAA
```

---

## Exercício 4

Qual registro informa servidores de e-mail?

Resposta:

```text
MX
```

---

## Exercício 5

Qual registro permite descobrir nameservers autoritativos?

Resposta:

```text
NS
```

---

## Exercício 6

Qual registro é utilizado para resolver:

```text
IP -> nome
```

Resposta:

```text
PTR
```

---

## Exercício 7

Execute:

```bash
dig A example.com
```

Identifique:

```text
QUESTION
ANSWER
AUTHORITY
ADDITIONAL
```

Tente entender o que cada seção representa.

---

## Exercício 8

Execute:

```bash
dig +trace example.com
```

Observe a sequência:

```text
Root
  |
TLD
  |
Autoritativo
```

---

## Exercício 9

Compare:

```bash
dig example.com
```

com:

```bash
dig @1.1.1.1 example.com
```

Perguntas:

* Qual servidor respondeu?
* A resposta é a mesma?
* Qual foi o tempo de consulta?
* O resultado veio de cache?

---

## Exercício 10

Simule um problema de DNS em laboratório.

Imagine:

```text
ping 8.8.8.8
```

funciona.

Mas:

```text
ping example.com
```

não funciona.

O que você investigaria?

Uma sequência possível:

```bash
cat /etc/resolv.conf
```

Depois:

```bash
dig example.com
```

Depois:

```bash
dig @1.1.1.1 example.com
```

---

# 48. Resumo

DNS é um sistema distribuído responsável por associar nomes a informações utilizadas na comunicação.

O exemplo mais conhecido é:

```text
Nome
  |
  v
IP
```

Mas DNS possui muito mais informações:

```text
A       -> IPv4
AAAA    -> IPv6
CNAME   -> Alias
MX      -> E-mail
NS      -> Nameserver
TXT     -> Texto / políticas
SOA     -> Autoridade da zona
PTR     -> IP -> nome
SRV     -> Serviços
CAA     -> Autoridades certificadoras
```

A arquitetura pode ser visualizada assim:

```text
                    DNS
                     |
          +----------+----------+
          |                     |
       Recursivo            Autoritativo
          |                     |
          |                     |
     Cache / busca          Zona DNS
          |
          v
       Cliente
```

Uma resolução completa pode envolver:

```text
Cliente
   |
   v
Resolver
   |
   v
Root
   |
   v
TLD
   |
   v
Authoritative
   |
   v
Resposta
```

Depois:

```text
Nome
 |
 v
DNS
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

---

# Conceitos que você deve dominar

Antes de avançar para tópicos mais complexos, certifique-se de entender:

* O que é DNS.
* Por que DNS é necessário.
* Diferença entre resolver recursivo e servidor autoritativo.
* Hierarquia Root → TLD → domínio.
* O que é uma zona.
* O que é nameserver.
* O que é cache DNS.
* O que significa TTL.
* Diferença entre A e AAAA.
* Diferença entre CNAME e A.
* Função do MX.
* Função do NS.
* Função do PTR.
* Como utilizar `dig`.
* Como utilizar `dig +trace`.
* Como especificar um DNS com `dig @servidor`.
* Como investigar problemas de resolução no Linux.

---

# Mapa mental

```text
DNS
│
├── Hierarquia
│   ├── Root
│   ├── TLD
│   ├── Domínio
│   └── Subdomínio
│
├── Servidores
│   ├── Resolver
│   ├── Recursivo
│   └── Autoritativo
│
├── Registros
│   ├── A
│   ├── AAAA
│   ├── CNAME
│   ├── MX
│   ├── NS
│   ├── TXT
│   ├── SOA
│   ├── PTR
│   ├── SRV
│   └── CAA
│
├── Cache
│   └── TTL
│
├── Linux
│   ├── /etc/hosts
│   ├── /etc/resolv.conf
│   ├── resolvectl
│   ├── dig
│   ├── host
│   └── nslookup
│
└── Segurança
    ├── DNSSEC
    ├── DoT
    └── DoH
```

> **Regra prática:** quando um domínio não funciona, não conclua imediatamente que "a Internet caiu". Primeiro descubra se o problema está na resolução DNS, na conectividade IP, na rota, na porta ou no serviço que está sendo acessado.

---

# Próximo passo

Depois de estudar DNS, o próximo arquivo recomendado é:

```text
Protocolos.md
```

Nele, vale aprofundar principalmente:

```text
TCP
UDP
ICMP
ARP
```

e entender como esses protocolos realmente aparecem nos pacotes de rede.
