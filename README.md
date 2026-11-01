# Cyber Sec Journey

> Anotações, writeups de labs, manuais de investigação, roteiros de estudo e automações sobre Linux, redes e segurança cibernética.

Este repositório registra uma jornada prática de aprendizado: dos fundamentos de Linux e redes à defesa de redes, metodologia de pentest, segurança de aplicações web e uso responsável de ferramentas do Kali Linux. Além das anotações de consulta, ele reúne **writeups de labs** (PortSwigger Web Security Academy, OverTheWire Bandit e Blue Team), **manuais de investigação em PDF** voltados ao dia a dia de operação e suporte, **roteiros de servidores** e **scripts de automação** que organizam a saída de ferramentas consagradas em relatórios.

O conteúdo é voltado a estudo contínuo e consulta. Não substitui treinamento formal, documentação oficial ou uma avaliação profissional.

## Uso responsável

Ferramentas e técnicas de segurança devem ser utilizadas **somente** em laboratórios próprios, CTFs, plataformas de treino ou ambientes para os quais exista autorização explícita e por escrito. Não execute reconhecimento, varreduras, captura de tráfego, testes de senha ou exploração contra sistemas, redes ou pessoas sem permissão.

Os writeups foram feitos exclusivamente em ambientes de treino criados para esse fim (Web Security Academy, OverTheWire) ou em equipamentos próprios. Os writeups do Bandit seguem as regras do OverTheWire: sem senhas e sem gabarito.

## O que você encontra aqui

| Área | Conteúdo |
| --- | --- |
| Linux e Bash | Terminal, shell, comandos, scripts e fundamentos do sistema |
| Redes | TCP/IP, endereçamento, DNS, protocolos, firewall, SSH e diagnóstico |
| Redes com visão de segurança | Broadcast, DHCP, TCP x UDP, roteamento, NAT, MAC x IP e utilitários de teste, sempre com riscos, detecção e defesa |
| Manuais de investigação (PDF) | DNS, políticas SPF, entrega de e-mails, DNS/MX/SPF/DMARC/DKIM, Wireshark, firewalls, logs do Windows/AD e Proxmox Mail Gateway |
| Defesa de redes (Cisco) | Anotações do curso Network Defense: defesa em profundidade, defesa de sistemas, ACLs, 802.1X/EAP/RADIUS e rogue APs |
| Kali Linux | Guias de ferramentas para reconhecimento, OSINT, firmware, credenciais, exploração, pós-exploração, SQLi e engenharia social |
| Metodologia | Tipos, níveis e equipes de pentest; OSSTMM, MITRE ATT&CK, regras de engajamento e compliance |
| Segurança de aplicações | Footprinting, scanning, exploração, SQL Injection e Google Hacking |
| Labs Web (PortSwigger) | 21 labs: SQLi, XSS, CSRF, Clickjacking, SSRF, CORS, XXE e OS Command Injection, com guias de Burp Suite |
| Labs OverTheWire | Writeups do wargame Bandit com vulnerabilidade, mapeamento MITRE ATT&CK e visão de Blue Team |
| Labs Blue Team | Análise forense de um pendrive suspeito: USBGuard, imagem forense, Sleuth Kit, carving e análise estatística |
| Servidores (PDF) | Roteiros de Windows Server 2025 e Linux (RHEL 10 e Ubuntu 26.04), do básico ao avançado |
| Automação | Orquestradores de recon, OSINT, varredura de vulnerabilidades e análise de tráfego, além de um cheat sheet de Python |

## Comece por aqui

Uma trilha sugerida para quem está iniciando:

