# John the Ripper — do básico ao avançado

## O que é

John the Ripper (frequentemente abreviado como "John" ou "JtR") é uma das ferramentas de quebra de senha mais antigas e conhecidas em segurança da informação, criada por Solar Designer e mantida pelo projeto Openwall. Assim como o Hashcat, trabalha de forma **offline**: recebe um arquivo de hashes já obtidos por algum outro meio e tenta descobrir a senha original.

A principal diferença histórica em relação ao Hashcat é o foco: o John nasceu como uma ferramenta orientada a CPU, com grande ênfase em detecção automática de formato de hash e em um sistema de regras bastante maduro, enquanto o Hashcat é historicamente mais voltado a desempenho bruto via GPU. A versão "Jumbo" do John — mantida pela comunidade e presente no Kali Linux — adiciona suporte a GPU e a uma quantidade muito maior de formatos, reduzindo boa parte dessa diferença.

## Instalação

```bash
sudo apt install john
```

Já vem pré-instalado no Kali Linux (versão Jumbo). O pacote inclui, além do binário principal `john`, uma série de scripts auxiliares para converter diferentes formatos de arquivo em hashes que o John consegue processar.

## Nível básico

### Sintaxe geral

```
john [opções] <arquivo_de_hashes>
```

### Detecção automática de formato

```bash
john hashes.txt
```

Sem nenhuma flag adicional, o John tenta identificar automaticamente o formato do hash e roda, por padrão, uma sequência de modos (single crack, depois wordlist, depois incremental) — um dos recursos mais citados da ferramenta, já que muitas vezes dispensa a necessidade de especificar manualmente o tipo de hash.

### Ataque de dicionário

```bash
john --wordlist=rockyou.txt hashes.txt
```

Testa cada palavra da wordlist informada contra os hashes do arquivo.

### Exibindo os resultados

```bash
john --show hashes.txt
```

Toda senha quebrada pelo John é armazenada automaticamente em um arquivo local chamado `john.pot`, que também evita reprocessar hashes já quebrados em execuções futuras. `--show` lê esse arquivo e exibe os resultados já descobertos, sem rodar um novo ataque.

## Nível intermediário

### Modos de ataque

```bash
john --single hashes.txt        # single crack mode
john --wordlist=lista.txt hashes.txt   # wordlist mode
john --incremental hashes.txt   # incremental (brute-force)
```

- **Single crack mode** (`--single`): gera candidatos de senha a partir de informações já presentes no próprio arquivo de hashes (como nome de usuário), testando variações delas — costuma ser o modo mais rápido a encontrar senhas fracas óbvias, justamente por isso é o primeiro a rodar no modo automático.
- **Wordlist mode** (`--wordlist`): o clássico ataque de dicionário.
- **Incremental mode** (`--incremental`): brute-force puro, testando todas as combinações possíveis dentro de um conjunto de caracteres — o mais exaustivo e o mais lento dos três.

### Regras de mutação

```bash
john --wordlist=rockyou.txt --rules hashes.txt
```

`--rules` aplica transformações automáticas a cada palavra da wordlist (capitalizar, adicionar números, trocar letras por símbolos parecidos) — o mesmo conceito das regras do Hashcat, aumentando a cobertura de uma wordlist sem precisar expandi-la fisicamente. Um exemplo comum: a palavra `password` sendo testada também como `Password1!` a partir de uma única regra.

### Preparando arquivos de hash

O John não lê qualquer arquivo diretamente — para diversos formatos, é preciso primeiro convertê-los para o formato de hash que ele espera, usando scripts auxiliares incluídos no pacote:

```bash
unshadow /etc/passwd /etc/shadow > hashes.txt   # hashes de senha do Linux
zip2john protegido.zip > zip_hash.txt           # arquivos .zip protegidos por senha
rar2john protegido.rar > rar_hash.txt           # arquivos .rar protegidos por senha
ssh2john id_rsa > ssh_hash.txt                  # chaves privadas SSH protegidas por senha
pdf2john.pl protegido.pdf > pdf_hash.txt        # PDFs protegidos por senha
```

