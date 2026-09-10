# Arping — do básico ao avançado

## O que é

Arping é uma ferramenta que envia requisições ARP (e, opcionalmente, ICMP) para um host específico e exibe as respostas — funcionando como um "ping" que opera na camada 2 (enlace) em vez da camada 3 (rede). O host pode ser identificado por hostname, IP ou endereço MAC.

A versão presente no Kali Linux é a implementação de Thomas Habets (`ARPing`, não confundir com a versão mais simples do pacote `iputils-arping`), que traz um conjunto bem mais amplo de opções — incluindo detecção de endereços duplicados, ARP gratuito e spoofing de origem para fins de diagnóstico.

Por operar em nível de ARP, o arping tem uma vantagem prática sobre o `ping` tradicional: como o protocolo ARP não costuma ser filtrado por firewalls (diferente do ICMP, frequentemente bloqueado), ele consegue confirmar a presença de um host na rede local mesmo quando esse host não responde a ping — situação comum tanto em ambientes corporativos quanto durante a fase de descoberta de hosts de um pentest.

## Instalação

```bash
sudo apt install arping
```

Já vem pré-instalado no Kali Linux, categorizado em Remote System Discovery / Discovery.

## Nível básico

### Sintaxe geral

```
arping [opções] <host/ip/MAC>
```

### Ping ARP básico

```bash
arping -i eth0 192.168.1.1
```

`-i` especifica a interface de rede a ser usada — obrigatória na maioria dos casos, já que o ARP opera dentro de um segmento de rede específico. O comando envia requisições ARP para o IP informado e exibe o endereço MAC de quem responder, junto com o tempo de resposta.

### Limitando o número de requisições

```bash
arping -i eth0 -c 4 192.168.1.1
```

`-c` define quantas requisições serão enviadas antes de parar — equivalente ao `-c` do `ping` tradicional.

### Definindo um timeout

```bash
arping -i eth0 -w 5 192.168.1.1
```

`-w` encerra a execução após o número de segundos informado, independentemente de quantos pacotes já tenham sido enviados ou recebidos — útil para não deixar o comando esperando indefinidamente por um host que pode não estar ativo.

## Nível intermediário

### Saída compacta e saída bruta

```bash
arping -i eth0 -D 192.168.1.1     # exibe respostas como "!" e ausências como "."
arping -i eth0 -r 192.168.1.1     # saída bruta: só o MAC/IP de cada resposta
arping -i eth0 -R 192.168.1.1     # saída bruta, mostrando "o outro lado" (MAC em vez de IP, ou vice-versa)
```

`-D` produz uma saída compacta, no estilo do `ping` do FreeBSD. `-r` e `-R` são pensados para uso em scripts, retornando apenas o dado essencial (o endereço) sem texto adicional ao redor — mais fácil de capturar em uma variável ou pipe.

### Modo silencioso e alertas sonoros

```bash
arping -i eth0 -q -c 1 192.168.1.1; echo $?
```

`-q` suprime a saída normal, deixando apenas o código de saída do comando (útil em scripts que só precisam saber se houve resposta ou não). As flags `-a` e `-e` fazem o oposto na direção de feedback ao usuário: emitem um beep sonoro a cada resposta recebida (`-a`) ou quando não há resposta (`-e`).

### Detecção de endereços duplicados (DAD)

```bash
arping -i eth0 -d 192.168.1.50
```

`-d` (Duplicate Address Detection) verifica se mais de um dispositivo na rede está respondendo pelo mesmo endereço IP — cenário que indica um conflito de IP real, ou, em contextos de segurança, pode ser sintoma de spoofing ativo na rede. O comando retorna código de saída `1` caso identifique respostas de MACs diferentes para o mesmo IP.

### Endereçando via broadcast

```bash
arping -i eth0 -B
```

`-B` substitui o host de destino por `255.255.255.255`, endereçando a requisição a todos os dispositivos do segmento local de uma vez — uma forma simples de descobrir hosts ativos sem precisar testar IP por IP.

## Nível avançado

### ARP gratuito (unsolicited ARP)

```bash
arping -i eth0 -U -S 192.168.1.100
```

