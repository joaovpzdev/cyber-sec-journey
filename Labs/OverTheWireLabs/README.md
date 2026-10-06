# OverTheWire Bandit — Writeups (Níveis 13 a 21)

Anotações de estudo sobre o wargame [Bandit](https://overthewire.org/wargames/bandit/) do OverTheWire, com foco nos níveis que exploram conceitos de **Red Team**: credenciais expostas, reconhecimento de rede, escalação de privilégio e persistência.

> **Sem spoilers e sem senhas.** Seguindo as [regras do OverTheWire](https://overthewire.org/rules/), nenhum arquivo contém senhas, chaves, portas específicas ou caminhos exatos que entreguem a solução. O objetivo é documentar **o raciocínio, as ferramentas e as vulnerabilidades**, não o gabarito.

## Índice

| Nível | Tema | Vulnerabilidade / Técnica | MITRE ATT&CK |
|---|---|---|---|
| [13 → 14](bandit-13.md) | Chave SSH privada exposta | Credencial em arquivo legível | T1552.004 |
| [14 → 15](bandit-14.md) | Serviço em porta TCP | Comunicação em texto puro | — |
| [15 → 16](bandit-15.md) | Serviço com SSL/TLS | Certificado autoassinado | — |
| [16 → 17](bandit-16.md) | Varredura de portas | Descoberta de serviços | T1046 |
| [17 → 18](bandit-17.md) | Comparação de arquivos | Credenciais em arquivos | T1552.001 |
| [18 → 19](bandit-18.md) | Restrição via `.bashrc` | Controle de acesso no lado errado | T1059.004 |
| [19 → 20](bandit-19.md) | Binário SUID | Escalação de privilégio | T1548.001 |
| [20 → 21](bandit-20.md) | Listener com netcat | Conexão reversa | T1095 |
| [21 → 22](bandit-21.md) | Tarefa agendada (cron) | Vazamento via arquivo temporário | T1053.003 |

## Ferramentas utilizadas

`ssh` · `scp` · `chmod` · `nc` (netcat) · `openssl s_client` · `nmap` · `diff` · `find` · `ls -l` · `cat` · `cron`

## Estrutura de cada writeup

1. **Objetivo** — o que o nível pede
2. **Conceitos** — teoria necessária
3. **Abordagem** — o raciocínio e os comandos (de forma genérica)
4. **A vulnerabilidade** — o que estava errado e por que é perigoso
5. **No mundo real** — onde isso aparece fora do laboratório
6. **Como corrigir / detectar** — visão de Blue Team