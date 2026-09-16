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
| Kali Linux | Guias de ferramentas para reconhecimento, OSINT, análise de firmware, credenciais, SQLi e pós-exploração |
| Metodologia | Tipos, níveis e equipes de pentest; OSSTMM, MITRE ATT&CK, regras de engajamento e compliance |
| Segurança de aplicações | Footprinting, scanning, exploração, SQL Injection e Google Hacking |
| Automação de estudo | Orquestradores para recon com Nmap/Gobuster e varredura com OWASP ZAP/Nessus |

## Comece por aqui

Uma trilha sugerida para quem está iniciando:

1. **Fundamentos:** [Linux](Linux/Fundaments.md), [terminal](Linux/TheTerminal.md) e [redes TCP/IP](Linux/Net/Fundaments.md).
2. **Administração e rede:** [endereçamento](Linux/Net/Adressing.md), [protocolos](Linux/Net/Protocols.md), [DNS](Linux/Net/DNS.md), [firewall](Linux/Net/Firewall.md) e [SSH](Linux/Net/SSH.md).
3. **Metodologia e escopo:** [tipos de pentest](Cybersecurity/PentestingChore/Types.md), [níveis](Cybersecurity/PentestingChore/Levels.md), [equipes](Cybersecurity/PentestingChore/Teams.md) e [OSSTMM 3](Cybersecurity/OSSTMM3.md).
4. **Segurança ofensiva em ambiente autorizado:** [footprinting](Cybersecurity/Footprinting.md), [scanning](Cybersecurity/Scanning.md), [Nmap](KaliLinux/NetAndReaching/Nmap.md) e [OWASP ZAP](Scripts/vulnscan-orchestrator/README.md).

## Mapa do repositório

```text
cyber-sec-journey/
├── Linux/                         # Sistema, terminal, Bash e redes
├── KaliLinux/                     # Fundamentos e guias de ferramentas
├── Cybersecurity/                 # Metodologia, vulnerabilidades e compliance
├── Scripts/
│   ├── recon-orchestrator/        # Nmap + Gobuster → relatórios HTML/JSON/CSV
│   └── vulnscan-orchestrator/     # OWASP ZAP + Nessus opcional → relatórios
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
- Outros tópicos: [SQLMap](KaliLinux/SQLiExploration/Sqlmap.md), [Binwalk](KaliLinux/FirmwareAnalis/Binwalk.md), [Maltego](KaliLinux/OSINT/Maltego.md), [Evil-WinRM](KaliLinux/PosExploitation/Evilwinrm.md) e [SET](KaliLinux/SocialEng/Setoolkit.md)

### Metodologia, defesa e vulnerabilidades

- Processo de pentest: [tipos](Cybersecurity/PentestingChore/Types.md), [níveis](Cybersecurity/PentestingChore/Levels.md), [times](Cybersecurity/PentestingChore/Teams.md) e [certificações](Cybersecurity/PentestingChore/ValidCertifications.md)
- Referências: [OSSTMM 3](Cybersecurity/OSSTMM3.md) e [MITRE ATT&CK](Cybersecurity/MITREATT@CK.md)
- Regras e compliance: [GDPR](Cybersecurity/PentestingChore/Rules/GDPR.md), [HIPAA](Cybersecurity/PentestingChore/Rules/HIPAA.md), [PCI DSS](Cybersecurity/PentestingChore/Rules/PCIDSS.md) e [FedRAMP](Cybersecurity/PentestingChore/Rules/FEDRAMP.md)
- Fases e temas: [footprinting](Cybersecurity/Footprinting.md), [scanning](Cybersecurity/Scanning.md), [exploração](Cybersecurity/Exploitation.md), [SQL Injection](Cybersecurity/SQLi.md) e [Google Hacking](Cybersecurity/GoogleHacking.md)

## Scripts de automação

Os scripts organizam a saída de ferramentas oficiais; eles não substituem a validação manual dos resultados nem concedem autorização para testar um alvo.

| Projeto | Objetivo | Saídas |
| --- | --- | --- |
| [Recon Orchestrator](Scripts/recon-orchestrator/README.md) | Executa Nmap com `vulners`, enumera serviços web com Gobuster e consolida os achados | HTML, JSON e CSV |
| [Vulnscan Orchestrator](Scripts/vulnscan-orchestrator/README.md) | Executa OWASP ZAP em Docker; pode integrar uma instância Nessus já configurada | HTML, JSON e CSV |

Leia o README de cada ferramenta antes de executar: eles descrevem requisitos, modos de operação, variáveis opcionais e limitações. Use o modo ativo do ZAP apenas com autorização específica, pois ele pode enviar payloads de teste à aplicação.

## Status da jornada

- [x] Base de Linux, Bash e redes
- [x] Fundamentos e ferramentas selecionadas do Kali Linux
- [x] Metodologia de pentest, OSSTMM e MITRE ATT&CK
- [x] Reconhecimento, varredura e relatórios automatizados para ambientes autorizados
- [ ] Administração e hardening de sistemas
- [ ] Vulnerabilidades web adicionais (por exemplo, XSS, CSRF e autenticação)
- [ ] Estudos de caso, labs e CTFs documentados

## Contribuições e fontes

Correções, referências oficiais e sugestões de melhoria são bem-vindas por meio de issue ou pull request. Sempre priorize a documentação oficial das ferramentas e execute atividades de segurança de forma ética e autorizada.

Mantido por [@joaovpzdev](https://github.com/joaovpzdev).
