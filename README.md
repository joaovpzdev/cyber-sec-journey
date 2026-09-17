# Cyber Sec Journey

> Anotações, referências e automações de estudo sobre Linux, redes e segurança cibernética.

Este repositório registra uma jornada prática de aprendizado: dos fundamentos de Linux e redes à metodologia de pentest, segurança de aplicações e uso responsável de ferramentas do Kali Linux. O conteúdo é voltado a consulta e estudo contínuo — não substitui treinamento formal, documentação oficial ou uma avaliação profissional.

## Uso responsável

Ferramentas e técnicas de segurança devem ser utilizadas **somente** em laboratórios próprios, CTFs ou ambientes para os quais exista autorização explícita. Não execute reconhecimento, varreduras, testes de senha ou exploração contra sistemas de terceiros sem permissão.

## O que você encontra aqui

| Área | Conteúdo |
| --- | --- |
| Linux e Bash | Terminal, shell, comandos, scripts e fundamentos do sistema |
| Redes | TCP/IP, endereçamento, DNS, protocolos, firewall, SSH e diagnóstico |
| Kali Linux | Guias de ferramentas para reconhecimento, OSINT, análise de firmware, credenciais, exploração, pós-exploração e SQLi |
| Metodologia | Tipos, níveis e equipes de pentest; OSSTMM, MITRE ATT&CK, regras de engajamento e compliance |
| Segurança de aplicações | Footprinting, scanning, exploração, SQL Injection e Google Hacking |
| Python para segurança | Cheat sheet de Python aplicado a automação e scripting de segurança |
| Automação de estudo | Orquestradores para recon (Nmap/Gobuster, recon-ng, SpiderFoot) e varredura de vulnerabilidades (OWASP ZAP/Nessus) |

## Comece por aqui

Uma trilha sugerida para quem está iniciando:

1. **Fundamentos:** [Linux](Linux/Fundaments.md), [terminal](Linux/TheTerminal.md) e [redes TCP/IP](Linux/Net/Fundaments.md).
2. **Administração e rede:** [endereçamento](Linux/Net/Adressing.md), [protocolos](Linux/Net/Protocols.md), [DNS](Linux/Net/DNS.md), [firewall](Linux/Net/Firewall.md) e [SSH](Linux/Net/SSH.md).
3. **Metodologia e escopo:** [tipos de pentest](Cybersecurity/PentestingChore/Types.md), [níveis](Cybersecurity/PentestingChore/Levels.md), [equipes](Cybersecurity/PentestingChore/Teams.md) e [OSSTMM 3](Cybersecurity/OSSTMM3.md).
4. **Segurança ofensiva em ambiente autorizado:** [footprinting](Cybersecurity/Footprinting.md), [scanning](Cybersecurity/Scanning.md), [Nmap](KaliLinux/NetAndReaching/Nmap.md) e [Metasploit](KaliLinux/Exploitation/Metasploit.md).
5. **Automação com Python:** [cheat sheet de Python para segurança](Scripts/python_sec_basics.md) antes de mergulhar nos orquestradores.

## Mapa do repositório

```text
cyber-sec-journey/
├── Linux/                              # Sistema, terminal, Bash e redes
├── KaliLinux/                          # Fundamentos e guias de ferramentas
├── Cybersecurity/                      # Metodologia, vulnerabilidades e compliance
├── Scripts/
│   ├── python_sec_basics.md            # Cheat sheet de Python para segurança
│   ├── recon-orchestrator/             # Nmap + Gobuster → relatórios HTML/JSON/CSV
│   ├── recon-ng-automation-kit/        # recon-ng → relatório HTML a partir do SQLite
│   ├── spiderfoot-automation-kit/      # SpiderFoot (OSINT) → relatório HTML a partir do CSV
│   └── vulnscan-orchestrator/          # OWASP ZAP + Nessus opcional → relatórios
└── README.md
```

### Linux, Bash e redes