1. **Fundamentos:** [Linux](Linux/Fundaments.md), [terminal](Linux/TheTerminal.md) e [redes TCP/IP](Linux/Net/Fundaments.md).
2. **Redes com visão de segurança:** [MAC x IP](Linux/CyberSecVisionOnNet/MACxIP.md), [broadcasts e roteadores](Linux/CyberSecVisionOnNet/BroadcastingAndRouters.md), [DHCP](Linux/CyberSecVisionOnNet/DHCP.md), [TCP x UDP](Linux/CyberSecVisionOnNet/TCPxUDP.md), [roteamento](Linux/CyberSecVisionOnNet/RoutersWebs.md), [NAT](Linux/CyberSecVisionOnNet/NAT.md) e [utilitários de teste](Linux/CyberSecVisionOnNet/Utilitarios.md).
3. **Administração e rede:** [endereçamento](Linux/Net/Adressing.md), [protocolos](Linux/Net/Protocols.md), [DNS](Linux/Net/DNS.md), [firewall](Linux/Net/Firewall.md) e [SSH](Linux/Net/SSH.md).
4. **Defesa de redes:** [defesa em profundidade](Cybersecurity/CiscoNetworkDefense/Module01-UnderstandingDefense.md), [ACLs](Cybersecurity/CiscoNetworkDefense/Module04-AccessControlLists.md) e [802.1X/EAP](Cybersecurity/CiscoNetworkDefense/AuthenticationProtocols-EAP.md).
5. **Prática no terminal:** [writeups do OverTheWire Bandit](Labs/OverTheWireLabs/README.md).
6. **Metodologia e escopo:** [tipos de pentest](Cybersecurity/PentestingChore/Types.md), [níveis](Cybersecurity/PentestingChore/Levels.md), [equipes](Cybersecurity/PentestingChore/Teams.md) e [OSSTMM 3](Cybersecurity/OSSTMM3.md).
7. **Segurança web na prática:** [guia do Burp Suite para XSS e SQLi](Labs/PortSwiggerLabs/BurpSuiteHowTo/XSS-SQLInjection.md) e, em seguida, os [writeups da PortSwigger](Labs/PortSwiggerLabs/README.md).
8. **Segurança ofensiva em ambiente autorizado:** [footprinting](Cybersecurity/Footprinting.md), [scanning](Cybersecurity/Scanning.md), [Nmap](KaliLinux/NetAndReaching/Nmap.md) e [Metasploit](KaliLinux/Exploitation/Metasploit.md).
9. **Automação com Python:** [cheat sheet de Python para segurança](Scripts/python_sec_basics.md) antes de mergulhar nos orquestradores.

## Mapa do repositório

```text
cyber-sec-journey/
├── Linux/
│   ├── Fundaments.md, TheTerminal.md     # Sistema e terminal
│   ├── Bash/                             # Conceitos de Bash e comandos
│   ├── Net/                              # Fundamentos de redes, DNS, firewall, SSH
│   │   └── Apostila/                     # Manuais de investigação em PDF (8 documentos)
│   └── CyberSecVisionOnNet/              # Guias de redes com olhar de segurança
├── Cybersecurity/
│   ├── CiscoNetworkDefense/              # Anotações do curso Network Defense (Cisco)
│   ├── PentestingChore/                  # Tipos, níveis, times, certificações e compliance
│   └── *.md                              # OSSTMM, MITRE ATT&CK, footprinting, scanning, SQLi...
├── KaliLinux/                            # Fundamentos e guias de ferramentas
├── Servers/
│   ├── WindowsServer/                    # Roteiro Windows Server 2025 em PDF (12 documentos)
│   └── LinuxServer/                      # Roteiro RHEL 10 + Ubuntu 26.04 em PDF (13 documentos)
├── Labs/
│   ├── PortSwiggerLabs/                  # Web Security Academy
│   │   ├── XSS/                          # Reflected, stored e DOM-based XSS
│   │   │   └── SQLinjection/             # Error-based e blind SQLi
│   │   ├── CSRF-Clickjacking-SSRF/       # CSRF, clickjacking e SSRF
│   │   ├── CORS-XXE-OSCommand/           # CORS, XXE e OS command injection
│   │   └── BurpSuiteHowTo/               # Guias de uso do Burp Suite
│   ├── OverTheWireLabs/                  # Writeups do wargame Bandit
│   └── BlueTeamLabs/SuspiciousUSBDrive/  # Análise forense de pendrive suspeito
├── Scripts/
│   ├── python_sec_basics.md              # Cheat sheet de Python para segurança
│   ├── recon-orchestrator/               # Nmap + Gobuster → relatórios HTML/JSON/CSV
│   ├── recon-ng-automation-kit/          # recon-ng → relatório HTML a partir do SQLite
│   ├── spiderfoot-automation-kit/        # SpiderFoot (OSINT) → relatório HTML a partir do CSV
│   ├── vulnscan-orchestrator/            # OWASP ZAP + Nessus opcional → relatórios
│   ├── full-recon-pipeline/              # subfinder → httpx → nuclei → relatório HTML
│   └── traffic-orchestrator/             # Captura (dumpcap/tcpdump) + análise com tshark
└── README.md
```

## Linux, Bash e redes

