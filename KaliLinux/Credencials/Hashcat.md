# Hashcat — do básico ao avançado

## O que é

Hashcat é uma ferramenta de recuperação/quebra de senhas a partir de hashes, amplamente considerada a mais rápida do gênero por usar aceleração via GPU. Diferente do Medusa, que testa credenciais diretamente contra um serviço em rede (ataque online), o Hashcat trabalha de forma offline: ele recebe um arquivo contendo hashes já obtidos por algum outro meio (um dump de banco de dados, um handshake WPA capturado, um hash NTLM extraído de um Windows, por exemplo) e tenta descobrir a senha original que gerou aquele hash.

Suporta centenas de algoritmos de hash — MD5, SHA-family, NTLM, bcrypt, hashes de WPA/WPA2, Kerberos, entre muitos outros — cada um identificado por um número de modo.

## Instalação

```bash
sudo apt install hashcat
```

Já vem pré-instalado no Kali Linux. Por depender de GPU para melhor desempenho, também costuma exigir os drivers gráficos corretos (OpenCL/CUDA) instalados para aproveitar a aceleração por hardware.

## Nível básico

### Sintaxe geral

```
hashcat -m <modo_hash> -a <modo_ataque> <arquivo_de_hashes> <wordlist_ou_mascara>
```

### Identificando o tipo de hash

```bash
hashcat --example-hashes | grep -i ntlm
```

Antes de tentar quebrar um hash, é preciso saber qual algoritmo o gerou — o `-m` exige esse número. Alguns dos modos mais comuns:

| Formato | `-m` | Descrição |
|---|---|---|
| MD5 | 0 | MD5 padrão |
| SHA1 | 100 | SHA-1 |
| md5crypt | 500 | MD5 do Unix (`$1$`) |
| bcrypt | 3200 | Blowfish do Unix (`$2a$`) |
| SHA512crypt | 1800 | SHA-512 do Unix (`$6$`) |
| NTLM | 1000 | Hash NTLM do Windows |
| LM | 3000 | Windows LAN Manager (legado) |
| NetNTLMv2 | 5600 | Challenge/response do Windows em rede |
| WPA/WPA2 | 22000 | Handshake de Wi-Fi capturado |
| Kerberos 5 TGS | 13100 | Kerberoasting |
| AS-REP Roasting | 18200 | Contas sem pré-autenticação Kerberos |

### Ataque de dicionário

```bash
hashcat -m 1000 -a 0 hashes.txt rockyou.txt
```

O modo de ataque `-a 0` é o mais básico: testa cada palavra de uma wordlist (nesse exemplo, a clássica `rockyou.txt`, presente por padrão no Kali) contra os hashes fornecidos. É o ponto de partida natural, já que boa parte das senhas fracas do mundo real está catalogada nesse tipo de lista.

### Exibindo os resultados

```bash
hashcat -m 1000 hashes.txt --show
```

`--show` exibe apenas os hashes já quebrados em sessões anteriores, sem rodar um novo ataque — útil para consultar o progresso acumulado.

## Nível intermediário

### Modos de ataque (`-a`)

| `-a` | Nome | Descrição |
|---|---|---|
| 0 | Dictionary | Testa palavras de uma wordlist |
| 1 | Combinator | Combina palavras de duas wordlists diferentes entre si |
| 3 | Brute-force (mask) | Testa combinações baseadas em uma máscara de caracteres |
| 6 | Hybrid Wordlist + Mask | Wordlist seguida de caracteres extras via máscara |
| 7 | Hybrid Mask + Wordlist | Máscara seguida de uma wordlist |

### Ataque por máscara

```bash
hashcat -m 0 -a 3 hashes.txt ?d?d?d?d?d?d?d?d
```

Em vez de depender de uma wordlist, o modo `-a 3` testa combinações geradas a partir de uma máscara de caracteres. Os símbolos mais usados: `?l` (letra minúscula), `?u` (letra maiúscula), `?d` (dígito) e `?s` (caractere especial). O exemplo acima testa todas as combinações de 8 dígitos numéricos — útil para PINs ou senhas puramente numéricas.

### Ataque híbrido

```bash
hashcat -m 1000 -a 6 hashes.txt rockyou.txt ?d?d?d
```

Combina uma wordlist com uma máscara — nesse caso, testa cada palavra da wordlist seguida de três dígitos, cobrindo o padrão comum de senha "palavra + números" (ex: `senha123`) sem precisar ter essa variação explicitamente na wordlist.

### Salvando e filtrando resultados

```bash
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -o resultado.txt
hashcat -m 1000 hashes.txt --left
```

`-o` grava as senhas quebradas em um arquivo de saída. `--left` faz o oposto do `--show`: lista apenas os hashes que **ainda não** foram quebrados, útil para saber o que continua pendente depois de uma rodada de ataques.

## Nível avançado

