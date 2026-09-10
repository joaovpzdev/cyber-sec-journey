# cyber-sec-journey

> Repositório em construção. Documento aqui, de forma incremental, meu processo de aprendizado em Linux e Cybersecurity — cada conteúdo é adicionado conforme avanço nos estudos.

## Sobre

Este repositório reúne minhas anotações, resumos e referências de estudo enquanto avanço em Linux e Cybersecurity, partindo dos fundamentos do sistema operacional em direção a tópicos de pentest e segurança ofensiva — incluindo um guia dedicado, ferramenta por ferramenta, das principais ferramentas do Kali Linux. A ideia é que sirva tanto de material de consulta pessoal quanto de registro público do meu progresso.

Não é um curso nem um guia definitivo — é um diário de estudo. O conteúdo é revisado e expandido continuamente.

## Estrutura atual

```
cyber-sec-journey/
├── Linux/
│   ├── Fundaments.md                          # Comandos essenciais do Linux
│   ├── TheTerminal.md                         # Arquitetura do terminal (TTY, PTY, shell)
│   └── Bash/
│       ├── BasicsConceptsBashPentesting.md     # Bash scripting aplicado a pentest
│       └── ComandsInternsExterns.md            # Comandos internos vs. externos do shell
│
├── KaliLinux/
│   ├── Basics.md                               # Fundamentos e configuração inicial do Kali
│   ├── Nmap.md                                 # Varredura de rede, do básico ao avançado
│   ├── Legion.md                               # Recon e scanning automatizado (fork do SPARTA)
│   ├── Medusa.md                               # Força bruta de credenciais (online)
│   ├── Sqlmap.md                               # Detecção e exploração automatizada de SQLi
│   ├── Hashcat.md                              # Quebra de hash offline (GPU)
│   ├── John.md                                 # Quebra de hash offline (John the Ripper)
│   ├── Netcat.md                               # Canivete suíço de redes
│   ├── Arping.md                               # Descoberta de host via ARP
│   ├── Binwalk.md                              # Análise e extração de firmware
│   ├── Maltego.md                              # OSINT e análise de vínculos
│   ├── Evilwinrm.md                            # Shell WinRM para pós-exploração em Windows
│   └── Setoolkit.md                            # Social-Engineer Toolkit
│
├── Cybersecurity/
│   ├── SQLi.md                                 # SQL Injection: conceito, tipos e prevenção
│   ├── GoogleHacking.md                        # Google Dorking: operadores e GHDB
│   ├── Footprinting.md                         # Metodologia da fase de reconhecimento
│   ├── Scanning.md                             # Metodologia da fase de varredura
│   ├── Exploitation.md                         # Metodologia da fase de exploração
│   └── PentestingChore/
│       ├── Levels.md                           # Níveis de pentest
│       ├── Types.md                            # Black Box, Gray Box e White Box
│       └── ValidCertifications.md              # Certificações reconhecidas na área
│
└── README.md
```

## Trilha de estudos

Progresso do que já foi documentado e do que está planejado a seguir.

**Linux**
- [x] Fundamentos do terminal e do shell
- [x] Comandos internos e externos do Bash
- [x] Bash scripting aplicado a pentest
- [ ] Administração de sistemas (systemd, cron, logs, processos)
- [ ] Redes (tcpdump, SSH, DNS, iptables/nftables)
- [ ] Hardening de sistemas

**Kali Linux — ferramentas**
- [x] Fundamentos e configuração inicial
- [x] Nmap, Legion, Arping, Netcat (rede e descoberta)
- [x] Medusa, Hashcat, John the Ripper (credenciais)
- [x] SQLMap (exploração de SQLi)
- [x] Binwalk (análise de firmware)
- [x] Maltego (OSINT)
- [x] Evil-WinRM (pós-exploração Windows)
- [x] Social-Engineer Toolkit (engenharia social)
- [ ] Metasploit Framework
- [ ] BloodHound / enumeração de Active Directory

**Cybersecurity — metodologia e vulnerabilidades**
- [x] Tipos e níveis de pentest
- [x] Certificações da área
- [x] Metodologia: Footprinting → Scanning → Exploitation
- [x] SQL Injection (SQLi)
- [x] Google Hacking
- [ ] Outras vulnerabilidades web (XSS, CSRF, autenticação quebrada)
- [ ] Writeups de labs e CTFs praticados

## Como navegar

Cada arquivo `.md` é independente e cobre um tópico específico — não é necessário ler em ordem, mas os arquivos dentro de `Linux/` formam uma boa base antes de avançar para `Cybersecurity/`. Os guias em `KaliLinux/` seguem todos o mesmo formato (do nível básico ao avançado, com tabela-resumo e referências ao final) e podem ser consultados avulsos, conforme a ferramenta que estiver em uso no momento.

---

Repositório mantido por [@joaovpzdev](https://github.com/joaovpzdev). Última atualização estrutural: setembro de 2026.