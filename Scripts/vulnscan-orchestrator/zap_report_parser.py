#!/usr/bin/env python3
"""
zap_report_parser.py — Parseia o relatório JSON do OWASP ZAP
(gerado com a flag -J do zap-baseline.py / zap-full-scan.py) e produz
um relatório HTML consolidado, além de exports em JSON e CSV.

Uso:
    python3 zap_report_parser.py <report.json> <saida.html>

Além do HTML, gera automaticamente (mesmo nome-base da saída):
    <saida>.json           — achados normalizados
    <saida>_alertas.csv     — um alerta por linha (host, risco, CWE, etc.)
    <saida>_ocorrencias.csv — uma linha por URL/instância afetada

Referências:
- Estrutura do relatório: https://www.zaproxy.org/docs/docker/baseline-scan/
- API/objeto de alertas: https://www.zaproxy.org/docs/api/
- CWE (Common Weakness Enumeration): https://cwe.mitre.org/

AVISO: use apenas contra alvos para os quais você tem autorização
explícita para realizar testes de segurança.
"""

import sys
import os
import json
import csv
import re
from datetime import datetime
from html import escape

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}")

# Nomenclatura padrão de riskcode usada pelo ZAP
RISK_LABELS = {
    "3": "Alto",
    "2": "Médio",
    "1": "Baixo",
    "0": "Informativo",
}
RISK_COLORS = {
    "3": "#c0392b",   # alto — vermelho
    "2": "#e67e22",   # médio — laranja
    "1": "#f1c40f",   # baixo — amarelo
    "0": "#95a5a6",   # informativo — cinza
}
RISK_ORDER = ["3", "2", "1", "0"]  # do mais crítico pro menos crítico


