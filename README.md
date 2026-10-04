# Cyber Sec Journey

> Anotações, writeups de labs, guias e automações de estudo sobre Linux, redes e segurança cibernética.

Este repositório registra uma jornada prática de aprendizado: dos fundamentos de Linux e redes à metodologia de pentest, segurança de aplicações web e uso responsável de ferramentas do Kali Linux. Além das anotações de consulta, ele reúne **writeups de labs resolvidos** na PortSwigger Web Security Academy, **guias de redes com olhar de segurança** (Red Team e Blue Team) e **scripts de automação** que organizam a saída de ferramentas consagradas em relatórios.

O conteúdo é voltado a estudo contínuo e consulta. Não substitui treinamento formal, documentação oficial ou uma avaliação profissional.

## Uso responsável

Ferramentas e técnicas de segurança devem ser utilizadas **somente** em laboratórios próprios, CTFs, plataformas de treino ou ambientes para os quais exista autorização explícita e por escrito. Não execute reconhecimento, varreduras, captura de tráfego, testes de senha ou exploração contra sistemas, redes ou pessoas sem permissão.

Os writeups de labs foram feitos exclusivamente em ambientes de treino criados para esse fim (Web Security Academy).

## O que você encontra aqui

| Área | Conteúdo |
| --- | --- |
| Linux e Bash | Terminal, shell, comandos, scripts e fundamentos do sistema |
| Redes | TCP/IP, endereçamento, DNS, protocolos, firewall, SSH e diagnóstico |
| Redes com visão de segurança | Guias didáticos sobre broadcast, DHCP, TCP x UDP, roteamento, NAT, MAC x IP e utilitários de teste, sempre com riscos, detecção e defesa |
| Kali Linux | Guias de ferramentas para reconhecimento, OSINT, análise de firmware, credenciais, exploração, pós-exploração e SQLi |
| Metodologia | Tipos, níveis e equipes de pentest; OSSTMM, MITRE ATT&CK, regras de engajamento e compliance |
| Segurança de aplicações | Footprinting, scanning, exploração, SQL Injection e Google Hacking |
| Labs (writeups) | 21 labs da Web Security Academy: SQLi, XSS, CSRF, Clickjacking, SSRF, CORS, XXE e OS Command Injection |
| Burp Suite | Guias de uso do Proxy, Repeater e Intruder aplicados aos labs |
| Python para segurança | Cheat sheet de Python aplicado a automação e scripting de segurança |
| Automação de estudo | Orquestradores de recon, OSINT, varredura de vulnerabilidades e análise de tráfego |

## Comece por aqui

Uma trilha sugerida para quem está iniciando:

1. **Fundamentos:** [Linux](Linux/Fundaments.md), [terminal](Linux/TheTerminal.md) e [redes TCP/IP](Linux/Net/Fundaments.md).
2. **Redes com visão de segurança:** [MAC x IP](Linux/CyberSecVisionOnNet/MACxIP.md), [broadcasts e roteadores](Linux/CyberSecVisionOnNet/BroadcastingAndRouters.md), [DHCP](Linux/CyberSecVisionOnNet/DHCP.md), [TCP x UDP](Linux/CyberSecVisionOnNet/TCPxUDP.md), [roteamento](Linux/CyberSecVisionOnNet/RoutersWebs.md), [NAT](Linux/CyberSecVisionOnNet/NAT.md) e [utilitários de teste](Linux/CyberSecVisionOnNet/Utilitarios.md).
3. **Administração e rede:** [endereçamento](Linux/Net/Adressing.md), [protocolos](Linux/Net/Protocols.md), [DNS](Linux/Net/DNS.md), [firewall](Linux/Net/Firewall.md) e [SSH](Linux/Net/SSH.md).
4. **Metodologia e escopo:** [tipos de pentest](Cybersecurity/PentestingChore/Types.md), [níveis](Cybersecurity/PentestingChore/Levels.md), [equipes](Cybersecurity/PentestingChore/Teams.md) e [OSSTMM 3](Cybersecurity/OSSTMM3.md).
5. **Segurança web na prática:** [guia do Burp Suite para XSS e SQLi](Labs/BurpSuiteHowTo/XSS-SQLInjection.md) e, em seguida, os [writeups de labs](Labs/README.md).
6. **Segurança ofensiva em ambiente autorizado:** [footprinting](Cybersecurity/Footprinting.md), [scanning](Cybersecurity/Scanning.md), [Nmap](KaliLinux/NetAndReaching/Nmap.md) e [Metasploit](KaliLinux/Exploitation/Metasploit.md).
7. **Automação com Python:** [cheat sheet de Python para segurança](Scripts/python_sec_basics.md) antes de mergulhar nos orquestradores.