- [Fundamentos de Linux](Linux/Fundaments.md) e [arquitetura do terminal](Linux/TheTerminal.md)
- [Conceitos de Bash aplicados a pentest](Linux/Bash/BasicsConceptsBashPentesting.md) e [comandos internos e externos](Linux/Bash/ComandsInternsExterns.md)
- [Fundamentos de rede](Linux/Net/Fundaments.md), [endereçamento IP e CIDR](Linux/Net/Adressing.md), [protocolos](Linux/Net/Protocols.md) e [transmissão IPv4](Linux/Net/IPV4Transmission.md)
- [DNS](Linux/Net/DNS.md), [ferramentas de diagnóstico](Linux/Net/NetTools.md), [firewall](Linux/Net/Firewall.md), [SSH](Linux/Net/SSH.md) e [rede doméstica](Linux/Net/DomesticsNet.md)

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

### Python para segurança

- [Cheat sheet de Python para cibersegurança](Scripts/python_sec_basics.md) — tipos de dados, networking (sockets), web scraping, manipulação de arquivos, criptografia, operações de sistema, bibliotecas de segurança e scripts de automação.

## Scripts de automação

Os scripts organizam a saída de ferramentas oficiais; eles não substituem a validação manual dos resultados nem concedem autorização para testar um alvo.

| Projeto | Objetivo | Saídas |
| --- | --- | --- |
| [Recon Orchestrator](Scripts/recon-orchestrator/README.md) | Executa Nmap com `vulners`, enumera serviços web com Gobuster e consolida os achados | HTML, JSON e CSV |
| [Recon-ng Automation Kit](Scripts/recon-ng-automation-kit/README.md) | Automatiza uma sessão do recon-ng (workspace, módulos OSINT) e lê o banco SQLite resultante | HTML |
| [SpiderFoot Automation Kit](Scripts/spiderfoot-automation-kit/README.md) | Roda um scan de OSINT com o SpiderFoot em modo headless e converte o CSV exportado | HTML |
| [Vulnscan Orchestrator](Scripts/vulnscan-orchestrator/README.md) | Executa OWASP ZAP em Docker; pode integrar uma instância Nessus já configurada | HTML, JSON e CSV |

Leia o README de cada ferramenta antes de executar: eles descrevem requisitos, modos de operação, variáveis opcionais e limitações. Use o modo ativo do ZAP e os módulos de OSINT apenas com autorização específica, pois podem enviar payloads de teste ou consultar dados sobre o alvo.

### Tecnologias usadas nos scripts

| Tecnologia | Onde é usada |
| --- | --- |
| **Python 3** (biblioteca padrão) | Todos os parsers/geradores de relatório: `argparse`, `json`, `csv`, `html`/`html.escape`, `sqlite3`, `xml.etree.ElementTree`, `collections.Counter`, `re`, `glob`, `datetime` |
| **Bash** (`set -euo pipefail`) | Scripts de orquestração (`run_recon.sh`, `run_vulnscan.sh`, `recon_scan.sh`, `spiderfoot_scan.sh`), incluindo automação de console interativo via *stdin* no `recon-ng` |
| **requests** (única dependência externa) | `nessus_trigger.py`, para consumir a API REST do Nessus/Tenable |
| **SQLite** | Leitura direta do schema do banco do recon-ng (`recon_report.py`) |
| **HTML/CSS embutido** | Todos os relatórios são gerados como HTML autocontido (sem dependências externas para visualização) |
| **Docker** | Execução do OWASP ZAP (`ghcr.io/zaproxy/zaproxy:stable`) no `vulnscan-orchestrator` |
| **Ferramentas integradas** | Nmap, Gobuster, OWASP ZAP, Nessus (Tenable), recon-ng e SpiderFoot |

## Status da jornada

- [x] Base de Linux, Bash e redes
- [x] Fundamentos e ferramentas selecionadas do Kali Linux
- [x] Metodologia de pentest, OSSTMM e MITRE ATT&CK
- [x] Reconhecimento, varredura e relatórios automatizados para ambientes autorizados
- [x] Exploração com Metasploit/Msfvenom e automação de OSINT (recon-ng, SpiderFoot)
- [ ] Administração e hardening de sistemas
- [ ] Vulnerabilidades web adicionais (por exemplo, XSS, CSRF e autenticação)
- [ ] Estudos de caso, labs e CTFs documentados

## Contribuições e fontes

Correções, referências oficiais e sugestões de melhoria são bem-vindas por meio de issue ou pull request. Sempre priorize a documentação oficial das ferramentas e execute atividades de segurança de forma ética e autorizada.

Mantido por [@joaovpzdev](https://github.com/joaovpzdev).