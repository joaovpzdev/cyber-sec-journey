# Entendendo Comandos Internos e Externos do Shell

## O que são Comandos Internos e Externos?

No ecossistema Linux/Unix, quando você digita um comando no terminal, o **shell** (como o Bash) precisa executá-lo. A principal diferença entre comandos internos e externos está na **localização do código** e no **modo como o sistema operacional os executa**:

* **Comandos Internos (*Builtins*):** São comandos embutidos diretamente dentro do próprio código-fonte do shell. Quando você os executa, nenhum programa adicional precisa ser carregado do disco rígido, e nenhum novo processo (*child process*) precisa ser criado. Eles rodam instantaneamente na própria memória do shell.
* **Comandos Externos:** São programas e utilitários independentes armazenados como arquivos binários executáveis no disco rígido (geralmente em diretórios como `/bin`, `/usr/bin` ou `/usr/local/bin`). Quando você digita um comando externo, o shell precisa localizar o arquivo no sistema de arquivos, criar um novo processo (`fork`) e carregar o programa na memória (`exec`).

---

## 20 Comandos Internos do Shell (Builtins)

| # | Comando | Descrição |
| :---: | :--- | :--- |
| 1 | **`cd`** | Altera o diretório de trabalho atual do shell. |
| 2 | **`echo`** | Exibe textos ou valores de variáveis na saída padrão. |
| 3 | **`pwd`** | Exibe o caminho absoluto do diretório atual (*Print Working Directory*). |
| 4 | **`alias`** | Cria apelidos ou atalhos para comandos mais longos. |
| 5 | **`unalias`** | Remove um atalho criado previamente com o comando `alias`. |
| 6 | **`export`** | Define variáveis de ambiente para serem herdadas por processos filhos. |
| 7 | **`exit`** | Encerra a sessão atual do shell ou fecha a janela do terminal. |
| 8 | **`history`** | Exibe o histórico de comandos executados na sessão. |
| 9 | **`type`** | Informa se um comando é interno, externo, uma função ou um alias. |
| 10 | **`read`** | Captura dados digitados pelo usuário via teclado e os salva em uma variável. |
| 11 | **`source`** | Executa os comandos de um arquivo dentro do contexto do shell atual (atalho: `.`). |
| 12 | **`set`** | Define ou exibe opções e variáveis do comportamento do shell. |
| 13 | **`unset`** | Remove ou desativa variáveis e funções salvas na memória do shell. |
| 14 | **`bg`** | Envia um processo pausado para continuar executando em segundo plano (*background*). |
| 15 | **`fg`** | Traz uma tarefa rodando em segundo plano para o primeiro plano (*foreground*). |
| 16 | **`jobs`** | Lista todas as tarefas ativas rodando em primeiro ou segundo plano na sessão. |
| 17 | **`exec`** | Substitui a imagem do processo do shell atual por outro programa sem criar novo PID. |
| 18 | **`shopt`** | Ativa ou desativa opções avançadas de comportamento do Bash. |
| 19 | **`builtin`** | Força a execução da versão interna de um comando caso exista um programa externo com mesmo nome. |
| 20 | **`declare`** | Declara variáveis definindo tipos e atributos específicos (ex: somente leitura, arrays). |

---

## 20 Comandos Externos do Shell

| # | Comando | Caminho Comum | Descrição |
| :---: | :--- | :--- | :--- |
| 1 | **`ls`** | `/bin/ls` | Lista os arquivos e diretórios de um local. |
| 2 | **`cp`** | `/bin/cp` | Copia arquivos ou diretórios de uma origem para um destino. |
| 3 | **`mv`** | `/bin/mv` | Move ou renomeia arquivos e diretórios. |
| 4 | **`rm`** | `/bin/rm` | Remove/deleta arquivos ou diretórios do sistema de arquivos. |
| 5 | **`cat`** | `/bin/cat` | Concatena e exibe o conteúdo de arquivos na tela. |
| 6 | **`grep`** | `/usr/bin/grep` | Busca por padrões de texto dentro de arquivos usando expressões regulares. |
| 7 | **`find`** | `/usr/bin/find` | Procura arquivos no sistema com base em critérios como nome, tamanho e data. |
| 8 | **`mkdir`** | `/bin/mkdir` | Cria novos diretórios/pastas na estrutura do sistema. |
| 9 | **`chmod`** | `/bin/chmod` | Altera as permissões de acesso de arquivos e diretórios (leitura, escrita, execução). |
| 10 | **`chown`** | `/bin/chown` | Altera o proprietário (*owner*) e o grupo de um arquivo ou diretório. |
| 11 | **`top`** | `/usr/bin/top` | Exibe o uso de CPU, memória e os processos do sistema em tempo real. |
| 12 | **`ps`** | `/bin/ps` | Exibe um instantâneo (*snapshot*) dos processos em execução no momento. |
| 13 | **`kill`** | `/bin/kill` | Envia sinais para encerrar ou alterar o estado de processos no sistema. |
| 14 | **`ping`** | `/usr/bin/ping` | Envia pacotes ICMP para testar a conectividade de rede com um host. |
| 15 | **`curl`** | `/usr/bin/curl` | Transfere dados de ou para um servidor usando protocolos como HTTP, HTTPS e FTP. |
| 16 | **`tar`** | `/bin/tar` | Compacta ou extrai arquivos em pacotes organizados (`.tar`, `.tar.gz`). |
| 17 | **`nano`** | `/usr/bin/nano` | Editor de texto simplificado que roda diretamente no modo terminal. |
| 18 | **`df`** | `/bin/df` | Exibe o relatório de uso de espaço em disco de todas as partições montadas. |
| 19 | **`du`** | `/usr/bin/du` | Calcula e estima o tamanho ocupado no disco por arquivos ou pastas. |
| 20 | **`awk`** | `/usr/bin/awk` | Linguagem de programação voltada para varredura e processamento de texto estruturado. |

---

## Como identificar se um comando é interno ou externo no terminal?

Você pode usar o próprio comando builtin `type` para descobrir a natureza de qualquer comando:

```bash
# Testando um comando interno:
$ type cd
cd is a shell builtin

# Testando um comando externo:
$ type ls
ls is hashed (/bin/ls)

# Descobrindo o caminho de um binário externo:
$ which grep
/usr/bin/grep