`-U` envia um ARP gratuito (unsolicited) — uma atualização de cache ARP enviada sem que ninguém tenha perguntado, normalmente usada por um host legítimo para anunciar seu próprio endereço na rede (por exemplo, depois de mudar de IP, ou ao assumir um IP virtual em um cluster de alta disponibilidade). `-P` faz o mesmo, mas usando pacotes de ARP REPLY em vez de ARP REQUEST.

Entender esse mecanismo é relevante do ponto de vista defensivo: como o protocolo ARP não possui autenticação, esse mesmo princípio (anunciar um MAC para um IP sem verificação) é a base técnica por trás de ataques de ARP spoofing/poisoning — realizados na prática por ferramentas dedicadas como `arpspoof` ou `ettercap`, fora do escopo do arping, que é uma ferramenta de diagnóstico pontual, não de spoofing contínuo.

### Spoofing de origem para diagnóstico

```bash
arping -i eth0 -p -s 00:11:22:33:44:55 -S 192.168.1.200 192.168.1.1
```

`-s` define um MAC de origem customizado e `-S` um IP de origem customizado — úteis para testar como a rede reage a um endereço específico sem precisar reconfigurar a própria interface. Como isso envolve usar um endereço que a interface não "possui" de fato, geralmente é necessário combinar com `-p`, que ativa o modo promíscuo na interface.

### Endereçamento direcionado por MAC

```bash
arping -i eth0 -S 192.168.1.200 -s 00:11:22:33:44:55 -p 192.168.1.1
```

Uma aplicação prática do spoofing de origem, citada na própria documentação da ferramenta: descobrir qual IP um MAC específico está usando na rede, sem precisar assumir esse IP para a própria máquina — útil em diagnósticos de rede onde já se conhece o MAC de um equipamento, mas não seu IP atual.

### VLAN tagging e prioridade 802.1p

```bash
arping -i eth0 -V 10 -Q 3 192.168.1.1
```

`-V` adiciona uma tag 802.1Q (VLAN) ao pacote ARP, e `-Q` define a prioridade 802.1p associada — relevante em ambientes de rede segmentados por VLAN, onde testar conectividade dentro de uma VLAN específica exige que o pacote já saia devidamente marcado.

### Timing entre pacotes

```bash
arping -i eth0 -W 2 -c 10 192.168.1.1
```

`-W` define o intervalo (em segundos) entre cada requisição enviada — diferente do `-w`, que define um timeout total para a execução inteira.

## Fluxo típico de uso

| Ordem | Cenário | Comando de exemplo |
|---|---|---|
| 1 | Confirmar se um host está ativo na rede local | `arping -i eth0 alvo` |
| 2 | Descobrir hosts ativos via broadcast | `arping -i eth0 -B` |
| 3 | Verificar conflito de IP na rede | `arping -i eth0 -d alvo` |
| 4 | Usar saída bruta em um script | `arping -i eth0 -r -c 1 alvo` |
| 5 | Testar anúncio de ARP gratuito | `arping -i eth0 -U -S ip_proprio` |

## Arping vs Ping vs arp-scan

O `ping` tradicional opera em ICMP (camada 3) e pode ser bloqueado por firewalls e configurações de host. O `arping` opera em ARP (camada 2), praticamente impossível de bloquear dentro do mesmo segmento de rede sem quebrar a comunicação normal — por isso costuma ser mais confiável para confirmar presença de um host na rede local. Já o `arp-scan`, outra ferramenta do Kali, resolve um problema diferente: em vez de testar um host por vez como o arping, ele varre uma faixa inteira de endereços de uma só vez, sendo mais indicado quando o objetivo é mapear todos os hosts ativos de uma sub-rede, e não confirmar um alvo específico.

## Considerações éticas e legais

Por operar apenas dentro do segmento de rede local (ARP não é roteável), o impacto do arping fica restrito à rede em que a máquina está conectada — ainda assim, seu uso para mapear dispositivos de uma rede que não é sua, ou o uso de spoofing de origem/ARP gratuito para interferir na comunicação de terceiros, deve se restringir a redes próprias ou a ambientes com autorização explícita, seguindo a mesma lógica já aplicada às demais ferramentas de descoberta e diagnóstico deste repositório.

## Referências

- Kali Linux Tools — arping
- Documentação oficial do ARPing (Thomas Habets) — habets.pp.se/synscan
- Repositório de desenvolvimento — github.com/ThomasHabets/arping