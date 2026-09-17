#!/usr/bin/env bash
#
# recon_scan.sh
# Automatiza uma sessao do recon-ng contra um dominio-alvo: cria o
# workspace, instala e roda uma lista de modulos, e gera um relatorio
# HTML a partir do banco SQLite resultante (via recon_report.py).
#
# IMPORTANTE sobre como isso funciona:
# O recon-ng e um console interativo (baseado em cmd2). Alguns comandos,
# como "db insert domains", pedem os valores campo a campo em vez de
# aceitar tudo numa linha so. Por isso este script nao usa "recon-cli"
# nem "-r arquivo.rc" -- ele monta a sessao inteira (workspace, seed do
# alvo, modulos, run) como um bloco de texto e alimenta via stdin para
# o "recon-ng", exatamente como se voce estivesse digitando cada linha
# na hora certa. E a forma mais robusta de automatizar um console
# interativo desse tipo.
#
# Uso:
#   ./recon_scan.sh -t alvo.com [opcoes]
#
# Exemplos:
#   ./recon_scan.sh -t exemplo.com
#   ./recon_scan.sh -t exemplo.com --with-keys
#   ./recon_scan.sh -t exemplo.com -o ~/osint/relatorios -w meu_workspace
#
# Requisitos: recon-ng instalado (comando 'recon-ng' no PATH -- ja vem
# assim no Kali), python3, recon_report.py no mesmo diretorio.

set -uo pipefail

# ------------------------------------------------------------------
# Cores
# ------------------------------------------------------------------
C_RESET='\033[0m'; C_INFO='\033[1;34m'; C_OK='\033[1;32m'
C_WARN='\033[1;33m'; C_ERR='\033[1;31m'

log_info() { echo -e "${C_INFO}[*]${C_RESET} $*"; }
log_ok()   { echo -e "${C_OK}[+]${C_RESET} $*"; }
log_warn() { echo -e "${C_WARN}[!]${C_RESET} $*"; }
log_err()  { echo -e "${C_ERR}[x]${C_RESET} $*" >&2; }

# ------------------------------------------------------------------
# Padroes
# ------------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
RECON_BIN="${RECON_BIN:-recon-ng}"
REPORT_SCRIPT="${REPORT_SCRIPT:-$SCRIPT_DIR/recon_report.py}"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/relatorios}"
WORKSPACE=""
TARGET=""
WITH_KEYS=0
ABRIR_NAVEGADOR=0

# Modulos que funcionam sem nenhuma chave de API.
FREE_MODULES=(
    "recon/domains-hosts/hackertarget"
    "recon/domains-hosts/netcraft"
    "recon/domains-hosts/certificate_transparency"
    "recon/domains-hosts/brute_hosts"
    "recon/domains-contacts/whois_pocs"
    "recon/domains-vulnerabilities/xssed"
)

# Modulos que exigem chave de API cadastrada (via 'keys add' dentro do
# recon-ng). So entram na varredura se -k/--with-keys for usado.
KEYED_MODULES=(
    "recon/domains-hosts/shodan_hostname"   # precisa de: shodan_api
    "recon/hosts-ports/shodan_ip"           # precisa de: shodan_api
)

usage() {
    cat <<EOF
Uso: $(basename "$0") -t ALVO [opcoes]

Opcoes:
  -t ALVO        Dominio alvo do scan (obrigatorio)
  -w WORKSPACE   Nome do workspace do recon-ng (padrao: derivado do alvo)
  -o DIRETORIO   Diretorio de saida para o relatorio (padrao: ./relatorios)
  -k, --with-keys  Inclui tambem os modulos que exigem chave de API (ex: Shodan)
  -a             Abre o relatorio HTML automaticamente no navegador ao terminar
  -h             Mostra esta ajuda

Variaveis de ambiente equivalentes: RECON_BIN, OUTPUT_DIR, REPORT_SCRIPT

Exemplos:
  $(basename "$0") -t exemplo.com
  $(basename "$0") -t exemplo.com -k -a
  $(basename "$0") -t exemplo.com -w investigacao_2026 -o ~/osint/caso01
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t) TARGET="$2"; shift 2 ;;
        -w) WORKSPACE="$2"; shift 2 ;;
        -o) OUTPUT_DIR="$2"; shift 2 ;;
        -k|--with-keys) WITH_KEYS=1; shift ;;
        -a) ABRIR_NAVEGADOR=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) log_err "Opcao invalida: $1"; usage; exit 1 ;;
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

if ! command -v "$RECON_BIN" &>/dev/null; then
    log_err "Comando '$RECON_BIN' nao encontrado no PATH."
    log_err "No Kali: sudo apt install recon-ng"
    log_err "Ou defina RECON_BIN=/caminho/para/recon-ng"
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    log_err "python3 nao encontrado no PATH."
    exit 1
fi

