# Conceitos Básicos e Automação com Bash Scripting: Guia para Pentesting e Segurança

## 1. Introdução e Visão Geral

O **Bash** (_Bourne Again Shell_) é o shell de linha de comando e linguagem de script padrão na maioria das distribuições Linux e sistemas Unix-like (incluindo distribuições especializadas em segurança como o Kali Linux e Debian). Criado por Brian Fox em 1989 para o Projeto GNU como substituto do _Bourne Shell_ (`sh`), o Bash atua como a interface primária entre o operador humano (ou scripts automatizados) e o núcleo do sistema operacional (_kernel_).

No contexto de **Pentesting**, **Red Teaming** e **Administração de Sistemas**, o domínio do Bash é essencial para a automação de tarefas repetitivas, encadeamento de ferramentas (_tool chaining_), manipulação de grandes volumes de texto/logs e execução rápida de recon de rede sem a necessidade de instalar dependências complexas.

---

## 2. Conceitos Fundamentais do Shell

### 2.1 Diferença entre Terminal, Shell e Bash

- **Terminal (ou Emulador de Terminal):** A interface gráfica ou de janela que recebe as entradas do teclado e exibe os resultados na tela (ex.: `qterminal`, `gnome-terminal`, `tmux`, `alacritty`).
- **Shell:** O programa encarregado de interpretar os comandos digitados pelo usuário e enviá-los ao sistema operacional.
- **Bash:** Uma implementação específica de shell que expande o `sh` clássico com recursos avançados de autocompletar, histórico de comandos, manipulação de strings e controle de processos.

### 2.2 Canais Padrão de Entrada e Saída (I/O Redirection)

O Bash gerencia o fluxo de dados através de três descritores de arquivo (_File Descriptors_ - FD) padrão:

| Descritor (FD) | Nome     | Descrição                                                 | Atalho Padrão |
| :------------: | :------- | :-------------------------------------------------------- | :-----------: |
|     **0**      | `stdin`  | Entrada padrão (teclado / entrada de dados)               |      `<`      |
|     **1**      | `stdout` | Saída padrão (resultado bem-sucedido exibido no terminal) |  `>` ou `>>`  |
|     **2**      | `stderr` | Saída de erro (mensagens de erro do sistema)              | `2>` ou `2>>` |

**Exemplos de Operadores:**

- `comando > arquivo.txt`: Redireciona o `stdout` sobrescrevendo o arquivo.
- `comando >> arquivo.txt`: Redireciona o `stdout` anexando ao final do arquivo.
- `comando 2> erro.log`: Redireciona apenas as mensagens de erro (`stderr`).
- `comando > output.txt 2>&1` ou `comando &> output.txt`: Redireciona tanto `stdout` quanto `stderr` para o mesmo arquivo.
- `comando 2> /dev/null`: Descarta silenciosamente qualquer mensagem de erro enviada para o dispositivo nulo.

### 2.3 Encanamento de Comandos (Pipes - `|`)

O operador _Pipe_ (`|`) conecta a saída padrão (`stdout`) de um comando diretamente à entrada padrão (`stdin`) do próximo comando. Esse conceito é pilar da filosofia Unix: "Construa programas pequenos que façam uma coisa bem feita e trabalhem juntos."

```bash
# Exemplo: Lista conexões, filtra portas HTTP/HTTPS (80/443), ordena e remove duplicatas
netstat -tuln | grep -E ':(80|443)' | sort -u
```

---

## 3. O Papel do Bash no Pentesting e Segurança Ofensiva

Durante uma auditoria de segurança, o Bash é utilizado principalmente para três grandes casos de uso:

- **Automação de Reconhecimento (OSINT / Port Scanning):** Processar listas de subdomínios, testar resolução de DNS em massa e filtrar respostas de servidores web.
- **Parsing e Filtragem de Resultados:** Extrair endereços IP, hashes, URLs e credenciais de arquivos de saída densos produzidos por ferramentas como Nmap, Masscan, Burp Suite e Gobuster.
- **One-Liners e Reverse Shells:** Execução de comandos diretos para obter shells reversos durante a etapa de exploração sem depender de linguagens como Python ou Perl na máquina alvo.

---