## Mapa do repositório

```text
cyber-sec-journey/
├── Linux/
│   ├── Fundaments.md, TheTerminal.md   # Sistema e terminal
│   ├── Bash/                           # Conceitos de Bash e comandos
│   ├── Net/                            # Fundamentos de redes, DNS, firewall, SSH
│   └── CyberSecVisionOnNet/            # Guias de redes com olhar de segurança
├── KaliLinux/                          # Fundamentos e guias de ferramentas
├── Cybersecurity/                      # Metodologia, vulnerabilidades e compliance
├── Labs/
│   ├── SQLinjection/                   # Error-based e blind SQLi
│   ├── XSS/                            # Reflected, stored e DOM-based XSS
│   ├── CSRF-Clickjacking-SSRF/         # CSRF, clickjacking e SSRF
│   ├── CORS-XXE-OSCommand/             # CORS, XXE e OS command injection
│   └── BurpSuiteHowTo/                 # Guias de uso do Burp Suite
├── Scripts/
│   ├── python_sec_basics.md            # Cheat sheet de Python para segurança
│   ├── recon-orchestrator/             # Nmap + Gobuster → relatórios HTML/JSON/CSV
│   ├── recon-ng-automation-kit/        # recon-ng → relatório HTML a partir do SQLite
│   ├── spiderfoot-automation-kit/      # SpiderFoot (OSINT) → relatório HTML a partir do CSV
│   ├── vulnscan-orchestrator/          # OWASP ZAP + Nessus opcional → relatórios
│   ├── full-recon-pipeline/            # subfinder → httpx → nuclei → relatório HTML
│   └── traffic-orchestrator/           # Captura (dumpcap/tcpdump) + análise com tshark
└── README.md
```

### Linux, Bash e redes

- [Fundamentos de Linux](Linux/Fundaments.md) e [arquitetura do terminal](Linux/TheTerminal.md)
- [Conceitos de Bash aplicados a pentest](Linux/Bash/BasicsConceptsBashPentesting.md) e [comandos internos e externos](Linux/Bash/ComandsInternsExterns.md)
- [Fundamentos de rede](Linux/Net/Fundaments.md), [endereçamento IP e CIDR](Linux/Net/Adressing.md), [protocolos](Linux/Net/Protocols.md) e [transmissão IPv4](Linux/Net/IPV4Transmission.md)
- [DNS](Linux/Net/DNS.md), [ferramentas de diagnóstico](Linux/Net/NetTools.md), [firewall](Linux/Net/Firewall.md), [SSH](Linux/Net/SSH.md) e [rede doméstica](Linux/Net/DomesticsNet.md)

### Redes com visão de Cybersecurity

Série de guias didáticos que explicam cada conceito de rede e, em seguida, o que ele significa para segurança: riscos (em nível conceitual), detecção, defesas, evidências para SOC, comparação Red Team x Blue Team, comandos e exercícios de lab.

| Guia | Temas principais |
| --- | --- |
| [MAC x IP](Linux/CyberSecVisionOnNet/MACxIP.md) | Estrutura do MAC e OUI, MAC aleatório, IPv4, sub-redes, IPv6, identidade de dispositivo, Port Security e 802.1X |
| [Broadcasts e Roteadores](Linux/CyberSecVisionOnNet/BroadcastingAndRouters.md) | Domínios de broadcast, segmentação, protocolos baseados em broadcast e hardening de roteadores |
| [DHCP](Linux/CyberSecVisionOnNet/DHCP.md) | Processo DORA, leases, relay, DHCPv6, servidor DHCP não autorizado, DHCP Snooping e logs como evidência |
| [TCP x UDP](Linux/CyberSecVisionOnNet/TCPxUDP.md) | Handshake, estados, flags, QUIC, SYN flood, amplificação, firewall stateful e detecção de C2 |
| [Roteamento entre redes](Linux/CyberSecVisionOnNet/RoutersWebs.md) | Tabela de roteamento, OSPF/BGP, roteamento entre VLANs, movimentação lateral e sequestro de rotas BGP |
| [NAT](Linux/CyberSecVisionOnNet/NAT.md) | PAT, SNAT/DNAT, CGNAT, Docker e WSL2, "NAT não é firewall", UPnP e atribuição em investigações |
| [Utilitários de teste de rede](Linux/CyberSecVisionOnNet/Utilitarios.md) | ping, traceroute, dig, ss/netstat, curl, tcpdump/Wireshark e *living off the land* |
| [Docker expondo banco de dados](Linux/CyberSecVisionOnNet/DockerProblems.md) | Lab mostrando por que o `ufw` não bloqueia portas publicadas pelo Docker e como corrigir |

