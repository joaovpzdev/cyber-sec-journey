#!/usr/bin/env python3
"""
recon_report.py
Gera um relatorio HTML autocontido a partir do banco SQLite de um
workspace do recon-ng (~/.recon-ng/workspaces/<workspace>/*.db).

Diferente do SpiderFoot, o recon-ng guarda os achados em varias tabelas
relacionais (domains, hosts, contacts, vulnerabilities, ports, etc.),
e o NOME EXATO das colunas pode variar entre versoes. Por isso, este
script LE O SCHEMA DIRETO DO BANCO em vez de assumir nomes de coluna
fixos -- ele funciona com qualquer tabela que o recon-ng tenha criado,
mesmo que o conjunto de colunas mude numa atualizacao futura.

Uso:
    python3 recon_report.py CAMINHO -o relatorio.html -t "alvo.com"

CAMINHO pode ser:
    - o diretorio do workspace (ex: ~/.recon-ng/workspaces/exemplo/)
      -> o script procura o arquivo .db dentro dele
    - o caminho direto para o arquivo .db

Dependencias: nenhuma (usa so a biblioteca padrao do Python 3)
"""
import argparse
import glob
import html
import json
import os
import sqlite3
import sys
from datetime import datetime

# Tabelas internas/de controle do recon-ng que nao sao achados de OSINT
# e por isso ficam de fora do relatorio.
SKIP_TABLES = {
    "sqlite_sequence",
    "schema_migrations",
    "schema_version",
    "config",
    "keys",
    "dashboard",
}


def find_db(path):
    if os.path.isfile(path):
        return path
    if os.path.isdir(path):
        candidates = sorted(glob.glob(os.path.join(path, "*.db")))
        if not candidates:
            sys.exit(f"Nenhum arquivo .db encontrado em: {path}")
        if len(candidates) > 1:
            # prioriza um arquivo chamado exatamente 'data.db', se existir
            preferred = [c for c in candidates if os.path.basename(c) == "data.db"]
            chosen = preferred[0] if preferred else max(candidates, key=os.path.getmtime)
            print(f"Aviso: mais de um .db encontrado, usando: {chosen}", file=sys.stderr)
            return chosen
        return candidates[0]
    sys.exit(f"Caminho nao encontrado: {path}")


