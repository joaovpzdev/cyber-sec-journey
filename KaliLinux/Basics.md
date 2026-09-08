* **Modelo Atual (2020.1+):** O Kali adotou por padrão o modelo de usuário não-root (*Non-Root Default User* - usuário padrão `kali`), exigindo a utilização explícita de `sudo` para comandos privilegiados, aumentando a segurança operacional.

### 3.3 Kernel Customizado para Injeção de Pacotes
O kernel Linux do Kali traz patches de segurança e drivers customizados nativamente ativados, incluindo suporte completo para **injeção de quadros em redes sem fio (Wireless Frame Injection)** em modo monitor (`airmon-ng`).

### 3.4 Ambientes de Trabalho (Desktop Environments)
* **XFCE:** Interface gráfica padrão desde a versão 2019.4. Leve, rápida e altamente estável para consumo otimizado de RAM em ambientes virtuais.
* **GNOME e KDE Plasma:** Suportados oficialmente e selecionáveis durante o processo de instalação.
* **Kali NetHunter:** Plataforma de pentesting mobile para dispositivos Android baseada no Kali.

---

## 4. Estrutura e Categorização de Ferramentas

O Kali Linux possui uma taxonomia bem definida, agrupando suas ferramentas no menu principal em **13 categorias fundamentais**, alinhadas com as fases de uma auditoria profissional:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CATEGORIAS DO KALI LINUX                        │
├──────────────────────────────────┬─────────────────────────────────────┤
│ 01. Information Gathering        │ Coleta de Informações / OSINT       │
│ 02. Vulnerability Analysis       │ Varredura de Falhas e Scans         │
│ 03. Web Application Analysis     │ Testes em Aplicações Web e APIs     │
│ 04. Database Assessment          │ Avaliação e Injeção em Bando Dados  │
│ 05. Password Attacks             │ Quebra de Hashes e Ataques Brute    │
│ 06. Wireless Attacks             │ Testes em Redes Wi-Fi / Bluetooth   │
│ 07. Reverse Engineering          │ Descompilação e Análise de Binários │
│ 08. Exploitation Tools           │ Execução e Desenvolvimento Exploits │
│ 09. Sniffing & Spoofing          │ Interceptação de Tráfego de Rede    │
│ 10. Post Exploitation            │ Escalada, Pivoting e Manutenção     │
│ 11. Forensics                    │ Análise Pericial e Memória          │
│ 12. Reporting Tools              │ Documentação e Relatórios           │
│ 13. Social Engineering Tools     │ Phishing e Engenharia Social        │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### 4.1 Principais Ferramentas por Categoria

| Categoria | Descrição / Objetivo | Exemplos de Ferramentas Nativas |
| :--- | :--- | :--- |
| **01. Information Gathering** | Mapeamento de alvos, DNS e OSINT | `Nmap`, `Masscan`, `Amass`, `TheHarvester`, `Maltego` |
| **02. Vulnerability Analysis** | Identificação de falhas conhecidas | `OpenVAS`, `Nessus` (instalação), `Nikto`, `Searchsploit` |
| **03. Web App Analysis** | Auditoria de segurança web e proxies | `Burp Suite`, `OWASP ZAP`, `Gobuster`, `Wfuzz`, `FFUF` |
| **04. Database Assessment** | Testes de injeção em banco de dados | `SQLmap`, `Sqlninja` |
| **05. Password Attacks** | Ataques offline e online a credenciais | `John the Ripper`, `Hashcat`, `Hydra`, `Medusa` |
| **06. Wireless Attacks** | Auditoria de protocolos Wi-Fi (802.11) | `Aircrack-ng`, `Reaver`, `Wifite`, `Kismet` |
| **07. Reverse Engineering** | Análise de engenharia reversa de código | `Ghidra`, `Radare2`, `GDB`, `apktool` |
| **08. Exploitation Tools** | Ambientes de exploração de falhas | `Metasploit Framework`, `Exploit-DB` |
| **09. Sniffing & Spoofing** | Captura e manipulação de pacotes | `Wireshark`, `Tcpdump`, `Ettercap`, `Bettercap` |
| **10. Post Exploitation** | Ações pós-comprometimento e pivoting | `Mimikatz`, `BloodHound`, `Powershell Empire`, `Chisel` |
| **11. Forensics** | Perícia em discos, imagens e memória | `Autopsy`, `Volatility`, `Sleuth Kit` |
| **12. Social Engineering** | Simulação de phishing e credenciais | `SET (Social-Engineer Toolkit)`, `Evilginx` |

