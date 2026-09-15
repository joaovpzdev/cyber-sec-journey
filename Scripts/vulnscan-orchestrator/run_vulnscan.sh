#!/bin/bash
# run_vulnscan.sh
# Uso: ./run_vulnscan.sh <alvo_autorizado> [rotulo] [baseline|full]
#
#   baseline (padrão) — spider + análise PASSIVA, não envia ataques
#   full               — inclui varredura ATIVA (envia payloads reais)
#
# ATENÇÃO: use apenas contra alvos que você tem autorização explícita
# para testar. O modo "full" é intrusivo e pode gerar instabilidade na
# aplicação alvo — nunca rode contra produção sem alinhamento prévio.

set -euo pipefail

TARGET="${1:?Uso: $0 <alvo_autorizado> [rotulo] [baseline|full]}"
LABEL="${2:-$TARGET}"
MODE="${3:-baseline}"

OUTDIR="$(pwd)/vulnscan_${LABEL}_$(date +%Y%m%d_%H%M%S)"
PARSER="$(dirname "$0")/zap_report_parser.py"
ZAP_IMAGE="ghcr.io/zaproxy/zaproxy:stable"

mkdir -p "$OUTDIR"
echo "[*] Diretório de saída: $OUTDIR"

if [ ! -f "$PARSER" ]; then
    echo "[!] Erro: $PARSER não encontrado."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "[!] Docker não encontrado. A imagem oficial do ZAP roda via container."
    echo "    Instale: https://docs.docker.com/engine/install/"
    exit 1
fi

case "$MODE" in
  baseline)
    ZAP_SCRIPT="zap-baseline.py"
    echo "[*] Modo: baseline (passivo — spider + análise passiva, sem ataque ativo)"
    ;;
  full)
    ZAP_SCRIPT="zap-full-scan.py"
    echo "[*] Modo: full (ATIVO — envia payloads de ataque reais contra a aplicação)"
    echo "[!] Confirme que você tem autorização explícita para testes ATIVOS contra $TARGET"
    ;;
  *)
    echo "[!] Modo inválido: $MODE (use 'baseline' ou 'full')"
    exit 1
    ;;
esac

# O container do ZAP escreve os relatórios como o usuário interno "zap" —
# liberar escrita no diretório evita erros de permissão ao montar o volume.
# Ref.: https://www.zaproxy.org/docs/docker/baseline-scan/
chmod 777 "$OUTDIR"

echo "[*] Rodando OWASP ZAP ($ZAP_SCRIPT) contra $TARGET..."
# zap-baseline.py / zap-full-scan.py retornam código de saída != 0 quando
# há alertas — isso NÃO é falha de execução, por isso o "|| true"
docker run --rm \
    -v "$OUTDIR:/zap/wrk/:rw" \
    -t "$ZAP_IMAGE" "$ZAP_SCRIPT" \
    -t "$TARGET" \
    -J report.json \
    -r report_raw.html \
    || true

if [ ! -s "$OUTDIR/report.json" ]; then
    echo "[!] Erro: report.json não foi gerado."
    echo "    Verifique se o alvo é acessível a partir do container Docker"
    echo "    (ex.: 'localhost' dentro do container não é o host — use"
    echo "    o IP da máquina ou --network=host se aplicável)."
    exit 1
fi

echo "[*] Gerando relatório consolidado (HTML + JSON + CSV)..."
python3 "$PARSER" "$OUTDIR/report.json" "$OUTDIR/relatorio.html"

# --- Integração opcional com Nessus (requer instância própria já licenciada) ---
# Só roda se as variáveis de ambiente abaixo estiverem definidas.
# O script apenas DISPARA e EXPORTA um scan já configurado no seu Nessus
# (por NESSUS_SCAN_ID) via API oficial — não cria política de varredura
# nova nem qualquer lógica de detecção.
# Docs: https://developer.tenable.com/reference
if [ -n "${NESSUS_URL:-}" ] && [ -n "${NESSUS_ACCESS_KEY:-}" ] && \
   [ -n "${NESSUS_SECRET_KEY:-}" ] && [ -n "${NESSUS_SCAN_ID:-}" ]; then
    echo "[*] Variáveis do Nessus detectadas — disparando scan existente (ID: $NESSUS_SCAN_ID)..."
    NESSUS_HELPER="$(dirname "$0")/nessus_trigger.py"
    if [ -f "$NESSUS_HELPER" ]; then
        python3 "$NESSUS_HELPER" --export "$OUTDIR/nessus_export.csv" || \
            echo "[!] Falha na integração com Nessus — resultado do ZAP não é afetado."
    else
        echo "[!] $NESSUS_HELPER não encontrado. Pulando integração com Nessus."
    fi
else
    echo "[*] Variáveis do Nessus não configuradas — pulando integração (opcional)."
fi

echo "[*] Concluído."
echo "[*] Relatório bruto do ZAP: $OUTDIR/report_raw.html"
echo "[*] Relatório consolidado: $OUTDIR/relatorio.html"