Esse padrão `*2john` se repete para vários outros formatos (Office, 7z, KeePass, etc.) — todos convertem o arquivo original em uma representação de hash que o `john` consegue processar normalmente com os modos de ataque já vistos.

## Nível avançado

### Forçando um formato específico

```bash
john --list=formats
john --format=raw-md5 hashes.txt
```

`--list=formats` mostra todos os formatos de hash suportados pela instalação atual. `--format` força um formato específico quando a detecção automática falha ou quando o arquivo contém hashes de mais de um tipo misturados.

### Gerenciamento de sessões

```bash
john --session=teste1 --wordlist=rockyou.txt hashes.txt
john --restore=teste1
john --status=teste1
```

`--session` nomeia a execução para retomá-la depois. `--restore` continua uma sessão interrompida a partir de onde parou, e `--status` consulta o progresso de uma sessão sem interrompê-la — essencial em ataques longos, assim como no Hashcat.

### Filtros de carga

```bash
john --users=root,admin hashes.txt
john --shells=-/bin/false hashes.txt
```

`--users` restringe o ataque a usuários específicos dentro do arquivo de hashes. `--shells` filtra por shell configurado no `/etc/passwd` — por exemplo, excluir (`-`) contas de serviço sem shell interativo (`/bin/false`), focando o ataque apenas em contas que realmente fazem login.

### Benchmark

```bash
john --test
```

Roda um benchmark de desempenho para os formatos suportados na máquina atual, útil para estimar se um ataque é viável em tempo razoável antes de iniciá-lo de fato — equivalente ao `-b` do Hashcat.

### Removendo hashes já quebrados

```bash
john --wordlist=rockyou.txt --format=raw-md5 --remove hashes.txt
```

`--remove` elimina do arquivo de entrada os hashes que já foram quebrados, mantendo apenas os que ainda resistem — útil para focar esforço computacional só no que falta.

## Fluxo típico de uso

| Ordem | Etapa | Comando de exemplo |
|---|---|---|
| 1 | Converter o arquivo de origem em hash | `unshadow` / `zip2john` / `ssh2john` |
| 2 | Rodar detecção automática | `john hashes.txt` |
| 3 | Ataque de dicionário com regras | `--wordlist=rockyou.txt --rules` |
| 4 | Ataque incremental, se necessário | `--incremental` |
| 5 | Consultar resultados | `--show` |
| 6 | Retomar sessões longas | `--session` / `--restore` |

## John vs Hashcat

Ambos resolvem o mesmo problema — quebra de hash offline — mas com ênfases diferentes. O John se destaca pela detecção automática de formato, pelo modo single crack (muito eficaz contra senhas fracas óbvias) e por um ecossistema maduro de scripts `*2john` para preparar hashes a partir de arquivos do mundo real (ZIPs, chaves SSH, documentos protegidos). O Hashcat historicamente leva vantagem em velocidade bruta via GPU, especialmente contra grandes volumes de hashes do mesmo tipo. Na prática, é comum um mesmo pentest usar os `*2john` para extrair e formatar o hash, e então decidir entre John ou Hashcat para a quebra propriamente dita, conforme o volume de dados e o hardware disponível.

## Considerações éticas e legais

Mesma ressalva já feita para Medusa e Hashcat: o John só deve ser usado sobre hashes que você tem autorização explícita para atacar — em um pentest com escopo definido, em um CTF, ou para recuperar uma senha própria esquecida. Extrair e tentar quebrar hashes de terceiros sem autorização configura acesso indevido a dados protegidos na maioria das legislações, independentemente do sucesso da tentativa.

## Referências

- Openwall — John the Ripper (openwall.com/john)
- Repositório da versão Jumbo — openwall/john (GitHub)
- Manual do John the Ripper (`man john`)