- [Fundamentos de Linux](Linux/Fundaments.md) e [arquitetura do terminal](Linux/TheTerminal.md)
- [Conceitos de Bash aplicados a pentest](Linux/Bash/BasicsConceptsBashPentesting.md) e [comandos internos e externos](Linux/Bash/ComandsInternsExterns.md)
- [Fundamentos de rede](Linux/Net/Fundaments.md), [endereçamento IP e CIDR](Linux/Net/Adressing.md), [protocolos](Linux/Net/Protocols.md) e [transmissão IPv4](Linux/Net/IPV4Transmission.md)
- [DNS](Linux/Net/DNS.md), [ferramentas de diagnóstico](Linux/Net/NetTools.md), [firewall](Linux/Net/Firewall.md), [SSH](Linux/Net/SSH.md) e [rede doméstica](Linux/Net/DomesticsNet.md)

### Redes com visão de Cybersecurity

Guias didáticos que explicam cada conceito de rede e, em seguida, o que ele significa para segurança: riscos (em nível conceitual), detecção, defesas, evidências para SOC, comparação Red Team x Blue Team, comandos e exercícios de lab.

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

### Manuais de investigação (PDF)

Manuais práticos voltados à rotina de operação, suporte e resposta a incidentes: como investigar um problema passo a passo, quais comandos e evidências usar e como documentar o diagnóstico.

| Manual | Foco |
| --- | --- |
| [Investigação de DNS](Linux/Net/Apostila/Manual_Investigacao_DNS_Edicao2.pdf) | Resolução de nomes, registros, propagação e diagnóstico de falhas |
| [Investigação de políticas SPF](Linux/Net/Apostila/manual_investigacao_politicas_spf_rev4.pdf) | Leitura e validação de registros SPF, includes, limites de consulta e falhas de autenticação |
| [Estudo de DNS, MX, SPF, DMARC e DKIM](<Linux/Net/Apostila/Estudo_DNS_MX_SPF_DMARC_DKIM (1).pdf>) | Como os registros de e-mail se relacionam na autenticação do domínio |
| [Investigação de entrega de e-mails](Linux/Net/Apostila/Manual_Investigacao_Entrega_Emails_Edicao2.pdf) | Rastreamento de mensagens, cabeçalhos, bounces e problemas de entrega |
| [Proxmox Mail Gateway](Linux/Net/Apostila/Proxmox_Mail_Gateway_Guia_Executivo_Operacional_Edicao2.pdf) | Guia executivo e operacional do gateway de e-mail |
| [Investigação de tráfego com Wireshark](Linux/Net/Apostila/Investigacao_Trafego_Wireshark_Edicao2.pdf) | Captura, filtros e análise de tráfego como evidência |
| [Firewalls](Linux/Net/Apostila/Firewalls_Tipos_Funcionamento_Operacao_Investigacao_Edicao2.pdf) | Tipos, funcionamento, operação e investigação de regras e bloqueios |
| [Logs do Windows e Active Directory](Linux/Net/Apostila/Investigacao_Logs_Windows_Active_Directory_Edicao3.pdf) | Eventos de segurança, autenticação e auditoria no Windows e no AD |

## Defesa de redes (Cisco Network Defense)

Anotações do curso **Network Defense** da Cisco Networking Academy (em andamento), complementadas por estudos próprios sobre os temas do curso.

| Anotação | Temas |
| --- | --- |
| [Módulo 1: Entendendo a defesa](Cybersecurity/CiscoNetworkDefense/Module01-UnderstandingDefense.md) | Ativos, vulnerabilidades e ameaças, defesa em profundidade, políticas, regulamentações e padrões |
| [Módulo 2: Defesa de sistemas e redes](Cybersecurity/CiscoNetworkDefense/Module02-SystemAndNetworkDefense.md) | Segurança física, segurança de aplicações e patches, hardening de serviços e protocolos, segmentação e DMZ, alta disponibilidade, Wi-Fi, mobile, IoT e hosts |
| [Módulo 4: Listas de controle de acesso (ACLs)](Cybersecurity/CiscoNetworkDefense/Module04-AccessControlLists.md) | Wildcard masks, ACLs padrão e estendidas (numeradas e nomeadas), proteção do VTY, mitigação de ataques e ACLs IPv6 |
| [Protocolos de autenticação](Cybersecurity/CiscoNetworkDefense/AuthenticationProtocols-EAP.md) | 802.1X, EAP, RADIUS e TACACS+ |
| [Rogue access points](Cybersecurity/CiscoNetworkDefense/RogueAccessPoints.md) | Tipos de dispositivos sem fio clandestinos, casos reais (TJX, DarkVishnya, Nearest Neighbor), detecção, prevenção e resposta |

## Kali Linux e ferramentas

