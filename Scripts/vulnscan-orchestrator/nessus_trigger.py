#!/usr/bin/env python3
"""
nessus_trigger.py — Dispara e exporta um scan JÁ CONFIGURADO no seu
Nessus (instância própria, licenciada) via API REST oficial.

Este script NÃO cria políticas de varredura nem qualquer lógica de
detecção de vulnerabilidades — ele apenas chama os endpoints
documentados da Tenable para (1) iniciar um scan que você já configurou
no painel do Nessus e (2) exportar o resultado quando terminar.

Requer que as seguintes variáveis de ambiente estejam definidas:
    NESSUS_URL          ex.: https://127.0.0.1:8834
    NESSUS_ACCESS_KEY   chave de API (gerada no painel do Nessus)
    NESSUS_SECRET_KEY   chave secreta de API
    NESSUS_SCAN_ID      ID do scan já existente e configurado
    NESSUS_VERIFY_SSL   opcional, "false" para instâncias locais com
                         certificado autoassinado (padrão: "true")

Uso:
    python3 nessus_trigger.py --export saida.csv [--format csv|html|pdf|nessus]

Documentação oficial da API: https://developer.tenable.com/reference

AVISO: use apenas contra scans que você já configurou e está
autorizado a executar.
"""

import argparse
import os
import sys
import time

try:
    import requests
except ImportError:
    print("[!] Este script requer a lib 'requests': pip install requests --break-system-packages")
    sys.exit(1)


def get_config():
    required = ["NESSUS_URL", "NESSUS_ACCESS_KEY", "NESSUS_SECRET_KEY", "NESSUS_SCAN_ID"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"[!] Variáveis de ambiente ausentes: {', '.join(missing)}")
        sys.exit(1)

    return {
        "url": os.environ["NESSUS_URL"].rstrip("/"),
        "scan_id": os.environ["NESSUS_SCAN_ID"],
        "headers": {
            "X-ApiKeys": (f"accessKey={os.environ['NESSUS_ACCESS_KEY']};"
                           f"secretKey={os.environ['NESSUS_SECRET_KEY']}"),
        },
        "verify_ssl": os.environ.get("NESSUS_VERIFY_SSL", "true").lower() != "false",
    }


def launch_scan(cfg):
    url = f"{cfg['url']}/scans/{cfg['scan_id']}/launch"
    r = requests.post(url, headers=cfg["headers"], verify=cfg["verify_ssl"])
    r.raise_for_status()
    print(f"[*] Scan {cfg['scan_id']} disparado.")


def wait_for_completion(cfg, poll_seconds=15, timeout_minutes=120):
    url = f"{cfg['url']}/scans/{cfg['scan_id']}"
    deadline = time.time() + timeout_minutes * 60

    while time.time() < deadline:
        r = requests.get(url, headers=cfg["headers"], verify=cfg["verify_ssl"])
        r.raise_for_status()
        status = r.json().get("info", {}).get("status", "unknown")
        print(f"[*] Status do scan: {status}")

        if status == "completed":
            return True
        if status in ("aborted", "canceled", "empty"):
            print(f"[!] Scan terminou com status '{status}', não é possível exportar.")
            return False

        time.sleep(poll_seconds)

    print("[!] Tempo limite excedido aguardando conclusão do scan.")
    return False


def export_results(cfg, output_path, fmt="csv"):
    export_url = f"{cfg['url']}/scans/{cfg['scan_id']}/export"
    r = requests.post(export_url, headers=cfg["headers"],
                       json={"format": fmt}, verify=cfg["verify_ssl"])
    r.raise_for_status()
    file_id = r.json()["file"]

    status_url = f"{cfg['url']}/scans/{cfg['scan_id']}/export/{file_id}/status"
    while True:
        r = requests.get(status_url, headers=cfg["headers"], verify=cfg["verify_ssl"])
        r.raise_for_status()
        if r.json().get("status") == "ready":
            break
        time.sleep(5)

    download_url = f"{cfg['url']}/scans/{cfg['scan_id']}/export/{file_id}/download"
    r = requests.get(download_url, headers=cfg["headers"], verify=cfg["verify_ssl"])
    r.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(r.content)
    print(f"[*] Exportado para: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dispara/exporta um scan existente do Nessus.")
    parser.add_argument("--export", required=True, help="Caminho do arquivo de saída")
    parser.add_argument("--format", default="csv", choices=["csv", "html", "pdf", "nessus"],
                         help="Formato de exportação (padrão: csv)")
    parser.add_argument("--skip-launch", action="store_true",
                         help="Não dispara o scan, apenas exporta o último resultado disponível")
    args = parser.parse_args()

    config = get_config()

    if not args.skip_launch:
        launch_scan(config)
        if not wait_for_completion(config):
            sys.exit(1)

    export_results(config, args.export, fmt=args.format)