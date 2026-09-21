# Traffic Orchestrator

Scripts de estudo para orquestrar **captura e análise de tráfego de rede**,
combinando o [Wireshark](https://www.wireshark.org/) (via `dumpcap`/`tshark`,
os componentes de linha de comando oficiais) e `tcpdump`, com um parser em
Python que consolida estatísticas em HTML, JSON e CSV.

> ⚠️ **Uso apenas em interfaces/redes autorizadas.** Diferente dos toolkits
> de [recon](../recon-orchestrator) e [vulnscan](../vulnscan-orchestrator),
> aqui não existe "alvo remoto" — você está escutando o tráfego que já
> passa pela sua própria interface de rede. Capture apenas em sua própria
> máquina, seu laboratório, ou um segmento de rede que você administra e
> tem autorização explícita para monitorar.

## O que faz

1. `run_capture.sh` captura pacotes em uma interface (via `dumpcap`, o
   motor de captura oficial do Wireshark, ou `tcpdump` como alternativa),
   com duração e filtro BPF configuráveis, salvando em `.pcap`.
2. `pcap_report.py` usa **`tshark`** (versão CLI do Wireshark) para
   extrair campos específicos do `.pcap` e gera:
   - Um relatório **HTML** com: total de pacotes/volume, distribuição de
     protocolos, principais pares de hosts por volume, portas de destino
     mais frequentes, consultas DNS observadas, nomes de servidor (SNI)
     vistos em handshakes TLS
   - Uma heurística simples de **possível varredura de portas recebida**
     (muitas portas distintas tocadas via SYN isolado, sem handshake
     completo, vindas do mesmo par origem/destino) — sinalizada
     claramente como heurística, não como detecção confirmada
   - Exports em **JSON** e **CSV** (talkers, protocolos, DNS, SNI)
3. `compare_captures.py` compara duas capturas (ex.: **antes** e
   **depois** de uma mudança de rede) e destaca o que apareceu, sumiu ou
   variou de volume: protocolos, pares de hosts, portas, consultas DNS,
   SNI e indícios de varredura — útil pra confirmar rapidamente o que
   uma mudança de configuração/topologia realmente alterou no tráfego.

Nenhum script reimplementa dissecação de protocolo — toda a análise de
pacote usa o `tshark`, que já faz esse trabalho de forma madura e
mantida pelo projeto Wireshark; este código só extrai campos e agrega.

## Limite de escopo: por que não extraímos credenciais em texto claro

Este é um limite **intencional e permanente** desta ferramenta, não uma
lacuna a ser preenchida depois.

Tecnicamente, seria trivial adicionar ao `pcap_report.py` uma extração
automática de credenciais em texto claro (usuário/senha de HTTP Basic,
FTP, Telnet, formulários HTTP não criptografados, etc.) — o `tshark` tem
filtros de campo prontos para isso (`http.authorization`, `ftp.request.arg`,
entre outros).

Optamos por **não implementar isso** porque:

- Essa funcionalidade transformaria a ferramenta de "analisador de
  estatísticas de tráfego" em "capturador automatizado de credenciais" —
  uma categoria de ferramenta fundamentalmente diferente, com potencial
  de abuso muito maior e utilidade legítima muito mais estreita.
- Um script público, mantido em repositório de estudos, que automatiza
  a coleta de credenciais não é compatível com o propósito educacional
  deste projeto, independentemente da intenção de quem o usa em um caso
  específico.
- As estatísticas de tráfego (protocolos, volume, pares de hosts,
  DNS/SNI, indícios de varredura) já cobrem os objetivos de estudo de
  análise de tráfego sem precisar desse recurso.

Se o objetivo for aprender a identificar tráfego em texto claro e o
risco que ele representa, a forma recomendada é abrir o `.pcap` gerado
diretamente no **Wireshark** (interface gráfica) e usar o filtro
`http.request or ftp or telnet` manualmente, em um ambiente de
laboratório próprio — como exercício interativo, e não como saída
automatizada de um script.

## Requisitos

```bash
sudo apt install tshark tcpdump -y
python3 --version   # 3.8+
```

Durante a instalação do `tshark` no Debian/Ubuntu, pode aparecer um
prompt perguntando se usuários não-root podem capturar pacotes — isso
configura uma capability no binário via `dpkg-reconfigure wireshark-common`
e é opcional (sem ela, basta rodar os scripts com `sudo`).

## Uso

```bash
chmod +x run_capture.sh
./run_capture.sh <interface> [duracao_segundos] [filtro_bpf] [rotulo]
```

Exemplos:

```bash
# Captura 60s na interface principal, sem filtro
sudo ./run_capture.sh eth0

# Captura 30s, só tráfego HTTP/HTTPS, com rótulo customizado
sudo ./run_capture.sh eth0 30 "tcp port 80 or tcp port 443" meu-teste

# Descobrir o nome das interfaces disponíveis
tcpdump -D
```

Cria `captura_<rotulo>_<timestamp>/` contendo:

```
captura.pcap              # captura bruta — abre direto no Wireshark
relatorio.html            # relatório consolidado
relatorio.json            # estatísticas completas em JSON
relatorio_talkers.csv     # pares de hosts por volume
relatorio_protocolos.csv  # distribuição de protocolos
relatorio_dns.csv         # consultas DNS observadas
relatorio_tls_sni.csv     # SNI visto em handshakes TLS
```

### Rodando o parser separadamente

Se você já tem um `.pcap` de outra captura (ex.: exportado do Wireshark):

```bash
python3 pcap_report.py captura.pcap relatorio.html
```

### Comparando duas capturas (antes/depois)

```bash
python3 compare_captures.py antes.pcap depois.pcap diff.html
```

Aceita tanto `.pcap` (analisa na hora) quanto `.json` já gerado pelo
`pcap_report.py` (reaproveita o resultado, mais rápido se você já rodou
o parser antes):

```bash
# Usando os JSONs já gerados por duas execuções do run_capture.sh
python3 compare_captures.py \
    captura_antes_20260101_100000/relatorio.json \
    captura_depois_20260101_180000/relatorio.json \
    diff.html
```

Pode misturar os dois formatos (um `.pcap` e um `.json`) sem problema.
Gera `diff.html` (destaque visual do que mudou), `diff.json` e CSVs
(`diff_protocolos_diff.csv`, `diff_talkers_diff.csv`, `diff_portas_diff.csv`,
`diff_dns_diff.csv`, `diff_tls_sni_diff.csv`).

## Referências

- [tshark(1) — manual oficial](https://www.wireshark.org/docs/man-pages/tshark.html)
- [Display Filter Reference (campos usados na extração)](https://www.wireshark.org/docs/dfref/)
- [pcap-filter(7) — sintaxe do filtro BPF usado no `tcpdump`/`dumpcap`](https://www.tcpdump.org/manpages/pcap-filter.7.html)
- [PTES — Penetration Testing Execution Standard](http://www.pentest-standard.org/) — metodologia geral de referência

## Estrutura do repositório

```
traffic-orchestrator/
├── README.md
├── run_capture.sh         # orquestração: dumpcap/tcpdump → parser
├── pcap_report.py          # parser tshark → HTML/JSON/CSV
└── compare_captures.py     # compara duas capturas (antes/depois) → diff em HTML/JSON/CSV
```

## Próximos passos de estudo

- Suporte a arquivos `.pcap` já existentes como entrada direta pro `run_capture.sh` (pular a etapa de captura)
- Adicionar exportação de gráfico de linha do tempo (pacotes por segundo) usando os mesmos dados já extraídos