### Kali Linux e ferramentas

- [Fundamentos do Kali](KaliLinux/Basics.md)
- Reconhecimento e rede: [Nmap](KaliLinux/NetAndReaching/Nmap.md), [Legion](KaliLinux/NetAndReaching/Legion.md), [Arping](KaliLinux/NetAndReaching/Arping.md) e [Netcat](KaliLinux/NetAndReaching/Netcat.md)
- Credenciais: [Medusa](KaliLinux/Credencials/Medusa.md), [Hashcat](KaliLinux/Credencials/Hashcat.md) e [John the Ripper](KaliLinux/Credencials/John.md)
- Exploração: [Metasploit](KaliLinux/Exploitation/Metasploit.md) e [Msfvenom](KaliLinux/Exploitation/Msfvenom.md)
- Outros tópicos: [SQLMap](KaliLinux/SQLiExploration/Sqlmap.md), [Binwalk](KaliLinux/FirmwareAnalis/Binwalk.md), [Maltego](KaliLinux/OSINT/Maltego.md), [Evil-WinRM](KaliLinux/PosExploitation/Evilwinrm.md) e [SET](KaliLinux/SocialEng/Setoolkit.md)

### Metodologia, defesa e vulnerabilidades

- Processo de pentest: [tipos](Cybersecurity/PentestingChore/Types.md), [níveis](Cybersecurity/PentestingChore/Levels.md), [times](Cybersecurity/PentestingChore/Teams.md) e [certificações](Cybersecurity/PentestingChore/ValidCertifications.md)
- Referências: [OSSTMM 3](Cybersecurity/OSSTMM3.md) e [MITRE ATT&CK](Cybersecurity/MITREATT@CK.md)
- Regras e compliance: [GDPR](Cybersecurity/PentestingChore/Rules/GDPR.md), [HIPAA](Cybersecurity/PentestingChore/Rules/HIPAA.md), [PCI DSS](Cybersecurity/PentestingChore/Rules/PCIDSS.md) e [FedRAMP](Cybersecurity/PentestingChore/Rules/FEDRAMP.md)
- Fases e temas: [footprinting](Cybersecurity/Footprinting.md), [scanning](Cybersecurity/Scanning.md), [exploração](Cybersecurity/Exploitation.md), [SQL Injection](Cybersecurity/SQLi.md) e [Google Hacking](Cybersecurity/GoogleHacking.md)

## Labs: PortSwigger Web Security Academy

Writeups de labs resolvidos manualmente com o **Burp Suite Community Edition**. Cada writeup registra o processo real (tentativas, erros e correções), com prints e a explicação de **por que** cada payload funciona, e não apenas o payload.

| Writeup | Labs | Vulnerabilidades |
| --- | :---: | --- |
| [SQL Injection](Labs/SQLinjection/README.md) | 2 | Visible error-based SQLi e blind SQLi com erros condicionais (com Burp Intruder) |
| [Cross-Site Scripting](Labs/XSS/README.md) | 8 | Reflected, stored e DOM-based XSS (jQuery, `document.write`, AngularJS, `eval()`) |
| [CSRF, Clickjacking e SSRF](Labs/CSRF-Clickjacking-SSRF/README.md) | 6 | CSRF sem defesas, clickjacking (com token CSRF, formulário pré-preenchido e frame buster) e SSRF básico |
| [CORS, XXE e OS Command Injection](Labs/CORS-XXE-OSCommand/README.md) | 5 | CORS com reflexão de origem e origem `null`, XXE para leitura de arquivos e para SSRF, OS command injection |

**Guias de Burp Suite** baseados nos labs:

- [Uso do Burp Suite aplicado a XSS e SQL Injection](Labs/BurpSuiteHowTo/XSS-SQLInjection.md): configuração, fluxo Proxy → Repeater → Intruder → Decoder e o passo a passo para cada classe.
- [Uso do Burp Suite em CORS, XXE e OS Command Injection](Labs/BurpSuiteHowTo/OSCommand-XXE-CORS/README.md): como cada ferramenta foi usada para identificar e confirmar as falhas.

Mais detalhes sobre a metodologia estão no [README da pasta Labs](Labs/README.md).

## Python para segurança

- [Cheat sheet de Python para cibersegurança](Scripts/python_sec_basics.md): tipos de dados, networking (sockets), web scraping, manipulação de arquivos, criptografia, operações de sistema, bibliotecas de segurança e scripts de automação.

## Scripts de automação

