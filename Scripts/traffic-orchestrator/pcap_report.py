#!/usr/bin/env python3
"""
pcap_report.py — Analisa um arquivo .pcap/.pcapng usando tshark (a versão
CLI do Wireshark) e gera relatório HTML consolidado de estatísticas de
tráfego, além de exports em JSON e CSV.

O tshark faz todo o parsing de protocolo (já testado e mantido pelo
projeto Wireshark); este script apenas extrai campos específicos via
`-T fields` e agrega os resultados em Python — não reimplementa nenhum
dissector de protocolo.

LIMITE DE ESCOPO INTENCIONAL: este script NÃO extrai payloads de
aplicação nem credenciais em texto claro (ex.: usuário/senha de HTTP
Basic, FTP, Telnet). Apenas metadados de tráfego (IPs, portas,
protocolos, contagens, nomes DNS/TLS-SNI). Ver README.md para o
raciocínio completo dessa decisão.

Uso:
    python3 pcap_report.py <captura.pcap> <saida.html>

Além do HTML, gera automaticamente (mesmo nome-base da saída):
    <saida>.json              — todas as estatísticas em JSON
    <saida>_talkers.csv        — pares de hosts por volume de tráfego
    <saida>_protocolos.csv     — distribuição de protocolos
    <saida>_dns.csv            — consultas DNS observadas
    <saida>_tls_sni.csv        — nomes de servidor (SNI) vistos em handshakes TLS

Referências:
- tshark(1): https://www.wireshark.org/docs/man-pages/tshark.html
- Guia de filtros de campo: https://www.wireshark.org/docs/dfref/
- BPF (filtro de captura): https://www.tcpdump.org/manpages/pcap-filter.7.html

AVISO: use apenas para analisar tráfego de redes/interfaces que você
tem autorização para monitorar.
"""

import sys
import os
import csv
import io
import json
import subprocess
from datetime import datetime
from collections import Counter, defaultdict
from html import escape

MAIN_FIELDS = [
    "frame.time_epoch", "ip.src", "ip.dst", "_ws.col.Protocol", "frame.len",
    "tcp.srcport", "tcp.dstport", "udp.srcport", "udp.dstport",
    "tcp.flags.syn", "tcp.flags.ack", "tcp.flags.reset",
]

# Limiar de portas distintas via SYN isolado pra considerar "possível
# varredura recebida" — heurística simples, não é detecção definitiva.
SCAN_HEURISTIC_THRESHOLD = 15

# Quantidade máxima de itens exibidos por tabela no HTML/CSV
TOP_N = 25


def run_tshark_fields(pcap_path, fields, display_filter=None):
    """Roda tshark -T fields e devolve uma lista de dicts (uma por linha)."""
    cmd = ["tshark", "-r", pcap_path, "-n", "-T", "fields"]
    for field in fields:
        cmd += ["-e", field]
    cmd += ["-E", "header=y", "-E", "separator=,", "-E", "quote=d", "-E", "occurrence=f"]
    if display_filter:
        cmd += ["-Y", display_filter]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print("[!] tshark não encontrado. Instale: sudo apt install tshark -y")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[!] Erro ao rodar tshark: {e.stderr.strip()}")
        sys.exit(1)

    # tshark imprime avisos (ex.: "Running as user root...") no stdout às
    # vezes antes do CSV — filtra só a partir da linha de cabeçalho real.
    lines = result.stdout.splitlines()
    header_idx = 0
    for i, line in enumerate(lines):
        if line.startswith(fields[0].split(".")[0]) or "," in line:
            header_idx = i
            break
    csv_text = "\n".join(lines[header_idx:])

    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def is_true(value):
    """tshark pode representar flags booleanas como 'True'/'False' ou '1'/'0'."""
    return value in ("1", "True", "true")


