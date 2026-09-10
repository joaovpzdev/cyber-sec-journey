# Scanning (Varredura)

## O que é

Scanning é a segunda fase de um teste de intrusão, executada logo após o footprinting. Enquanto o footprinting mapeia o alvo de forma majoritariamente passiva (domínio, subdomínios, informações públicas), o scanning parte para a interação ativa e direta com a infraestrutura já identificada, com o objetivo de descobrir hosts ativos, portas abertas, serviços em execução e possíveis vulnerabilidades.

Costuma-se dividir o scanning em três frentes complementares:

- **Network scanning**: identificar quais hosts estão ativos dentro de uma rede ou faixa de IPs.
- **Port scanning**: identificar quais portas estão abertas em cada host ativo, e portanto quais serviços podem estar expostos.
- **Vulnerability scanning**: identificar, entre os serviços encontrados, quais possuem vulnerabilidades conhecidas.

A ordem abaixo segue a lógica natural do processo: primeiro descobrir o que está vivo na rede, depois o que está aberto, em seguida o que está rodando ali, e só então buscar falhas — fechando com o mapeamento da topologia observada.

## 1. Descoberta de hosts ativos (host discovery)

```
nmap -sn 192.168.1.0/24
```

Primeiro passo do scanning: determinar quais IPs dentro de uma faixa de rede estão realmente ativos, antes de gastar tempo escaneando portas em endereços que nem respondem. A flag `-sn` faz o Nmap pular a etapa de escaneamento de portas e realizar apenas a descoberta de hosts (ping scan). Em redes locais, ferramentas como `arp-scan` também são úteis, já que operam em nível de ARP e tendem a ser mais confiáveis que ICMP quando há firewalls bloqueando ping.

## 2. Escaneamento de portas (port scanning)

```
nmap -sS alvo
nmap -sT alvo
```

Com os hosts ativos identificados, o próximo passo é descobrir quais portas TCP/UDP estão abertas em cada um. O `-sS` (SYN scan) é o método mais usado por ser mais rápido e discreto — não completa o handshake TCP — mas exige privilégios de root. O `-sT` (TCP connect scan) completa o handshake e não exige privilégios elevados, sendo uma alternativa quando o SYN scan não está disponível. Também é possível ajustar a velocidade e o comportamento da varredura com os timing templates do Nmap (`-T0` a `-T5`), equilibrando velocidade contra discrição.

## 3. Identificação de serviços e versões

```
nmap -sV alvo
```

Portas abertas por si só dizem pouco — o próximo passo é identificar qual serviço está rodando em cada porta e, quando possível, sua versão exata. Essa informação é o que permite, mais adiante, cruzar com bases de vulnerabilidades conhecidas (CVEs) associadas àquela versão específica.

## 4. Fingerprinting de sistema operacional

```
nmap -O alvo
```

Analisa características da pilha TCP/IP do host (como valores de TTL, opções do cabeçalho TCP e comportamento diante de pacotes malformados) para inferir o sistema operacional em execução. Saber o SO ajuda a direcionar quais vulnerabilidades e exploits fazem sentido investigar nas fases seguintes.

## 5. Banner grabbing

```
nc alvo porta
telnet alvo porta
```

Conexão manual e direta a um serviço específico para capturar o "banner" que ele retorna — muitas aplicações revelam nome e versão do software logo ao serem contatadas (por exemplo, um servidor SSH ou FTP que se identifica na primeira linha da conexão). É uma forma simples e direta de confirmar ou complementar o que o `-sV` do Nmap já indicou, útil especialmente quando o serviço não é reconhecido automaticamente.

## 6. Escaneamento de vulnerabilidades

```
nmap --script vuln alvo
```

Com serviços e versões já identificados, essa etapa busca vulnerabilidades conhecidas associadas a eles. O Nmap possui scripts NSE (Nmap Scripting Engine) voltados a essa finalidade, mas ferramentas dedicadas como **Nessus**, **OpenVAS** e, no caso de aplicações web, **Nikto**, costumam ter bases de vulnerabilidades mais completas e atualizadas, sendo mais indicadas para essa etapa em um teste mais aprofundado.

## 7. Mapeamento da rede (network mapping)

```
nmap --traceroute alvo
traceroute alvo
```

Etapa final do scanning: consolidar tudo o que foi levantado — hosts ativos, portas, serviços, sistema operacional — em um mapa da topologia da rede. Ferramentas como o **Zenmap** (interface gráfica do Nmap) ajudam a visualizar essa topologia automaticamente a partir dos resultados coletados. Esse mapa serve de base para planejar as próximas fases do pentest (enumeration e exploitation).

## Fluxo resumido

| Ordem | Etapa | O que identifica |
|---|---|---|
| 1 | Descoberta de hosts ativos | Quais IPs estão vivos na rede |
| 2 | Escaneamento de portas | Quais portas estão abertas |
| 3 | Identificação de serviços e versões | O que está rodando em cada porta |
| 4 | Fingerprinting de SO | Sistema operacional do host |
| 5 | Banner grabbing | Confirmação manual de serviço/versão |
| 6 | Escaneamento de vulnerabilidades | Falhas conhecidas nos serviços encontrados |
| 7 | Mapeamento da rede | Topologia consolidada do ambiente |

## Considerações éticas e legais

Diferente do footprinting, o scanning já envolve interação direta com os sistemas do alvo — portanto deve ser realizado exclusivamente contra ambientes próprios ou com autorização explícita e escopo definido (contrato de pentest). Varreduras não autorizadas contra terceiros podem configurar acesso indevido a sistema de informação, independentemente da intenção.

## Referências

- Documentação oficial do Nmap (nmap.org)
- Nmap Scripting Engine (NSE) — categoria vuln
- EC-Council CEH — metodologia de scanning
- OWASP Testing Guide — Network and Infrastructure Testing