## 4. Estruturas de Linguagem e Scripting

Um script Bash é um arquivo de texto simples que contém uma sequência de comandos executados sequencialmente pelo interpretador.

### 4.1 O Shebang (`#!/bin/bash`)

A primeira linha de um script deve conter o _shebang_ (`#!`), indicando ao sistema operacional qual interpretador deve carregar o arquivo:

```bash
#!/bin/bash
```

### 4.2 Variáveis e Argumentos

No Bash, a atribuição de variáveis não permite espaços ao redor do sinal de igual (`=`). O acesso ao valor da variável é feito prefixando o nome com `$`.

```bash
#!/bin/bash

# Atribuição de variáveis
ALVO="192.168.1.1"
PORTAS="80,443,22"

# Parâmetros passados via linha de comando ($1, $2, etc.)
# Exemplo de execução: ./script.sh exemplo.com 80
DOMINIO=$1
PORTA_PADRAO=$2

echo "Iniciando scan no alvo: $ALVO"
echo "Total de argumentos recebidos: $#"
echo "Nome do script em execução: $0"
```

### 4.3 Estruturas Condicionais (`if`/`else`)

As condicionais testam expressões lógicas utilizando colchetes simples (`[ ]`) ou duplos (`[[ ]]`), recomendados para suporte a expressões regulares.

```bash
#!/bin/bash

ALVO=$1

# Verifica se o argumento $1 foi fornecido
if [ -z "$ALVO" ]; then
    echo "[!] Erro: Você deve fornecer um alvo!"
    echo "Uso: $0 <IP_ou_Dominio>"
    exit 1
fi

# Verifica se o host responde ao ping
if ping -c 1 "$ALVO" &> /dev/null; then
    echo "[+] Host $ALVO está ativo na rede."
else
    echo "[-] Host $ALVO inacessível ou bloqueando ICMP."
fi
```

### 4.4 Laços de Repetição (`for` e `while`)

```bash
#!/bin/bash

# Exemplo 1: Laço FOR iterando sobre uma lista de subdomínios
for sub in www mail dev api admin; do
    echo "Testando resolução de: $sub.empresa.com"
done

# Exemplo 2: Laço WHILE lendo um arquivo linha por linha (ex.: lista de IPs)
while read -r ip; do
    echo "Varrendo IP: $ip"
    nmap -sV -p 80 "$ip" -oG - | grep "Open"
done < lista_ips.txt
```

---

## 5. Ferramentas Essenciais do Bash para Processamento de Texto

O pentester utiliza intensamente o ecossistema de utilitários POSIX para manipulação de texto:

- **`grep`:** Filtra linhas de texto com base em padrões de busca ou expressões regulares (regex).
- **`awk`:** Linguagem de processamento de texto estruturado ideal para extrair colunas específicas de tabelas.
- **`sed`:** Editor de fluxo de texto usado para substituições em massa.
- **`cut`:** Delimita e extrai seções específicas de cada linha de um arquivo, como em arquivos `/etc/passwd`.
- **`sort` e `uniq`:** Ordenam entradas e removem duplicatas em listas de dados.
- **`tr`:** Traduz ou deleta caracteres específicos, como na conversão de maiúsculas em minúsculas.

### Tabela de Uso Rápido de Utilitários em Pentesting

| Comando de Exemplo                           | Objetivo no Pentest                                                       |
| :------------------------------------------- | :------------------------------------------------------------------------ |
| `grep -i "password" config.php`              | Busca pela palavra `password` ignorando maiúsculas e minúsculas.          |
| `cut -d ":" -f 1 /etc/passwd`                | Extrai a primeira coluna, com os nomes de usuários, do arquivo de senhas. |
| `cat ips.txt \| sort -u`                     | Ordena a lista de IPs e elimina endereços repetidos.                      |
| `awk '{print $2}' nmap_output.gnmap`         | Imprime a segunda coluna da saída do Nmap no formato _greppable_.         |
| `sed -i 's/http:\/\//https:\/\//g' urls.txt` | Substitui todas as ocorrências de `http://` por `https://` no arquivo.    |

---

## 6. Exemplos Práticos de Scripts para Pentesting

