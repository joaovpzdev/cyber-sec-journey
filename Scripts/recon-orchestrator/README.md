# Recon Orchestrator

Scripts de estudo para orquestrar a fase de **reconhecimento** em um pentest,
combinando o [Nmap](https://nmap.org/) com um parser em Python que gera um
relatório HTML legível, destacando CVEs encontrados pelos scripts NSE.

> ⚠️ **Uso apenas em ambientes autorizados.** Rode estes scripts somente
> contra alvos para os quais você tem permissão explícita por escrito
> (labs próprios, CTFs, ou engajamentos de pentest formalmente contratados).
> Scans não autorizados podem configurar crime, dependendo da jurisdição.

## O que faz

1. `run_recon.sh` executa `nmap -sV --script vulners` contra um alvo (ou uma
   **lista de alvos**, um por linha) e salva o resultado em XML/texto (`-oA`).
2. Para cada porta web (http/https) detectada, roda o **Gobuster** em modo
   `dir` e salva o output em `gobuster_<porta>.txt`.
3. `nmap_report.py` parseia o XML do Nmap **e** os arquivos do Gobuster,
   gerando:
   - Um relatório **HTML** com portas, serviços, versões, scripts NSE,
     CVEs (destacados no topo) e enumeração web colorida por status
   - Um **JSON** com todos os achados estruturados
   - **CSVs** separados: portas abertas, CVEs e achados do Gobuster —
     prontos para importar em planilhas ou outras ferramentas

Nenhum dos scripts reimplementa lógica de varredura, enumeração ou
exploração — eles apenas chamam os binários oficiais (Nmap, Gobuster) e
organizam a saída.

## Requisitos

```bash
sudo apt install nmap gobuster -y
python3 --version   # 3.8+
```

O script `--script vulners` do Nmap consulta a API pública da
[Vulners](https://vulners.com/) para mapear versões de serviço a CVEs
conhecidos. O Gobuster precisa de uma wordlist (padrão usado:
`/usr/share/wordlists/dirb/common.txt`, instalada com o pacote `dirb`).

## Uso

### Alvo único

```bash
chmod +x run_recon.sh
./run_recon.sh <alvo_autorizado> [rotulo_opcional] [caminho_wordlist_opcional]
```

Cria `recon_<rotulo>_<timestamp>/` contendo:

```
scan.xml               # output bruto do Nmap
scan.nmap               # output em texto (usado para detectar portas web)
scan.gnmap
gobuster_<porta>.txt    # um arquivo por porta web encontrada
relatorio.html          # relatório visual consolidado
relatorio.json          # todos os achados em JSON
relatorio_portas.csv    # portas abertas por host
relatorio_cves.csv      # CVEs identificados
relatorio_gobuster.csv  # achados do Gobuster (se houver portas web)
```

### Múltiplos alvos

Crie um arquivo de texto com um alvo por linha (linhas vazias e iniciadas
com `#` são ignoradas):

```
# alvos.txt
alvo1.exemplo.com
alvo2.exemplo.com
192.168.1.10
```

E rode passando o **arquivo** no lugar do alvo:

```bash
./run_recon.sh alvos.txt meu-lote
```

O script detecta automaticamente que o primeiro argumento é um arquivo
(não um alvo) e roda o pipeline completo para cada linha, criando uma
subpasta por alvo dentro de um diretório mestre:

```
recon_meu-lote_<timestamp>/
├── alvo1.exemplo.com/
│   ├── scan.xml
│   ├── relatorio.html
│   └── ...
├── alvo2.exemplo.com/
│   └── ...
└── 192.168.1.10/
    └── ...
```

Se um alvo da lista falhar (ex.: host fora do ar), o script registra a
falha e segue para o próximo — o lote inteiro não é interrompido.

### Rodando o parser separadamente

Se você já tem um XML de um scan anterior (com ou sem `--script vuln`/`vulners`):

```bash
python3 nmap_report.py scan.xml relatorio.html
```

Se também houver arquivos `gobuster_<porta>.txt` na **mesma pasta** do XML,
eles são detectados e incluídos automaticamente — sem precisar de nenhum
argumento extra.

## Referências

- [Nmap XML Output Format](https://nmap.org/book/output-formats-xml-output.html) — estrutura das tags parseadas (`host`, `port`, `service`, `script`)
- [Nmap NSE Documentation](https://nmap.org/book/nse.html)
- [MITRE CVE Identifier Syntax](https://cve.mitre.org/cve/identifiers/syntaxchange.html) — padrão usado na regex de extração de CVEs
- [Gobuster (OJ/gobuster)](https://github.com/OJ/gobuster) — formato do output em modo `-q` parseado pelo script
- [PTES — Penetration Testing Execution Standard](http://www.pentest-standard.org/) — metodologia geral de referência para a fase de recon

## Estrutura do repositório

```
recon-orchestrator/
├── README.md
├── run_recon.sh       # orquestração: Nmap → parser
└── nmap_report.py      # parser XML → HTML com CVEs
```

## Próximos passos de estudo

- [x] Integrar output de enumeração web (Gobuster) como seção adicional no HTML
- [x] Exportar achados também em JSON/CSV para importar em outras ferramentas
- [x] Adicionar suporte a múltiplos alvos (loop sobre uma lista de IPs/domínios)
- [ ] Paralelizar o loop de múltiplos alvos (hoje é sequencial)
- [ ] Adicionar opção de severidade/score dos CVEs (via saída estruturada do `vulners`)