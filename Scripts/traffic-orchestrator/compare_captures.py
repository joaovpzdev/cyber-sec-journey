#!/usr/bin/env python3
"""
compare_captures.py — Compara duas capturas de tráfego (ex.: "antes" e
"depois" de uma mudança de rede) e destaca as diferenças: protocolos,
hosts, portas, consultas DNS, SNI e indícios de varredura que apareceram,
sumiram ou variaram de volume entre as duas.

Aceita como entrada, para cada lado, um .pcap/.pcapng (analisado na hora
via as mesmas funções do pcap_report.py) OU um .json já gerado por
`pcap_report.py` (reaproveita o resultado, sem rodar tshark de novo).

Uso:
    python3 compare_captures.py <antes.pcap|antes.json> <depois.pcap|depois.json> <saida.html>

Além do HTML, gera automaticamente (mesmo nome-base da saída):
    <saida>.json                — diffs completos em JSON
    <saida>_protocolos_diff.csv
    <saida>_talkers_diff.csv
    <saida>_portas_diff.csv
    <saida>_dns_diff.csv
    <saida>_tls_sni_diff.csv

AVISO: use apenas com capturas de interfaces/redes que você tem
autorização para monitorar. Mesmo limite de escopo do pcap_report.py:
não compara nem exibe payload de aplicação/credenciais em texto claro.
"""

import sys
import os
import json
import csv
from datetime import datetime
from html import escape

import pcap_report as pr  # reaproveita build_summary / get_dns_queries / get_tls_sni


def load_analysis(path):
    """Carrega um .json já gerado, ou analisa um .pcap na hora."""
    if path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["summary"], data["dns_queries"], data["tls_sni"]

    if not os.path.isfile(path):
        print(f"[!] Arquivo não encontrado: {path}")
        sys.exit(1)

    summary = pr.build_summary(path)
    dns = pr.get_dns_queries(path)
    tls = pr.get_tls_sni(path)
    return summary, dns, tls


def diff_counter_list(before, after):
    """Compara duas listas [(chave, contagem), ...] -> novos, sumidos, variação nos comuns."""
    before_d = dict(before)
    after_d = dict(after)
    keys_before, keys_after = set(before_d), set(after_d)

    novos = sorted(
        ({"chave": k, "depois": after_d[k]} for k in keys_after - keys_before),
        key=lambda x: x["depois"], reverse=True,
    )
    sumidos = sorted(
        ({"chave": k, "antes": before_d[k]} for k in keys_before - keys_after),
        key=lambda x: x["antes"], reverse=True,
    )
    variacao = sorted(
        ({"chave": k, "antes": before_d[k], "depois": after_d[k], "delta": after_d[k] - before_d[k]}
         for k in keys_before & keys_after if after_d[k] != before_d[k]),
        key=lambda x: abs(x["delta"]), reverse=True,
    )
    return {"novos": novos, "sumidos": sumidos, "variacao": variacao}


def diff_talkers(before, after):
    """Compara listas de talkers (dicts com host_a/host_b/packets/bytes)."""
    def key(t):
        return tuple(sorted([t["host_a"], t["host_b"]]))

    before_d = {key(t): t for t in before}
    after_d = {key(t): t for t in after}
    keys_before, keys_after = set(before_d), set(after_d)

    novos = sorted(
        (after_d[k] for k in keys_after - keys_before),
        key=lambda x: x["bytes"], reverse=True,
    )
    sumidos = sorted(
        (before_d[k] for k in keys_before - keys_after),
        key=lambda x: x["bytes"], reverse=True,
    )
    variacao = sorted(
        ({"host_a": k[0], "host_b": k[1],
          "bytes_antes": before_d[k]["bytes"], "bytes_depois": after_d[k]["bytes"],
          "delta_bytes": after_d[k]["bytes"] - before_d[k]["bytes"]}
         for k in keys_before & keys_after if after_d[k]["bytes"] != before_d[k]["bytes"]),
        key=lambda x: abs(x["delta_bytes"]), reverse=True,
    )
    return {"novos": novos, "sumidos": sumidos, "variacao": variacao}


def diff_scan_candidates(before, after):
    def key(c):
        return (c["origem"], c["destino"])

    before_d = {key(c): c for c in before}
    after_d = {key(c): c for c in after}
    keys_before, keys_after = set(before_d), set(after_d)

    return {
        "novos": [after_d[k] for k in keys_after - keys_before],
        "sumidos": [before_d[k] for k in keys_before - keys_after],
    }


def build_diff(summary_before, dns_before, tls_before, summary_after, dns_after, tls_after):
    return {
        "volume": {
            "pacotes_antes": summary_before["total_packets"],
            "pacotes_depois": summary_after["total_packets"],
            "pacotes_delta": summary_after["total_packets"] - summary_before["total_packets"],
            "bytes_antes": summary_before["total_bytes"],
            "bytes_depois": summary_after["total_bytes"],
            "bytes_delta": summary_after["total_bytes"] - summary_before["total_bytes"],
        },
        "protocolos": diff_counter_list(summary_before["protocols"], summary_after["protocols"]),
        "portas": diff_counter_list(summary_before["top_ports"], summary_after["top_ports"]),
        "talkers": diff_talkers(summary_before["talkers"], summary_after["talkers"]),
        "dns": diff_counter_list(dns_before, dns_after),
        "tls_sni": diff_counter_list(tls_before, tls_after),
        "varreduras": diff_scan_candidates(
            summary_before.get("scan_candidates", []), summary_after.get("scan_candidates", [])
        ),
    }


