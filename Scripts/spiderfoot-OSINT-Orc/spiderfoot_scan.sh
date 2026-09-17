#!/usr/bin/env bash
#
# spiderfoot_scan.sh
# Automatiza um scan headless do SpiderFoot (sem precisar da interface web)
# e gera um relatorio HTML a partir do resultado, usando spiderfoot_report.py.
#
# Uso:
#   ./spiderfoot_scan.sh -t alvo.com [opcoes]
#
# Exemplos:
#   ./spiderfoot_scan.sh -t exemplo.com
#   ./spiderfoot_scan.sh -t exemplo.com -u footprint
#   ./spiderfoot_scan.sh -t exemplo.com -m sfp_dnsresolve,sfp_whois,sfp_shodan
#   ./spiderfoot_scan.sh -t 1.2.3.4 -u passive -o ~/osint/relatorios
#
# Requisitos: python3, SpiderFoot instalado (sf.py), spiderfoot_report.py no mesmo diretorio.

set -euo pipefail

# ------------------------------------------------------------------
# Cores para saida no terminal
# ------------------------------------------------------------------
C_RESET='\033[0m'
C_INFO='\033[1;34m'
C_OK='\033[1;32m'
C_WARN='\033[1;33m'
C_ERR='\033[1;31m'

log_info() { echo -e "${C_INFO}[*]${C_RESET} $*"; }
log_ok()   { echo -e "${C_OK}[+]${C_RESET} $*"; }
log_warn() { echo -e "${C_WARN}[!]${C_RESET} $*"; }
log_err()  { echo -e "${C_ERR}[x]${C_RESET} $*" >&2; }

# ------------------------------------------------------------------
# Valores padrao (pode sobrescrever via variaveis de ambiente ou flags)
# ------------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
SPIDERFOOT_DIR="${SPIDERFOOT_DIR:-$HOME/spiderfoot}"
REPORT_SCRIPT="${REPORT_SCRIPT:-$SCRIPT_DIR/spiderfoot_report.py}"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/relatorios}"
USECASE="all"
MODULES=""
TARGET=""
TIMEOUT_SECS=""
ABRIR_NAVEGADOR=0

usage() {
    cat <<EOF
Uso: $(basename "$0") -t ALVO [opcoes]

Opcoes:
  -t ALVO           Alvo do scan: dominio, IP, e-mail, etc. (obrigatorio)
  -p CAMINHO         Caminho da instalacao do SpiderFoot (padrao: \$SPIDERFOOT_DIR ou ~/spiderfoot)
  -u USECASE         Caso de uso: all | footprint | investigate | passive (padrao: all)
  -m MOD1,MOD2,...   Lista de modulos especificos (sobrepoe -u se usado)
  -o DIRETORIO        Diretorio de saida para CSV/HTML (padrao: ./relatorios)
  -T SEGUNDOS         Timeout maximo para o scan (usa 'timeout' do coreutils)
  -a                  Abrir o relatorio HTML automaticamente no navegador ao terminar
  -h                  Mostra esta ajuda

Variaveis de ambiente equivalentes: SPIDERFOOT_DIR, OUTPUT_DIR, REPORT_SCRIPT

Exemplos:
  $(basename "$0") -t exemplo.com
  $(basename "$0") -t exemplo.com -u footprint -a
  $(basename "$0") -t 1.2.3.4 -m sfp_shodan,sfp_virustotal,sfp_ipinfo
EOF
}

while getopts ":t:p:u:m:o:T:ah" opt; do
    case "$opt" in
        t) TARGET="$OPTARG" ;;
        p) SPIDERFOOT_DIR="$OPTARG" ;;
        u) USECASE="$OPTARG" ;;
        m) MODULES="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        T) TIMEOUT_SECS="$OPTARG" ;;
        a) ABRIR_NAVEGADOR=1 ;;
        h) usage; exit 0 ;;
        \?) log_err "Opcao invalida: -$OPTARG"; usage; exit 1 ;;
        :) log_err "A opcao -$OPTARG requer um argumento."; usage; exit 1 ;;
    esac
done

# ------------------------------------------------------------------
# Validacoes
# ------------------------------------------------------------------
if [[ -z "$TARGET" ]]; then
    log_err "Voce precisa informar um alvo com -t."
    usage
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    log_err "python3 nao encontrado no PATH. Instale com: sudo apt install python3"
    exit 1
fi

SF_PY="$SPIDERFOOT_DIR/sf.py"
if [[ ! -f "$SF_PY" ]]; then
    log_err "Nao encontrei sf.py em: $SF_PY"
    log_err "Aponte o caminho correto com -p /caminho/para/spiderfoot ou defina SPIDERFOOT_DIR."
    exit 1
