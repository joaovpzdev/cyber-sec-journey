# Medusa — do básico ao avançado

## O que é

Medusa é uma ferramenta de força bruta de credenciais (login brute-forcer), massivamente paralela e modular, criada por JoMo-Kun e mantida pela Foofus Networks. O objetivo declarado do projeto é oferecer suporte ao maior número possível de serviços que permitem autenticação remota — SSH, FTP, HTTP, Telnet, VNC, MySQL, SMB, entre muitos outros.

Sua principal característica é o desempenho: os testes são feitos em threads paralelas, permitindo atacar múltiplos hosts, usuários ou senhas simultaneamente, o que a torna consideravelmente mais rápida que ferramentas de brute force sequenciais.

## Instalação

```bash
sudo apt install medusa
```

Já vem pré-instalado no Kali Linux, categorizado nas seções Brute Force e Credential Access. A arquitetura é modular: cada serviço suportado existe como um arquivo `.mod` independente, o que permite estender a lista de serviços atacáveis sem modificar o núcleo da aplicação.

## Nível básico

### Sintaxe geral

```
medusa [-h host|-H arquivo] [-u usuario|-U arquivo] [-p senha|-P arquivo] [-C arquivo] -M módulo [OPT]
```

### Testando uma credencial única

```bash
medusa -h 192.168.1.10 -u admin -p senha123 -M ssh
```

Testa um único par usuário/senha contra o serviço SSH do host informado.

### Testando com wordlists

```bash
medusa -h 192.168.1.10 -U usuarios.txt -P senhas.txt -M ftp
```

`-U` e `-P` apontam para arquivos contendo, respectivamente, listas de usuários e senhas — o Medusa testa as combinações entre eles contra o módulo indicado (nesse caso, FTP).

### Listando os módulos disponíveis

```bash
medusa -d
```

Retorna todos os módulos de serviço instalados na versão atual do Medusa. Alguns dos mais usados:

| Módulo (`-M`) | Serviço |
|---|---|
| `ssh` | SSH |
| `ftp` | FTP |
| `http` | HTTP (autenticação básica) |
| `telnet` | Telnet |
| `smbnt` | SMB / Windows |
| `mysql` | MySQL |
| `mssql` | Microsoft SQL Server |
| `postgres` | PostgreSQL |
| `vnc` | VNC |
| `pop3` / `imap` / `smtp` | E-mail (POP3, IMAP, SMTP) |
| `snmp` | SNMP |
| `svn` | Subversion |
| `rlogin` / `rsh` / `rexec` | Serviços remotos legados (r-commands) |
| `web-form` | Formulários de login web (HTTP POST) |
| `generic` | Wrapper genérico, para protocolos não cobertos nativamente |

## Nível intermediário

### Múltiplos hosts simultâneos

```bash
medusa -H hosts.txt -U usuarios.txt -P senhas.txt -M ssh
```

`-H` funciona como o `-U`/`-P`, mas para uma lista de hosts — o Medusa distribui os testes entre todos eles, respeitando o nível de paralelismo configurado.

### Verificações adicionais de senha

```bash
medusa -h alvo -U usuarios.txt -e ns -M ssh
```

A flag `-e` adiciona testes automáticos além da wordlist: `n` testa senha vazia, `s` testa senha igual ao próprio nome de usuário, e `ns` combina os dois — útil para capturar credenciais fracas óbvias sem precisar incluí-las manualmente na wordlist.

### Porta não padrão e SSL

```bash
medusa -h alvo -n 2222 -s -U usuarios.txt -P senhas.txt -M ssh
```

`-n` especifica uma porta diferente da padrão do serviço (útil quando o SSH, por exemplo, roda em uma porta customizada), e `-s` habilita SSL/TLS na conexão, quando aplicável ao módulo.

### Parar ao encontrar uma credencial válida

```bash
medusa -h alvo -U usuarios.txt -P senhas.txt -M ftp -f
```

`-f` interrompe o teste naquele host assim que a primeira combinação válida é encontrada. `-F` vai além: interrompe o teste em **todos** os hosts do escopo assim que a primeira credencial válida for encontrada em qualquer um deles.

### Controle de paralelismo

```bash
medusa -h alvo -U usuarios.txt -P senhas.txt -M ssh -t 4 -T 2
```

`-t` define quantas tentativas de login são testadas simultaneamente por host, e `-T` define quantos hosts são testados simultaneamente. Ajustar esses valores é o principal jeito de equilibrar velocidade contra o risco de sobrecarregar o serviço-alvo ou disparar bloqueios de conta.

## Nível avançado

### Arquivo de combinações (combo file)

```bash
medusa -C combo.txt -M ssh
```

