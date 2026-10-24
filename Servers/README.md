# Servidores: roteiros de estudo de Windows Server e Linux

Dois roteiros de estudo em PDF, do básico ao avançado, com um PDF técnico por módulo. Cada módulo traz conceitos, comandos, laboratórios práticos, checklist de revisão e links para a documentação oficial que embasou o texto.

Todo o conteúdo foi pesquisado **apenas em fontes oficiais**: Microsoft Learn e blogs oficiais da Microsoft, documentação da Red Hat, Ubuntu Server e Debian, projeto systemd, kernel.org e as páginas oficiais das certificações. Situação das versões verificada em outubro de 2026.

> Os laboratórios usam redes privadas e domínios fictícios (`corp.lab.internal`, `linux.lab.internal`). Monte-os em VMs isoladas, nunca na rede de produção.

## Windows Server 2025

Referência: Windows Server 2025 (LTSC). Alinhado ao exame **AZ-802: Administering Windows Server**, que substituiu o AZ-800 e o AZ-801 em 30/09/2026. Cerca de 22 semanas com 8 a 10 h por semana.

| Nº | Módulo | Nível |
| --- | --- | --- |
| 00 | [Roteiro geral, laboratório e certificação](WindowsServer/00-Roteiro-Geral-Windows-Server.pdf) | Visão geral |
| 01 | [Fundamentos, edições e instalação](WindowsServer/01-Fundamentos-Edicoes-e-Instalacao.pdf) | Básico |
| 02 | [Ferramentas de administração e PowerShell](WindowsServer/02-Ferramentas-de-Administracao-e-PowerShell.pdf) | Básico |
| 03 | [Active Directory Domain Services](WindowsServer/03-Active-Directory-Domain-Services.pdf) | Intermediário |
| 04 | [Group Policy](WindowsServer/04-Group-Policy.pdf) | Intermediário |
| 05 | [DNS, DHCP e serviços de rede](WindowsServer/05-DNS-DHCP-e-Servicos-de-Rede.pdf) | Intermediário |
| 06 | [Armazenamento e serviços de arquivo](WindowsServer/06-Armazenamento-e-Servicos-de-Arquivo.pdf) | Intermediário |
| 07 | [Hyper-V e contêineres](WindowsServer/07-Hyper-V-e-Conteineres.pdf) | Intermediário a avançado |
| 08 | [Segurança e hardening](WindowsServer/08-Seguranca-e-Hardening.pdf) | Avançado |
| 09 | [Alta disponibilidade e recuperação](WindowsServer/09-Alta-Disponibilidade-e-Recuperacao.pdf) | Avançado |
| 10 | [Monitoramento, troubleshooting e atualizações](WindowsServer/10-Monitoramento-Troubleshooting-e-Atualizacoes.pdf) | Avançado |
| 11 | [Windows Server híbrido com Azure e preparação AZ-802](WindowsServer/11-Windows-Server-Hibrido-e-Preparacao-AZ-802.pdf) | Avançado |

## Servidores Linux (RHEL 10 e Ubuntu Server 26.04 LTS)

As duas famílias aparecem lado a lado, com os comandos marcados como `[RHEL]` ou `[Ubuntu]` quando diferem. Alinhado às certificações **RHCSA (EX200)**, que é baseada no RHEL 10, e **LFCS**. Cerca de 21 semanas com 8 a 10 h por semana.

| Nº | Módulo | Nível |
| --- | --- | --- |
| 00 | [Roteiro geral, laboratório e certificações](LinuxServer/00-Roteiro-Geral-Linux-Server.pdf) | Visão geral |
| 01 | [Fundamentos, distribuições e instalação](LinuxServer/01-Fundamentos-Distribuicoes-e-Instalacao.pdf) | Básico |
| 02 | [Shell, linha de comando e scripts](LinuxServer/02-Shell-Linha-de-Comando-e-Scripts.pdf) | Básico |
| 03 | [Usuários, grupos, permissões e sudo](LinuxServer/03-Usuarios-Grupos-Permissoes-e-sudo.pdf) | Básico |
| 04 | [systemd, processos, boot e logs](LinuxServer/04-systemd-Processos-Boot-e-Logs.pdf) | Intermediário |
| 05 | [Pacotes, repositórios e atualizações](LinuxServer/05-Pacotes-Repositorios-e-Atualizacoes.pdf) | Intermediário |
| 06 | [Armazenamento: partições, LVM e sistemas de arquivos](LinuxServer/06-Armazenamento-Particoes-LVM-e-Sistemas-de-Arquivos.pdf) | Intermediário |
| 07 | [Rede, firewall e SSH](LinuxServer/07-Rede-Firewall-e-SSH.pdf) | Intermediário |
| 08 | [Serviços de rede: hora, DNS, DHCP, web e arquivos](LinuxServer/08-Servicos-de-Rede-Hora-DNS-DHCP-Web-e-Arquivos.pdf) | Intermediário |
| 09 | [Segurança: SELinux, AppArmor e hardening](LinuxServer/09-Seguranca-SELinux-AppArmor-e-Hardening.pdf) | Avançado |
| 10 | [Virtualização (KVM) e contêineres (Podman)](LinuxServer/10-Virtualizacao-KVM-e-Conteineres.pdf) | Avançado |
| 11 | [Monitoramento, desempenho, troubleshooting e backup](LinuxServer/11-Monitoramento-Desempenho-Troubleshooting-e-Backup.pdf) | Avançado |
| 12 | [Automação, integração com Active Directory e revisão final](LinuxServer/12-Automacao-Integracao-com-AD-e-Revisao-Final.pdf) | Avançado |

## Como os dois roteiros se conectam

- Os dois usam o mesmo formato e o mesmo ciclo de estudo: ler, abrir a documentação oficial, fazer o laboratório, quebrar de propósito, consertar e documentar.
- O **Módulo 12 de Linux** coloca os servidores RHEL e Ubuntu no domínio `corp.lab.internal` montado no roteiro de Windows, com acesso controlado por grupos e GPOs do Active Directory.
- Para quem mira Blue Team, os módulos de segurança (Windows 08 e Linux 09) e de monitoramento (Windows 10 e Linux 11) trazem auditoria, Event IDs, auditd e detecção em logs.
