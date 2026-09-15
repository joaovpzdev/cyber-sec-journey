# Vulnscan Orchestrator

Scripts de estudo para orquestrar a fase de **varredura de vulnerabilidades**
em um pentest (a etapa seguinte ao recon), combinando o
[OWASP ZAP](https://www.zaproxy.org/) — via sua automação oficial em Docker —
com um parser em Python que consolida os achados em HTML, JSON e CSV.
Inclui também uma integração **opcional** com [Nessus](https://www.tenable.com/products/nessus)
para quem já tem uma instância própria licenciada.

> ⚠️ **Uso apenas em ambientes autorizados.** Rode estes scripts somente
> contra alvos para os quais você tem permissão explícita por escrito
> (labs próprios, CTFs, ou engajamentos de pentest formalmente contratados).
> O modo `full` do ZAP envia payloads de ataque reais e pode causar
> instabilidade na aplicação — trate com ainda mais cautela.

## O que faz

1. `run_vulnscan.sh` roda a **imagem oficial Docker do OWASP ZAP**
   (`ghcr.io/zaproxy/zaproxy:stable`) em modo `baseline` (passivo, padrão)
   ou `full` (ativo, opt-in) contra o alvo.
2. `zap_report_parser.py` lê o `report.json` gerado pelo ZAP e produz:
   - Um relatório **HTML** com contagem de alertas por risco (Alto/Médio/
     Baixo/Informativo), detalhes, CWE, URLs afetadas e correção sugerida
   - Um **JSON** com todos os alertas normalizados
   - **CSVs**: um por alerta e outro por ocorrência/URL afetada
3. `nessus_trigger.py` (opcional) dispara e exporta um scan que você **já
   configurou** no seu próprio Nessus, via API REST oficial da Tenable —
   ativado automaticamente se as variáveis de ambiente do Nessus estiverem
   definidas.

Nenhum script reimplementa lógica de detecção de vulnerabilidades — eles
chamam ferramentas/APIs oficiais (ZAP, Nessus) e organizam a saída, no
mesmo espírito do [recon-orchestrator](../recon-orchestrator).

## Requisitos

```bash
# Docker é necessário para rodar o ZAP oficial
# https://docs.docker.com/engine/install/

python3 --version   # 3.8+
pip install requests --break-system-packages   # só necessário se for usar nessus_trigger.py
```

## Uso

### Varredura com OWASP ZAP (obrigatória)

```bash
chmod +x run_vulnscan.sh
./run_vulnscan.sh <alvo_autorizado> [rotulo_opcional] [baseline|full]
```

Exemplos:

```bash
# Modo passivo (padrão) — spider + análise passiva, sem ataque ativo
./run_vulnscan.sh https://app-teste.local

# Modo ativo — envia payloads de ataque reais (use com cautela redobrada)
./run_vulnscan.sh https://app-teste.local meu-teste full
```

Cria `vulnscan_<rotulo>_<timestamp>/` contendo:

```
report.json              # output bruto do ZAP
report_raw.html          # relatório HTML nativo do ZAP
relatorio.html           # relatório consolidado (nosso parser)
relatorio.json           # alertas normalizados em JSON
relatorio_alertas.csv    # um alerta por linha
relatorio_ocorrencias.csv # uma linha por URL/instância afetada
```

> **Nota sobre `localhost`:** como o ZAP roda dentro de um container Docker,
> `localhost`/`127.0.0.1` dentro do container **não** é o host que está
> rodando o Docker. Para testar uma aplicação local, use o IP da máquina
> na rede (ex.: `http://192.168.1.50:3000`) ou configure a rede do
> container conforme a [documentação oficial](https://www.zaproxy.org/docs/docker/baseline-scan/).

### Integração opcional com Nessus

Só faz sentido se você **já tem** uma instância do Nessus rodando, com um
scan já configurado (alvo, política, credenciais — tudo definido por você
no painel do Nessus). O script não cria nada disso; ele só dispara e
exporta um scan existente via API.

```bash
export NESSUS_URL="https://127.0.0.1:8834"
export NESSUS_ACCESS_KEY="sua_access_key"
export NESSUS_SECRET_KEY="sua_secret_key"
export NESSUS_SCAN_ID="42"          # ID do scan já configurado
export NESSUS_VERIFY_SSL="false"     # se a instância usa certificado autoassinado

./run_vulnscan.sh https://app-teste.local
```

Com essas variáveis definidas, `run_vulnscan.sh` chama automaticamente
`nessus_trigger.py` ao final, salvando `nessus_export.csv` na mesma pasta
de saída. Sem elas, essa etapa é simplesmente pulada — o resultado do ZAP
não é afetado.

Você também pode rodar o helper isoladamente:

```bash
python3 nessus_trigger.py --export resultado.csv --format csv
```

## Referências

- [OWASP ZAP — Baseline Scan (Docker)](https://www.zaproxy.org/docs/docker/baseline-scan/)
- [OWASP ZAP — Full Scan (Docker)](https://www.zaproxy.org/docs/docker/full-scan/)
- [OWASP ZAP API Reference](https://www.zaproxy.org/docs/api/)
- [CWE — Common Weakness Enumeration](https://cwe.mitre.org/)
- [Tenable Nessus API Reference](https://developer.tenable.com/reference)
- [PTES — Penetration Testing Execution Standard](http://www.pentest-standard.org/) — metodologia geral de referência

## Estrutura do repositório

```
vulnscan-orchestrator/
├── README.md
├── run_vulnscan.sh        # orquestração: ZAP (Docker) → parser → Nessus (opcional)
├── zap_report_parser.py    # parser JSON do ZAP → HTML/JSON/CSV
└── nessus_trigger.py       # helper opcional: dispara/exporta scan existente do Nessus
```

## Próximos passos de estudo

- Rodar ZAP com contexto autenticado (login automático via script de autenticação do ZAP) para cobrir áreas logadas da aplicação
- Consolidar achados do ZAP + Nessus em um único relatório (hoje ficam em arquivos separados)
- Adicionar suporte a múltiplos alvos (mesmo padrão de lista usado no `recon-orchestrator`)