Em vez de testar todo o produto cartesiano entre usuários e senhas, o `-C` aceita um arquivo com combinações já definidas (no formato `host:usuario:senha`), permitindo um ataque mais direcionado quando já se tem alguma informação sobre credenciais prováveis, em vez de uma varredura completa e menos eficiente.

### Paralelização por usuário

```bash
medusa -h alvo -U usuarios.txt -P senhas.txt -M ssh -L
```

Por padrão, o Medusa processa toda a lista de senhas para um usuário antes de passar ao próximo. A flag `-L` altera esse comportamento, paralelizando por thread de usuário — cada usuário é testado em uma thread separada desde o início, o que pode acelerar o processo dependendo do tamanho relativo das listas de usuários e senhas.

### Log e retomada de varredura

```bash
medusa -h alvo -U usuarios.txt -P senhas.txt -M ssh -O log.txt
medusa -Z mapa_anterior -M ssh
```

`-O` grava as tentativas em um arquivo de log. `-Z` permite retomar uma varredura anterior a partir de um mapa de progresso salvo, útil em testes longos contra listas grandes que precisam ser interrompidos e continuados depois.

### Controle fino de timeout e reconexão

```bash
medusa -h alvo -U usuarios.txt -P senhas.txt -M ssh -g 5 -r 2 -R 3
```

`-g` define quantos segundos esperar por uma conexão antes de desistir, `-r` define o intervalo entre novas tentativas, e `-R` define quantas vezes tentar reconectar antes de desistir daquele alvo — parâmetros úteis para adaptar o comportamento em redes instáveis ou serviços com limitação de taxa.

### Verbosidade e depuração

```bash
medusa -h alvo -U usuarios.txt -P senhas.txt -M ssh -v 4 -w 3
```

`-v` controla o nível de detalhe exibido durante a execução (0 a 6), e `-w` controla o nível de depuração de erros (0 a 10) — úteis para diagnosticar por que um módulo específico não está se conectando como esperado.

### Parâmetros específicos de módulo

```bash
medusa -M http -q
```

A flag `-q`, combinada com `-M`, exibe as informações de uso específicas daquele módulo — muitos módulos aceitam parâmetros próprios via `-m` (por exemplo, o módulo `web-form` precisa que sejam informados os nomes dos campos do formulário de login a ser atacado).

### Extensibilidade via módulos

Como cada serviço é implementado como um arquivo `.mod` independente, é possível desenvolver novos módulos para protocolos não cobertos nativamente, seguindo a estrutura documentada no próprio projeto — o mesmo princípio de extensibilidade citado no `Legion.md`, aqui aplicado especificamente à camada de autenticação.

## Fluxo típico de uso

| Ordem | Ação | Comando de exemplo |
|---|---|---|
| 1 | Confirmar o serviço-alvo (via footprinting/scanning) | `nmap -sV alvo` |
| 2 | Listar módulos disponíveis | `medusa -d` |
| 3 | Teste inicial com credencial única | `medusa -h alvo -u usuario -p senha -M módulo` |
| 4 | Ataque com wordlists | `medusa -h alvo -U usuarios.txt -P senhas.txt -M módulo` |
| 5 | Ajuste de paralelismo e verificações extras | `-t`, `-T`, `-e ns` |
| 6 | Parar ao encontrar credencial válida | `-f` / `-F` |
| 7 | Log e retomada de varreduras longas | `-O`, `-Z` |

## Medusa vs Hydra

Ambas cumprem o mesmo papel — força bruta de autenticação — e frequentemente aparecem juntas em discussões de brute force (inclusive como dependências de ferramentas de orquestração como o Legion). A diferença mais citada entre as duas está na arquitetura de módulos: no Medusa, cada serviço é um arquivo `.mod` isolado, o que facilita a manutenção e a adição de novos serviços sem alterar o núcleo do programa. Na prática, a escolha entre uma e outra costuma se dar por familiaridade com a sintaxe ou por qual delas já possui um módulo mais maduro para o serviço específico sendo testado.

## Considerações éticas e legais

Diferente de ferramentas de reconhecimento passivo, o Medusa realiza tentativas de autenticação reais contra o serviço-alvo — cada tentativa gera tráfego e, na maioria dos sistemas, entradas de log. Usar essa ferramenta sem autorização explícita configura tentativa de acesso indevido a sistema de informação na maioria das legislações, independentemente de as credenciais testadas serem ou não bem-sucedidas. Além do risco legal, ataques de força bruta mal calibrados (paralelismo alto, sem pausas) podem causar bloqueio de contas legítimas ou instabilidade no serviço atacado — mesmo em testes autorizados, o volume e a velocidade devem ser combinados previamente com o cliente.

## Referências

- Kali Linux Tools — medusa
- Manual oficial do Medusa (`man medusa`)
- Foofus Networks — projeto original do Medusa