# SQL Injection (SQLi)

## O que é

SQL Injection é uma vulnerabilidade que ocorre quando uma aplicação insere dados fornecidos pelo usuário diretamente em uma consulta SQL, sem validação ou tratamento adequado. Isso permite que um atacante manipule a consulta original, alterando seu comportamento — podendo ler, modificar ou apagar dados do banco, e em alguns casos até executar comandos no servidor.

A causa raiz é sempre a mesma: **mistura de dado com código**. A aplicação confia que o que o usuário digitou é apenas um valor, mas o banco de dados o interpreta como parte da instrução SQL.

## Por que acontece

Considere uma consulta construída por concatenação de strings, como em um formulário de login:

```sql
SELECT * FROM usuarios WHERE login = 'INPUT_LOGIN' AND senha = 'INPUT_SENHA';
```

Se a aplicação simplesmente concatena o que o usuário digitou no campo `login`, sem tratamento, o valor digitado passa a fazer parte da estrutura da consulta — não é apenas um dado.

## Exemplo conceitual

Suponha o seguinte código (pseudocódigo, propositalmente vulnerável, para fins de estudo):

```python
query = "SELECT * FROM usuarios WHERE login = '" + login + "' AND senha = '" + senha + "'"
```

Se o valor digitado no campo `login` for:

```
' OR '1'='1
```

A consulta final se torna:

```sql
SELECT * FROM usuarios WHERE login = '' OR '1'='1' AND senha = '...'
```

Como `'1'='1'` é sempre verdadeiro, a condição do `WHERE` pode ser satisfeita independentemente das credenciais reais, o que pode permitir login sem senha válida, dependendo da lógica da aplicação.

Esse é o exemplo mais clássico e didático de SQLi, usado para ilustrar o conceito — na prática, ataques reais costumam ser mais elaborados e adaptados à estrutura específica de cada aplicação.

## Tipos de SQL Injection

**In-band (clássica)**
O atacante usa o mesmo canal para enviar o ataque e receber o resultado. Se divide em:
- *Error-based*: o atacante provoca erros no banco que revelam informações na própria mensagem de erro retornada pela aplicação.
- *Union-based*: o atacante usa a cláusula `UNION` para combinar o resultado de uma consulta maliciosa com o de uma consulta legítima, extraindo dados adicionais.

**Blind (cega)**
A aplicação não retorna o erro nem o dado diretamente na tela, mas o atacante consegue inferir informações observando o comportamento da aplicação. Se divide em:
- *Boolean-based*: o atacante envia condições verdadeiras ou falsas e observa diferenças na resposta da aplicação (ex: página carrega normalmente ou não).
- *Time-based*: o atacante usa comandos que atrasam a resposta do banco (ex: `SLEEP()`) para inferir informações a partir do tempo de resposta.

**Out-of-band**
O atacante usa um canal diferente (como uma requisição DNS ou HTTP) para receber os dados extraídos, útil quando não há retorno direto na aplicação.

## Impacto

- Leitura de dados sensíveis (senhas, dados pessoais, informações financeiras)
- Modificação ou exclusão de dados
- Bypass de autenticação
- Em cenários mais graves, execução de comandos no sistema operacional do servidor, dependendo da configuração do banco

## Como prevenir

**Consultas parametrizadas (prepared statements)**
A forma mais eficaz de prevenção. O valor do usuário é tratado como dado, nunca como parte do código SQL.

```python
cursor.execute("SELECT * FROM usuarios WHERE login = %s AND senha = %s", (login, senha))
```

**ORMs (Object-Relational Mapping)**
Frameworks como Prisma, SQLAlchemy ou Sequelize já tratam a parametrização internamente quando usados corretamente, reduzindo o risco de erro manual.

**Validação e sanitização de entrada**
Complementar às consultas parametrizadas — nunca deve ser a única linha de defesa.

**Princípio do menor privilégio**
O usuário do banco de dados usado pela aplicação deve ter apenas as permissões estritamente necessárias, limitando o dano em caso de exploração bem-sucedida.

**Web Application Firewall (WAF)**
Camada adicional de proteção que pode detectar e bloquear padrões suspeitos, mas não substitui a correção na aplicação.

## Ferramentas usadas em testes de segurança

- **sqlmap**: ferramenta open source para automatizar a identificação e exploração de SQLi em ambientes de teste autorizados
- **Burp Suite**: usado para interceptar e manipular requisições HTTP durante testes manuais
- **OWASP ZAP**: scanner de vulnerabilidades web, inclui detecção de SQLi

Testes de SQLi devem ser realizados apenas em ambientes próprios ou com autorização explícita (ex: labs como TryHackMe, HackTheBox, DVWA, PortSwigger Web Security Academy).

## Para praticar

- **DVWA (Damn Vulnerable Web Application)**: aplicação propositalmente vulnerável para prática local
- **PortSwigger Web Security Academy**: labs gratuitos com cenários de SQLi de dificuldade crescente
- **TryHackMe / HackTheBox**: salas e máquinas dedicadas ao tema

## Referências

- OWASP — SQL Injection Prevention Cheat Sheet
- PortSwigger Web Security Academy — SQL Injection