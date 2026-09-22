# Full Recon Pipeline (subfinder → httpx → nuclei)

Encadeia três ferramentas padrão de mercado da [ProjectDiscovery](https://projectdiscovery.io/) num pipeline único: **subfinder** (enumeração passiva de subdomínios) → **httpx** (confirma quais estão vivos, com título/tecnologia/status) → **nuclei** (varre vulnerabilidades conhecidas via templates) → relatório HTML único e navegável.


## O que tem aqui

| Arquivo | Função |
|---|---|
| `full_recon_pipeline.sh` | Orquestra as 3 ferramentas em sequência e chama o gerador de relatório |
| `recon_pipeline_report.py` | Combina subfinder (texto) + httpx (JSONL) + nuclei (JSONL) num relatório HTML |
| `README.md` | Este arquivo |

---

## Requisitos

- **Kali Linux** com acesso à internet.
- **Go 1.21+** (para instalar as ferramentas da ProjectDiscovery). Confira com `go version`; se não tiver, `sudo apt install golang-go`.
- **subfinder**, **httpx** e **nuclei** instalados e no `PATH` (ver instalação abaixo).
- **Python 3.7+** (já vem no Kali) — `recon_pipeline_report.py` não usa nenhuma biblioteca externa.
- **Bash**.

### Instalação das ferramentas

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

Isso instala os binários em `$HOME/go/bin`. Garanta que esse diretório está no seu `PATH`:
```bash
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc
```

Confirme:
```bash
subfinder -version
httpx -version
nuclei -version
```

Na primeira execução, o nuclei baixa automaticamente o repositório de templates da comunidade (nuclei-templates) — isso é esperado e só acontece uma vez (depois só atualiza).

---

## Instalação do kit

```bash
mkdir -p ~/osint-toolkit
# copie full_recon_pipeline.sh e recon_pipeline_report.py para ~/osint-toolkit/
cd ~/osint-toolkit
chmod +x full_recon_pipeline.sh
```

---

## Uso

### Sintaxe
```bash
./full_recon_pipeline.sh -t ALVO [opcoes]
```

### Opções

| Flag | Descrição | Padrão |
|---|---|---|
| `-t ALVO` | Domínio alvo (**obrigatório**) | — |
| `-o DIRETORIO` | Diretório de saída do relatório | `./relatorios` |
| `--severity LISTA` | Filtra o nuclei por severidade (`info,low,medium,high,critical`) | todas |
| `--skip-nuclei` | Pula o scan de vulnerabilidades — só enumera e confirma hosts vivos | desativado |
| `-a` | Abre o relatório automaticamente no navegador | desativado |
| `-h` | Ajuda | — |

### Exemplos

```bash
# Pipeline completo
./full_recon_pipeline.sh -t exemplo.com

# Só reconhecimento passivo + confirmação de hosts, sem scan ativo de vulnerabilidade
./full_recon_pipeline.sh -t exemplo.com --skip-nuclei

# Só severidades altas, abrindo o relatório ao final
./full_recon_pipeline.sh -t exemplo.com --severity critical,high -a
```

---

## O que cada etapa faz

1. **subfinder** — consulta dezenas de fontes passivas (Certificate Transparency, mecanismos de busca, bancos públicos) para listar subdomínios do alvo. Não faz nenhuma requisição direta ao alvo nesta etapa.
2. **httpx** — para cada subdomínio encontrado (+ o domínio raiz), faz uma requisição HTTP/HTTPS para confirmar se está no ar, capturando status code, título da página, servidor web e tecnologias detectadas (via Wappalyzer).
3. **nuclei** — roda contra os hosts confirmados vivos, testando milhares de templates comunitários (exposições conhecidas, CVEs, painéis administrativos expostos, configurações incorretas comuns). **Esta é a única etapa com requisições ativas de teste, não apenas coleta.**

O relatório final tem uma seção por etapa, com busca própria em cada uma, e os achados do nuclei vêm com badge de severidade colorido e ordenados do mais crítico para o menos.

---

## Solução de problemas

**`Comando(s) nao encontrado(s) no PATH: ...`**
As ferramentas não foram instaladas ou `$HOME/go/bin` não está no `PATH`. Revise a seção de instalação acima.

**subfinder retorna poucos ou nenhum subdomínio**
Muitas fontes do subfinder funcionam melhor com chave de API configurada (Shodan, SecurityTrails, Censys etc. — ver `$HOME/.config/subfinder/provider-config.yaml`). Sem chaves, ele ainda funciona com as fontes gratuitas, só que com menos cobertura.

**httpx demora muito ou trava**
Normal para listas grandes de subdomínios. Você pode reduzir o escopo filtrando o `subs.txt` antes, ou aumentar o timeout com flags nativas do httpx (edite a chamada dentro do script se quiser customizar).

**nuclei não encontra nada**
Pode ser um bom sinal (alvo bem configurado) ou os templates instalados estarem desatualizados — rode `nuclei -update-templates` manualmente de vez em quando.

**Quero customizar quais probes o httpx roda, ou trocar/adicionar templates do nuclei**
Edite diretamente as linhas de `httpx ...` e `nuclei ...` dentro do `full_recon_pipeline.sh` — todas as flags nativas de cada ferramenta funcionam normalmente ali.

---

## Uma ressalva importante

 As flags de cada ferramenta foram conferidas diretamente nos repositórios oficiais da ProjectDiscovery no GitHub antes de escrever o script, mas — como essas ferramentas recebem atualizações frequentes — vale rodar `-version` em cada uma e testar contra um alvo próprio antes de confiar no pipeline por completo.

---

## Aviso legal e ético

**Este pipeline inclui uma etapa ativa (nuclei), diferente dos kits anteriores que eram majoritariamente passivos.** O nuclei envia requisições reais de teste contra os hosts alvo. **Use apenas contra alvos que você tem autorização explícita para testar** — domínios/sistemas próprios, ou escopos formalmente autorizados em um teste de intrusão/pentest/bug bounty. Rodar scans ativos contra terceiros sem autorização pode configurar acesso não autorizado a sistema de informação, além de violar a LGPD se dados pessoais forem coletados no processo. A responsabilidade pelo uso é de quem executa o scan.