def render_counter_diff_section(title, diff, label_chave="Item"):
    html = f"<section><h2>{escape(title)}</h2>"

    if diff["novos"]:
        html += f'<h3 style="color:#27ae60;">Novos ({len(diff["novos"])})</h3>'
        html += f"<table><tr><th>{label_chave}</th><th>Contagem</th></tr>"
        for item in diff["novos"][:30]:
            html += f'<tr><td>{escape(str(item["chave"]))}</td><td>{item["depois"]}</td></tr>'
        html += "</table>"

    if diff["sumidos"]:
        html += f'<h3 style="color:#c0392b;">Sumiram ({len(diff["sumidos"])})</h3>'
        html += f"<table><tr><th>{label_chave}</th><th>Contagem (antes)</th></tr>"
        for item in diff["sumidos"][:30]:
            html += f'<tr><td>{escape(str(item["chave"]))}</td><td>{item["antes"]}</td></tr>'
        html += "</table>"

    if diff["variacao"]:
        html += '<h3 style="color:#e67e22;">Variação de volume</h3>'
        html += f"<table><tr><th>{label_chave}</th><th>Antes</th><th>Depois</th><th>Delta</th></tr>"
        for item in diff["variacao"][:30]:
            delta = item["delta"]
            sign = "+" if delta > 0 else ""
            html += (f'<tr><td>{escape(str(item["chave"]))}</td><td>{item["antes"]}</td>'
                      f'<td>{item["depois"]}</td><td>{sign}{delta}</td></tr>')
        html += "</table>"

    if not diff["novos"] and not diff["sumidos"] and not diff["variacao"]:
        html += "<p><em>Nenhuma diferença.</em></p>"

    html += "</section>"
    return html


def render_talkers_diff(diff):
    html = "<section><h2>Pares de hosts (talkers)</h2>"

    if diff["novos"]:
        html += f'<h3 style="color:#27ae60;">Novos pares ({len(diff["novos"])})</h3>'
        html += "<table><tr><th>Host A</th><th>Host B</th><th>Pacotes</th><th>Bytes</th></tr>"
        for t in diff["novos"][:30]:
            html += (f'<tr><td>{escape(t["host_a"])}</td><td>{escape(t["host_b"])}</td>'
                      f'<td>{t["packets"]}</td><td>{t["bytes"]}</td></tr>')
        html += "</table>"

    if diff["sumidos"]:
        html += f'<h3 style="color:#c0392b;">Pares que sumiram ({len(diff["sumidos"])})</h3>'
        html += "<table><tr><th>Host A</th><th>Host B</th><th>Pacotes</th><th>Bytes</th></tr>"
        for t in diff["sumidos"][:30]:
            html += (f'<tr><td>{escape(t["host_a"])}</td><td>{escape(t["host_b"])}</td>'
                      f'<td>{t["packets"]}</td><td>{t["bytes"]}</td></tr>')
        html += "</table>"

    if diff["variacao"]:
        html += '<h3 style="color:#e67e22;">Maior variação de volume</h3>'
        html += "<table><tr><th>Host A</th><th>Host B</th><th>Bytes antes</th><th>Bytes depois</th><th>Delta</th></tr>"
        for t in diff["variacao"][:30]:
            delta = t["delta_bytes"]
            sign = "+" if delta > 0 else ""
            html += (f'<tr><td>{escape(t["host_a"])}</td><td>{escape(t["host_b"])}</td>'
                      f'<td>{t["bytes_antes"]}</td><td>{t["bytes_depois"]}</td><td>{sign}{delta}</td></tr>')
        html += "</table>"

    if not diff["novos"] and not diff["sumidos"] and not diff["variacao"]:
        html += "<p><em>Nenhuma diferença.</em></p>"

    html += "</section>"
    return html


def render_scan_diff(diff):
    if not diff["novos"] and not diff["sumidos"]:
        return ""

    html = '<section><div class="warn"><strong>⚠ Diferenças em possíveis varreduras (heurística):</strong>'
    if diff["novos"]:
        html += f'<h4>Novas ({len(diff["novos"])})</h4><table><tr><th>Origem</th><th>Destino</th><th>Portas distintas</th></tr>'
        for c in diff["novos"]:
            html += f'<tr><td>{escape(c["origem"])}</td><td>{escape(c["destino"])}</td><td>{c["portas_distintas"]}</td></tr>'
        html += "</table>"
    if diff["sumidos"]:
        html += f'<h4>Não observadas mais ({len(diff["sumidos"])})</h4><table><tr><th>Origem</th><th>Destino</th><th>Portas distintas</th></tr>'
        for c in diff["sumidos"]:
            html += f'<tr><td>{escape(c["origem"])}</td><td>{escape(c["destino"])}</td><td>{c["portas_distintas"]}</td></tr>'
        html += "</table>"
    html += "</div></section>"
    return html