def load_tables(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [r[0] for r in cur.fetchall()]

    tables = []
    for name in all_tables:
        if name in SKIP_TABLES or name.startswith("sqlite_"):
            continue
        try:
            cur.execute(f'SELECT * FROM "{name}"')
        except sqlite3.OperationalError:
            continue
        rows = cur.fetchall()
        if not rows:
            continue
        columns = [d[0] for d in cur.description]
        tables.append({
            "name": name,
            "columns": columns,
            "rows": [dict(r) for r in rows],
        })
    conn.close()
    return tables


def esc(s):
    if s is None:
        return ""
    return html.escape(str(s))


def humanize(name):
    return name.replace("_", " ").strip().capitalize()


def build_table_section(table):
    name = table["name"]
    columns = table["columns"]
    rows = table["rows"]
    anchor = f"tbl-{name}"

    thead = "".join(f"<th>{esc(humanize(c))}</th>" for c in columns)
    tbody_rows = []
    for row in rows:
        cells = "".join(f"<td>{esc(row.get(c))}</td>" for c in columns)
        tbody_rows.append(f"<tr>{cells}</tr>")
    tbody = "\n".join(tbody_rows)

    return f"""
  <section id="{anchor}">
    <h2>{esc(humanize(name))} <span class="count-badge">{len(rows)}</span></h2>
    <div class="toolbar">
      <input type="text" class="search-box" data-target="{anchor}-body" placeholder="Buscar em {esc(humanize(name))}...">
    </div>
    <div class="panel table-scroll">
      <table>
        <thead><tr>{thead}</tr></thead>
        <tbody id="{anchor}-body">{tbody}</tbody>
      </table>
    </div>
  </section>
"""


def build_html(tables, target, workspace_name):
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_rows = sum(len(t["rows"]) for t in tables)

    nav_items = "\n".join(
        f'<a href="#tbl-{t["name"]}">{esc(humanize(t["name"]))} '
        f'<span class="count-badge">{len(t["rows"])}</span></a>'
        for t in tables
    )

    sections_html = "\n".join(build_table_section(t) for t in tables)

    if not tables:
        sections_html = '<p class="empty-msg">Nenhum achado encontrado neste workspace ainda.</p>'
        nav_items = ""

    return TEMPLATE.format(
        target=esc(target) if target else esc(workspace_name),
        workspace=esc(workspace_name),
        generated_at=generated_at,
        total_tables=len(tables),
        total_rows=total_rows,
        nav_items=nav_items,
        sections_html=sections_html,
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Relatorio OSINT (recon-ng) - {target}</title>
<style>
  :root {{
    --bg: #0f1216; --panel: #171b21; --border: #262c35; --text: #e6e9ef;
    --muted: #8a93a3; --accent: #4f8cff; --accent-alt: #ff9f4f;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.5;
  }}
  header {{
    padding: 28px 32px; border-bottom: 1px solid var(--border);
    background: linear-gradient(135deg, #171b21, #11141a);
  }}
  header h1 {{ margin: 0 0 4px; font-size: 22px; }}
  header .meta {{ color: var(--muted); font-size: 13px; }}
  .layout {{ display: flex; max-width: 1200px; margin: 0 auto; align-items: flex-start; }}
  nav {{
    position: sticky; top: 0; width: 220px; flex-shrink: 0; padding: 24px 12px;
    display: flex; flex-direction: column; gap: 4px;
  }}
  nav a {{
    color: var(--muted); text-decoration: none; font-size: 13px; padding: 8px 10px;
    border-radius: 6px; display: flex; justify-content: space-between; gap: 8px;
  }}
  nav a:hover {{ background: var(--panel); color: var(--text); }}
  main {{ flex: 1; padding: 24px 32px 64px; min-width: 0; }}
  .stats {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 28px; }}
  .stat {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
    padding: 16px 20px; min-width: 140px; flex: 1;
  }}
  .stat .num {{ font-size: 26px; font-weight: 700; }}
  .stat .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
  section {{ margin-bottom: 36px; scroll-margin-top: 16px; }}
  section h2 {{
    font-size: 16px; letter-spacing: .02em; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
  }}
  .count-badge {{
    background: var(--accent); color: #08111f; font-size: 11px; font-weight: 700;
    padding: 2px 7px; border-radius: 999px;
  }}
  .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
  .table-scroll {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; white-space: nowrap; }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; }}
  tr:last-child td {{ border-bottom: none; }}
  td {{ white-space: normal; max-width: 420px; word-break: break-word; }}
  .toolbar {{ margin-bottom: 10px; }}
  .search-box {{
    background: var(--panel); border: 1px solid var(--border); color: var(--text);
    padding: 8px 12px; border-radius: 8px; font-size: 13px; width: 100%; max-width: 320px;
  }}
  tbody tr[hidden] {{ display: none; }}
  .empty-msg {{ color: var(--muted); }}
  @media (max-width: 800px) {{
    .layout {{ flex-direction: column; }}
    nav {{ position: static; width: 100%; flex-direction: row; flex-wrap: wrap; }}
  }}
</style>
</head>
<body>

<header>
  <h1>Relatorio OSINT (recon-ng) &mdash; {target}</h1>
  <div class="meta">Workspace: {workspace} &middot; Gerado em {generated_at} &middot; {total_tables} tabelas com dados, {total_rows} registros no total</div>
</header>

<div class="layout">
  <nav>
    {nav_items}
  </nav>
  <main>
    {sections_html}
  </main>
</div>

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
    parser = argparse.ArgumentParser(description="Gera relatorio HTML a partir do banco de um workspace do recon-ng")
    parser.add_argument("path", help="Diretorio do workspace do recon-ng, ou caminho direto para o .db")
    parser.add_argument("-o", "--output", default="relatorio.html", help="Arquivo HTML de saida (padrao: relatorio.html)")
    parser.add_argument("-t", "--target", default="", help="Nome do alvo investigado (aparece no titulo)")
    args = parser.parse_args()

    db_path = find_db(args.path)
    workspace_name = os.path.basename(os.path.normpath(os.path.dirname(db_path))) or os.path.basename(db_path)
    tables = load_tables(db_path)

    html_out = build_html(tables, args.target, workspace_name)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_out)

    total_rows = sum(len(t["rows"]) for t in tables)
    print(f"OK: {len(tables)} tabelas com dados, {total_rows} registros -> {args.output}")


if __name__ == "__main__":
    main()