def format_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def build_summary(pcap_path):
    rows = run_tshark_fields(pcap_path, MAIN_FIELDS)

    total_packets = len(rows)
    total_bytes = 0
    protocol_counter = Counter()
    talkers = defaultdict(lambda: {"packets": 0, "bytes": 0})
    port_counter = Counter()
    syn_only_ports = defaultdict(set)  # (src, dst) -> {portas tocadas via SYN isolado}

    for r in rows:
        proto = r.get("_ws.col.protocol") or r.get("_ws.col.Protocol") or "Desconhecido"
        protocol_counter[proto] += 1

        try:
            length = int(r.get("frame.len") or 0)
        except ValueError:
            length = 0
        total_bytes += length

        src, dst = r.get("ip.src"), r.get("ip.dst")
        if src and dst:
            key = tuple(sorted([src, dst]))
            talkers[key]["packets"] += 1
            talkers[key]["bytes"] += length

        dstport = r.get("tcp.dstport") or r.get("udp.dstport") or ""
        if dstport:
            port_counter[dstport] += 1

        syn = is_true(r.get("tcp.flags.syn"))
        ack = is_true(r.get("tcp.flags.ack"))
        if syn and not ack and src and dst and dstport:
            syn_only_ports[(src, dst)].add(dstport)

    scan_candidates = [
        {"origem": src, "destino": dst, "portas_distintas": len(ports)}
        for (src, dst), ports in syn_only_ports.items()
        if len(ports) >= SCAN_HEURISTIC_THRESHOLD
    ]
    scan_candidates.sort(key=lambda x: x["portas_distintas"], reverse=True)

    talkers_list = sorted(
        ({"host_a": k[0], "host_b": k[1], **v} for k, v in talkers.items()),
        key=lambda x: x["bytes"], reverse=True
    )[:TOP_N]

    return {
        "total_packets": total_packets,
        "total_bytes": total_bytes,
        "protocols": protocol_counter.most_common(TOP_N),
        "talkers": talkers_list,
        "top_ports": port_counter.most_common(TOP_N),
        "scan_candidates": scan_candidates,
    }


def get_dns_queries(pcap_path):
    rows = run_tshark_fields(
        pcap_path, ["ip.src", "dns.qry.name"],
        display_filter="dns.flags.response==0 && dns.qry.name",
    )
    counter = Counter()
    for r in rows:
        name = r.get("dns.qry.name")
        if name:
            counter[name] += 1
    return counter.most_common(TOP_N)


def get_tls_sni(pcap_path):
    rows = run_tshark_fields(
        pcap_path, ["ip.dst", "tls.handshake.extensions_server_name"],
        display_filter="tls.handshake.extensions_server_name",
    )
    counter = Counter()
    for r in rows:
        sni = r.get("tls.handshake.extensions_server_name")
        if sni:
            counter[sni] += 1
    return counter.most_common(TOP_N)


