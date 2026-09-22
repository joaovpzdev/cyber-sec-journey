#!/usr/bin/env python3
"""
recon_pipeline_report.py
Combina a saida de subfinder (subdominios), httpx (hosts vivos, JSONL) e
nuclei (vulnerabilidades, JSONL) num unico relatorio HTML autocontido.

Assim como no kit do recon-ng, os nomes de campo exatos do JSON do httpx e
do nuclei podem variar um pouco entre versoes. Por isso este script tenta
reconhecer os campos mais comuns e documentados (url, status_code, title,
tech, webserver / template-id, info.name, info.severity, matched-at...),
mas SEMPRE guarda o JSON bruto de cada achado num details/summary
expansivel -- se algum campo nao for reconhecido, a informacao continua
visivel, so nao ganha uma coluna dedicada.

Uso:
    python3 recon_pipeline_report.py \\
        --subs subs.txt --httpx httpx.jsonl --nuclei nuclei.jsonl \\
        -o relatorio.html -t alvo.com

Qualquer uma das 3 entradas pode ser omitida (ex: se voce pulou o nuclei).

Dependencias: nenhuma (usa so a biblioteca padrao do Python 3)
"""
import argparse
import html
import json
import os
from datetime import datetime

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info", "unknown"]
SEVERITY_COLOR = {
    "critical": "#ff4d6d",
    "high": "#ff7a4f",
    "medium": "#ff9f4f",
    "low": "#f5d90a",
    "info": "#4f8cff",
    "unknown": "#8a93a3",
}


def esc(s):
    if s is None:
        return ""
    return html.escape(str(s))


def read_lines(path):
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as f:
        return [ln.strip() for ln in f if ln.strip()]


def read_jsonl(path):
    items = []
    for ln in read_lines(path):
        try:
            items.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return items


def first(d, *keys, default=""):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] not in (None, ""):
            return d[k]
    return default


def build_subs_section(subs):
    if not subs:
        return '<section id="subs"><h2>Subdominios <span class="count-badge">0</span></h2><p class="empty-msg">Nenhum dado.</p></section>'
    rows = "\n".join(f"<tr><td>{esc(s)}</td></tr>" for s in subs)
    return f"""
  <section id="subs">
    <h2>Subdominios encontrados <span class="count-badge">{len(subs)}</span></h2>
    <div class="toolbar"><input type="text" class="search-box" data-target="subs-body" placeholder="Buscar subdominio..."></div>
    <div class="panel table-scroll">
      <table><thead><tr><th>Subdominio</th></tr></thead><tbody id="subs-body">{rows}</tbody></table>
    </div>
  </section>
"""


def build_httpx_section(items):
    if not items:
        return '<section id="hosts"><h2>Hosts vivos <span class="count-badge">0</span></h2><p class="empty-msg">Nenhum dado.</p></section>'
    rows = []
    for it in items:
        url = first(it, "url", "input", default="?")
        status = first(it, "status_code", "status-code", "statuscode", default="")
        title = first(it, "title", default="")
        tech = it.get("tech") if isinstance(it, dict) else None
        tech_str = ", ".join(tech) if isinstance(tech, list) else esc(tech or "")
        server = first(it, "webserver", "web-server", "server", default="")
        raw = esc(json.dumps(it, ensure_ascii=False, indent=2))
        rows.append(f"""<tr>
            <td>{esc(url)}</td><td>{esc(status)}</td><td>{esc(title)}</td>
            <td>{tech_str}</td><td>{esc(server)}</td>
            <td><details><summary>JSON</summary><pre>{raw}</pre></details></td>
        </tr>""")
    tbody = "\n".join(rows)
    return f"""
  <section id="hosts">
    <h2>Hosts vivos (httpx) <span class="count-badge">{len(items)}</span></h2>
    <div class="toolbar"><input type="text" class="search-box" data-target="hosts-body" placeholder="Buscar host..."></div>
    <div class="panel table-scroll">
      <table>
        <thead><tr><th>URL</th><th>Status</th><th>Titulo</th><th>Tecnologias</th><th>Servidor</th><th>Detalhe</th></tr></thead>
        <tbody id="hosts-body">{tbody}</tbody>
      </table>
    </div>
  </section>
"""


def build_nuclei_section(items):
    if not items:
        return '<section id="vulns"><h2>Achados do nuclei <span class="count-badge">0</span></h2><p class="empty-msg">Nenhum dado (ou nuclei nao foi rodado).</p></section>'

    def sev_key(it):
        info = it.get("info", {}) if isinstance(it, dict) else {}
        sev = (first(info, "severity") or first(it, "severity") or "unknown").lower()
        return SEVERITY_ORDER.index(sev) if sev in SEVERITY_ORDER else len(SEVERITY_ORDER)

    items_sorted = sorted(items, key=sev_key)
    counts = {}
    rows = []
    for it in items_sorted:
        info = it.get("info", {}) if isinstance(it, dict) else {}
        name = first(info, "name") or first(it, "name") or "?"
        sev = (first(info, "severity") or first(it, "severity") or "unknown").lower()
        if sev not in SEVERITY_COLOR:
            sev = "unknown"
        counts[sev] = counts.get(sev, 0) + 1
        template_id = first(it, "template-id", "template_id", "templateID", default="")
        matched = first(it, "matched-at", "matched_at", "host", default="")
        color = SEVERITY_COLOR[sev]
        raw = esc(json.dumps(it, ensure_ascii=False, indent=2))
        rows.append(f"""<tr data-sev="{sev}">
            <td><span class="sev-badge" style="background:{color}">{esc(sev)}</span></td>
            <td>{esc(name)}</td><td>{esc(template_id)}</td><td>{esc(matched)}</td>
            <td><details><summary>JSON</summary><pre>{raw}</pre></details></td>
        </tr>""")

    summary_chips = " ".join(
        f'<span class="sev-badge" style="background:{SEVERITY_COLOR.get(s, "#8a93a3")}">{s}: {c}</span>'
        for s, c in sorted(counts.items(), key=lambda kv: SEVERITY_ORDER.index(kv[0]) if kv[0] in SEVERITY_ORDER else 99)
    )
    tbody = "\n".join(rows)
    return f"""
  <section id="vulns">
    <h2>Achados do nuclei <span class="count-badge">{len(items)}</span></h2>
    <div class="sev-summary">{summary_chips}</div>
    <div class="toolbar"><input type="text" class="search-box" data-target="vulns-body" placeholder="Buscar achado..."></div>
    <div class="panel table-scroll">
      <table>
        <thead><tr><th>Severidade</th><th>Nome</th><th>Template</th><th>Alvo</th><th>Detalhe</th></tr></thead>
        <tbody id="vulns-body">{tbody}</tbody>
      </table>
    </div>
  </section>
"""


