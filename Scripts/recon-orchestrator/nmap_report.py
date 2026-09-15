#!/usr/bin/env python3
"""
nmap_report.py — Parseia XML do Nmap (+ outputs opcionais do Gobuster) e
gera relatório HTML consolidado.

Requisitos: o XML deve ter sido gerado com -oX ou -oA, idealmente com
    nmap -sV --script vulners -oX scan.xml <alvo>   (recomendado, CVEs com score)

Opcionalmente, se existirem arquivos "gobuster_<porta>.txt" na MESMA pasta
do XML (gerados com `gobuster dir ... -o gobuster_<porta>.txt -q`), eles são
detectados automaticamente e incluídos como seção de enumeração web para a
porta correspondente. Ver run_recon.sh, que já gera esses arquivos.

Uso:
    python3 nmap_report.py <arquivo.xml> <saida.html>

Além do HTML, o script gera automaticamente (mesmo diretório/nome-base
do arquivo de saída):
    <saida>.json          — todos os achados estruturados
    <saida>_portas.csv     — portas abertas por host
    <saida>_cves.csv       — CVEs identificados
    <saida>_gobuster.csv   — achados do Gobuster (se houver)

Referência da estrutura XML: https://nmap.org/book/output-formats-xml-output.html
(DTD oficial: /usr/share/nmap/nmap.dtd)
Formato do output do Gobuster: https://github.com/OJ/gobuster

Padrão de identificador CVE conforme MITRE:
https://cve.mitre.org/cve/identifiers/syntaxchange.html

AVISO: use apenas contra alvos para os quais você tem autorização
explícita para realizar testes de segurança.
"""

import sys
import os
import re
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from html import escape

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}")

# Portas web reconhecidas — usadas para saber em quais portas procurar
# arquivos de output do Gobuster (gobuster_<porta>.txt)
WEB_SERVICES = {"http", "https", "http-proxy", "http-alt", "ssl/http"}

# Formato de linha do Gobuster em modo quiet (-q), dir mode:
#   /admin                (Status: 301) [Size: 178] [--> /admin/]
#   /images               (Status: 200) [Size: 1234]
GOBUSTER_LINE = re.compile(
    r'^(?P<path>\S+)\s+\(Status:\s*(?P<status>\d+)\)\s*\[Size:\s*(?P<size>\d+)\]'
    r'(?:\s*\[-->\s*(?P<redirect>\S+)\])?'
)


def parse_gobuster_file(path):
    """Parseia um arquivo de output do Gobuster (modo -q) em uma lista de achados."""
    findings = []
    if not os.path.isfile(path):
        return findings

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = GOBUSTER_LINE.match(line)
            if m:
                findings.append({
                    "path": m.group("path"),
                    "status": m.group("status"),
                    "size": m.group("size"),
                    "redirect": m.group("redirect") or "",
                })
    return findings


def status_color(status):
    """Cor de destaque por faixa de status HTTP."""
    code = int(status)
    if 200 <= code < 300:
        return "#27ae60"   # verde — encontrado
    if 300 <= code < 400:
        return "#2980b9"   # azul — redirect
    if code == 403:
        return "#e67e22"   # laranja — proibido (ainda existe!)
    if 400 <= code < 500:
        return "#95a5a6"   # cinza — erro de cliente
    return "#c0392b"       # vermelho — erro de servidor


def parse_nmap_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    scan_info = {
        "start": root.get("startstr", "N/A"),
        "args": root.get("args", "N/A"),
    }

    hosts = []
    for host in root.findall("host"):
        status = host.find("status")
        if status is not None and status.get("state") != "up":
            continue

        addr_elem = host.find("address")
        ip = addr_elem.get("addr") if addr_elem is not None else "desconhecido"

        hostname_elem = host.find("hostnames/hostname")
        hostname = hostname_elem.get("name") if hostname_elem is not None else ""

        # --- Portas + serviços + scripts NSE por porta ---
        ports = []
        ports_elem = host.find("ports")
        if ports_elem is not None:
            for port in ports_elem.findall("port"):
                state = port.find("state")
                if state is None or state.get("state") != "open":
                    continue

                service = port.find("service")

                scripts = []
                for script in port.findall("script"):
                    output = script.get("output", "").strip()
                    scripts.append({
                        "id": script.get("id"),
                        "output": output,
                        "cves": sorted(set(CVE_PATTERN.findall(output))),
                    })

                ports.append({
                    "port": port.get("portid"),
                    "protocol": port.get("protocol"),
                    "service": service.get("name") if service is not None else "?",
                    "product": service.get("product", "") if service is not None else "",
                    "version": service.get("version", "") if service is not None else "",
                    "scripts": scripts,
                })

        # --- Scripts NSE a nível de host (ex.: smb-vuln-*) ---
        host_scripts = []
        hostscript_elem = host.find("hostscript")
        if hostscript_elem is not None:
            for script in hostscript_elem.findall("script"):
                output = script.get("output", "").strip()
                host_scripts.append({
                    "id": script.get("id"),
                    "output": output,
                    "cves": sorted(set(CVE_PATTERN.findall(output))),
                })

        hosts.append({
            "ip": ip,
            "hostname": hostname,
            "ports": ports,
            "host_scripts": host_scripts,
        })

    return scan_info, hosts


