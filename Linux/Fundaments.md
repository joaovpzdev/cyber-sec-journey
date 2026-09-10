# Fundamentos Linux — Comandos

Referência de comandos essenciais do Linux, organizada por categoria.

## Navegação e listagem

| Comando | Descrição |
|---|---|
| `pwd` | Exibe o diretório atual |
| `ls` | Lista arquivos e diretórios |
| `ls -la` | Lista todos os arquivos, incluindo ocultos, em formato detalhado |
| `cd diretorio` | Muda para o diretório especificado |
| `cd ..` | Sobe um nível na hierarquia |
| `cd ~` | Vai para o diretório home do usuário |
| `tree` | Exibe a estrutura de diretórios em árvore |

## Manipulação de arquivos e diretórios

| Comando | Descrição |
|---|---|
| `touch arquivo` | Cria um arquivo vazio |
| `mkdir diretorio` | Cria um diretório |
| `mkdir -p a/b/c` | Cria diretórios aninhados |
| `cp origem destino` | Copia arquivo ou diretório |
| `cp -r origem destino` | Copia diretórios recursivamente |
| `mv origem destino` | Move ou renomeia arquivo/diretório |
| `rm arquivo` | Remove um arquivo |
| `rm -r diretorio` | Remove um diretório recursivamente |
| `rm -rf diretorio` | Remove sem confirmação (usar com cautela) |
| `ln -s alvo link` | Cria um link simbólico |

## Leitura e edição de arquivos

| Comando | Descrição |
|---|---|
| `cat arquivo` | Exibe o conteúdo completo de um arquivo |
| `less arquivo` | Exibe o conteúdo com paginação |
| `head arquivo` | Exibe as primeiras linhas |
| `tail arquivo` | Exibe as últimas linhas |
| `tail -f arquivo` | Acompanha o arquivo em tempo real (útil para logs) |
| `nano arquivo` | Editor de texto simples em terminal |
| `vim arquivo` | Editor de texto avançado em terminal |

## Busca

| Comando | Descrição |
|---|---|
| `find /caminho -name "*.txt"` | Busca arquivos por nome |
| `find /caminho -type d` | Busca apenas diretórios |
| `grep "termo" arquivo` | Busca um termo dentro de um arquivo |
| `grep -r "termo" diretorio` | Busca recursivamente em um diretório |
| `which comando` | Mostra o caminho do executável de um comando |
| `locate arquivo` | Busca arquivos usando índice pré-construído |

## Permissões e propriedade

| Comando | Descrição |
|---|---|
| `chmod 755 arquivo` | Define permissões (rwx para dono, r-x para grupo/outros) |
| `chmod +x arquivo` | Adiciona permissão de execução |
| `chown usuario:grupo arquivo` | Altera o dono e o grupo de um arquivo |
| `chgrp grupo arquivo` | Altera apenas o grupo de um arquivo |
| `umask` | Exibe ou define a máscara de permissões padrão |

Notação numérica de permissões: leitura = 4, escrita = 2, execução = 1. A soma define a permissão de cada classe (dono, grupo, outros). Exemplo: `755` = dono com leitura/escrita/execução, grupo e outros com leitura/execução.

## Processos

| Comando | Descrição |
|---|---|
| `ps aux` | Lista todos os processos em execução |
| `top` | Monitor de processos em tempo real |
| `htop` | Versão interativa do `top` (requer instalação) |
| `kill PID` | Envia sinal de término a um processo |
| `kill -9 PID` | Força o encerramento de um processo |
| `comando &` | Executa um comando em segundo plano |
| `jobs` | Lista processos em segundo plano da sessão atual |
| `fg` | Traz um processo em segundo plano para primeiro plano |

## Redirecionamento e pipes

| Operador | Descrição |
|---|---|
| `>` | Redireciona saída para um arquivo (sobrescreve) |
| `>>` | Redireciona saída para um arquivo (concatena) |
| `<` | Usa um arquivo como entrada de um comando |
| `\|` | Encadeia a saída de um comando como entrada de outro |
| `2>` | Redireciona apenas mensagens de erro |
| `2>&1` | Redireciona erro para o mesmo destino da saída padrão |

## Variáveis de ambiente e shell

| Comando | Descrição |
|---|---|
| `echo $VARIAVEL` | Exibe o valor de uma variável de ambiente |
| `export VARIAVEL=valor` | Define uma variável de ambiente |
| `env` | Lista todas as variáveis de ambiente |
| `echo $PATH` | Exibe os diretórios onde o shell busca executáveis |
| `alias nome='comando'` | Cria um atalho para um comando |
| `history` | Exibe o histórico de comandos executados |

## Gerenciamento de pacotes

| Distribuição | Instalar | Atualizar | Remover |
|---|---|---|---|
| Debian/Ubuntu (apt) | `apt install pacote` | `apt update && apt upgrade` | `apt remove pacote` |
| Fedora/RHEL (dnf) | `dnf install pacote` | `dnf upgrade` | `dnf remove pacote` |
| Arch (pacman) | `pacman -S pacote` | `pacman -Syu` | `pacman -R pacote` |

## Informações do sistema

| Comando | Descrição |
|---|---|
| `uname -a` | Exibe informações do kernel e sistema |
| `df -h` | Exibe uso de espaço em disco |
| `du -sh diretorio` | Exibe o tamanho de um diretório |
| `free -h` | Exibe uso de memória RAM |
| `whoami` | Exibe o usuário atual |
| `uptime` | Exibe o tempo de atividade do sistema |

## Referências

- Documentação oficial de cada distribuição
- `man comando` — manual de qualquer comando diretamente no terminal