if [[ ! -f "$REPORT_SCRIPT" ]]; then
    log_err "Nao encontrei recon_report.py em: $REPORT_SCRIPT"
    log_err "Coloque-o no mesmo diretorio deste script, ou defina REPORT_SCRIPT."
    exit 1
fi

if [[ -z "$WORKSPACE" ]]; then
    WORKSPACE="$(printf '%s' "$TARGET" | tr -c 'A-Za-z0-9_-' '_')"
fi

mkdir -p "$OUTPUT_DIR"

RECON_HOME="${RECON_NG_HOME:-$HOME/.recon-ng}"
WORKSPACE_DIR="$RECON_HOME/workspaces/$WORKSPACE"

# ------------------------------------------------------------------
# Aviso etico
# ------------------------------------------------------------------
log_warn "Use este scan apenas contra alvos que voce tem autorizacao para investigar."
log_warn "Coleta de OSINT sobre terceiros sem consentimento pode ter implicacoes legais."
echo ""

# ------------------------------------------------------------------
# Montar a lista de modulos desta execucao
# ------------------------------------------------------------------
MODULES=("${FREE_MODULES[@]}")
if [[ $WITH_KEYS -eq 1 ]]; then
    MODULES+=("${KEYED_MODULES[@]}")
    log_info "Alvo: $TARGET | Workspace: $WORKSPACE | Modulos: ${#MODULES[@]} (incluindo os que usam chave de API)"
else
    log_info "Alvo: $TARGET | Workspace: $WORKSPACE | Modulos: ${#MODULES[@]} (somente sem chave de API)"
fi

# ------------------------------------------------------------------
# Montar o roteiro de comandos do recon-ng
# ------------------------------------------------------------------
CMD_FILE="$(mktemp)"
trap 'rm -f "$CMD_FILE"' EXIT

{
    for m in "${MODULES[@]}"; do
        echo "marketplace install $m"
    done

    # Seed do alvo: 'db insert domains' pede os campos um a um.
    echo "db insert domains"
    echo "$TARGET"
    echo ""

    for m in "${MODULES[@]}"; do
        echo "modules load $m"
        echo "run"
    done

    echo "exit"
} > "$CMD_FILE"

# ------------------------------------------------------------------
# Rodar o recon-ng alimentando os comandos via stdin
# ------------------------------------------------------------------
log_info "Iniciando sessao do recon-ng... isso pode levar alguns minutos,"
log_info "dependendo de quantos modulos e quao responsivas as fontes externas estao."
echo ""

SCAN_START=$(date +%s)
"$RECON_BIN" -w "$WORKSPACE" < "$CMD_FILE"
SCAN_STATUS=$?
SCAN_END=$(date +%s)
SCAN_DURATION=$((SCAN_END - SCAN_START))

if [[ $SCAN_STATUS -ne 0 ]]; then
    log_warn "recon-ng terminou com codigo $SCAN_STATUS. Isso pode ser so um modulo"
    log_warn "individual falhando (ex: sem chave de API) -- verifique a saida acima."
    log_warn "Vou tentar gerar o relatorio mesmo assim com o que foi coletado."
fi

if [[ ! -d "$WORKSPACE_DIR" ]]; then
    log_err "Workspace nao encontrado em: $WORKSPACE_DIR"
    log_err "O recon-ng pode estar usando um diretorio home diferente."
    log_err "Se necessario, defina RECON_NG_HOME=/caminho/correto e rode novamente."
    exit 1
fi

log_ok "Sessao concluida em ${SCAN_DURATION}s."

# ------------------------------------------------------------------
# Gerar relatorio HTML
# ------------------------------------------------------------------
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
HTML_FILE="$OUTPUT_DIR/${WORKSPACE}_${TIMESTAMP}.html"

log_info "Gerando relatorio HTML a partir de: $WORKSPACE_DIR"
python3 "$REPORT_SCRIPT" "$WORKSPACE_DIR" -o "$HTML_FILE" -t "$TARGET"
REPORT_STATUS=$?

if [[ $REPORT_STATUS -ne 0 ]]; then
    log_err "Falha ao gerar o relatorio HTML."
    exit "$REPORT_STATUS"
fi

log_ok "Relatorio gerado: $HTML_FILE"

if [[ $ABRIR_NAVEGADOR -eq 1 ]]; then
    if command -v xdg-open &>/dev/null; then
        xdg-open "$HTML_FILE" &>/dev/null &
    elif command -v sensible-browser &>/dev/null; then
        sensible-browser "$HTML_FILE" &>/dev/null &
    else
        log_warn "Nao encontrei xdg-open nem sensible-browser para abrir automaticamente."
    fi
fi

echo ""
log_ok "Concluido."
echo "  Workspace (banco recon-ng): $WORKSPACE_DIR"
echo "  Relatorio HTML:             $HTML_FILE"