def collect_all_cves(hosts):
    """Consolida todos os CVEs encontrados, mapeados para host/porta de origem."""
    findings = []
    for h in hosts:
        for p in h["ports"]:
            for s in p["scripts"]:
                for cve in s["cves"]:
                    findings.append({
                        "cve": cve, "host": h["ip"],
                        "port": p["port"], "script": s["id"],
                    })
        for s in h["host_scripts"]:
            for cve in s["cves"]:
                findings.append({
                    "cve": cve, "host": h["ip"],
                    "port": "-", "script": s["id"],
                })
    return findings


def collect_all_ports(hosts):
    """Achata a lista de portas abertas de todos os hosts, para exportação tabular."""
    rows = []
    for h in hosts:
        for p in h["ports"]:
            rows.append({
                "host": h["ip"],
                "hostname": h["hostname"],
                "port": p["port"],
                "protocol": p["protocol"],
                "service": p["service"],
                "product": p["product"],
                "version": p["version"],
            })
    return rows


def collect_all_gobuster(hosts, base_dir):
    """Achata os achados do Gobuster de todas as portas web, para exportação tabular."""
    rows = []
    if not base_dir:
        return rows
    for h in hosts:
        for p in h["ports"]:
            if p["service"] not in WEB_SERVICES:
                continue
            gobuster_path = os.path.join(base_dir, f'gobuster_{p["port"]}.txt')
            for f in parse_gobuster_file(gobuster_path):
                rows.append({
                    "host": h["ip"],
                    "port": p["port"],
                    "path": f["path"],
                    "status": f["status"],
                    "size": f["size"],
                    "redirect": f["redirect"],
                })
    return rows


