# Legion — do básico ao avançado

## O que é

Legion é uma ferramenta open source, semi-automatizada e altamente extensível de teste de intrusão em redes, focada em recon, descoberta e exploração inicial de sistemas. É um fork do SPARTA (projeto da SECFORCE), atualmente desenvolvido e mantido pela GoVanguard.

A diferença central em relação ao Nmap é a abordagem: enquanto o Nmap é operado inteiramente por linha de comando e exige que o usuário monte cada varredura manualmente, o Legion oferece uma interface gráfica que orquestra e correlaciona automaticamente os resultados de dezenas de outras ferramentas em um único painel — reduzindo bastante o trabalho manual de cruzar resultados entre ferramentas separadas.

Vem pré-instalado no Kali Linux desde a versão 2020.1, como sucessor direto do SPARTA.

## Instalação e dependências

```bash
sudo apt install legion
```

Geralmente já vem instalado por padrão no Kali; o comando acima só é necessário se não estiver presente. O Legion não faz o trabalho pesado por conta própria — ele orquestra um conjunto extenso de ferramentas de terceiros já conhecidas, entre elas:

| Categoria | Ferramentas integradas |
|---|---|
| Escaneamento de rede | Nmap, Unicornscan, Hping3 |
| Força bruta | Hydra, Medusa |
| Web | Nikto, Whatweb, Wapiti, WPScan, Dirbuster |
| SMB/NetBIOS | Enum4linux, SMBClient, NBTScan, Polenum |
| DNS/OSINT | TheHarvester, Dnsmap |
| TLS/SSL | SSLScan, SSLyze |
| Exploração | SQLMap, Metasploit Framework |
| WAF | Wafw00f |
| Screenshots | Eyewitness / CutyCapt, VNCViewer, RDesktop |

## Nível básico

### Iniciando a ferramenta

```bash
sudo legion
```

Costuma ser executado com privilégios de root, já que dispara internamente scans do Nmap (como SYN scan) que exigem esse nível de acesso.

### Adicionando um alvo

No campo de adição de host, é possível informar um IP único, um hostname ou uma faixa em notação CIDR. Assim que o alvo é adicionado ao escopo do projeto, o Legion já inicia automaticamente a descoberta e o escaneamento inicial daquele alvo, sem exigir mais nenhum comando manual.

### Painéis principais da interface

- **Scan** — árvore com os hosts e portas descobertas
- **Services** — serviços agrupados por host
- **Information** — dados do host (sistema operacional, hostname)
- **Screenshots** — capturas automáticas de serviços web, RDP e VNC encontrados
- **Brute** — painel de força bruta integrado (Hydra/Medusa)
- **CVEs/CPEs** — vulnerabilidades e plataformas detectadas automaticamente
- **Notes** — anotações vinculadas a cada host, direto na interface

## Nível intermediário

### Escaneamento em estágios (staged scanning)

Um dos diferenciais do Legion é o escaneamento configurável em estágios: em vez de disparar um único scan pesado de uma vez, ele executa passes progressivamente mais profundos — uma varredura inicial mais leve e discreta, seguida de estágios adicionais (detecção de versão, scripts, etc.) apenas quando justificado pelos resultados anteriores. Esse comportamento é documentado pelo próprio projeto como pensado para dificultar a detecção por IDS.

### Listas de alvos em lote

O Legion permite adicionar listas inteiras de IPs, hostnames ou subnets em notação CIDR de uma só vez, disparando o mesmo fluxo automatizado de descoberta e escaneamento para todos os alvos simultaneamente — útil quando o escopo do teste inclui uma faixa de rede inteira.

### Gerenciamento de hosts

- **Purge results** — limpa os resultados acumulados de um host, mantendo-o no escopo
- **Rescan** — refaz a varredura de um host já presente no projeto
- **Delete host** — remove o host completamente do escopo

### Resolução de hostname e vhosts/SNI

O Legion suporta resolução de hostname e escaneamento de vhosts baseados em SNI (Server Name Indication) — relevante quando múltiplos sites estão hospedados sob o mesmo IP, compartilhando o mesmo certificado TLS, situação comum em ambientes com balanceadores de carga ou hospedagem compartilhada.

### Menu de contexto