def build_html(target, subs, httpx_items, nuclei_items):
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    sections = (
        build_subs_section(subs)
        + build_httpx_section(httpx_items)
        + build_nuclei_section(nuclei_items)
    )
    return TEMPLATE.format(
        target=esc(target) if target else "Alvo nao especificado",
        generated_at=generated_at,
        n_subs=len(subs),
        n_hosts=len(httpx_items),
        n_vulns=len(nuclei_items),
        sections=sections,
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Pipeline de Recon - {target}</title>
<style>
  :root {{
    --bg: #0f1216; --panel: #171b21; --border: #262c35; --text: #e6e9ef;
    --muted: #8a93a3; --accent: #4f8cff;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
  header {{ padding: 28px 32px; border-bottom: 1px solid var(--border); background: linear-gradient(135deg, #171b21, #11141a); }}
  header h1 {{ margin: 0 0 4px; font-size: 22px; }}
  header .meta {{ color: var(--muted); font-size: 13px; }}
  main {{ max-width: 1200px; margin: 0 auto; padding: 24px 32px 64px; }}
  .stats {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 28px; }}
  .stat {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px; min-width: 140px; flex: 1; }}
  .stat .num {{ font-size: 26px; font-weight: 700; }}
  .stat .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
  section {{ margin-bottom: 36px; }}
  section h2 {{ font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }}
  .count-badge {{ background: var(--accent); color: #08111f; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 999px; }}
  .sev-badge {{ color: #08111f; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 999px; display: inline-block; }}
  .sev-summary {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }}
  .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
  .table-scroll {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; }}
  tr:last-child td {{ border-bottom: none; }}
  td {{ max-width: 380px; word-break: break-word; }}
  details summary {{ cursor: pointer; color: var(--accent); font-size: 12px; }}
  details pre {{ background: #0c0f13; padding: 10px; border-radius: 6px; font-size: 11px; overflow-x: auto; max-width: 480px; }}
  .toolbar {{ margin-bottom: 10px; }}
  .search-box {{ background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 8px; font-size: 13px; width: 100%; max-width: 320px; }}
  tbody tr[hidden] {{ display: none; }}
  .empty-msg {{ color: var(--muted); }}
</style>
</head>
<body>

<header>
  <h1>Pipeline de Recon &mdash; {target}</h1>
  <div class="meta">subfinder &rarr; httpx &rarr; nuclei &middot; Gerado em {generated_at}</div>
</header>

<main>
  <div class="stats">
    <div class="stat"><div class="num">{n_subs}</div><div class="label">Subdominios</div></div>
    <div class="stat"><div class="num">{n_hosts}</div><div class="label">Hosts vivos</div></div>
    <div class="stat"><div class="num">{n_vulns}</div><div class="label">Achados do nuclei</div></div>
  </div>

  {sections}
</main>

<script>
  document.querySelectorAll('.search-box').forEach(function (box) {{
    box.addEventListener('input', function () {{
      var q = box.value.toLowerCase();
      var body = document.getElementById(box.dataset.target);
      if (!body) return;
      Array.from(body.querySelectorAll('tr')).forEach(function (row) {{
        row.hidden = q.length > 0 && !row.textContent.toLowerCase().includes(q);
      }});
    }});
  }});
</script>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Combina saida de subfinder + httpx + nuclei num relatorio HTML")
    parser.add_argument("--subs", help="Arquivo de subdominios do subfinder (texto, um por linha)")
    parser.add_argument("--httpx", help="Arquivo JSONL de saida do httpx")
    parser.add_argument("--nuclei", help="Arquivo JSONL de saida do nuclei")
    parser.add_argument("-o", "--output", default="relatorio.html", help="Arquivo HTML de saida")
    parser.add_argument("-t", "--target", default="", help="Nome do alvo (aparece no titulo)")
    args = parser.parse_args()

    subs = read_lines(args.subs)
    httpx_items = read_jsonl(args.httpx)
    nuclei_items = read_jsonl(args.nuclei)

    html_out = build_html(args.target, subs, httpx_items, nuclei_items)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"OK: {len(subs)} subdominios, {len(httpx_items)} hosts vivos, {len(nuclei_items)} achados -> {args.output}")


if __name__ == "__main__":
    main()