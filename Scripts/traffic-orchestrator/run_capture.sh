#!/bin/bash
# run_capture.sh
# Uso: ./run_capture.sh <interface> [duracao_segundos] [filtro_bpf] [rotulo]
#
# Requer privilégio para captura de pacotes (raw socket): rode com sudo,
# ou configure a capability necessária no binário (ver README).
#
# ATENÇÃO: capture apenas tráfego de interfaces/redes que você tem
# autorização para monitorar — sua própria máquina, seu laboratório, ou
# um segmento de rede que você administra. Diferente do recon/vulnscan,
# aqui não existe "alvo remoto": você está escutando o que já passa pela
# sua interface de rede.

set -euo pipefail

IFACE="${1:?Uso: $0 <interface> [duracao_segundos] [filtro_bpf] [rotulo]}"
DURATION="${2:-60}"
BPF_FILTER="${3:-}"
LABEL="${4:-$IFACE}"

OUTDIR="captura_${LABEL}_$(date +%Y%m%d_%H%M%S)"
PCAP_FILE="${OUTDIR}/captura.pcap"
HTML_FILE="${OUTDIR}/relatorio.html"
PARSER="$(dirname "$0")/pcap_report.py"

mkdir -p "$OUTDIR"
echo "[*] Diretório de saída: $OUTDIR"

if [ ! -f "$PARSER" ]; then
    echo "[!] Erro: $PARSER não encontrado."
    exit 1
fi

if ! command -v tshark &> /dev/null; then
    echo "[!] tshark não encontrado (necessário para o parser)."
    echo "    Instale: sudo apt install tshark -y"
    exit 1
fi

# Prefere dumpcap (motor de captura oficial do Wireshark, feito para uso
# programático/por outras ferramentas) e cai para tcpdump se ausente.
if command -v dumpcap &> /dev/null; then
    CAPTURE_BIN="dumpcap"
elif command -v tcpdump &> /dev/null; then
    CAPTURE_BIN="tcpdump"
else
    echo "[!] Nem dumpcap nem tcpdump encontrados."
    echo "    Instale: sudo apt install tshark tcpdump -y"
    exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
    echo "[!] Aviso: captura de pacotes normalmente requer privilégio de root."
    echo "    Se falhar por permissão, rode: sudo $0 $*"
fi

echo "[*] Capturando na interface '$IFACE' por ${DURATION}s (via $CAPTURE_BIN)..."
[ -n "$BPF_FILTER" ] && echo "[*] Filtro BPF: $BPF_FILTER"

if [ "$CAPTURE_BIN" = "dumpcap" ]; then
    if [ -n "$BPF_FILTER" ]; then
        dumpcap -i "$IFACE" -a duration:"$DURATION" -w "$PCAP_FILE" -f "$BPF_FILTER"
    else
        dumpcap -i "$IFACE" -a duration:"$DURATION" -w "$PCAP_FILE"
    fi
else
    # BPF filter é passado sem aspas de propósito: tcpdump espera os
    # termos do filtro como argumentos separados (ex.: tcp port 80)
    if [ -n "$BPF_FILTER" ]; then
        timeout "$DURATION" tcpdump -i "$IFACE" -w "$PCAP_FILE" $BPF_FILTER || true
    else
        timeout "$DURATION" tcpdump -i "$IFACE" -w "$PCAP_FILE" || true
    fi
fi

if [ ! -s "$PCAP_FILE" ]; then
    echo "[!] Erro: nenhum pacote foi capturado (arquivo vazio ou ausente)."
    echo "    Verifique o nome da interface (ip link show) e as permissões."
    exit 1
fi

echo "[*] Captura concluída: $PCAP_FILE"
echo "[*] Gerando relatório (HTML + JSON + CSV)..."
python3 "$PARSER" "$PCAP_FILE" "$HTML_FILE"

echo "[*] Concluído."
echo "[*] Pcap bruto: $PCAP_FILE (também abre direto no Wireshark)"
echo "[*] Relatório: $HTML_FILE"