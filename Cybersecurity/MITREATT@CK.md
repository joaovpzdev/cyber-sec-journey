# MITRE ATT&CK® — Táticas e Cenários de Ataque (Estudo)

> Baseado no framework público [MITRE ATT&CK](https://attack.mitre.org/), usado por times de defesa (Blue Team), resposta a incidentes e threat intelligence para entender o comportamento de adversários. As "táticas" respondem ao *porquê* de uma ação do atacante; as "técnicas" respondem ao *como*.

## As 14 Táticas Enterprise

| ID | Tática | Objetivo do Adversário |
|----|--------|-------------------------|
| TA0043 | Reconnaissance | Coletar informações sobre o alvo (OSINT, scanning, phishing para informação) |
| TA0042 | Resource Development | Preparar infraestrutura, contas e ferramentas para a operação |
| TA0001 | Initial Access | Obter o primeiro ponto de entrada no ambiente |
| TA0002 | Execution | Executar código malicioso em sistema local ou remoto |
| TA0003 | Persistence | Manter acesso mesmo após reinicializações ou troca de credenciais |
| TA0004 | Privilege Escalation | Obter permissões mais altas no sistema |
| TA0005 | Defense Evasion | Evitar detecção (maior tática em número de técnicas) |
| TA0006 | Credential Access | Roubar credenciais (dump de senhas, força bruta, captura de input) |
| TA0007 | Discovery | Mapear o ambiente (contas, rede, softwares de segurança) |
| TA0008 | Lateral Movement | Mover-se entre sistemas dentro da rede |
| TA0009 | Collection | Coletar dados de interesse antes da exfiltração |
| TA0011 | Command and Control | Manter comunicação com sistemas comprometidos |
| TA0010 | Exfiltration | Retirar dados do ambiente da vítima |
| TA0040 | Impact | Manipular, interromper ou destruir sistemas e dados |

---

## Cenários de Ataque (Attack Chains)

Os cenários abaixo são **mapeamentos conceituais** de tática → técnica, no formato usado em relatórios de threat intelligence e exercícios de Red Team/Purple Team para fins de estudo, detecção e defesa — não são instruções operacionais de exploração.

### Cenário 1 — Phishing → Ransomware

| Ordem | Tática | Técnica (ID) |
|-------|--------|--------------|
| 1 | Reconnaissance | Gather Victim Identity Information (T1589) |
| 2 | Initial Access | Phishing (T1566) |
| 3 | Execution | User Execution: Malicious Link (T1204.001) |
| 4 | Persistence | Scheduled Task/Job (T1053) |
| 5 | Privilege Escalation | Valid Accounts (T1078) |
| 6 | Defense Evasion | Obfuscated Files or Information (T1027) |
| 7 | Credential Access | OS Credential Dumping (T1003) |
| 8 | Lateral Movement | Remote Services (T1021) |
| 9 | Impact | Data Encrypted for Impact (T1486) |

### Cenário 2 — Exploração de Aplicação Web Pública

| Ordem | Tática | Técnica (ID) |
|-------|--------|--------------|
| 1 | Reconnaissance | Active Scanning (T1595) |
| 2 | Initial Access | Exploit Public-Facing Application (T1190) |
| 3 | Execution | Command and Scripting Interpreter (T1059) |
| 4 | Discovery | Network Service Discovery (T1046) |
| 5 | Privilege Escalation | Exploitation for Privilege Escalation (T1068) |
| 6 | Defense Evasion | Indicator Removal (T1070) |
| 7 | Command and Control | Application Layer Protocol (T1071) |
| 8 | Exfiltration | Exfiltration Over C2 Channel (T1041) |

### Cenário 3 — Comprometimento via Conta Válida (Insider/Credencial Vazada)

| Ordem | Tática | Técnica (ID) |
|-------|--------|--------------|
| 1 | Resource Development | Compromise Accounts (T1586) |
| 2 | Initial Access | Valid Accounts (T1078) |
| 3 | Discovery | Account Discovery (T1087) |
| 4 | Collection | Data from Information Repositories (T1213) |
| 5 | Defense Evasion | Masquerading (T1036) |
| 6 | Persistence | Create Account (T1136) |
| 7 | Command and Control | Web Service (T1102) |
| 8 | Exfiltration | Exfiltration Over Web Service (T1567) |

---

## Como usar este material

- Cada técnica listada pode ser buscada diretamente em [attack.mitre.org](https://attack.mitre.org/techniques/enterprise/) pelo ID (ex: T1566) para ver detecção, mitigação e exemplos reais de grupos de ameaça (APTs) que a utilizaram.
- Esses cenários servem como base para: criar regras de detecção (SIEM), simulações de Purple Team, e checklists de hardening.
- Próximo passo sugerido: mapear cada técnica acima às mitigações oficiais do ATT&CK (coluna "Mitigations" de cada página de técnica).

## Referências

- MITRE ATT&CK® — https://attack.mitre.org/
- Matriz Enterprise — https://attack.mitre.org/matrices/enterprise/