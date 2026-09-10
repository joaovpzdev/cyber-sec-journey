# cyber-sec-journey

> Repositório em construção. Documento aqui, de forma incremental, meu processo de aprendizado em Linux e Cybersecurity — cada conteúdo é adicionado conforme avanço nos estudos.

## Sobre

Este repositório reúne minhas anotações, resumos e referências de estudo enquanto avanço em Linux e Cybersecurity, partindo dos fundamentos do sistema operacional em direção a tópicos de pentest e segurança ofensiva. A ideia é que sirva tanto de material de consulta pessoal quanto de registro público do meu progresso.

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
│   └── Basics.md                               # Fundamentos do Kali Linux
│
├── Cybersecurity/
│   ├── SQLi.md                                 # SQL Injection: conceito, tipos e prevenção
│   └── PentestingChore/
│       ├── Levels.md                           # Níveis de pentest
│       ├── Types.md                            # Tipos de pentest
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

**Kali Linux**
- [x] Fundamentos e configuração inicial
- [ ] Ferramentas de reconhecimento e scanning
- [ ] Ambientes de laboratório (VMs vulneráveis)

**Cybersecurity**
- [x] Tipos e níveis de pentest
- [x] Certificações da área
- [x] SQL Injection (SQLi)
- [ ] Outras vulnerabilidades web (XSS, CSRF, autenticação quebrada)
- [ ] Writeups de labs e CTFs praticados

## Como navegar

Cada arquivo `.md` é independente e cobre um tópico específico — não é necessário ler em ordem, mas os arquivos dentro de `Linux/` formam uma boa base antes de avançar para `Cybersecurity/`.

---

Repositório mantido por [@joaovpzdev](https://github.com/joaovpzdev). Última atualização estrutural: setembro de 2026.