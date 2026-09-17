#!/usr/bin/env python3
"""
spiderfoot_report.py
Gera um relatorio HTML autocontido a partir de um export CSV do SpiderFoot.

Como exportar o CSV no SpiderFoot:
    1. Abra o scan finalizado na interface web (http://127.0.0.1:5001)
    2. Va em "Browse" > selecione os resultados > "Export" > "CSV"

Uso:
    python3 spiderfoot_report.py entrada.csv -o relatorio.html -t "exemplo.com"

Dependencias: nenhuma (usa so a biblioteca padrao do Python 3)
"""
import argparse
import csv
import html
import json
import sys
from collections import Counter
from datetime import datetime

# O SpiderFoot exporta CSV em DOIS formatos diferentes dependendo de como
# os dados foram obtidos, e cada um usa nomes de coluna diferentes:
#
# 1) Interface web (Browse > Export > CSV), export de um scan ja salvo:
#       Updated, Type, Module, Source, F/P, Data
#    Aqui "Source" = dado de origem (o que levou aquele achado a ser encontrado)
#
# 2) sf.py em modo headless (linha de comando, usado pelo spiderfoot_scan.sh):
#       Source, Type, Data            (formato padrao)
#       Source, Type, Source Data, Data   (com a flag -r)
#    Aqui "Source" = MODULO que gerou o achado (nao ha coluna "Module" separada)
#
# resolve_columns detecta automaticamente qual dos dois formatos esta em uso.
WEBUI_ALIASES = {
    "type": ["Type"],
    "module": ["Module"],
    "source": ["Source"],
    "data": ["Data"],
    "updated": ["Updated", "Last Seen", "Date"],
    "fp": ["F/P", "False Positive"],
}

CLI_ALIASES = {
    "type": ["Type"],
    "module": ["Source"],       # no modo CLI, "Source" e o nome do modulo
    "source": ["Source Data"],  # so existe se o scan foi rodado com -r
    "data": ["Data"],
}


def resolve_columns(fieldnames):
    fieldnames = set(fieldnames)
    # Se existir uma coluna "Module" explicita, e o export da interface web.
    aliases = WEBUI_ALIASES if "Module" in fieldnames else CLI_ALIASES
    resolved = {}
    for key, opts in aliases.items():
        for alias in opts:
            if alias in fieldnames:
                resolved[key] = alias
                break
    return resolved


def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            sys.exit("Arquivo CSV vazio ou sem cabecalho.")
        cols = resolve_columns(reader.fieldnames)
        if "type" not in cols or "data" not in cols:
            sys.exit(
                "Nao encontrei colunas 'Type' e 'Data' no CSV.\n"
                f"Colunas encontradas: {reader.fieldnames}\n"
                "Confira se o CSV veio de um export do SpiderFoot (interface web ou sf.py -o csv)."
            )
        rows = []
        for r in reader:
            rows.append({
                "type": (r.get(cols.get("type")) or "").strip(),
                "module": (r.get(cols.get("module")) or "").strip() if "module" in cols else "",
                "source": (r.get(cols.get("source")) or "").strip() if "source" in cols else "",
                "data": (r.get(cols.get("data")) or "").strip(),
                "updated": (r.get(cols.get("updated")) or "").strip() if "updated" in cols else "",
                "fp": (r.get(cols.get("fp")) or "").strip() if "fp" in cols else "",
            })
    return rows


def esc(s):
    return html.escape(s or "")