---

## 5. Pacotes Metapackages (`kali-tools`)

O Kali utiliza o conceito de **Metapackages** para permitir a personalização do sistema de acordo com a necessidade do projeto ou limitação de armazenamento:

* `kali-linux-core`: Instalação mínima contendo apenas as ferramentas base essenciais do sistema.
* `kali-tools-top10`: Instala as 10 ferramentas mais utilizadas do Kali (ex.: Nmap, Burp Suite, Metasploit, Wireshark, John, Hashcat, Aircrack-ng, Hydra, Sqlmap, Nikto).
* `kali-linux-default`: Instalação padrão recomendada para a maioria dos Pentesters (~2GB a 4GB).
* `kali-linux-large`: Coleção expandida de ferramentas para ambientes sem limitação de espaço.
* `kali-tools-web`: Metapackage específico contendo todas as ferramentas focadas em aplicações web.
* `kali-tools-wireless`: Metapackage focado exclusivamente em testes sem fio.

**Exemplo de Instalação via Terminal:**
```bash
sudo apt update
sudo apt install -y kali-tools-top10
```

---

## 6. Recursos Especiais do Kali Linux

1. **Kali Undercover Mode:**
   * Script nativo (`kali-undercover`) que altera instantaneamente o tema visual do sistema para simular a interface do Windows 10/11. É utilizado para auditorias presenciais (*onsite*) em ambientes públicos para evitar chamar atenção indiscreta.
2. **ISO Live com Criptografia e Persistência LUKS:**
   * Permite rodar o sistema a partir de um Pendrive sem alterar o disco rígido da máquina hospedeira, mantendo dados salvos e criptografados via LUKS (*Linux Unified Key Setup*).
3. **Emergency Self-Destruct (Nuke):**
   * Configuração avançada de persistência onde uma senha especial de emergência no boot pode apagar completamente a chave de criptografia LUKS, inutilizando o conteúdo do disco em caso de apreensão.
4. **Modo Forense (Forensic Mode):**
   * Opção no menu de boot Live que garante que nenhum disco interno do computador seja montado ou alterado automaticamente (nem mesmo partições swap), preservando a cadeia de custódia das evidências.

---

## 7. Boas Práticas e Segurança de Uso

* **Utilização em Máquinas Virtuais (VMs):** Recomenda-se a execução do Kali Linux dentro de hipervisores como VMware Workstation, VirtualBox ou Hyper-V, garantindo o uso de *Snapshots* antes de testes críticos.
* **Manutenção do Sistema:** Manter os repositórios atualizados usando sempre os comandos oficiais:
  ```bash
  sudo apt update && sudo apt full-upgrade -y
  ```
* **Uso Ético e Legal:** O Kali Linux é uma ferramenta poderosa de auditoria. O uso não autorizado de suas ferramentas contra redes ou sistemas de terceiros sem autorização prévia por escrito constitui crime cibernético.

---

## 8. Referências e Fontes Bibliográficas

A fundamentação deste documento baseia-se na documentação oficial e literatura técnica da distribuição:

1. **Documentação Oficial do Kali Linux (OffSec)**
   * *URL:* https://www.kali.org/docs/
   * *Descrição:* Documentação técnica cobrindo instalação, metapacotes, desenvolvimento e customização de kernel.

2. **Livro "Kali Linux Revealed: Mastering the Penetration Testing Distribution"**
   * *Autores:* Raphaël Hertzog, Jim O'Gorman, Mati Aharoni (OffSec Press).
   * *URL:* https://www.kali.org/kali-linux-revealed/
   * *Descrição:* Livro oficial publicado pela OffSec sobre administração, arquitetura e segurança do Kali Linux.

3. **Repositórios Oficiais do Debian Linux**
   * *URL:* https://www.debian.org/doc/
   * *Descrição:* Diretrizes de pacotes, política FHS e gerenciador de pacotes `apt` sobre o qual o Kali é construído.

4. **NIST SP 800-115 – Technical Guide to Information Security Testing and Assessment**
   * *Publicado por:* National Institute of Standards and Technology (NIST).
   * *Descrição:* Guia de testes e avaliações técnicas que serve de base para o uso de ferramentas de varredura e exploração presentes no Kali Linux.

5. **OffSec (Offensive Security) – Educational & Industry Resources**
   * *URL:* https://www.offsec.com/
   * *Descrição:* Material de referência e treinamento associado às certificações OSCP, KLCP (Kali Linux Certified Professional) e uso de ferramentas ofensivas.