fi

if [[ ! -f "$REPORT_SCRIPT" ]]; then
    log_err "Nao encontrei spiderfoot_report.py em: $REPORT_SCRIPT"
    log_err "Coloque-o no mesmo diretorio deste script, ou defina REPORT_SCRIPT."
    exit 1
fi

if [[ -n "$MODULES" && "$USECASE" != "all" ]]; then
    log_warn "Voce definiu -m e -u ao mesmo tempo; -m tem prioridade e -u sera ignorado."
fi

mkdir -p "$OUTPUT_DIR"

# ------------------------------------------------------------------
# Aviso etico
# ------------------------------------------------------------------
log_warn "Use este scan apenas contra alvos que voce tem autorizacao para investigar."
log_warn "Coleta de OSINT sobre terceiros sem consentimento pode ter implicacoes legais."
echo ""

# ------------------------------------------------------------------
# Preparar nomes de arquivo
# ------------------------------------------------------------------
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
SAFE_TARGET="$(printf '%s' "$TARGET" | tr -c 'A-Za-z0-9._-' '_')"
CSV_FILE="$OUTPUT_DIR/${SAFE_TARGET}_${TIMESTAMP}.csv"
HTML_FILE="$OUTPUT_DIR/${SAFE_TARGET}_${TIMESTAMP}.html"

# ------------------------------------------------------------------
# Montar comando do scan
# ------------------------------------------------------------------
SF_ARGS=(-s "$TARGET" -o csv -r)

if [[ -n "$MODULES" ]]; then
    SF_ARGS+=(-m "$MODULES")
    log_info "Alvo: $TARGET | Modulos: $MODULES"
else
    SF_ARGS+=(-u "$USECASE")
    log_info "Alvo: $TARGET | Caso de uso: $USECASE"
fi

RUN_CMD=(python3 "$SF_PY" "${SF_ARGS[@]}")
if [[ -n "$TIMEOUT_SECS" ]]; then
    if ! command -v timeout &>/dev/null; then
        log_warn "'timeout' nao encontrado; ignorando -T."
    else
        RUN_CMD=(timeout "${TIMEOUT_SECS}s" "${RUN_CMD[@]}")
        log_info "Timeout definido em ${TIMEOUT_SECS}s"
    fi
fi

# ------------------------------------------------------------------
# Rodar o scan (headless, sem interface web)
# ------------------------------------------------------------------
log_info "Iniciando scan do SpiderFoot... isso pode levar de alguns minutos a varias horas,"
log_info "dependendo do alvo e do numero de modulos habilitados."
log_info "Saida bruta (CSV): $CSV_FILE"
echo ""

SCAN_START=$(date +%s)

set +e
"${RUN_CMD[@]}" > "$CSV_FILE"
SCAN_STATUS=$?
set -e

SCAN_END=$(date +%s)
SCAN_DURATION=$((SCAN_END - SCAN_START))

if [[ $SCAN_STATUS -ne 0 ]]; then
    log_err "O scan terminou com codigo de erro $SCAN_STATUS."
    log_err "Verifique a saida acima e o conteudo parcial em: $CSV_FILE"
    exit "$SCAN_STATUS"
fi

DATA_LINES=$(($(wc -l < "$CSV_FILE") - 1))
if [[ $DATA_LINES -le 0 ]]; then
    log_warn "O scan terminou mas nao retornou nenhum achado para '$TARGET'."
    log_warn "Isso pode ser normal (alvo com pouca exposicao) ou indicar um problema de configuracao/modulos."
    exit 0
fi

log_ok "Scan concluido em ${SCAN_DURATION}s. $DATA_LINES achados coletados."

# ------------------------------------------------------------------
# Gerar relatorio HTML
# ------------------------------------------------------------------
log_info "Gerando relatorio HTML..."
python3 "$REPORT_SCRIPT" "$CSV_FILE" -o "$HTML_FILE" -t "$TARGET"

log_ok "Relatorio gerado: $HTML_FILE"

if [[ $ABRIR_NAVEGADOR -eq 1 ]]; then
    if command -v xdg-open &>/dev/null; then
        xdg-open "$HTML_FILE" &>/dev/null &
    elif command -v sensible-browser &>/dev/null; then
        sensible-browser "$HTML_FILE" &>/dev/null &
    else
        log_warn "Nao encontrei xdg-open nem sensible-browser para abrir o relatorio automaticamente."
    fi
fi

echo ""
log_ok "Concluido."
echo "  CSV:  $CSV_FILE"
echo "  HTML: $HTML_FILE"