def parse_zap_json(json_path):
    """Lê o report.json do ZAP e normaliza em uma lista plana de alertas."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scan_info = {
        "generated": data.get("@generated", "N/A"),
        "version": data.get("@version", "N/A"),
    }

    alerts = []
    for site in data.get("site", []):
        site_name = site.get("@name", "desconhecido")
        for a in site.get("alerts", []):
            desc = (a.get("desc") or "").strip()
            solution = (a.get("solution") or "").strip()

            instances = []
            for inst in a.get("instances", []):
                instances.append({
                    "uri": inst.get("uri", ""),
                    "method": inst.get("method", ""),
                    "param": inst.get("param", ""),
                    "evidence": inst.get("evidence", ""),
                })

            alerts.append({
                "site": site_name,
                "pluginid": a.get("pluginid", ""),
                "name": a.get("name") or a.get("alert", "Alerta sem nome"),
                "riskcode": str(a.get("riskcode", "0")),
                "confidence": a.get("confidence", ""),
                "riskdesc": a.get("riskdesc", ""),
                "desc": desc,
                "solution": solution,
                "reference": (a.get("reference") or "").strip(),
                "cweid": a.get("cweid", ""),
                "wascid": a.get("wascid", ""),
                "count": a.get("count", str(len(instances))),
                "instances": instances,
                "cves": sorted(set(CVE_PATTERN.findall(desc + " " + solution))),
            })

    return scan_info, alerts


def collect_all_instances(alerts):
    """Achata alertas -> uma linha por instância/URL afetada, para CSV."""
    rows = []
    for a in alerts:
        if not a["instances"]:
            rows.append({
                "site": a["site"], "alert": a["name"], "risco": RISK_LABELS.get(a["riskcode"], "?"),
                "url": "", "method": "", "param": "", "evidence": "",
            })
            continue
        for inst in a["instances"]:
            rows.append({
                "site": a["site"], "alert": a["name"], "risco": RISK_LABELS.get(a["riskcode"], "?"),
                "url": inst["uri"], "method": inst["method"],
                "param": inst["param"], "evidence": inst["evidence"],
            })
    return rows


def export_json(scan_info, alerts, path):
    data = {
        "scan_info": scan_info,
        "generated_at": datetime.now().isoformat(),
        "alerts": alerts,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_csv(rows, fieldnames, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_alert(a):
    color = RISK_COLORS.get(a["riskcode"], "#95a5a6")
    cve_tags = "".join(
        f'<span style="background:#c0392b;color:white;padding:2px 6px;'
        f'border-radius:3px;font-size:0.8em;margin-right:4px;">{c}</span>'
        for c in a["cves"]
    )

    block = (
        f'<div style="background:white;border-left:6px solid {color};'
        f'padding:12px 16px;margin:10px 0;border-radius:4px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.08);">'
        f'<h4 style="margin:0 0 6px;">{escape(a["name"])} '
        f'<span style="background:{color};color:white;padding:2px 8px;'
        f'border-radius:3px;font-size:0.75em;">{escape(a["riskdesc"])}</span> {cve_tags}</h4>'
    )

    if a["cweid"]:
        block += (f'<p style="margin:2px 0;font-size:0.85em;color:#555;">'
                   f'CWE-{escape(str(a["cweid"]))} — '
                   f'<a href="https://cwe.mitre.org/data/definitions/{escape(str(a["cweid"]))}.html" '
                   f'target="_blank">detalhes</a></p>')

    if a["desc"]:
        block += f'<p>{escape(a["desc"])}</p>'

    if a["instances"]:
        block += ('<table style="width:100%;font-size:0.85em;"><tr>'
                   '<th>URL</th><th>Método</th><th>Parâmetro</th><th>Evidência</th></tr>')
        for inst in a["instances"][:20]:  # limita instâncias mostradas por alerta
            block += (f'<tr><td>{escape(inst["uri"])}</td><td>{escape(inst["method"])}</td>'
                       f'<td>{escape(inst["param"])}</td>'
                       f'<td><code>{escape(inst["evidence"][:120])}</code></td></tr>')
        if len(a["instances"]) > 20:
            block += (f'<tr><td colspan="4"><em>+{len(a["instances"]) - 20} '
                       f'outra(s) instância(s) — ver JSON/CSV completo</em></td></tr>')
        block += "</table>"

    if a["solution"]:
        block += f'<p style="margin-top:8px;"><strong>Correção sugerida:</strong> {escape(a["solution"])}</p>'

    block += "</div>"
    return block


def generate_html(scan_info, alerts, output_path):
    counts = {r: 0 for r in RISK_ORDER}
    for a in alerts:
        counts[a["riskcode"]] = counts.get(a["riskcode"], 0) + 1

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Relatório de Varredura de Vulnerabilidades - OWASP ZAP</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; color: #222; }}
  h1 {{ color: #2c3e50; }}
  .meta {{ color: #666; font-size: 0.9em; }}
  .summary {{ display: flex; gap: 12px; margin: 20px 0; }}
  .badge {{ flex: 1; text-align: center; color: white; padding: 14px; border-radius: 6px; }}
  table {{ border-collapse: collapse; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: #34495e; color: white; }}
  section {{ margin-bottom: 30px; }}
</style>
</head>
<body>
<h1>Relatório de Varredura de Vulnerabilidades — OWASP ZAP</h1>
<p class="meta">Versão do ZAP: {escape(scan_info['version'])}<br>
Scan gerado em: {escape(scan_info['generated'])}<br>
Relatório consolidado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<div class="summary">
"""
    for r in RISK_ORDER:
        html += (f'<div class="badge" style="background:{RISK_COLORS[r]};">'
                  f'<div style="font-size:1.8em;">{counts.get(r, 0)}</div>'
                  f'<div>{RISK_LABELS[r]}</div></div>')
    html += "</div>"

    for r in RISK_ORDER:
        group = [a for a in alerts if a["riskcode"] == r]
        if not group:
            continue
        html += f'<section><h2 style="color:{RISK_COLORS[r]};">Risco {RISK_LABELS[r]} ({len(group)})</h2>'
        for a in group:
            html += render_alert(a)
        html += "</section>"

    if not alerts:
        html += "<p>Nenhum alerta encontrado.</p>"

    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 zap_report_parser.py <report.json> <saida.html>")
        sys.exit(1)

    json_file, out_file = sys.argv[1], sys.argv[2]
    info, alerts_data = parse_zap_json(json_file)
    generate_html(info, alerts_data, out_file)

    out_base, _ = os.path.splitext(out_file)

    json_out = f"{out_base}.json"
    export_json(info, alerts_data, json_out)

    alerts_csv = f"{out_base}_alertas.csv"
    export_csv(
        [{"site": a["site"], "alert": a["name"], "risco": RISK_LABELS.get(a["riskcode"], "?"),
          "confianca": a["confidence"], "cwe": a["cweid"], "wasc": a["wascid"],
          "ocorrencias": a["count"]} for a in alerts_data],
        ["site", "alert", "risco", "confianca", "cwe", "wasc", "ocorrencias"],
        alerts_csv,
    )

    instances_csv = f"{out_base}_ocorrencias.csv"
    export_csv(
        collect_all_instances(alerts_data),
        ["site", "alert", "risco", "url", "method", "param", "evidence"],
        instances_csv,
    )

    print(f"[*] Relatório HTML: {out_file}")
    print(f"[*] Dados completos (JSON): {json_out}")
    print(f"[*] Alertas (CSV): {alerts_csv}")
    print(f"[*] Ocorrências por URL (CSV): {instances_csv}")
    print(f"[*] Total de alertas: {len(alerts_data)}")