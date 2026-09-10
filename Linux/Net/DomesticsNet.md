# Construindo uma Rede Doméstica

> Este documento apresenta os conceitos, componentes e etapas necessárias para planejar, construir e evoluir uma rede doméstica. O objetivo é conectar os conhecimentos de redes, endereçamento IP, DNS, protocolos, firewall e ferramentas de diagnóstico em um ambiente prático.

---

# Sumário

- [1. O que é uma rede doméstica](#1-o-que-é-uma-rede-doméstica)
- [2. Objetivos de uma rede doméstica](#2-objetivos-de-uma-rede-doméstica)
- [3. Visão geral da arquitetura](#3-visão-geral-da-arquitetura)
- [4. Componentes necessários](#4-componentes-necessários)
- [5. Internet e ISP](#5-internet-e-isp)
- [6. Modem e ONT](#6-modem-e-ont)
- [7. Roteador](#7-roteador)
- [8. NAT](#8-nat)
- [9. DHCP](#9-dhcp)
- [10. DNS](#10-dns)
- [11. Firewall](#11-firewall)
- [12. Switch](#12-switch)
- [13. Access Point](#13-access-point)
- [14. Wi-Fi](#14-wi-fi)
- [15. Dispositivos cabeados](#15-dispositivos-cabeados)
- [16. Planejamento de endereçamento IP](#16-planejamento-de-endereçamento-ip)
- [17. Reservas DHCP e IP estático](#17-reservas-dhcp-e-ip-estático)
- [18. Servidor doméstico](#18-servidor-doméstico)
- [19. NAS e armazenamento](#19-nas-e-armazenamento)
- [20. Segmentação de rede](#20-segmentação-de-rede)
- [21. VLANs](#21-vlans)
- [22. Rede para IoT](#22-rede-para-iot)
- [23. Rede de visitantes](#23-rede-de-visitantes)
- [24. Port Forwarding](#24-port-forwarding)
- [25. VPN](#25-vpn)
- [26. Segurança](#26-segurança)
- [27. Monitoramento](#27-monitoramento)
- [28. Troubleshooting](#28-troubleshooting)
- [29. Exemplo de arquitetura básica](#29-exemplo-de-arquitetura-básica)
- [30. Exemplo de arquitetura avançada](#30-exemplo-de-arquitetura-avançada)
- [31. Evoluindo a rede](#31-evoluindo-a-rede)
- [32. Laboratório doméstico](#32-laboratório-doméstico)
- [33. Exercícios](#33-exercícios)
- [34. Resumo](#34-resumo)

---

# 1. O que é uma rede doméstica

Uma rede doméstica é o conjunto de dispositivos conectados entre si dentro de uma residência.

Exemplo:

```text
Computadores
Notebooks
Celulares
Smart TVs
Videogames
Impressoras
Servidores
NAS
Dispositivos IoT
```

Esses dispositivos normalmente compartilham:

```text
Acesso à Internet
Comunicação local
Arquivos
Serviços
Impressoras
Armazenamento
```

Uma rede doméstica simples pode ser representada assim:

```text
                    INTERNET
                        |
                        v
                   [ ROTEADOR ]
                    /    |    \
                   /     |     \
                  v      v      v
                PC    Notebook  Wi-Fi
                                  |
                         +--------+--------+
                         |        |        |
                         v        v        v
                      Celular   TV       IoT
```

---

# 2. Objetivos de uma rede doméstica

Uma boa rede doméstica deve fornecer:

```text
[ ] Conectividade
[ ] Estabilidade
[ ] Segurança
[ ] Cobertura Wi-Fi
[ ] Velocidade adequada
[ ] Facilidade de administração
[ ] Possibilidade de expansão
```

Uma rede pode começar simples:

```text
Internet
   |
Roteador Wi-Fi
   |
Dispositivos
```

E evoluir para:

```text
Internet
   |
Firewall
   |
Switch
   |
+-------------------+
|        |          |
PC      NAS      Servidor
|
Access Point
```

---

# 3. Visão geral da arquitetura

Uma arquitetura doméstica completa pode seguir este modelo:

```text
                         INTERNET
                            |
                            v
                       [ ISP / ONT ]
                            |
                            v
                     [ ROUTER/FIREWALL ]
                            |
                            v
                         [ SWITCH ]
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
           PC              NAS          Servidor
                                            |
                                            v
                                      Serviços Linux

                            |
                            v

                       [ ACCESS POINT ]
                            |
                  +---------+---------+
                  |         |         |
                  v         v         v
               Celular    Notebook   IoT
```

Cada componente possui uma função diferente.

---

# 4. Componentes necessários

Uma rede doméstica pode possuir os seguintes componentes:

## Essenciais

```text
Internet
Equipamento do ISP
Roteador
Dispositivos
```

## Recomendados dependendo do tamanho da rede

```text
Switch
Access Point
Cabos Ethernet
```

## Avançados

```text
Firewall dedicado
Switch gerenciável
Servidor Linux
NAS
Access Points adicionais
UPS
```

---

# 5. Internet e ISP

O ISP é o provedor de acesso à Internet.

Exemplo:

```text
Sua casa
   |
   v
ISP
   |
   v
Internet
```

Dependendo da tecnologia utilizada, a conexão pode chegar através de:

```text
Fibra óptica
Cabo
DSL
Rede móvel
```

Em muitas conexões modernas:

```text
Internet
   |
Fibra óptica
   |
ONT
   |
Ethernet
   |
Roteador
```

---

# 6. Modem e ONT

Dependendo da tecnologia, você pode encontrar um modem ou uma ONT.

## Modem

Um modem realiza a conversão necessária entre o meio utilizado pelo provedor e a rede local.

Exemplo conceitual:

```text
ISP
 |
 v
MODEM
 |
Ethernet
 |
Roteador
```

## ONT

Em conexões de fibra:

```text
Fibra
  |
  v
ONT
  |
Ethernet
  |
Roteador
```

A ONT normalmente faz a interface entre a fibra óptica e a rede Ethernet.

---

# 7. Roteador

O roteador é um dos componentes mais importantes da rede.

Ele conecta redes diferentes.

Exemplo:

```text
Rede Local
192.168.1.0/24
       |
       v
    Roteador
       |
       v
    Internet
```

Um roteador doméstico pode fornecer:

```text
Routing
NAT
DHCP
Firewall
DNS forwarding
Wi-Fi
```

Fluxo:

```text
PC
 |
 v
Roteador
 |
 v
Internet
```

---

# 8. NAT

Dispositivos domésticos normalmente utilizam endereços IP privados.

Exemplo:

```text
192.168.1.10
192.168.1.20
192.168.1.30
```

Esses endereços não são diretamente roteáveis pela Internet pública.

O roteador utiliza NAT.

```text
PC
192.168.1.10
      |
      v
   Roteador
      |
      | NAT
      v
IP Público
      |
      v
Internet
```

Conceitualmente:

```text
192.168.1.10
      |
      +----\
192.168.1.20     NAT ---> IP Público
      +----/
192.168.1.30
```

Isso permite que vários dispositivos compartilhem uma conexão com a Internet.

---

# 9. DHCP

DHCP distribui configurações de rede automaticamente.

Normalmente:

```text
Dispositivo conecta
        |
        v
Solicita configuração
        |
        v
Servidor DHCP
        |
        v
Recebe:
IP
Máscara
Gateway
DNS
```

Exemplo:

```text
Cliente

IP:      192.168.1.100
Máscara: 255.255.255.0
Gateway: 192.168.1.1
DNS:     192.168.1.1
```

O roteador doméstico frequentemente atua como servidor DHCP.

---

# 10. DNS

DNS transforma nomes em endereços IP.

Exemplo:

```text
github.com
     |
     v
DNS
     |
     v
IP
```

Em uma rede doméstica, você pode utilizar:

```text
Roteador
   |
DNS Forwarder
   |
   +---- DNS Público
```

Ou:

```text
Dispositivo
   |
   v
Servidor DNS local
   |
   v
Internet
```

Um servidor DNS local pode ser útil para estudos e organização da rede.

Exemplo:

```text
192.168.10.10 -> servidor.lan
192.168.10.20 -> nas.lan
192.168.10.30 -> pc.lan
```

---

# 11. Firewall

O firewall controla o tráfego entre redes.

Exemplo:

```text
Internet
   |
   v
[ FIREWALL ]
   |
   v
Rede Local
```

Ele pode controlar:

```text
IPs
Portas
Protocolos
Direção do tráfego
Estado da conexão
```

Uma regra conceitual:

```text
Internet
   |
TCP 22
   |
Firewall
   |
DROP
```

Ou:

```text
LAN
   |
Internet
   |
ACCEPT
```

Uma política comum:

```text
Bloquear conexões iniciadas externamente
Permitir conexões iniciadas internamente
```

---

# 12. Switch

Um switch conecta vários dispositivos dentro da mesma rede local.

Exemplo:

```text
              Roteador
                  |
                  v
               Switch
          +-------+-------+
          |       |       |
          v       v       v
         PC      NAS   Servidor
```

O switch permite expandir a quantidade de conexões Ethernet disponíveis.

Exemplo:

```text
Switch de 5 portas
Switch de 8 portas
Switch de 16 portas
Switch de 24 portas
```

---

# 13. Access Point

Um Access Point fornece acesso sem fio à rede.

```text
Rede Ethernet
      |
      v
Access Point
      |
      v
Wi-Fi
```

Exemplo:

```text
Switch
   |
   +---- Access Point
            |
            +---- Celular
            +---- Notebook
            +---- Tablet
```

Em redes maiores, múltiplos Access Points podem melhorar a cobertura.

---

# 14. Wi-Fi

O Wi-Fi permite conectar dispositivos sem cabos.

Exemplo:

```text
               Access Point
                  )))
                )))  )))
              )))      )))
             /           \
            v             v
         Celular       Notebook
```

Ao planejar Wi-Fi, considere:

```text
Cobertura
Distância
Paredes
Interferência
Quantidade de dispositivos
Localização do Access Point
```

Uma casa maior pode precisar de:

```text
AP 1
 |
 +---- Área principal

AP 2
 |
 +---- Quartos

AP 3
 |
 +---- Área externa
```

---

# 15. Dispositivos cabeados

Dispositivos importantes podem ser conectados via Ethernet.

Exemplos:

```text
Desktop
Servidor
NAS
Console
Smart TV
Access Point
```

Arquitetura:

```text
Switch
 |
 +---- PC
 |
 +---- Servidor
 |
 +---- NAS
 |
 +---- Access Point
```

Conexões cabeadas normalmente oferecem:

```text
Estabilidade
Baixa latência
Boa velocidade
Menor interferência
```

---

# 16. Planejamento de endereçamento IP

Mesmo em uma rede doméstica, é útil planejar os endereços.

Uma estrutura simples:

```text
Rede:
192.168.1.0/24
```

Exemplo:

```text
192.168.1.1   Gateway

192.168.1.10  Servidor
192.168.1.20  NAS

192.168.1.100 - 192.168.1.200
DHCP
```

Representação:

```text
192.168.1.0/24

.1
 |
Gateway

.10 - .50
 |
Servidores

.100 - .200
 |
DHCP
```

Planejar evita conflitos e facilita a administração.

---

# 17. Reservas DHCP e IP estático

Servidores geralmente precisam manter o mesmo endereço IP.

Existem duas abordagens.

## IP estático

Configurado diretamente no dispositivo.

```text
Servidor
IP: 192.168.1.10
```

## Reserva DHCP

O servidor DHCP sempre entrega o mesmo IP para determinado dispositivo.

```text
MAC
 |
 v
DHCP
 |
 v
192.168.1.10
```

A reserva DHCP costuma facilitar o gerenciamento centralizado.

---

# 18. Servidor doméstico

Um servidor Linux pode transformar a rede doméstica em um laboratório prático.

Exemplo:

```text
Servidor Linux
     |
     +---- SSH
     |
     +---- Docker
     |
     +---- DNS
     |
     +---- Monitoramento
     |
     +---- Serviços Web
```

Arquitetura:

```text
Internet
   |
Roteador
   |
Switch
   |
Servidor Linux
```

É possível utilizar equipamentos antigos ou hardware dedicado.

---

# 19. NAS e armazenamento

Um NAS é um dispositivo voltado para armazenamento em rede.

Exemplo:

```text
PC --------\
Notebook ---\
             >---- NAS
Servidor ---/
```

Pode ser utilizado para:

```text
Arquivos
Backups
Fotos
Vídeos
Documentos
Compartilhamento
```

Uma arquitetura simples:

```text
Switch
 |
 +---- NAS
 |
 +---- PCs
```

---

# 20. Segmentação de rede

À medida que a quantidade de dispositivos aumenta, separar tudo em uma única rede pode não ser ideal.

Exemplo simples:

```text
192.168.1.0/24

PC
Servidor
NAS
TV
Celular
Câmera
IoT
```

Uma alternativa é segmentar:

```text
Usuários
Servidores
IoT
Visitantes
```

Exemplo:

```text
192.168.10.0/24
Usuários

192.168.20.0/24
Servidores

192.168.30.0/24
IoT

192.168.40.0/24
Visitantes
```

---

# 21. VLANs

VLANs permitem criar redes lógicas separadas utilizando a mesma infraestrutura física.

Exemplo:

```text
                 Switch Gerenciável
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
      VLAN 10          VLAN 20          VLAN 30
      Usuários        Servidores          IoT
```

Plano:

```text
VLAN 10
192.168.10.0/24

VLAN 20
192.168.20.0/24

VLAN 30
192.168.30.0/24
```

O roteador ou firewall controla a comunicação entre elas.

---

# 22. Rede para IoT

Dispositivos IoT incluem:

```text
Câmeras
Lâmpadas
Tomadas
Assistentes virtuais
Sensores
Smart TVs
```

Uma estratégia de segurança é colocá-los em uma rede separada.

```text
Internet
   |
Firewall
   |
   +---- VLAN Usuários
   |
   +---- VLAN Servidores
   |
   +---- VLAN IoT
```

Exemplo de política:

```text
IoT
 |
 +---- Internet: permitido
 |
 +---- PCs: bloqueado
 |
 +---- Servidores: bloqueado
```

Isso reduz a exposição caso um dispositivo IoT seja comprometido.

---

# 23. Rede de visitantes

Visitantes podem utilizar uma rede separada.

```text
Wi-Fi Principal
 |
 +---- Seus dispositivos

Wi-Fi Visitantes
 |
 +---- Dispositivos externos
```

Uma política comum:

```text
Visitantes
    |
Internet
    |
Permitido

Visitantes
    |
Rede interna
    |
Bloqueado
```

---

# 24. Port Forwarding

Port forwarding permite encaminhar conexões externas para um dispositivo interno.

Exemplo:

```text
Internet
   |
IP Público
Porta 443
   |
Roteador
   |
Port Forward
   |
Servidor
192.168.20.10
Porta 443
```

Fluxo:

```text
Cliente
   |
   | IP_PUBLICO:443
   v
Firewall/Roteador
   |
   | 192.168.20.10:443
   v
Servidor
```

Isso deve ser utilizado com cuidado.

Antes de expor um serviço:

```text
[ ] O serviço precisa realmente ser público?
[ ] Existe autenticação?
[ ] O software está atualizado?
[ ] O firewall está configurado?
[ ] Existe uma alternativa como VPN?
```

---

# 25. VPN

Uma VPN permite acesso remoto seguro à rede.

Exemplo:

```text
Notebook remoto
       |
       | Internet
       |
       v
     VPN
       |
       v
Rede Doméstica
       |
       +---- NAS
       +---- Servidor
       +---- Outros serviços
```

Uma alternativa conceitual:

```text
Sem VPN:

Internet
   |
   v
Serviço exposto

Com VPN:

Internet
   |
   v
VPN
   |
   v
Rede privada
```

Para administração remota, uma VPN pode reduzir a necessidade de expor vários serviços diretamente.

---

# 26. Segurança

Uma rede doméstica também precisa de segurança.

Checklist:

```text
[ ] Senha forte no roteador
[ ] Interface administrativa protegida
[ ] Firmware atualizado
[ ] Wi-Fi protegido
[ ] Serviços desnecessários desativados
[ ] Firewall ativo
[ ] IoT separado
[ ] Rede de visitantes separada
[ ] Backups configurados
[ ] Acesso remoto protegido
```

Uma arquitetura recomendada:

```text
                     INTERNET
                         |
                         v
                    FIREWALL
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Usuários       Servidores        IoT
```

---

# 27. Monitoramento

À medida que a rede cresce, monitoramento se torna útil.

É possível acompanhar:

```text
Uso de banda
Latência
Disponibilidade
CPU
Memória
Espaço em disco
Serviços
```

Exemplo:

```text
Internet
   |
Monitoramento
   |
   +---- Roteador
   +---- Servidor
   +---- NAS
   +---- Serviços
```

Ferramentas de diagnóstico também são fundamentais:

```text
ping
ip
ss
tcpdump
dig
traceroute
```

---

# 28. Troubleshooting

Uma estratégia útil é investigar por camadas.

## Interface

```bash
ip link
```

Pergunta:

```text
A interface está ativa?
```

---

## Endereço IP

```bash
ip addr
```

Pergunta:

```text
O dispositivo possui um IP válido?
```

---

## Gateway

```bash
ip route
```

Teste:

```bash
ping GATEWAY
```

---

## Internet

Teste um IP externo:

```bash
ping 8.8.8.8
```

---

## DNS

```bash
dig example.com
```

---

## Porta

```bash
nc -vz HOST PORTA
```

---

## Serviço

```bash
ss -tlnp
```

---

## Firewall

```bash
sudo nft list ruleset
```

Ou:

```bash
sudo iptables -L -v -n
```

---

## Captura de pacotes

```bash
sudo tcpdump -i any host IP
```

Fluxo de diagnóstico:

```text
Interface
   |
   v
IP
   |
   v
Gateway
   |
   v
Rota
   |
   v
Internet
   |
   v
DNS
   |
   v
Porta
   |
   v
Serviço
   |
   v
Firewall
   |
   v
Pacotes
```

---

# 29. Exemplo de arquitetura básica

Uma rede doméstica simples:

```text
                       INTERNET
                           |
                           v
                        [ ISP ]
                           |
                           v
                    [ ROTEADOR ]
                      /       \
                     /         \
                    v           v
                   PC          Wi-Fi
                                |
                    +-----------+-----------+
                    |           |           |
                    v           v           v
                 Celular     Notebook       TV
```

Componentes:

```text
1. Internet
2. Equipamento do ISP
3. Roteador Wi-Fi
4. Dispositivos
```

---

# 30. Exemplo de arquitetura avançada

Uma rede voltada para estudos:

```text
                            INTERNET
                                |
                                v
                             ISP / ONT
                                |
                                v
                       [ ROUTER / FIREWALL ]
                                |
                                v
                       [ SWITCH GERENCIÁVEL ]
                                |
         +----------------------+----------------------+
         |                      |                      |
         v                      v                      v
      VLAN 10                VLAN 20                VLAN 30
     USUÁRIOS              SERVIDORES                 IoT
         |                      |                      |
         |                 +----+----+                 |
         |                 |         |                 |
         v                 v         v                 v
        PCs              Linux       NAS             Smart Devices
                          Server
                             |
                             +---- SSH
                             +---- Docker
                             +---- DNS
                             +---- Monitoramento

                                |
                                v

                         [ ACCESS POINT ]
                                |
                       Wi-Fi / Visitantes
```

---

# 31. Evoluindo a rede

Uma boa estratégia é evoluir gradualmente.

## Nível 1

```text
Internet
   |
Roteador Wi-Fi
   |
Dispositivos
```

---

## Nível 2

Adicionar:

```text
Switch
Dispositivos cabeados
```

```text
Roteador
   |
Switch
 |
 +---- PC
 +---- Servidor
```

---

## Nível 3

Adicionar servidor Linux:

```text
Roteador
   |
Switch
 |
 +---- PC
 |
 +---- Linux Server
```

Estudar:

```text
SSH
DNS
Docker
Firewall
```

---

## Nível 4

Adicionar NAS:

```text
Switch
 |
 +---- PC
 +---- Server
 +---- NAS
```

---

## Nível 5

Adicionar switch gerenciável e VLANs:

```text
Firewall
   |
Managed Switch
   |
   +---- VLAN Usuários
   |
   +---- VLAN Servidores
   |
   +---- VLAN IoT
```

---

# 32. Laboratório doméstico

Uma rede doméstica pode funcionar como laboratório.

Exemplo:

```text
                   [ FIREWALL ]
                         |
                    [ SWITCH ]
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       CLIENTE        SERVER 1       SERVER 2
                       Linux          Linux
```

Experimentos possíveis:

```text
[ ] Criar sub-redes
[ ] Configurar DHCP
[ ] Configurar DNS
[ ] Criar regras de firewall
[ ] Capturar pacotes
[ ] Criar VLANs
[ ] Testar SSH
[ ] Criar VPN
[ ] Configurar NAT
[ ] Criar serviços Docker
[ ] Monitorar tráfego
```

---

# 33. Exercícios

## Exercício 1 — Mapear sua rede

Faça um diagrama:

```text
Internet
   |
ISP
   |
Roteador
   |
+--+--+
|     |
PC   Wi-Fi
```

Adicione todos os seus dispositivos.

---

## Exercício 2 — Descobrir o gateway

Execute:

```bash
ip route
```

Identifique:

```text
Gateway padrão
```

---

## Exercício 3 — Identificar seu IP

Execute:

```bash
ip addr
```

Identifique:

```text
IPv4
Prefixo
Interface
```

---

## Exercício 4 — Identificar dispositivos

Observe quais dispositivos estão conectados à sua rede.

Tente identificar:

```text
PC
Celular
Roteador
TV
Impressora
Outros dispositivos
```

---

## Exercício 5 — Planejar uma rede

Crie um plano:

```text
192.168.10.0/24
Usuários

192.168.20.0/24
Servidores

192.168.30.0/24
IoT
```

---

## Exercício 6 — Criar um servidor

Configure um computador ou máquina virtual com Linux.

Atribua:

```text
Hostname
IP
Gateway
DNS
```

Teste:

```bash
ping
ssh
dig
ss
```

---

## Exercício 7 — Criar regras de firewall

Defina conceitualmente:

```text
Usuários -> Internet
Permitido

Internet -> Servidores
Bloqueado

Usuários -> Servidores
Permitido apenas em portas específicas
```

---

## Exercício 8 — Troubleshooting

Desconecte temporariamente uma configuração em um ambiente de laboratório e tente diagnosticar o problema.

Use:

```bash
ip addr
ip route
ping
dig
ss
tcpdump
```

---

# 34. Resumo

Uma rede doméstica pode começar simples:

```text
Internet
   |
Roteador
   |
Dispositivos
```

E evoluir para:

```text
Internet
   |
ISP / ONT
   |
Firewall
   |
Switch
   |
+--------+---------+---------+
|        |         |         |
PC      NAS      Server     AP
```

Com segmentação:

```text
Internet
   |
Firewall
   |
Managed Switch
   |
+----------+----------+----------+
|          |          |          |
Usuários  Servidores    IoT
VLAN 10   VLAN 20      VLAN 30
```

Os principais componentes são:

```text
Internet
ISP / ONT
Roteador
Firewall
Switch
Access Point
Cabos Ethernet
Dispositivos
```

Componentes adicionais para um laboratório:

```text
Servidor Linux
NAS
Switch gerenciável
VLANs
VPN
Monitoramento
UPS
```

A evolução ideal é:

```text
REDE SIMPLES
     |
     v
DISPOSITIVOS CABEADOS
     |
     v
SERVIDOR LINUX
     |
     v
SERVIÇOS INTERNOS
     |
     v
FIREWALL
     |
     v
VLANs
     |
     v
SEGMENTAÇÃO
     |
     v
MONITORAMENTO
```

> Uma rede doméstica é um excelente laboratório para estudar redes na prática. Ela permite aplicar conceitos de endereçamento IP, roteamento, DNS, DHCP, NAT, firewall, protocolos, SSH e análise de pacotes em um ambiente real e controlado.