# Nmap — do básico ao avançado

## O que é

Nmap (Network Mapper) é uma ferramenta open source de descoberta de rede e auditoria de segurança, criada por Gordon Lyon (conhecido como Fyodor). É a ferramenta mais usada na fase de scanning de um pentest, cobrindo desde a descoberta simples de hosts ativos até detecção de versão de serviços, fingerprinting de sistema operacional e varredura de vulnerabilidades através de scripts.

Este arquivo organiza o uso do Nmap em três níveis progressivos de profundidade.

---

## Nível básico

### Sintaxe mínima

```
nmap alvo
```

Sem nenhuma flag, o Nmap faz um SYN scan (se executado como root) ou TCP connect scan (sem privilégios) contra as 1000 portas TCP mais comuns do alvo.

### Descoberta de hosts (ping scan)

```
nmap -sn 192.168.1.0/24
```

A flag `-sn` desativa o escaneamento de portas e apenas verifica quais hosts dentro da faixa informada estão ativos — o primeiro passo antes de investir tempo escaneando endereços que nem respondem.

### Escaneando portas específicas

```
nmap -p 80,443 alvo        # portas específicas
nmap -p 1-1000 alvo        # intervalo de portas
nmap -p- alvo              # todas as 65535 portas
```

### Escaneamento rápido

```
nmap --top-ports 100 alvo
```

Escaneia apenas as portas estatisticamente mais comuns (segundo o próprio banco de dados do Nmap), útil quando o objetivo é uma visão geral rápida antes de uma varredura completa.

---

## Nível intermediário

### Tipos de escaneamento de porta

| Flag | Nome | Característica |
|---|---|---|
| `-sS` | SYN scan | Não completa o handshake TCP; mais rápido e discreto; exige privilégio root |
| `-sT` | TCP connect scan | Completa o handshake TCP; não exige privilégio elevado |
| `-sU` | UDP scan | Escaneia portas UDP; geralmente mais lento que TCP |
| `-sA` | ACK scan | Não identifica portas abertas diretamente, mas ajuda a mapear regras de firewall |

### Detecção de serviço e versão

```
nmap -sV alvo
```

Identifica o serviço e a versão exata em cada porta aberta, comparando as respostas com o banco de assinaturas do Nmap (`nmap-service-probes`).

### Detecção de sistema operacional

```
nmap -O alvo
```

Analisa características da pilha TCP/IP do host (TTL, opções do cabeçalho, comportamento diante de pacotes malformados) para inferir o sistema operacional.

### Escaneamento agressivo

```
nmap -A alvo
```

Combina, em uma única flag, detecção de SO (`-O`), detecção de versão (`-sV`), scripts padrão do NSE (`-sC`) e traceroute (`--traceroute`). É mais lento e mais "ruidoso" na rede, mas entrega um panorama bem mais completo em uma única execução.

### Timing templates

```
nmap -T0 alvo   # paranoid — extremamente lento, minimiza detecção
nmap -T3 alvo   # normal — padrão do Nmap
nmap -T5 alvo   # insane — máxima velocidade, mais fácil de detectar
```

Controla o equilíbrio entre velocidade e discrição da varredura. Os templates vão de `-T0` (mais lento e discreto) a `-T5` (mais rápido e perceptível).

### Formatos de saída

```
nmap -oN saida.txt alvo    # formato normal (legível)
nmap -oX saida.xml alvo    # formato XML (integração com outras ferramentas)
nmap -oG saida.gnmap alvo  # formato "grepable" (fácil de filtrar com grep/awk)
nmap -oA saida alvo        # gera os três formatos de uma vez
```

---

## Nível avançado

### Nmap Scripting Engine (NSE)

O NSE permite estender o Nmap com scripts (escritos em Lua) organizados por categoria, cobrindo desde verificações simples até varredura de vulnerabilidades conhecidas.

```
nmap -sC alvo                  # executa os scripts padrão (categoria default)
nmap --script vuln alvo        # scripts de detecção de vulnerabilidades conhecidas
nmap --script discovery alvo   # scripts de reconhecimento adicional
nmap --script "nome-do-script" alvo   # executa um script específico
```

Principais categorias de scripts: `default`, `vuln`, `safe`, `discovery`, `auth`, `brute` (testes de força bruta) e `exploit` (categoria mais sensível, deve ser usada apenas em laboratório autorizado).

### Intensidade de detecção de versão

```
nmap -sV --version-intensity 9 alvo
```

Ajusta quão a fundo o Nmap tenta confirmar a versão de um serviço (escala de 0 a 9). Valores mais altos aumentam a precisão, mas também o tempo e o volume de pacotes enviados.

### Evasão de firewall e IDS

O Nmap documenta oficialmente técnicas para dificultar a detecção da varredura por firewalls e sistemas de detecção de intrusão (IDS) — usadas legitimamente também para testar a eficácia das próprias defesas de uma rede, dentro de um escopo autorizado:

```
nmap -f alvo                        # fragmenta os pacotes
nmap -D decoy1,decoy2,ME alvo       # mistura o IP real com IPs "isca"
nmap --source-port 53 alvo          # força uma porta de origem específica
nmap --data-length 25 alvo          # adiciona dados extras para dificultar fingerprint
```

Essas técnicas devem ser usadas apenas em ambientes próprios ou autorizados — o objetivo em um pentest legítimo é validar se as defesas do cliente detectam a varredura, não burlar proteções de terceiros sem consentimento.

### Zenmap

Interface gráfica oficial do Nmap. Útil para visualizar a topologia de rede automaticamente a partir dos resultados de uma varredura, especialmente quando o volume de hosts e portas torna a leitura em texto menos prática.

---

## Tabela-resumo por nível

| Nível | Comando | Função |
|---|---|---|
| Básico | `nmap alvo` | Scan padrão das 1000 portas mais comuns |
| Básico | `nmap -sn rede` | Descoberta de hosts ativos |
| Básico | `nmap -p portas alvo` | Escaneia portas específicas |
| Intermediário | `nmap -sS / -sT / -sU alvo` | Tipos de escaneamento de porta |
| Intermediário | `nmap -sV alvo` | Detecção de serviço e versão |
| Intermediário | `nmap -O alvo` | Detecção de sistema operacional |
| Intermediário | `nmap -A alvo` | Escaneamento agressivo combinado |
| Avançado | `nmap --script vuln alvo` | Varredura de vulnerabilidades via NSE |
| Avançado | `nmap -f / -D / --source-port` | Técnicas de evasão de firewall/IDS |
| Avançado | `nmap -oA saida alvo` | Exportação de resultados em múltiplos formatos |

## Considerações éticas e legais

O Nmap é uma ferramenta legítima, amplamente usada tanto por profissionais de segurança quanto por administradores de rede para auditoria dos próprios ambientes. Ainda assim, escaneá-lo contra sistemas de terceiros sem autorização explícita pode configurar acesso indevido a sistema de informação, dependendo da legislação local — o uso deve se restringir a ambientes próprios ou com escopo autorizado.

## Referências

- Documentação oficial do Nmap (nmap.org)
- Gordon "Fyodor" Lyon — *Nmap Network Scanning*
- Nmap Scripting Engine (NSE) — documentação oficial