def generate_html(diff, label_antes, label_depois, output_path):
    v = diff["volume"]
    sign_pkt = "+" if v["pacotes_delta"] > 0 else ""
    sign_bytes = "+" if v["bytes_delta"] > 0 else ""

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Comparação de Capturas — Antes/Depois</title>
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
</style>
</head>
<body>
<h1>Comparação de Capturas — Antes / Depois</h1>
<p class="meta">Antes: {escape(label_antes)}<br>
Depois: {escape(label_depois)}<br>
Relatório gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<div class="summary">
  <div class="badge"><div style="font-size:1.6em;">{v['pacotes_antes']} → {v['pacotes_depois']}</div><div>Pacotes ({sign_pkt}{v['pacotes_delta']})</div></div>
  <div class="badge"><div style="font-size:1.6em;">{pr.format_bytes(v['bytes_antes'])} → {pr.format_bytes(v['bytes_depois'])}</div><div>Volume ({sign_bytes}{pr.format_bytes(abs(v['bytes_delta']))})</div></div>
</div>
"""

    html += render_scan_diff(diff["varreduras"])
    html += render_counter_diff_section("Protocolos", diff["protocolos"], "Protocolo")
    html += render_talkers_diff(diff["talkers"])
    html += render_counter_diff_section("Portas de destino", diff["portas"], "Porta")
    html += render_counter_diff_section("Consultas DNS", diff["dns"], "Nome consultado")
    html += render_counter_diff_section("SNI (TLS)", diff["tls_sni"], "SNI")

    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def export_csv(rows, fieldnames, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_counter_diff_csv(diff, path):
    rows = []
    for item in diff["novos"]:
        rows.append({"item": item["chave"], "status": "novo", "antes": "", "depois": item["depois"], "delta": ""})
    for item in diff["sumidos"]:
        rows.append({"item": item["chave"], "status": "sumiu", "antes": item["antes"], "depois": "", "delta": ""})
    for item in diff["variacao"]:
        rows.append({"item": item["chave"], "status": "variou", "antes": item["antes"],
                      "depois": item["depois"], "delta": item["delta"]})
    export_csv(rows, ["item", "status", "antes", "depois", "delta"], path)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python3 compare_captures.py <antes.pcap|antes.json> <depois.pcap|depois.json> <saida.html>")
        sys.exit(1)

    path_before, path_after, out_file = sys.argv[1], sys.argv[2], sys.argv[3]

    print(f"[*] Analisando 'antes': {path_before}")
    summary_before, dns_before, tls_before = load_analysis(path_before)

    print(f"[*] Analisando 'depois': {path_after}")
    summary_after, dns_after, tls_after = load_analysis(path_after)

    diff_data = build_diff(summary_before, dns_before, tls_before,
                            summary_after, dns_after, tls_after)

    generate_html(diff_data, os.path.basename(path_before), os.path.basename(path_after), out_file)

    out_base, _ = os.path.splitext(out_file)

    with open(f"{out_base}.json", "w", encoding="utf-8") as f:
        json.dump(diff_data, f, ensure_ascii=False, indent=2)

    export_counter_diff_csv(diff_data["protocolos"], f"{out_base}_protocolos_diff.csv")
    export_counter_diff_csv(diff_data["portas"], f"{out_base}_portas_diff.csv")
    export_counter_diff_csv(diff_data["dns"], f"{out_base}_dns_diff.csv")
    export_counter_diff_csv(diff_data["tls_sni"], f"{out_base}_tls_sni_diff.csv")

    talkers_rows = (
        [{"host_a": t["host_a"], "host_b": t["host_b"], "status": "novo",
          "bytes_antes": "", "bytes_depois": t["bytes"], "delta": ""} for t in diff_data["talkers"]["novos"]]
        + [{"host_a": t["host_a"], "host_b": t["host_b"], "status": "sumiu",
            "bytes_antes": t["bytes"], "bytes_depois": "", "delta": ""} for t in diff_data["talkers"]["sumidos"]]
        + [{"host_a": t["host_a"], "host_b": t["host_b"], "status": "variou",
            "bytes_antes": t["bytes_antes"], "bytes_depois": t["bytes_depois"],
            "delta": t["delta_bytes"]} for t in diff_data["talkers"]["variacao"]]
    )
    export_csv(talkers_rows, ["host_a", "host_b", "status", "bytes_antes", "bytes_depois", "delta"],
               f"{out_base}_talkers_diff.csv")

    print(f"[*] Relatório HTML: {out_file}")
    print(f"[*] Dados completos (JSON): {out_base}.json")
    v = diff_data["volume"]
    print(f"[*] Pacotes: {v['pacotes_antes']} -> {v['pacotes_depois']} ({'+' if v['pacotes_delta']>=0 else ''}{v['pacotes_delta']})")