Os scripts organizam a saída de ferramentas oficiais; eles não substituem a validação manual dos resultados nem concedem autorização para testar um alvo.

| Projeto | Objetivo | Saídas |
| --- | --- | --- |
| [Recon Orchestrator](Scripts/recon-orchestrator/README.md) | Executa Nmap com `vulners`, enumera serviços web com Gobuster e consolida os achados | HTML, JSON e CSV |
| [Recon-ng Automation Kit](Scripts/recon-ng-automation-kit/README.md) | Automatiza uma sessão do recon-ng (workspace, módulos OSINT) e lê o banco SQLite resultante | HTML |
| [SpiderFoot Automation Kit](Scripts/spiderfoot-automation-kit/README.md) | Roda um scan de OSINT com o SpiderFoot em modo headless e converte o CSV exportado | HTML |
| [Vulnscan Orchestrator](Scripts/vulnscan-orchestrator/README.md) | Executa OWASP ZAP em Docker; pode integrar uma instância Nessus já configurada | HTML, JSON e CSV |
| [Full Recon Pipeline](Scripts/full-recon-pipeline/README.md) | Encadeia subfinder (subdomínios) → httpx (hosts vivos) → nuclei (vulnerabilidades por templates) | HTML |
| [Traffic Orchestrator](Scripts/traffic-orchestrator/README.md) | Captura tráfego da própria interface (dumpcap/tcpdump), analisa com `tshark` e compara capturas "antes x depois" | HTML, JSON e CSV |

Leia o README de cada ferramenta antes de executar: eles descrevem requisitos, modos de operação, variáveis opcionais e limitações. Use o modo ativo do ZAP, os módulos de OSINT e a captura de tráfego apenas com autorização específica.

### Tecnologias usadas nos scripts

| Tecnologia | Onde é usada |
| --- | --- |
| **Python 3** (biblioteca padrão) | Parsers e geradores de relatório: `argparse`, `json`, `csv`, `html`, `sqlite3`, `xml.etree.ElementTree`, `collections.Counter`, `re`, `glob`, `datetime`, `subprocess` |
| **Bash** (`set -euo pipefail`) | Scripts de orquestração (`run_recon.sh`, `run_vulnscan.sh`, `recon_scan.sh`, `spiderfoot_scan.sh`, `run_capture.sh`, `full_recon_pipeline.sh`) |
| **requests** | `nessus_trigger.py`, para consumir a API REST do Nessus/Tenable |
| **SQLite** | Leitura direta do schema do banco do recon-ng (`recon_report.py`) |
| **tshark / dumpcap / tcpdump** | Captura e extração de campos de pacotes no `traffic-orchestrator` |
| **HTML/CSS embutido** | Relatórios HTML autocontidos, sem dependências externas para visualização |
| **Go** | Instalação das ferramentas da ProjectDiscovery usadas no `full-recon-pipeline` |
| **Docker** | Execução do OWASP ZAP (`ghcr.io/zaproxy/zaproxy:stable`) no `vulnscan-orchestrator` |
| **Ferramentas integradas** | Nmap, Gobuster, OWASP ZAP, Nessus, recon-ng, SpiderFoot, subfinder, httpx, nuclei e Wireshark (CLI) |

## Status da jornada

- [x] Base de Linux, Bash e redes
- [x] Guias de redes com visão de segurança (broadcast, DHCP, TCP/UDP, roteamento, NAT, MAC x IP, utilitários)
- [x] Fundamentos e ferramentas selecionadas do Kali Linux
- [x] Metodologia de pentest, OSSTMM e MITRE ATT&CK
- [x] Reconhecimento, varredura e relatórios automatizados para ambientes autorizados
- [x] Exploração com Metasploit/Msfvenom e automação de OSINT (recon-ng, SpiderFoot)
- [x] Captura e análise de tráfego automatizada (traffic-orchestrator)
- [x] Labs documentados de vulnerabilidades web: SQLi, XSS, CSRF, Clickjacking, SSRF, CORS, XXE e OS Command Injection
- [ ] Labs de autenticação, controle de acesso, lógica de negócio e upload de arquivos
- [ ] Administração e hardening de sistemas
- [ ] Monitoramento e detecção (Blue Team) com Zabbix
- [ ] CTFs documentados

## Contribuições e fontes

Correções, referências oficiais e sugestões de melhoria são bem-vindas por meio de issue ou pull request. Sempre priorize a documentação oficial das ferramentas e execute atividades de segurança de forma ética e autorizada.

Mantido por [João Victor Paixão Zolim](https://www.linkedin.com/in/joao-victor-paixao-zolim) ([@joaovpzdev](https://github.com/joaovpzdev)).