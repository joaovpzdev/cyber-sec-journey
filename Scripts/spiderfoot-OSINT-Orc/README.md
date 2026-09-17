# SpiderFoot Automation Kit

Automatiza um scan de OSINT com o [SpiderFoot](https://github.com/smicallef/spiderfoot) e gera um relatório HTML navegável (busca, filtro por tipo, gráficos de contagem) a partir do resultado — em um único comando, sem precisar abrir a interface web.

## O que tem aqui

| Arquivo | Função |
|---|---|
| `spiderfoot_scan.sh` | Roda o SpiderFoot em modo headless contra um alvo e chama o gerador de relatório |
| `spiderfoot_report.py` | Lê o CSV gerado pelo scan e produz um relatório HTML autocontido (funciona offline) |
| `README.md` | Este arquivo |

Fluxo: `spiderfoot_scan.sh` → chama `sf.py` (do SpiderFoot) → gera CSV → chama `spiderfoot_report.py` → gera HTML.

---

## Requisitos

- **Kali Linux** (ou qualquer Debian-based) com acesso à internet — o SpiderFoot consulta APIs externas durante o scan.
- **Python 3.7+** (o Kali já vem com Python 3 instalado).
- **SpiderFoot** instalado (ver seção abaixo). Testado com a v4.0.
- **Bash** (padrão no Kali).
- Nenhuma biblioteca Python adicional é necessária para o `spiderfoot_report.py` — ele usa apenas a biblioteca padrão.

---

## Instalação

### 1. Instalar o SpiderFoot

Recomendado (versão oficial, direto do GitHub):

```bash
cd ~
git clone https://github.com/smicallef/spiderfoot.git
cd spiderfoot
pip3 install -r requirements.txt --break-system-packages
```

> No Kali (Debian 12+/Python 3.11+), pip bloqueia instalações fora de ambiente virtual por padrão — por isso o `--break-system-packages`. Se preferir isolar em um venv:
> ```bash
> python3 -m venv ~/spiderfoot-venv
> source ~/spiderfoot-venv/bin/activate
> pip3 install -r requirements.txt
> ```
> Se usar venv, ative-o (`source ~/spiderfoot-venv/bin/activate`) antes de rodar `spiderfoot_scan.sh`.

Teste se instalou certo:

```bash
python3 sf.py --version
```

### 2. Baixar os scripts deste kit

Coloque `spiderfoot_scan.sh` e `spiderfoot_report.py` **no mesmo diretório**, em qualquer lugar do seu sistema (não precisa ser dentro da pasta do SpiderFoot). Exemplo:

```bash
mkdir -p ~/osint-toolkit
# copie spiderfoot_scan.sh e spiderfoot_report.py para ~/osint-toolkit/
cd ~/osint-toolkit
chmod +x spiderfoot_scan.sh
```

### 3. Apontar o script para a instalação do SpiderFoot

Por padrão, `spiderfoot_scan.sh` procura o SpiderFoot em `~/spiderfoot`. Se você instalou em outro lugar, tem duas opções:

**Opção A — variável de ambiente (fixa, recomendada se sempre usa o mesmo caminho):**
```bash
echo 'export SPIDERFOOT_DIR=$HOME/spiderfoot' >> ~/.bashrc
source ~/.bashrc
```

**Opção B — flag `-p` a cada execução:**
```bash
./spiderfoot_scan.sh -t exemplo.com -p /caminho/para/spiderfoot
```

---

## Uso

### Sintaxe

```bash
./spiderfoot_scan.sh -t ALVO [opcoes]
```

### Opções

| Flag | Descrição | Padrão |
|---|---|---|
| `-t ALVO` | Alvo do scan: domínio, subdomínio, IP, e-mail, username, etc. (**obrigatório**) | — |
| `-p CAMINHO` | Caminho da instalação do SpiderFoot | `$SPIDERFOOT_DIR` ou `~/spiderfoot` |
| `-u USECASE` | Caso de uso: `all`, `footprint`, `investigate` ou `passive` | `all` |
| `-m MOD1,MOD2,...` | Lista de módulos específicos (sobrepõe `-u`) | — |
| `-o DIRETORIO` | Diretório de saída para os arquivos CSV/HTML | `./relatorios` |
| `-T SEGUNDOS` | Timeout máximo para o scan | sem limite |
| `-a` | Abre o relatório HTML no navegador ao terminar | desativado |
| `-h` | Mostra a ajuda | — |

### O que significa cada `-u` (caso de uso)

- **`passive`** — só consulta fontes passivas (WHOIS, DNS, certificados, bancos de dados públicos). Não faz nenhum contato direto e "barulhento" com a infraestrutura do alvo. Mais rápido e discreto.
- **`footprint`** — mapeia a superfície exposta do alvo (subdomínios, IPs, tecnologias, certificados). Bom ponto de partida.
- **`investigate`** — foca em reputação/ameaça (blacklists, malware, breaches). Mais lento, mais "ativo".
- **`all`** — habilita todos os 200+ módulos. Mais completo, também o mais demorado (pode levar de minutos a várias horas dependendo do alvo).

### Exemplos

```bash
# Scan completo de um domínio
./spiderfoot_scan.sh -t exemplo.com

# Scan rápido e discreto (só fontes passivas)
./spiderfoot_scan.sh -t exemplo.com -u passive

# Scan de um IP, abrindo o relatório automaticamente ao terminar
./spiderfoot_scan.sh -t 200.100.50.10 -u footprint -a

# Scan de um e-mail
./spiderfoot_scan.sh -t contato@exemplo.com -u investigate

# Só módulos específicos (mais rápido, mais controlado)
./spiderfoot_scan.sh -t exemplo.com -m sfp_dnsresolve,sfp_whois,sfp_certspotter,sfp_shodan

# Limitar o scan a 10 minutos e salvar em outro diretório
./spiderfoot_scan.sh -t exemplo.com -T 600 -o ~/osint/casos/caso01
```

### Listar os módulos disponíveis (para montar sua própria lista com `-m`)

```bash
python3 ~/spiderfoot/sf.py -M
```

---

## Passo a passo completo (do zero até o relatório)

1. Instale o SpiderFoot (seção *Instalação*, passo 1).
2. Copie os dois scripts deste kit para uma pasta de sua preferência e dê permissão de execução:
   ```bash
   chmod +x spiderfoot_scan.sh
   ```
3. Rode um primeiro scan de teste contra um alvo que você mesmo controla (ex: seu próprio domínio ou IP):
   ```bash
   ./spiderfoot_scan.sh -t seudominio.com -u passive
   ```
4. Acompanhe a saída no terminal — o script mostra o progresso e, ao final, o caminho dos dois arquivos gerados:
   ```
   CSV:  ./relatorios/seudominio.com_20260916_143022.csv
   HTML: ./relatorios/seudominio.com_20260916_143022.html
   ```
5. Abra o `.html` no navegador (ou use `-a` para abrir automaticamente da próxima vez):
   ```bash
   xdg-open ./relatorios/seudominio.com_20260916_143022.html
   ```
6. No relatório, use a busca e o filtro por tipo para explorar os achados. O CSV bruto fica salvo ao lado, caso você queira processar os dados de outra forma.

---

## Estrutura do relatório HTML gerado

- **Cartões de resumo**: total de achados, tipos distintos, módulos usados, falsos positivos marcados (quando aplicável).
- **Achados por tipo**: contagem e barra proporcional por tipo de evento (ex: `IP_ADDRESS`, `EMAILADDR`, `VULNERABILITY`).
- **Top módulos**: quais módulos do SpiderFoot mais contribuíram com achados.
- **Tabela completa**: todos os achados, com busca por texto livre, filtro por tipo e opção de ocultar falsos positivos. Tudo roda no navegador, sem precisar de internet.

---

## Solução de problemas

**`Nao encontrei sf.py em: ...`**
O caminho do SpiderFoot está errado. Confirme com `ls ~/spiderfoot/sf.py` (ou o caminho que você usou) e ajuste `-p` ou `SPIDERFOOT_DIR`.

**`Nao encontrei spiderfoot_report.py em: ...`**
Os dois scripts precisam estar na mesma pasta, ou defina a variável `REPORT_SCRIPT` apontando para o caminho correto.

**O scan trava ou demora demais**
Alvos grandes com `-u all` podem levar muito tempo. Use `-u passive` ou `-u footprint` para algo mais rápido, ou limite módulos específicos com `-m`. Use `-T SEGUNDOS` para impor um teto de tempo.

**`pip3 install` falha com "externally-managed-environment"**
É a proteção do Python no Debian/Kali recentes. Use `--break-system-packages` (mostrado acima) ou instale em um venv.

**O relatório saiu vazio ("Sem dados")**
Pode ser um alvo com pouquíssima exposição pública, ou os módulos escolhidos não geraram achados para aquele tipo de alvo. Tente `-u all` para uma cobertura mais ampla, ou verifique se o alvo foi reconhecido corretamente pelo SpiderFoot (domínios, IPs e e-mails costumam funcionar melhor sem aspas ou espaços extras).

**Erro de coluna no `spiderfoot_report.py` ao usar um CSV exportado manualmente da interface web**
O script reconhece automaticamente tanto o CSV gerado pelo `sf.py` (linha de comando) quanto o exportado pela interface web (Browse → Export → CSV). Se mesmo assim der erro, rode o script apontando o CSV problemático e envie a mensagem de erro — ela mostra as colunas que foram encontradas, o que ajuda a identificar a diferença.

---

## Aviso legal e ético

Este kit automatiza coleta de informações públicas (OSINT). **Use apenas contra alvos que você tem autorização explícita para investigar** — domínios/sistemas próprios, ou escopos formalmente autorizados em um teste de intrusão/pentest. Coletar informações sobre terceiros sem consentimento pode violar leis de proteção de dados (como a LGPD no Brasil) e termos de uso de diversos serviços consultados pelo SpiderFoot. A responsabilidade pelo uso é de quem executa o scan.