- [Fundamentos do Kali](KaliLinux/Basics.md)
- Reconhecimento e rede: [Nmap](KaliLinux/NetAndReaching/Nmap.md), [Legion](KaliLinux/NetAndReaching/Legion.md), [Arping](KaliLinux/NetAndReaching/Arping.md) e [Netcat](KaliLinux/NetAndReaching/Netcat.md)
- Credenciais: [Medusa](KaliLinux/Credencials/Medusa.md), [Hashcat](KaliLinux/Credencials/Hashcat.md) e [John the Ripper](KaliLinux/Credencials/John.md)
- Exploração: [Metasploit](KaliLinux/Exploitation/Metasploit.md) e [Msfvenom](KaliLinux/Exploitation/Msfvenom.md)
- Outros tópicos: [SQLMap](KaliLinux/SQLiExploration/Sqlmap.md), [Binwalk](KaliLinux/FirmwareAnalis/Binwalk.md), [Maltego](KaliLinux/OSINT/Maltego.md), [Evil-WinRM](KaliLinux/PosExploitation/Evilwinrm.md) e [SET](KaliLinux/SocialEng/Setoolkit.md)

## Metodologia, defesa e vulnerabilidades

- Processo de pentest: [tipos](Cybersecurity/PentestingChore/Types.md), [níveis](Cybersecurity/PentestingChore/Levels.md), [times](Cybersecurity/PentestingChore/Teams.md) e [certificações](Cybersecurity/PentestingChore/ValidCertifications.md)
- Referências: [OSSTMM 3](Cybersecurity/OSSTMM3.md) e [MITRE ATT&CK](Cybersecurity/MITREATT@CK.md)
- Regras e compliance: [GDPR](Cybersecurity/PentestingChore/Rules/GDPR.md), [HIPAA](Cybersecurity/PentestingChore/Rules/HIPAA.md), [PCI DSS](Cybersecurity/PentestingChore/Rules/PCIDSS.md) e [FedRAMP](Cybersecurity/PentestingChore/Rules/FEDRAMP.md)
- Fases e temas: [footprinting](Cybersecurity/Footprinting.md), [scanning](Cybersecurity/Scanning.md), [exploração](Cybersecurity/Exploitation.md), [SQL Injection](Cybersecurity/SQLi.md) e [Google Hacking](Cybersecurity/GoogleHacking.md)

## Servidores: roteiros de Windows Server e Linux

Dois roteiros de estudo em PDF, com um documento técnico por módulo (conceitos, comandos, laboratórios, checklist e referências oficiais). Veja o [índice completo dos módulos](Servers/README.md).

| Roteiro | Módulos | Certificações relacionadas | Comece por |
| --- | --- | --- | --- |
| Windows Server 2025 | 11 módulos: AD DS, Group Policy, DNS/DHCP, armazenamento, Hyper-V, hardening, cluster e backup, monitoramento, Azure híbrido | AZ-802 | [Roteiro geral](Servers/WindowsServer/00-Roteiro-Geral-Windows-Server.pdf) |
| Linux (RHEL 10 e Ubuntu 26.04) | 12 módulos: shell, permissões, systemd, pacotes, LVM, rede e SSH, serviços, SELinux/AppArmor, KVM e Podman, troubleshooting e backup, Ansible e integração com AD | RHCSA, LFCS | [Roteiro geral](Servers/LinuxServer/00-Roteiro-Geral-Linux-Server.pdf) |

## Labs: PortSwigger Web Security Academy

Writeups de labs resolvidos manualmente com o **Burp Suite Community Edition**. Cada writeup registra o processo real (tentativas, erros e correções), com prints e a explicação de **por que** cada payload funciona, e não apenas o payload.

| Writeup | Labs | Vulnerabilidades |
| --- | :---: | --- |
| [SQL Injection](Labs/PortSwiggerLabs/XSS/SQLinjection/README.md) | 2 | Visible error-based SQLi e blind SQLi com erros condicionais (com Burp Intruder) |
| [Cross-Site Scripting](Labs/PortSwiggerLabs/XSS/README.md) | 8 | Reflected, stored e DOM-based XSS (jQuery, `document.write`, AngularJS, `eval()`) |
| [CSRF, Clickjacking e SSRF](Labs/PortSwiggerLabs/CSRF-Clickjacking-SSRF/README.md) | 6 | CSRF sem defesas, clickjacking (com token CSRF, formulário pré-preenchido e frame buster) e SSRF básico |
| [CORS, XXE e OS Command Injection](Labs/PortSwiggerLabs/CORS-XXE-OSCommand/README.md) | 5 | CORS com reflexão de origem e origem `null`, XXE para leitura de arquivos e para SSRF, OS command injection |