### 6.1 Ping Sweeper Simples (Descoberta de Hosts na Rede Local)

Este script identifica quais endereços IP de uma sub-rede `/24` respondem a requisições ICMP _echo_.

```bash
#!/bin/bash
# Nome: ping_sweeper.sh
# Uso: ./ping_sweeper.sh 192.168.1

if [ -z "$1" ]; then
    echo "Uso: $0 <3_Primeiros_Octetos_IP>"
    echo "Exemplo: $0 192.168.1"
    exit 1
fi

SUBNET=$1

echo "[+] Verificando hosts ativos no bloco $SUBNET.0/24..."

for ip in $(seq 1 254); do
    ping -c 1 -W 1 "$SUBNET.$ip" &> /dev/null && echo "[+] Host Ativo: $SUBNET.$ip" &
done
wait
echo "[+] Varredura concluída."
```

### 6.2 Port Scanner Básico usando o Pseudo-dispositivo `/dev/tcp`

O Bash possui uma funcionalidade nativa capaz de abrir conexões TCP diretamente usando o caminho especial `/dev/tcp/HOST/PORTA`, dispensando utilitários externos como Netcat ou Nmap.

```bash
#!/bin/bash
# Nome: bash_portscan.sh
# Uso: ./bash_portscan.sh 10.10.10.10

ALVO=$1
PORTAS=(21 22 23 25 53 80 110 139 443 445 3306 3389 8080)

if [ -z "$ALVO" ]; then
    echo "Uso: $0 <IP_Alvo>"
    exit 1
fi

echo "[+] Testando portas principais em: $ALVO"

for porta in "${PORTAS[@]}"; do
    (timeout 1 bash -c "echo > /dev/tcp/$ALVO/$porta") 2>/dev/null && \
        echo "[*] Porta $porta [ABERTA]"
done
```

---

## 7. Boas Práticas e Segurança em Scripts Bash

### Ativação de Modo Rígido de Erros (`set -euo pipefail`)

Incluir estes parâmetros no topo do script impede a execução de comandos subsequentes caso um comando intermediário falhe ou tente acessar uma variável não definida:

- `set -e`: Interrompe a execução se qualquer comando retornar erro.
- `set -u`: Gera erro ao tentar utilizar uma variável não declarada.
- `set -o pipefail`: Garante que um _pipe_ retorne erro se qualquer um de seus comandos falhar.

### Sanitização e Aspas nas Variáveis

Sempre envolva expansões de variáveis entre aspas duplas, como `"$MINHA_VARIAVEL"`, para evitar problemas com espaços em branco e injeção indesejada de comandos.

### Permissões de Execução Seguras

Defina apenas as permissões necessárias para o script usando o comando `chmod`:

```bash
chmod 700 meu_script.sh # Apenas o proprietário pode ler, escrever e executar
```

---

## 8. Referências e Fontes Bibliográficas

1. **GNU Bash Reference Manual**
   - **Publicado por:** Free Software Foundation (FSF).
   - **URL:** https://www.gnu.org/software/bash/manual/
   - **Descrição:** Documentação técnica oficial e completa da linguagem Bash e de suas extensões POSIX.

2. **Advanced Bash-Scripting Guide**
   - **Autor:** Mendel Cooper (Linux Documentation Project - LDP).
   - **URL:** https://tldp.org/LDP/abs/html/
   - **Descrição:** Guia avançado de referência e livro de receitas de scripts em linha de comando Linux.

3. **Linux Command Line and Shell Scripting Bible**
   - **Autores:** Richard Blum e Christine Bresnahan (Wiley Press).
   - **Descrição:** Manual de referência sobre automação e criação de scripts para sistemas operacionais Unix/Linux.

4. **OffSec (Offensive Security) - Penetration Testing with Kali Linux (PWK)**
   - **Publicado por:** OffSec.
   - **Descrição:** Material de estudo oficial do curso OSCP, cobrindo o uso do Bash para automação de reconhecimento, processamento de logs e exploração local.

5. **Google Shell Style Guide**
   - **URL:** https://google.github.io/styleguide/shellguide.html
   - **Descrição:** Guia de estilo e boas práticas da Google para desenvolvimento seguro e legível de scripts em Shell/Bash.