def export_json(scan_info, hosts, cve_findings, gobuster_findings, path):
    """Exporta todos os achados estruturados em um único arquivo JSON."""
    data = {
        "scan_info": scan_info,
        "generated_at": datetime.now().isoformat(),
        "hosts": hosts,
        "cve_findings": cve_findings,
        "gobuster_findings": gobuster_findings,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_csv(rows, fieldnames, path):
    """Exporta uma lista de dicts para CSV com o cabeçalho fornecido."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_scripts(scripts):
    block = ""
    for s in scripts:
        cve_tags = "".join(
            f'<span style="background:#c0392b;color:white;padding:2px 6px;'
            f'border-radius:3px;font-size:0.8em;margin-right:4px;">{c}</span>'
            for c in s["cves"]
        )
        block += (
            '<div style="background:#fdf3f3;border-left:4px solid #c0392b;'
            'padding:8px;margin:6px 0;">'
            f'<strong>{escape(s["id"])}</strong> {cve_tags}'
            f'<pre style="white-space:pre-wrap;margin:6px 0 0;">{escape(s["output"])}</pre>'
            '</div>'
        )
    return block


def render_gobuster(findings):
    if not findings:
        return "<p><em>Nenhum caminho encontrado (ou arquivo do Gobuster ausente/vazio).</em></p>"

    block = "<table><tr><th>Caminho</th><th>Status</th><th>Tamanho</th><th>Redirect</th></tr>"
    for f in findings:
        color = status_color(f["status"])
        block += (
            f'<tr><td>{escape(f["path"])}</td>'
            f'<td><span style="color:{color};font-weight:bold;">{f["status"]}</span></td>'
            f'<td>{f["size"]}</td>'
            f'<td>{escape(f["redirect"])}</td></tr>'
        )
    block += "</table>"
    return block


def generate_html(scan_info, hosts, output_path, base_dir=None):
    cve_findings = collect_all_cves(hosts)

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Relatório de Recon - Nmap</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
  h1 {{ color: #2c3e50; }}
  .host {{ background: white; padding: 15px; margin-bottom: 20px; border-radius: 6px;
           box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #34495e; color: white; }}
  .meta {{ color: #666; font-size: 0.9em; }}
  .cve-summary {{ background: #fff3cd; border: 1px solid #ffeeba; padding: 12px;
                   border-radius: 6px; margin-bottom: 20px; }}
</style>
</head>
<body>
<h1>Relatório de Reconhecimento</h1>
<p class="meta">Scan iniciado em: {escape(scan_info['start'])}<br>
Comando: <code>{escape(scan_info['args'])}</code><br>
Relatório gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""

    # --- Sumário de CVEs no topo ---
    if cve_findings:
        html += f'<div class="cve-summary"><strong>{len(cve_findings)} referência(s) de CVE encontradas:</strong>'
        html += "<table><tr><th>CVE</th><th>Host</th><th>Porta</th><th>Script</th></tr>"
        for f in cve_findings:
            html += (f'<tr><td>{f["cve"]}</td><td>{f["host"]}</td>'
                      f'<td>{f["port"]}</td><td>{escape(f["script"])}</td></tr>')
        html += "</table></div>"
    else:
        html += '<div class="cve-summary">Nenhum CVE identificado nos scripts NSE.</div>'

    # --- Detalhe por host ---
    for h in hosts:
        title = f'{h["ip"]}' + (f' ({escape(h["hostname"])})' if h["hostname"] else "")
        html += f'<div class="host"><h2>{title}</h2>'

        if h["ports"]:
            html += "<table><tr><th>Porta</th><th>Protocolo</th><th>Serviço</th><th>Produto/Versão</th></tr>"
            for p in h["ports"]:
                prod_ver = f'{p["product"]} {p["version"]}'.strip() or "-"
                html += (f'<tr><td>{p["port"]}</td><td>{p["protocol"]}</td>'
                          f'<td>{p["service"]}</td><td>{escape(prod_ver)}</td></tr>')
            html += "</table>"

            for p in h["ports"]:
                if p["scripts"]:
                    html += f'<h3>Scripts NSE — Porta {p["port"]}</h3>'
                    html += render_scripts(p["scripts"])

                # NOVO: seção de enumeração web (Gobuster), se aplicável
                if p["service"] in WEB_SERVICES and base_dir:
                    gobuster_path = os.path.join(base_dir, f'gobuster_{p["port"]}.txt')
                    if os.path.isfile(gobuster_path):
                        gobuster_findings = parse_gobuster_file(gobuster_path)
                        html += f'<h3>Enumeração Web (Gobuster) — Porta {p["port"]}</h3>'
                        html += render_gobuster(gobuster_findings)
        else:
            html += "<p>Nenhuma porta aberta detectada.</p>"

        if h["host_scripts"]:
            html += "<h3>Scripts NSE — Host</h3>"
            html += render_scripts(h["host_scripts"])

        html += "</div>"

    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 nmap_report.py <arquivo.xml> <saida.html>")
        sys.exit(1)

    xml_file, out_file = sys.argv[1], sys.argv[2]
    # Arquivos gobuster_<porta>.txt são procurados na mesma pasta do XML
    base_dir = os.path.dirname(os.path.abspath(xml_file))

    info, hosts_data = parse_nmap_xml(xml_file)
    generate_html(info, hosts_data, out_file, base_dir=base_dir)

    # --- Exportações JSON/CSV, nomeadas a partir do HTML de saída ---
    out_base, _ = os.path.splitext(out_file)
    cve_findings = collect_all_cves(hosts_data)
    port_rows = collect_all_ports(hosts_data)
    gobuster_rows = collect_all_gobuster(hosts_data, base_dir)

    json_file = f"{out_base}.json"
    export_json(info, hosts_data, cve_findings, gobuster_rows, json_file)

    ports_csv = f"{out_base}_portas.csv"
    export_csv(port_rows,
               ["host", "hostname", "port", "protocol", "service", "product", "version"],
               ports_csv)

    cves_csv = f"{out_base}_cves.csv"
    export_csv(cve_findings, ["cve", "host", "port", "script"], cves_csv)

    if gobuster_rows:
        gobuster_csv = f"{out_base}_gobuster.csv"
        export_csv(gobuster_rows,
                   ["host", "port", "path", "status", "size", "redirect"],
                   gobuster_csv)
    else:
        gobuster_csv = None

    print(f"[*] Relatório HTML: {out_file}")
    print(f"[*] Dados completos (JSON): {json_file}")
    print(f"[*] Portas (CSV): {ports_csv}")
    print(f"[*] CVEs (CSV): {cves_csv}")
    if gobuster_csv:
        print(f"[*] Gobuster (CSV): {gobuster_csv}")
    print(f"[*] CVEs encontrados: {len(cve_findings)}")