def build_html(rows, target):
    total = len(rows)
    fp_count = sum(1 for r in rows if r["fp"].lower() in ("true", "1", "yes"))
    type_counts = Counter(r["type"] for r in rows if r["type"])
    module_counts = Counter(r["module"] for r in rows if r["module"])
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    top_types = sorted(type_counts.items(), key=lambda x: -x[1])
    top_modules = sorted(module_counts.items(), key=lambda x: -x[1])[:12]
    max_type_count = max((c for _, c in top_types), default=1)
    max_mod_count = max((c for _, c in top_modules), default=1)

    type_rows_html = "\n".join(
        f'<tr><td>{esc(t)}</td><td class="num">{c}</td>'
        f'<td><div class="bar-track"><div class="bar" style="width:{(c/max_type_count)*100:.1f}%"></div></div></td></tr>'
        for t, c in top_types
    )

    module_rows_html = "\n".join(
        f'<tr><td>{esc(m)}</td><td class="num">{c}</td>'
        f'<td><div class="bar-track"><div class="bar bar-alt" style="width:{(c/max_mod_count)*100:.1f}%"></div></div></td></tr>'
        for m, c in top_modules
    )

    findings_rows_html = "\n".join(
        f'<tr data-type="{esc(r["type"])}" data-fp="{esc(r["fp"]).lower()}">'
        f'<td>{esc(r["type"])}</td>'
        f'<td>{esc(r["module"])}</td>'
        f'<td class="data-cell">{esc(r["data"])}</td>'
        f'<td>{esc(r["source"])}</td>'
        f'<td>{esc(r["updated"])}</td>'
        f'</tr>'
        for r in rows
    )

    type_options_html = "\n".join(
        f'<option value="{esc(t)}">{esc(t)}</option>' for t in sorted(type_counts)
    )

    return TEMPLATE.format(
        target=esc(target) if target else "Alvo nao especificado",
        generated_at=generated_at,
        total=total,
        fp_count=fp_count,
        unique_types=len(type_counts),
        unique_modules=len(module_counts),
        type_rows_html=type_rows_html or '<tr><td colspan="3">Sem dados</td></tr>',
        module_rows_html=module_rows_html or '<tr><td colspan="3">Sem dados</td></tr>',
        findings_rows_html=findings_rows_html or '<tr><td colspan="5">Sem achados</td></tr>',
        type_options_html=type_options_html,
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Relatorio OSINT - {target}</title>
<style>
  :root {{
    --bg: #0f1216; --panel: #171b21; --border: #262c35; --text: #e6e9ef;
    --muted: #8a93a3; --accent: #4f8cff; --accent-alt: #ff9f4f; --danger: #ff5f6d;
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
  main {{ max-width: 1100px; margin: 0 auto; padding: 24px 32px 64px; }}
  .stats {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 28px; }}
  .stat {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
    padding: 16px 20px; min-width: 140px; flex: 1;
  }}
  .stat .num {{ font-size: 26px; font-weight: 700; }}
  .stat .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
  section {{ margin-bottom: 32px; }}
  section h2 {{ font-size: 15px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); margin-bottom: 12px; }}
  .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); vertical-align: middle; }}
  th {{ color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; }}
  tr:last-child td {{ border-bottom: none; }}
  td.num {{ text-align: right; width: 60px; }}
  .bar-track {{ background: #0c0f13; border-radius: 4px; overflow: hidden; height: 8px; width: 160px; }}
  .bar {{ background: var(--accent); height: 100%; }}
  .bar-alt {{ background: var(--accent-alt); }}
  .data-cell {{ max-width: 480px; word-break: break-word; }}
  .toolbar {{ display: flex; gap: 10px; margin-bottom: 12px; flex-wrap: wrap; }}
  .toolbar input[type="text"], .toolbar select {{
    background: var(--panel); border: 1px solid var(--border); color: var(--text);
    padding: 8px 12px; border-radius: 8px; font-size: 13px;
  }}
  .toolbar input[type="text"] {{ flex: 1; min-width: 200px; }}
  .toolbar label {{ display: flex; align-items: center; gap: 6px; color: var(--muted); font-size: 13px; }}
  #findingsCount {{ color: var(--muted); font-size: 12px; margin: 8px 0; }}
  tbody tr[hidden] {{ display: none; }}
</style>
</head>
<body>

<header>
  <h1>Relatorio OSINT &mdash; {target}</h1>
  <div class="meta">Gerado em {generated_at} &middot; Fonte: SpiderFoot (export CSV)</div>
</header>

<main>
  <div class="stats">
    <div class="stat"><div class="num">{total}</div><div class="label">Total de achados</div></div>
    <div class="stat"><div class="num">{unique_types}</div><div class="label">Tipos distintos</div></div>
    <div class="stat"><div class="num">{unique_modules}</div><div class="label">Modulos usados</div></div>
    <div class="stat"><div class="num">{fp_count}</div><div class="label">Marcados como falso positivo</div></div>
  </div>

  <section>
    <h2>Achados por tipo</h2>
    <div class="panel"><table><tbody>{type_rows_html}</tbody></table></div>
  </section>

  <section>
    <h2>Top modulos</h2>
    <div class="panel"><table><tbody>{module_rows_html}</tbody></table></div>
  </section>

  <section>
    <h2>Todos os achados</h2>
    <div class="toolbar">
      <input type="text" id="searchBox" placeholder="Buscar nos achados...">
      <select id="typeFilter"><option value="">Todos os tipos</option>{type_options_html}</select>
      <label><input type="checkbox" id="hideFp"> Ocultar falsos positivos</label>
    </div>
    <div id="findingsCount"></div>
    <div class="panel">
      <table>
        <thead><tr><th>Tipo</th><th>Modulo</th><th>Dado</th><th>Fonte</th><th>Atualizado</th></tr></thead>
        <tbody id="findingsBody">{findings_rows_html}</tbody>
      </table>
    </div>
  </section>
</main>

<script>
  const search = document.getElementById('searchBox');
  const typeFilter = document.getElementById('typeFilter');
  const hideFp = document.getElementById('hideFp');
  const rows = Array.from(document.querySelectorAll('#findingsBody tr'));
  const countEl = document.getElementById('findingsCount');

  function applyFilters() {{
    const q = search.value.toLowerCase();
    const t = typeFilter.value;
    const hide = hideFp.checked;
    let visible = 0;
    rows.forEach(row => {{
      const matchesText = row.textContent.toLowerCase().includes(q);
      const matchesType = !t || row.dataset.type === t;
      const isFp = row.dataset.fp === 'true' || row.dataset.fp === '1' || row.dataset.fp === 'yes';
      const show = matchesText && matchesType && !(hide && isFp);
      row.hidden = !show;
      if (show) visible++;
    }});
    countEl.textContent = visible + ' de ' + rows.length + ' achados exibidos';
  }}

  search.addEventListener('input', applyFilters);
  typeFilter.addEventListener('change', applyFilters);
  hideFp.addEventListener('change', applyFilters);
  applyFilters();
</script>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Gera relatorio HTML a partir de export CSV do SpiderFoot")
    parser.add_argument("csv_file", help="Caminho do CSV exportado do SpiderFoot")
    parser.add_argument("-o", "--output", default="relatorio.html", help="Arquivo HTML de saida (padrao: relatorio.html)")
    parser.add_argument("-t", "--target", default="", help="Nome do alvo/dominio investigado (aparece no titulo)")
    args = parser.parse_args()

    rows = load_rows(args.csv_file)
    html_out = build_html(rows, args.target)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"OK: {len(rows)} achados processados -> {args.output}")


if __name__ == "__main__":
    main()