### Ataque baseado em regras

```bash
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -r rules/best64.rule
```

`-r` aplica um conjunto de regras de transformação sobre cada palavra da wordlist — capitalizar a primeira letra, adicionar números ao final, trocar letras por caracteres visualmente parecidos (`a` → `@`, `e` → `3`), entre outras variações comuns que usuários reais aplicam às próprias senhas. É um dos recursos mais poderosos do Hashcat, porque multiplica a cobertura de uma wordlist sem precisar aumentá-la fisicamente.

### Charsets customizados

```bash
hashcat -m 0 -a 3 hashes.txt -1 ?l?d ?1?1?1?1?1?1
```

As flags `-1`, `-2`, `-3` e `-4` definem conjuntos de caracteres customizados para uso em máscaras — no exemplo, `?1` passa a representar "letra minúscula ou dígito", permitindo montar máscaras mais específicas do que os conjuntos padrão (`?l`, `?u`, `?d`, `?s`) sozinhos permitem.

### Benchmark e seleção de dispositivo

```bash
hashcat -b
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -d 1
```

`-b` roda um benchmark, útil para saber a velocidade estimada de quebra em diferentes algoritmos de hash na máquina atual antes de decidir se um ataque é viável em tempo razoável. `-d` restringe a execução a um dispositivo específico (GPU ou CPU), quando há mais de um disponível e se quer isolar o uso a um deles.

### Perfil de workload

```bash
hashcat -m 1000 -a 0 hashes.txt rockyou.txt -w 3
```

`-w` (1 a 4) ajusta o quanto o Hashcat prioriza a velocidade de quebra em detrimento da responsividade do sistema — `-w 1` é mais leve, `-w 4` extrai o máximo de desempenho possível, mas pode deixar a máquina praticamente inutilizável para outras tarefas enquanto roda.

### Sessões e retomada

```bash
hashcat -m 1000 -a 0 hashes.txt rockyou.txt --session teste1
hashcat --session teste1 --restore
```

`--session` nomeia a execução, permitindo retomá-la depois de uma interrupção com `--restore` — essencial em ataques longos, especialmente wordlists grandes combinadas com regras, que podem levar horas ou dias.

### Casos de uso em ambiente Active Directory

Dois modos específicos aparecem com frequência em testes contra ambientes Windows/Active Directory: **Kerberoasting** (`-m 13100`), que ataca hashes de tickets de serviço Kerberos (TGS) solicitados para contas de serviço, e **AS-REP Roasting** (`-m 18200`), que ataca hashes obtidos de contas configuradas sem exigência de pré-autenticação Kerberos. Em ambos os casos, o Hashcat entra na etapa final de um ataque que começou com a extração dos hashes por outra ferramenta (como o Impacket, mencionado como dependência do Legion) — o Hashcat propriamente só cuida da quebra offline depois que o hash já foi obtido.

## Fluxo típico de uso

| Ordem | Etapa | Comando de exemplo |
|---|---|---|
| 1 | Identificar o tipo de hash | `hashcat --example-hashes` |
| 2 | Rodar benchmark (opcional) | `hashcat -b` |
| 3 | Ataque de dicionário inicial | `hashcat -m X -a 0 hashes.txt rockyou.txt` |
| 4 | Aplicar regras sobre a wordlist | `-r rules/best64.rule` |
| 5 | Ataque por máscara para padrões específicos | `-a 3` com `?l?u?d?s` |
| 6 | Consultar resultados | `--show` / `--left` |
| 7 | Retomar sessões longas | `--session` / `--restore` |

## Hashcat vs Medusa/Hydra

A distinção mais importante para não confundir as ferramentas: Medusa e Hydra atacam um serviço **online**, tentando autenticar de verdade contra ele — cada tentativa gera uma conexão real e fica sujeita a bloqueios de conta, rate limiting e logs do serviço-alvo. O Hashcat ataca um hash **offline**, sem nenhuma interação com o sistema de origem — a única limitação é o poder de processamento disponível. Isso também muda completamente o contexto de uso: o Hashcat só entra em jogo depois que os hashes já foram obtidos por algum outro meio (dump de banco, extração de memória, captura de handshake Wi-Fi, etc.), geralmente numa etapa de pós-exploração.

## Considerações éticas e legais

Assim como as demais ferramentas de quebra de credenciais já documentadas, o Hashcat só deve ser usado sobre hashes que você tem autorização explícita para atacar — seja em um pentest com escopo definido, em um CTF, ou para recuperar uma senha própria esquecida. Obter e tentar quebrar hashes de terceiros sem autorização configura acesso indevido a dados protegidos na maioria das legislações, mesmo que a tentativa não seja bem-sucedida.

## Referências

- Documentação oficial do Hashcat (hashcat.net)
- Manual do Hashcat (`man hashcat`)
- Kali Linux Tools — hashcat