**Guias de Burp Suite** baseados nos labs:

- [Uso do Burp Suite aplicado a XSS e SQL Injection](Labs/PortSwiggerLabs/BurpSuiteHowTo/XSS-SQLInjection.md): configuração, fluxo Proxy → Repeater → Intruder → Decoder e o passo a passo para cada classe.
- [Uso do Burp Suite em CORS, XXE e OS Command Injection](Labs/PortSwiggerLabs/BurpSuiteHowTo/OSCommand-XXE-CORS/README.md): como cada ferramenta foi usada para identificar e confirmar as falhas.

Mais detalhes sobre a metodologia estão no [README dos labs da PortSwigger](Labs/PortSwiggerLabs/README.md).

## Labs: OverTheWire Bandit

Writeups do wargame [Bandit](https://overthewire.org/wargames/bandit/) focados em conceitos de Red Team. Cada nível documenta objetivo, conceitos, abordagem, a vulnerabilidade, onde ela aparece no mundo real e como corrigir ou detectar (visão Blue Team), **sem senhas e sem gabarito**.

| Writeup | Tema | Vulnerabilidade / técnica | MITRE ATT&CK |
| --- | --- | --- | --- |
| [Bandit 13 → 14](Labs/OverTheWireLabs/Bandit13.md) | Chave SSH privada exposta | Credencial em arquivo legível | T1552.004 |
| [Bandit 14 → 15](Labs/OverTheWireLabs/Bandit14.md) | Serviço em porta TCP | Comunicação em texto puro | — |
| [Bandit 15 → 16](Labs/OverTheWireLabs/Bandit15.md) | Serviço com SSL/TLS | Certificado autoassinado | — |
| [Troubleshooting SSH](Labs/OverTheWireLabs/TroubleshootingSSH.md) | Conexão SSH fechada | Diagnóstico de rate limiting | — |

Os demais níveis planejados estão no [índice do Bandit](Labs/OverTheWireLabs/README.md).

## Labs: Blue Team

Análises defensivas feitas em ambiente próprio, documentadas com o processo real, as evidências (prints com dados sensíveis ocultados) e o raciocínio por trás de cada conclusão.

| Writeup | Tema | Técnicas e ferramentas |
| --- | --- | --- |
| [Análise forense de um pendrive suspeito](Labs/BlueTeamLabs/SuspiciousUSBDrive/README.md) | Mídia removível não confiável (BadUSB, malware, área oculta, capacidade falsa) | USBGuard, `dmesg`/`udev`, bloqueio de escrita, `dd` + SHA-256, Sleuth Kit, binwalk, PhotoRec, entropia, ClamAV, f3 e MITRE ATT&CK (T1200, T1091) |

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
- [x] Manuais de investigação: DNS, SPF, entrega de e-mails, Wireshark, firewalls, logs do Windows/AD e Proxmox Mail Gateway
- [ ] Curso Cisco Network Defense (módulos 1, 2 e 4 documentados; demais em andamento)
- [x] Fundamentos e ferramentas selecionadas do Kali Linux
- [x] Metodologia de pentest, OSSTMM e MITRE ATT&CK
- [x] Reconhecimento, varredura e relatórios automatizados para ambientes autorizados
- [x] Exploração com Metasploit/Msfvenom e automação de OSINT (recon-ng, SpiderFoot)
- [x] Captura e análise de tráfego automatizada (traffic-orchestrator)
- [x] Labs documentados de vulnerabilidades web: SQLi, XSS, CSRF, Clickjacking, SSRF, CORS, XXE e OS Command Injection
- [ ] Labs de autenticação, controle de acesso, lógica de negócio e upload de arquivos
- [ ] OverTheWire Bandit (níveis 13 a 16 documentados; 16 a 22 em andamento)
- [x] Roteiros de estudo de servidores Windows Server e Linux (RHEL e Ubuntu)
- [ ] Administração e hardening de sistemas (laboratórios dos roteiros em andamento)
- [x] Lab Blue Team: análise forense de mídia removível suspeita
- [ ] Monitoramento e detecção (Blue Team) com Zabbix
- [ ] CTFs documentados

## Contribuições e fontes

Correções, referências oficiais e sugestões de melhoria são bem-vindas por meio de issue ou pull request. Sempre priorize a documentação oficial das ferramentas e execute atividades de segurança de forma ética e autorizada.

Mantido por [João Victor Paixão Zolim](https://www.linkedin.com/in/joao-victor-paixao-zolim) ([@joaovpzdev](https://github.com/joaovpzdev)).