Clicar com o botão direito em um host ou porta específica dá acesso rápido a ferramentas adicionais direcionadas àquele alvo — por exemplo, disparar o Nikto contra uma porta web ou o Enum4linux contra uma porta SMB — com o resultado integrado diretamente na mesma interface, sem precisar abrir um terminal separado.

## Nível avançado

### Detecção automática de CPE/CVE e correlação com exploits

O Legion identifica automaticamente CPEs (Common Platform Enumeration) a partir dos serviços encontrados, cruza essas informações com CVEs conhecidas e, indo um passo além, já correlaciona essas CVEs com exploits catalogados no Exploit Database. Na prática, isso automatiza boa parte da etapa manual de "seleção do exploit" (via `searchsploit`) descrita no fluxo de exploitation, entregando o candidato a exploit já vinculado ao serviço identificado.

### Extensibilidade

O design modular do Legion permite adicionar scripts e ferramentas próprias ao menu de contexto da aplicação, através de arquivos de configuração — ou seja, é possível integrar rotinas de reconhecimento ou enumeração personalizadas ao fluxo automatizado, sem depender apenas do que já vem embutido.

### Modo headless (linha de comando)

Versões mais recentes do Legion trazem um modo headless, permitindo executar por linha de comando sem abrir a interface gráfica:

```bash
legion --headless --input-file alvos.txt --discovery --staged-scan --output-file resultado.json
```

Útil para integrar o Legion a pipelines automatizados ou rodar em ambientes sem interface gráfica disponível.

### Integração com IA via servidor MCP

```bash
legion --mcp-server
```

Versões recentes do Legion expõem um servidor MCP (Model Context Protocol), permitindo que assistentes de IA se conectem à ferramenta para orquestrar scans e interpretar resultados de forma programática — um recurso ainda raro entre as ferramentas tradicionais do Kali.

### Autosave em tempo real

Resultados e tarefas do projeto são salvos automaticamente e em tempo real, o que evita perda de progresso em varreduras longas ou em caso de fechamento inesperado da aplicação.

## Fluxo típico de uso

| Etapa | Ação no Legion | Equivalente manual |
|---|---|---|
| 1 | Adicionar alvo/faixa ao escopo | `nmap -sn` |
| 2 | Escaneamento automático em estágios | `nmap -sS / -sV / -O / -sC` escalonado |
| 3 | Consulta automática de CPEs/CVEs | busca manual no `searchsploit` |
| 4 | Correlação de CVEs com exploits | pesquisa manual no Exploit-DB |
| 5 | Screenshot automático de serviços web/RDP/VNC | acesso manual a cada porta |
| 6 | Força bruta integrada (Hydra/Medusa) | execução manual do Hydra |
| 7 | Notas e autosave do projeto | documentação manual |

## Vantagens e limitações

O Legion acelera bastante a combinação de footprinting e scanning, correlacionando automaticamente resultados de dezenas de ferramentas que, de outra forma, precisariam ser executadas e cruzadas manualmente uma a uma — é especialmente útil como visão panorâmica inicial em redes com muitos hosts.

Em contrapartida, por depender de tantas ferramentas de terceiros integradas, herda as limitações de cada uma — incluindo falsos positivos nas correlações automáticas de CVE, a mesma ressalva já feita no `Scanning.md`: sempre confirmar manualmente antes de qualquer tentativa de exploração. Além disso, por padrão dispara um volume alto de scans simultâneos, o que o torna significativamente mais "ruidoso" na rede do que uma varredura manual e cuidadosa.

## Considerações éticas e legais

Por orquestrar ferramentas de reconhecimento, força bruta e até módulos de exploração (via integração com Metasploit e SQLMap), o Legion deve ser usado exclusivamente contra ambientes próprios ou com autorização explícita e escopo bem definido. O volume de tráfego gerado automaticamente é bem maior do que uma varredura manual equivalente, o que aumenta tanto o risco de detecção quanto o potencial de impacto em sistemas de produção caso usado fora de um ambiente controlado.

## Referências

- Kali Linux Tools — Legion (kali.org/tools/legion)
- Repositório oficial do Legion, mantido pela GoVanguard
- SECFORCE — SPARTA (projeto original que deu origem ao Legion)