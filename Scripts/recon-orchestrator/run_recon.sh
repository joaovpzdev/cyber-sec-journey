#!/bin/bash
# run_recon.sh
# Uso:
#   Alvo único:      ./run_recon.sh <alvo_autorizado> [rotulo] [wordlist]
#   Múltiplos alvos:  ./run_recon.sh <arquivo_com_alvos.txt> [rotulo] [wordlist]
#                      (um alvo por linha; linhas vazias ou "#" são ignoradas)
#
# ATENÇÃO: use apenas contra alvos que você tem autorização
# explícita para testar. Scans não autorizados podem violar leis
# como a Lei 12.737/2012 (Brasil) e legislações equivalentes em
# outras jurisdições.

set -euo pipefail

INPUT="${1:?Uso: $0 <alvo_ou_arquivo_com_alvos> [rotulo] [wordlist]}"
LABEL_ARG="${2:-}"
WORDLIST="${3:-/usr/share/wordlists/dirb/common.txt}"
PARSER="$(dirname "$0")/nmap_report.py"

if [ ! -f "$PARSER" ]; then
    echo "[!] Erro: $PARSER não encontrado."
    exit 1
fi

# Sanitiza um alvo para uso seguro em nome de pasta (troca caracteres
# especiais por "_")
sanitize() {
    echo "$1" | tr -c 'A-Za-z0-9._-' '_'
}

# Executa o pipeline completo (Nmap -> Gobuster -> parser) para UM alvo,
# salvando tudo dentro do diretório passado em $2
run_single_target() {
    local TARGET="$1"
    local OUTDIR="$2"

    local NMAP_BASE="${OUTDIR}/scan"
    local XML_FILE="${NMAP_BASE}.xml"
    local NMAP_TEXT="${NMAP_BASE}.nmap"
    local HTML_FILE="${OUTDIR}/relatorio.html"

    mkdir -p "$OUTDIR"
    echo "[*] === Alvo: $TARGET -> $OUTDIR ==="

    echo "[*] Rodando Nmap (-sV --script vulners)..."
    nmap -sV --script vulners -oA "$NMAP_BASE" "$TARGET"

    if [ ! -s "$XML_FILE" ]; then
        echo "[!] Erro: scan.xml não foi gerado para $TARGET. Pulando este alvo."
        return 1
    fi

    echo "[*] Identificando portas web abertas..."
    local WEB_PORTS
    WEB_PORTS=$(grep -oP '^\d+(?=/tcp\s+open\s+(http|https|http-proxy|http-alt|ssl/http))' \
        "$NMAP_TEXT" || true)

    if [ -z "$WEB_PORTS" ]; then
        echo "[*] Nenhuma porta web detectada. Pulando Gobuster."
    elif ! command -v gobuster &> /dev/null; then
        echo "[!] Gobuster não está instalado (sudo apt install gobuster). Pulando enumeração web."
    else
        local PORT LINE SCHEME
        for PORT in $WEB_PORTS; do
            LINE=$(grep -P "^${PORT}/tcp" "$NMAP_TEXT" || true)
            if echo "$LINE" | grep -qi "ssl"; then
                SCHEME="https"
            else
                SCHEME="http"
            fi

            echo "[*] Rodando Gobuster em ${SCHEME}://${TARGET}:${PORT} ..."
            gobuster dir \
                -u "${SCHEME}://${TARGET}:${PORT}" \
                -w "$WORDLIST" \
                -o "${OUTDIR}/gobuster_${PORT}.txt" \
                -k -q || true
        done
    fi

    echo "[*] Gerando relatório (HTML + JSON + CSV)..."
    python3 "$PARSER" "$XML_FILE" "$HTML_FILE"

    echo "[*] Concluído para $TARGET. Resultados em: $OUTDIR"
    echo
}

if [ -f "$INPUT" ]; then
    # --- Modo múltiplos alvos: $INPUT é um arquivo de lista ---
    LABEL="${LABEL_ARG:-lote}"
    MASTER_DIR="recon_${LABEL}_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$MASTER_DIR"
    echo "[*] Lista de alvos: $INPUT"
    echo "[*] Diretório mestre: $MASTER_DIR"
    echo

    TOTAL=0
    FALHAS=0
    while IFS= read -r LINE || [ -n "$LINE" ]; do
        # Ignora linhas vazias e comentários (#)
        LINE="$(echo "$LINE" | xargs)"
        [ -z "$LINE" ] && continue
        [[ "$LINE" == \#* ]] && continue

        TOTAL=$((TOTAL + 1))
        TARGET_DIR="${MASTER_DIR}/$(sanitize "$LINE")"
        if ! run_single_target "$LINE" "$TARGET_DIR"; then
            FALHAS=$((FALHAS + 1))
        fi
    done < "$INPUT"

    echo "[*] Lote concluído: $TOTAL alvo(s) processado(s), $FALHAS falha(s)."
    echo "[*] Resultados em: $MASTER_DIR/<alvo>/"
else
    # --- Modo alvo único (comportamento original) ---
    LABEL="${LABEL_ARG:-$INPUT}"
    OUTDIR="recon_${LABEL}_$(date +%Y%m%d_%H%M%S)"
    run_single_target "$INPUT" "$OUTDIR"
fi