# Recon-ng Automation Kit

Automatiza uma sessão do [recon-ng](https://github.com/lanmaster53/recon-ng) contra um domínio-alvo — cria o workspace, instala e roda um conjunto de módulos, e gera um relatório HTML navegável a partir dos dados coletados, com um único comando.

## O que tem aqui

| Arquivo | Função |
|---|---|
| `recon_scan.sh` | Roda a sessão do recon-ng (seed do alvo + módulos) e chama o gerador de relatório |
| `recon_report.py` | Lê o banco SQLite do workspace do recon-ng e produz um relatório HTML autocontido |
| `README.md` | Este arquivo |

---

## Como isso difere do que fizemos com o SpiderFoot

Vale ler antes de usar, porque muda como o kit funciona por dentro:

- O recon-ng guarda os achados em **várias tabelas relacionais** (domínios, hosts, contatos, vulnerabilidades, portas...), não num fluxo único de eventos. Por isso `recon_report.py` lê o **schema do banco SQLite diretamente** e monta uma seção por tabela — funciona com qualquer conjunto de colunas que o recon-ng tenha criado, mesmo que mude numa atualização futura.
- Não existe um "rode tudo contra o alvo" como o `-u all` do SpiderFoot. O `recon_scan.sh` roda uma lista fixa de módulos (ver abaixo), que você pode editar.
- A partir da v5, os módulos do recon-ng **não vêm todos pré-instalados** — precisam ser baixados do marketplace na primeira vez (`marketplace install <módulo>`). O script faz isso automaticamente a cada execução (é rápido se já estiver instalado).
- O console do recon-ng é **interativo**: alguns comandos (como cadastrar o alvo) pedem os valores campo a campo em vez de aceitar tudo numa linha. Por isso `recon_scan.sh` não usa `recon-cli` — ele monta a sessão inteira como um roteiro de comandos e alimenta via *stdin* para o `recon-ng`, exatamente como se você estivesse digitando cada linha na hora certa. É a forma mais robusta de automatizar esse tipo de console.

---

## Requisitos

- **Kali Linux** com acesso à internet.
- **recon-ng** — já vem pré-instalado no Kali. Se não tiver: `sudo apt install recon-ng`.
- **Python 3.7+** (já vem no Kali).
- **Bash**.
- Nenhuma biblioteca Python adicional é necessária para o `recon_report.py` — usa só a biblioteca padrão.

Confirme a instalação:
```bash
recon-ng --version
```

---

## Instalação

1. Coloque `recon_scan.sh` e `recon_report.py` **no mesmo diretório**:
   ```bash
   mkdir -p ~/osint-toolkit
   # copie recon_scan.sh e recon_report.py para ~/osint-toolkit/
   cd ~/osint-toolkit
   chmod +x recon_scan.sh
   ```
2. Rode o teste de fumaça contra um domínio seu, só com os módulos gratuitos:
   ```bash
   ./recon_scan.sh -t seudominio.com
   ```
   Isso valida que o `recon-ng` está funcionando certo no seu ambiente antes de confiar no restante do fluxo.

---

## Módulos incluídos

### Sem chave de API (rodam sempre)

| Módulo | O que faz |
|---|---|
| `recon/domains-hosts/hackertarget` | Enumera hosts/subdomínios via HackerTarget |
| `recon/domains-hosts/netcraft` | Enumera subdomínios via Netcraft |
| `recon/domains-hosts/certificate_transparency` | Descobre subdomínios via logs de Certificate Transparency |
| `recon/domains-hosts/brute_hosts` | Brute-force de subdomínios comuns |
| `recon/domains-contacts/whois_pocs` | Extrai contatos do WHOIS do domínio |
| `recon/domains-vulnerabilities/xssed` | Consulta o banco do XSSed por vulnerabilidades já catalogadas para o domínio |

### Com chave de API (só entram com a flag `-k` / `--with-keys`)

| Módulo | Chave necessária | O que faz |
|---|---|---|
| `recon/domains-hosts/shodan_hostname` | `shodan_api` | Hosts do domínio indexados pelo Shodan |
| `recon/hosts-ports/shodan_ip` | `shodan_api` | Portas/serviços abertos nos hosts encontrados, via Shodan |

### Cadastrando a chave do Shodan

As chaves ficam salvas globalmente em `~/.recon-ng/keys.db` (não por workspace), então isso é um cadastro único:

```bash
recon-ng
[recon-ng][default] > keys add shodan_api SUA_CHAVE_AQUI
[recon-ng][default] > exit
```

Para conseguir a chave: crie uma conta em [shodan.io](https://www.shodan.io/) e copie a API key do seu perfil.

### Adicionando outros módulos com chave (Censys, VirusTotal, BuiltWith, etc.)

O recon-ng suporta dezenas de chaves de terceiros. A lista completa de como obter cada uma está na [wiki oficial do marketplace](https://github.com/lanmaster53/recon-ng-marketplace/wiki/API-Keys) — inclui Bing, BuiltWith, Censys (`censysio_id`/`censysio_secret`), Flickr, FullContact, GitHub, Google, Twitter, VirusTotal (`virustotal_api`) e outras.

Para descobrir o caminho exato de um módulo antes de adicioná-lo ao script:
```bash
recon-ng
[recon-ng][default] > marketplace search censys
[recon-ng][default] > marketplace search virustotal
```
Depois é só cadastrar a chave com `keys add <nome> <valor>` e adicionar a linha do módulo no array `KEYED_MODULES` dentro do `recon_scan.sh`.

> **Nota sobre o Censys:** os módulos de Censys mais completos vêm de um pacote de terceiros ([censys/censys-recon-ng](https://github.com/censys/censys-recon-ng)), que exige clonar o repositório e rodar o `install.sh` dele à parte — não é só `marketplace install`. Se for usar, siga as instruções desse repositório antes de adicionar os módulos ao array.

---

## Uso

### Sintaxe
```bash
./recon_scan.sh -t ALVO [opcoes]
```

### Opções

| Flag | Descrição | Padrão |
|---|---|---|
| `-t ALVO` | Domínio alvo (**obrigatório**) | — |
| `-w WORKSPACE` | Nome do workspace do recon-ng | derivado do alvo |
| `-o DIRETORIO` | Diretório de saída do relatório HTML | `./relatorios` |
| `-k`, `--with-keys` | Inclui também os módulos que usam chave de API | desativado |
| `-a` | Abre o relatório automaticamente no navegador | desativado |
| `-h` | Ajuda | — |

### Exemplos

```bash
# Scan só com módulos gratuitos
./recon_scan.sh -t exemplo.com

# Incluindo os módulos com chave (Shodan), abrindo o relatório ao final
./recon_scan.sh -t exemplo.com -k -a

# Workspace e diretório de saída customizados
./recon_scan.sh -t exemplo.com -w investigacao_2026 -o ~/osint/caso01
```

---

## Passo a passo completo

1. Instale/confirme o recon-ng (`recon-ng --version`).
2. Copie os dois scripts para uma pasta e dê permissão de execução (`chmod +x recon_scan.sh`).
3. (Opcional) Cadastre a chave do Shodan se for usar `-k` (ver seção acima).
4. Rode contra um alvo próprio primeiro:
   ```bash
   ./recon_scan.sh -t seudominio.com
   ```
5. Acompanhe a saída no terminal — cada módulo instalado e rodado aparece em tempo real.
6. Ao final, o caminho do relatório é impresso:
   ```
   Workspace (banco recon-ng): ~/.recon-ng/workspaces/seudominio_com
   Relatorio HTML:             ./relatorios/seudominio_com_20260917_120000.html
   ```
7. Abra o `.html` no navegador. A barra lateral lista cada tabela com achados (Domains, Hosts, Contacts...) e cada uma tem busca própria.
8. Rodadas seguintes no mesmo alvo reaproveitam o mesmo workspace (dados se acumulam) a menos que você troque o nome com `-w`.

---

## Solução de problemas

**`Comando 'recon-ng' nao encontrado no PATH`**
Instale com `sudo apt install recon-ng`, ou aponte o binário com `RECON_BIN=/caminho/recon-ng ./recon_scan.sh ...`.

**`Workspace nao encontrado em: ...`**
O recon-ng pode estar usando um `$HOME` diferente do esperado (comum se você rodar com `sudo`, que muda o home). Rode sem `sudo`, ou defina `RECON_NG_HOME=/caminho/correto`.

**Um módulo falha ou não retorna nada**
Normal — fontes externas mudam de comportamento, ficam fora do ar, ou têm limites de taxa. O script continua e gera o relatório com o que foi coletado; verifique a saída do terminal para ver qual módulo especificamente falhou.

**Módulos com chave "somem" da lista**
Se a chave não estiver cadastrada (`keys add ...`), o recon-ng carrega o módulo mas ele não retorna resultado útil ao rodar. Cadastre a chave antes de usar `-k`.

**O relatório mostra "Nenhum achado encontrado"**
Pode ser um domínio com pouquíssima exposição pública, um problema de conectividade durante o scan, ou os módulos escolhidos não gerarem achados para aquele alvo específico. Rode `recon-ng -w SEU_WORKSPACE` manualmente e confira com `show hosts`, `show domains` etc. para depurar.

**Quero adicionar/trocar módulos**
Edite os arrays `FREE_MODULES` e `KEYED_MODULES` no topo do `recon_scan.sh`. Use `marketplace search <termo>` dentro do recon-ng para descobrir módulos disponíveis antes de adicionar.

---

## Uma ressalva importante

Diferente do kit do SpiderFoot — que testei de ponta a ponta com o `sf.py` real simulado e cujo comportamento de linha de comando eu confirmei diretamente no código-fonte — a automação via *stdin* do recon-ng aqui foi validada quanto à **mecânica do script** (parsing de argumentos, sequência de comandos, geração do relatório) com uma simulação do `recon-ng`. O comportamento interativo do `db insert domains` está documentado e confirmado via fontes oficiais (documentação de integração do Shodan com recon-ng v5), mas vale rodar o passo 4 do "passo a passo" acima como teste real antes de usar em algo importante — se algo no prompt em ambiente real diferir do esperado, relate.

---

## Aviso legal e ético

Este kit automatiza coleta de informações públicas (OSINT). **Use apenas contra alvos que você tem autorização explícita para investigar** — domínios/sistemas próprios, ou escopos formalmente autorizados em um teste de intrusão/pentest. Coletar informações sobre terceiros sem consentimento pode violar leis de proteção de dados (como a LGPD no Brasil) e os termos de uso dos serviços consultados pelos módulos. A responsabilidade pelo uso é de quem executa o scan.