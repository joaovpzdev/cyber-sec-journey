#!/usr/bin/env bash
#
# full_recon_pipeline.sh
# Encadeia subfinder (subdominios) -> httpx (probe de hosts vivos) ->
# nuclei (scan de vulnerabilidades conhecidas) e gera um relatorio HTML
# unico a partir do resultado, via recon_pipeline_report.py.
#
# Uso:
#   ./full_recon_pipeline.sh -t alvo.com [opcoes]
#
# Exemplos:
#   ./full_recon_pipeline.sh -t exemplo.com
#   ./full_recon_pipeline.sh -t exemplo.com --skip-nuclei
#   ./full_recon_pipeline.sh -t exemplo.com --severity critical,high -a
#
# Requisitos: subfinder, httpx e nuclei instalados e no PATH (ferramentas
# da ProjectDiscovery, ver README), python3, recon_pipeline_report.py no
# mesmo diretorio.

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
REPORT_SCRIPT="${REPORT_SCRIPT:-$SCRIPT_DIR/recon_pipeline_report.py}"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/relatorios}"
TARGET=""
SEVERITY=""
SKIP_NUCLEI=0
ABRIR_NAVEGADOR=0

usage() {
    cat <<EOF
Uso: $(basename "$0") -t ALVO [opcoes]

Opcoes:
  -t ALVO             Dominio alvo (obrigatorio)
  -o DIRETORIO         Diretorio de saida (padrao: ./relatorios)
  --severity LISTA     Filtra o nuclei por severidade (ex: critical,high)
  --skip-nuclei        Pula a etapa de scan de vulnerabilidades (so recon + probe)
  -a                   Abre o relatorio HTML automaticamente no navegador
  -h                   Mostra esta ajuda

Exemplos:
  $(basename "$0") -t exemplo.com
  $(basename "$0") -t exemplo.com --skip-nuclei
  $(basename "$0") -t exemplo.com --severity critical,high -a
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t) TARGET="$2"; shift 2 ;;
        -o) OUTPUT_DIR="$2"; shift 2 ;;
        --severity) SEVERITY="$2"; shift 2 ;;
        --skip-nuclei) SKIP_NUCLEI=1; shift ;;
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

MISSING=()
for bin in subfinder httpx python3; do
    command -v "$bin" &>/dev/null || MISSING+=("$bin")
done
if [[ $SKIP_NUCLEI -eq 0 ]]; then
    command -v nuclei &>/dev/null || MISSING+=("nuclei")
fi
if [[ ${#MISSING[@]} -gt 0 ]]; then
    log_err "Comando(s) nao encontrado(s) no PATH: ${MISSING[*]}"
    log_err "Ver secao de instalacao no README (ferramentas da ProjectDiscovery, via 'go install')."
    exit 1
fi

if [[ ! -f "$REPORT_SCRIPT" ]]; then
    log_err "Nao encontrei recon_pipeline_report.py em: $REPORT_SCRIPT"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

SUBS_FILE="$WORKDIR/subs.txt"
HTTPX_FILE="$WORKDIR/httpx.jsonl"
LIVE_FILE="$WORKDIR/live_hosts.txt"
NUCLEI_FILE="$WORKDIR/nuclei.jsonl"

log_warn "Use este pipeline apenas contra alvos que voce tem autorizacao para investigar."
log_warn "O nuclei envia requisicoes ativas contra os hosts -- nao e so coleta passiva."
echo ""
log_info "Alvo: $TARGET"

# ------------------------------------------------------------------
# Etapa 1: subfinder
# ------------------------------------------------------------------
log_info "[1/3] Enumerando subdominios (subfinder)..."
subfinder -d "$TARGET" -silent -o "$SUBS_FILE"
echo "$TARGET" >> "$SUBS_FILE"
sort -u -o "$SUBS_FILE" "$SUBS_FILE"
N_SUBS=$(wc -l < "$SUBS_FILE")
log_ok "$N_SUBS subdominios (incluindo o dominio raiz)."

# ------------------------------------------------------------------
# Etapa 2: httpx
# ------------------------------------------------------------------
log_info "[2/3] Verificando hosts vivos (httpx)..."
httpx -l "$SUBS_FILE" -silent -json -title -status-code -tech-detect -o "$HTTPX_FILE"

if [[ ! -s "$HTTPX_FILE" ]]; then
    log_warn "httpx nao retornou nenhum host vivo."
    touch "$LIVE_FILE"
else
    python3 -c "
import json, sys
with open('$HTTPX_FILE', encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        url = d.get('url') or d.get('input')
        if url:
            print(url)
" > "$LIVE_FILE"
fi
N_LIVE=$(wc -l < "$LIVE_FILE")
log_ok "$N_LIVE hosts vivos."

# ------------------------------------------------------------------
# Etapa 3: nuclei (opcional)
# ------------------------------------------------------------------
if [[ $SKIP_NUCLEI -eq 1 ]]; then
    log_info "[3/3] Pulando nuclei (--skip-nuclei)."
    touch "$NUCLEI_FILE"
elif [[ $N_LIVE -eq 0 ]]; then
    log_warn "[3/3] Nenhum host vivo para escanear -- pulando nuclei."
    touch "$NUCLEI_FILE"
else
    log_info "[3/3] Rodando scan de vulnerabilidades conhecidas (nuclei)..."
    NUCLEI_ARGS=(-l "$LIVE_FILE" -silent -jsonl -o "$NUCLEI_FILE")
    if [[ -n "$SEVERITY" ]]; then
        NUCLEI_ARGS+=(-severity "$SEVERITY")
        log_info "Filtro de severidade: $SEVERITY"
    fi
    nuclei "${NUCLEI_ARGS[@]}"
    N_VULNS=$(wc -l < "$NUCLEI_FILE" 2>/dev/null || echo 0)
    log_ok "$N_VULNS achados do nuclei."
fi

# ------------------------------------------------------------------
# Relatorio final
# ------------------------------------------------------------------
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
SAFE_TARGET="$(printf '%s' "$TARGET" | tr -c 'A-Za-z0-9._-' '_')"
HTML_FILE="$OUTPUT_DIR/${SAFE_TARGET}_${TIMESTAMP}.html"

log_info "Gerando relatorio HTML..."
python3 "$REPORT_SCRIPT" --subs "$SUBS_FILE" --httpx "$HTTPX_FILE" --nuclei "$NUCLEI_FILE" -o "$HTML_FILE" -t "$TARGET"

log_ok "Relatorio gerado: $HTML_FILE"

if [[ $ABRIR_NAVEGADOR -eq 1 ]]; then
    if command -v xdg-open &>/dev/null; then
        xdg-open "$HTML_FILE" &>/dev/null &
    elif command -v sensible-browser &>/dev/null; then
        sensible-browser "$HTML_FILE" &>/dev/null &
    else
        log_warn "Nao encontrei xdg-open nem sensible-browser."
    fi
fi

echo ""
log_ok "Concluido."
echo "  Relatorio: $HTML_FILE"
echo "  Hosts vivos: $LIVE_FILE"
echo "  Vulnerabilidades (nuclei): $NUCLEI_FILE"
echo "  Relatorio HTML: $HTML_FILE"
echo "  Subdominios encontrados: $SUBS_FILE"
echo "  Data e hora do relatorio: $TIMESTAMP"