def export_json(summary, dns_queries, tls_sni, path):
    data = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "dns_queries": dns_queries,
        "tls_sni": tls_sni,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_csv(rows, fieldnames, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_html(summary, dns_queries, tls_sni, output_path, source_file):
    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Relatório de Análise de Tráfego</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; color: #222; }}
  h1 {{ color: #2c3e50; }}
  .meta {{ color: #666; font-size: 0.9em; }}
  .summary {{ display: flex; gap: 12px; margin: 20px 0; }}
  .badge {{ flex: 1; text-align: center; background: #34495e; color: white; padding: 14px; border-radius: 6px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; background: white; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
  th {{ background: #34495e; color: white; }}
  section {{ margin-bottom: 30px; }}
  .warn {{ background: #fff3cd; border: 1px solid #ffeeba; padding: 12px; border-radius: 6px; }}
  .scope-note {{ background: #eef7ee; border: 1px solid #c3e6c3; padding: 10px 14px;
                  border-radius: 6px; font-size: 0.85em; color: #2d5a2d; }}
</style>
</head>
<body>
<h1>Relatório de Análise de Tráfego</h1>
<p class="meta">Arquivo analisado: {escape(source_file)}<br>
Relatório gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<p class="scope-note">Este relatório mostra apenas metadados de tráfego
(IPs, portas, protocolos, contagens). Por escopo intencional, não extrai
payload de aplicação nem credenciais em texto claro — ver README.md.</p>

<div class="summary">
  <div class="badge"><div style="font-size:1.8em;">{summary['total_packets']}</div><div>Pacotes</div></div>
  <div class="badge"><div style="font-size:1.8em;">{format_bytes(summary['total_bytes'])}</div><div>Volume total</div></div>
  <div class="badge"><div style="font-size:1.8em;">{len(summary['talkers'])}</div><div>Pares de hosts (top)</div></div>
</div>
"""

    if summary["scan_candidates"]:
        html += ('<section><div class="warn"><strong>⚠ Possível varredura de portas recebida '
                  '(heurística — não é uma detecção confirmada):</strong>'
                  '<table><tr><th>Origem</th><th>Destino</th><th>Portas distintas (SYN isolado)</th></tr>')
        for c in summary["scan_candidates"]:
            html += (f'<tr><td>{escape(c["origem"])}</td><td>{escape(c["destino"])}</td>'
                      f'<td>{c["portas_distintas"]}</td></tr>')
        html += "</table></div></section>"

    html += '<section><h2>Distribuição de protocolos</h2><table><tr><th>Protocolo</th><th>Pacotes</th></tr>'
    for proto, count in summary["protocols"]:
        html += f'<tr><td>{escape(proto)}</td><td>{count}</td></tr>'
    html += "</table></section>"

    html += ('<section><h2>Principais pares de hosts (por volume)</h2>'
              '<table><tr><th>Host A</th><th>Host B</th><th>Pacotes</th><th>Bytes</th></tr>')
    for t in summary["talkers"]:
        html += (f'<tr><td>{escape(t["host_a"])}</td><td>{escape(t["host_b"])}</td>'
                  f'<td>{t["packets"]}</td><td>{format_bytes(t["bytes"])}</td></tr>')
    html += "</table></section>"

    html += '<section><h2>Portas de destino mais frequentes</h2><table><tr><th>Porta</th><th>Pacotes</th></tr>'
    for port, count in summary["top_ports"]:
        html += f'<tr><td>{escape(port)}</td><td>{count}</td></tr>'
    html += "</table></section>"

    if dns_queries:
        html += '<section><h2>Consultas DNS observadas</h2><table><tr><th>Nome consultado</th><th>Ocorrências</th></tr>'
        for name, count in dns_queries:
            html += f'<tr><td>{escape(name)}</td><td>{count}</td></tr>'
        html += "</table></section>"

    if tls_sni:
        html += '<section><h2>Nomes de servidor (SNI) em handshakes TLS</h2><table><tr><th>SNI</th><th>Ocorrências</th></tr>'
        for sni, count in tls_sni:
            html += f'<tr><td>{escape(sni)}</td><td>{count}</td></tr>'
        html += "</table></section>"

    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 pcap_report.py <captura.pcap> <saida.html>")
        sys.exit(1)

    pcap_file, out_file = sys.argv[1], sys.argv[2]

    if not os.path.isfile(pcap_file):
        print(f"[!] Arquivo não encontrado: {pcap_file}")
        sys.exit(1)

    summary_data = build_summary(pcap_file)
    dns_data = get_dns_queries(pcap_file)
    tls_data = get_tls_sni(pcap_file)

    generate_html(summary_data, dns_data, tls_data, out_file, os.path.basename(pcap_file))

    out_base, _ = os.path.splitext(out_file)

    export_json(summary_data, dns_data, tls_data, f"{out_base}.json")

    export_csv(summary_data["talkers"], ["host_a", "host_b", "packets", "bytes"],
               f"{out_base}_talkers.csv")

    export_csv([{"protocolo": p, "pacotes": c} for p, c in summary_data["protocols"]],
               ["protocolo", "pacotes"], f"{out_base}_protocolos.csv")

    export_csv([{"nome": n, "ocorrencias": c} for n, c in dns_data],
               ["nome", "ocorrencias"], f"{out_base}_dns.csv")

    export_csv([{"sni": s, "ocorrencias": c} for s, c in tls_data],
               ["sni", "ocorrencias"], f"{out_base}_tls_sni.csv")

    print(f"[*] Relatório HTML: {out_file}")
    print(f"[*] Dados completos (JSON): {out_base}.json")
    print(f"[*] Pacotes analisados: {summary_data['total_packets']}")
    print(f"[*] Volume total: {format_bytes(summary_data['total_bytes'])}")
    if summary_data["scan_candidates"]:
        print(f"[!] Possíveis varreduras recebidas (heurística): {len(summary_data['scan_candidates'])}")