# Access Points Não Autorizados (Rogue APs) e Dispositivos Sem Fio Clandestinos

> Anotações de estudo complementares ao curso **Network Defense** da Cisco Networking Academy, com casos reais de ataques.

**Ideia central:** um único dispositivo sem fio ligado em uma tomada de rede pode **furar todo o perímetro** da empresa. O firewall protege a entrada da internet, mas o dispositivo clandestino cria uma **porta lateral** que não passa por ele.

---

## Sumário

1. [O que é um rogue AP](#1-o-que-é-um-rogue-ap)
2. [Tipos de dispositivos sem fio indesejados](#2-tipos-de-dispositivos-sem-fio-indesejados)
3. [Por que são tão perigosos](#3-por-que-são-tão-perigosos)
4. [Como um ataque acontece](#4-como-um-ataque-acontece)
5. [Casos reais](#5-casos-reais)
6. [O que os casos ensinam](#6-o-que-os-casos-ensinam)
7. [Como detectar](#7-como-detectar)
8. [Como prevenir e responder](#8-como-prevenir-e-responder)
9. [Relação com os labs de Packet Tracer](#9-relação-com-os-labs-de-packet-tracer)
10. [Resumo rápido](#10-resumo-rápido)
11. [Vocabulário](#11-vocabulário-inglês--português)
12. [Fontes](#12-fontes)

---

## 1. O que é um rogue AP

Um **rogue AP** (*access point* não autorizado, ou "AP clandestino") é um ponto de acesso sem fio **ligado à rede cabeada da empresa sem autorização** da equipe de TI ou segurança.

```text
          Internet
             │
        [Firewall]  ← protege a entrada "oficial"
             │
   ──────────┴──────────  rede cabeada interna (confiável)
      │            │
  [Switch]     [Switch]
      │            │
  [PCs]       [Rogue AP] ))) ))) ))) 📶 ← porta lateral sem fio
                                   │
                         [Atacante no estacionamento]
```

O atacante conectado ao rogue AP fica **"dentro" da rede**, como se estivesse em uma mesa do escritório, **sem passar pelo firewall**.

---

## 2. Tipos de dispositivos sem fio indesejados

| Tipo | Descrição | Intenção |
| --- | --- | --- |
| **Rogue AP de funcionário** (*shadow IT*) | Um funcionário compra um roteador Wi-Fi e liga na tomada da mesa, para ter sinal melhor | Sem má intenção, mas costuma ficar **aberto ou com senha fraca** |
| **Rogue AP malicioso** | O atacante esconde um AP na empresa (sala de reunião, embaixo de uma mesa, no forro) | Acesso remoto à rede interna |
| **Soft AP** | Um notebook ou celular ligado na rede cabeada compartilha a conexão por Wi-Fi (*hotspot*) | Pode ser acidental ou malicioso. Difícil de achar, porque não é um AP físico. |
| **Evil twin** (gêmeo do mal) | AP do atacante com o **mesmo nome (SSID)** da rede legítima | Enganar os usuários para capturar senhas e tráfego |
| **Drop box com modem celular** | Pequeno computador (Raspberry Pi, por exemplo) ligado na rede cabeada, com modem 3G/4G | Acesso remoto **sem passar por nenhum controle da empresa** |
| **AP vizinho** (*neighbor AP*) | AP de outra empresa ou de um morador próximo | Normalmente inofensivo, mas precisa ser classificado para não ser confundido com um rogue |

**Rogue x evil twin:**
- O **rogue AP** está **ligado à rede da empresa** e dá acesso a ela.
- O **evil twin** **não precisa** estar ligado à rede da empresa. Ele **imita** a rede para enganar os usuários.

---

## 3. Por que são tão perigosos

1. **Ignoram o firewall de borda.** O tráfego do atacante entra pela rede interna, não pela internet.
2. **A rede interna costuma confiar demais.** Muitas empresas protegem bem a borda e deixam o interior "plano", sem segmentação.
3. **O sinal atravessa paredes.** O atacante pode ficar no estacionamento, em um prédio vizinho ou até usar um drone.
4. **São baratos e pequenos.** Um Raspberry Pi ou um AP de bolso custa pouco e cabe em qualquer canto.
5. **Um canal celular é invisível para a rede.** Se o dispositivo usa 4G, os dados saem **sem passar** pelo firewall, pelo proxy nem pelo IDS da empresa.
6. **Funcionários criam o problema sem querer.** Um AP doméstico configurado com padrões de fábrica é uma porta aberta.

---

## 4. Como um ataque acontece

| Etapa | O que o atacante faz | Exemplo |
| --- | --- | --- |
| 1. **Reconhecimento** | Mapeia redes sem fio próximas e o prédio | *Wardriving*: dirigir com um notebook procurando redes |
| 2. **Acesso inicial** | Instala o dispositivo ou explora um Wi-Fi fraco | Entra como entregador e liga um Raspberry Pi na sala de reunião |
| 3. **Canal remoto** | Garante acesso de fora | Wi-Fi do rogue AP, ou modem 4G |
| 4. **Descoberta** | Varre a rede interna em busca de servidores e senhas | Scans de portas, captura de tráfego |
| 5. **Movimento lateral** | Pula de máquina em máquina | Usa credenciais roubadas e RDP |
| 6. **Objetivo final** | Rouba dados ou dinheiro, ou instala malware | Captura números de cartão, transfere fundos |

---

## 5. Casos reais

### 5.1 TJX / TJ Maxx (2005–2007): Wi-Fi com WEP como porta de entrada

- **O que aconteceu:** em julho de 2005, o grupo de **Albert Gonzalez** encontrou uma rede sem fio insegura em uma loja **Marshalls** em Miami, protegida apenas com **WEP**.
- **Como:** o grupo fazia *wardriving* em centros comerciais e ficava em estacionamentos próximos até invadir o perímetro da rede da loja. A partir dali, chegaram aos sistemas internos e instalaram programas que **capturavam números de cartão**.
- **Impacto:** o grupo roubou **mais de 40 milhões** de números de cartões de crédito e débito de redes como TJ Maxx, Barnes & Noble e BJ's Wholesale Club.
- **Consequência:** Gonzalez foi condenado a **20 anos de prisão**.
- **Lição:** um Wi-Fi fraco **ligado à rede cabeada** expõe a rede inteira, não só as conexões sem fio. O WEP já era considerado quebrado na época.

### 5.2 Lowe's (2003): rede sem fio sem proteção em uma loja

- **O que aconteceu:** fazendo *wardriving*, dois homens encontraram uma **rede sem fio sem proteção** em uma loja **Lowe's** em Southfield, Michigan.
- **Como:** meses depois, um deles voltou com **Brian Salcedo**. Pela rede da loja, chegaram ao **data center corporativo** e às redes de lojas em vários estados. Em duas lojas, **alteraram o software de pagamento** para gravar os números de cartão dos clientes.
- **Detecção:** a Lowe's percebeu as invasões e chamou o FBI, que encontrou o grupo **no estacionamento da loja**. O programa alterado tinha coletado seis números de cartão.
- **Consequência:** Salcedo recebeu **9 anos de prisão**, uma das maiores penas por crime de hacking da época.
- **Lição:** **uma loja** com Wi-Fi aberto deu acesso à **rede de toda a empresa**. Faltava segmentação entre as lojas e o data center.

### 5.3 DarkVishnya (2017–2018): dispositivos plantados em bancos

- **O que aconteceu:** a Kaspersky investigou ataques a **pelo menos oito bancos no Leste Europeu**, com prejuízo estimado em **dezenas de milhões de dólares**.
- **Como:**
    1. Um criminoso entrava no prédio **se passando por entregador ou candidato a emprego**.
    2. Ligava um dispositivo em uma **tomada de rede**, por exemplo em uma sala de reunião, e o escondia no ambiente.
    3. Os dispositivos eram um **notebook barato**, um **Raspberry Pi** ou um **Bash Bunny** (ferramenta de ataque por USB).
    4. O acesso remoto vinha por um **modem celular GPRS, 3G ou LTE**, embutido ou ligado por USB. Assim, os criminosos **contornavam o firewall e o proxy** do banco.
    5. De fora, eles exploravam a rede interna, buscavam acesso a servidores e usavam **RDP** em computadores escolhidos para roubar dinheiro e dados.
- **Lição:** **portas de rede ativas em áreas públicas** (salas de reunião, recepção) são um risco. Um canal sem fio celular torna o firewall inútil contra esse dispositivo.

### 5.4 NASA JPL (2018): Raspberry Pi não autorizado na rede

- **O que aconteceu:** um **Raspberry Pi ligado à rede do Jet Propulsion Laboratory (JPL) sem autorização** foi usado como ponto de entrada.
- **Como:** os invasores usaram o dispositivo como base para se **mover lateralmente** pela rede, aproveitando a **falta de segmentação**. A invasão ficou **10 meses sem ser detectada**.
- **Impacto:** cerca de **500 MB de dados** foram roubados de 23 arquivos. Dois deles tinham informações controladas (ITAR) da missão **Mars Science Laboratory**.
- **O relatório:** a auditoria do escritório do inspetor-geral da NASA apontou **pouca visibilidade sobre os dispositivos conectados**. Novos equipamentos nem sempre passavam por avaliação de segurança, e a agência não sabia que o Raspberry Pi estava lá.
- **Observação:** o relatório não diz se o Raspberry Pi usava conexão sem fio. O caso entra aqui como exemplo de **dispositivo não autorizado** na rede, a mesma falha que permite os rogue APs.
- **Lição:** **sem inventário e sem controle de acesso nas portas** (802.1X/NAC), qualquer dispositivo vira uma porta de entrada.

### 5.5 Agência de inteligência russa (GRU) contra a OPCW (2018): ataque de proximidade ao Wi-Fi

- **O que aconteceu:** quatro oficiais do **GRU** foram flagrados pela inteligência militar holandesa (**MIVD**) perto da sede da **OPCW** (Organização para a Proibição de Armas Químicas), em Haia.
- **Como:** no **porta-malas de um carro** estacionado no hotel ao lado, havia equipamentos para **interceptar o Wi-Fi** da organização e capturar credenciais, com a antena escondida e apontada para o prédio.
- **Consequência:** os quatro foram **expulsos da Holanda** em abril de 2018.
- **Lição:** atacantes com muitos recursos fazem **operações de proximidade** contra o Wi-Fi quando o ataque pela internet é difícil.

### 5.6 Nearest Neighbor Attack (2022): invasão pelo Wi-Fi do prédio vizinho

- **O que aconteceu:** a Volexity detectou, em **fevereiro de 2022**, a invasão de um cliente em **Washington, D.C.** que trabalhava com temas relacionados à Ucrânia. Depois, ligou o ataque ao **APT28** (ligado ao GRU).
- **Como:**
    1. Os atacantes conseguiram **senhas do Wi-Fi** da vítima com ataques de *password spraying* contra serviços expostos na internet.
    2. Mas o Wi-Fi só funcionava **perto do prédio**. Então, eles **invadiram organizações vizinhas**, dentro do alcance do sinal.
    3. Usaram computadores com Wi-Fi **dessas vizinhas** para se conectar à rede da vítima.
- **Por que é importante:** o atacante tem as vantagens de estar **fisicamente perto** sem correr o risco de ser visto ou preso. Ele pode estar a milhares de quilômetros.
- **Lição:** o Wi-Fi corporativo precisa da **mesma proteção** dos serviços da internet: **MFA ou certificados** (EAP-TLS), não só senha.

### 5.7 Ataque com drones a uma empresa financeira (2022)

- **O que aconteceu:** o pesquisador **Greg Linares** relatou um ataque a uma **empresa de investimentos** na costa leste dos EUA.
- **Como:**
    1. Dias antes do ataque, um drone **DJI Phantom** carregando um **WiFi Pineapple** (ferramenta de teste de invasão da Hak5) capturou as **credenciais e os dados do Wi-Fi** de um funcionário.
    2. Depois, um drone **DJI Matrice 600** pousou no **telhado**, carregando um **Raspberry Pi**, um mini notebook, um **modem 4G** e um dispositivo Wi-Fi.
    3. Usando o **endereço MAC e as credenciais** do funcionário, o equipamento acessou a página interna do **Confluence** da empresa.
- **Detecção:** a equipe estranhou que o MAC do funcionário aparecia **conectado no escritório e na casa dele ao mesmo tempo**. Então, isolou o sinal Wi-Fi e localizou o equipamento no telhado.
- **Lição:** o perímetro físico inclui o **telhado**. Detectar sessões duplicadas ou impossíveis é uma ótima forma de achar invasores.

### 5.8 Evil twin em voos e aeroportos na Austrália (2024)

- **O que aconteceu:** uma companhia aérea percebeu uma **rede Wi-Fi suspeita** durante um voo doméstico.
- **Como:** um homem criava **redes Wi-Fi gratuitas falsas** que imitavam redes legítimas, em aeroportos (Perth, Melbourne e Adelaide), em voos e em locais ligados a um antigo emprego. Páginas falsas pediam login e capturavam as **credenciais** das vítimas.
- **Investigação:** a Polícia Federal Australiana (AFP) apreendeu um **dispositivo portátil de acesso sem fio**, um notebook e um celular, e encontrou **dezenas de credenciais** de outras pessoas.
- **Consequência:** foi condenado a **7 anos e 4 meses de prisão**.
- **Lição:** **nunca digitar senhas em portais de Wi-Fi público**; preferir a rede de dados do celular ou uma VPN. Este caso é de **evil twin**, sem ligação com uma rede cabeada.

### Visão geral dos casos

| Caso | Ano | Técnica | Ligou-se à rede cabeada? | Impacto |
| --- | --- | --- | --- | --- |
| Lowe's | 2003 | Wi-Fi sem proteção em uma loja | Sim, pelo Wi-Fi da própria empresa | Software de pagamento alterado |
| TJX | 2005–2007 | Wi-Fi com WEP em lojas | Sim, pelo Wi-Fi da própria empresa | 40+ milhões de cartões |
| DarkVishnya | 2017–2018 | Dispositivo plantado + modem celular | **Sim, dispositivo físico na tomada** | Dezenas de milhões de dólares |
| NASA JPL | 2018 | Raspberry Pi não autorizado | **Sim, dispositivo físico** | 500 MB de dados da missão a Marte |
| OPCW | 2018 | Equipamento Wi-Fi em um carro | Tentativa, pelo Wi-Fi | Frustrado e expulsões |
| Nearest Neighbor | 2022 | Wi-Fi da vítima, a partir de vizinhos invadidos | Sim, pelo Wi-Fi da empresa | Servidor comprometido |
| Drones | 2022 | WiFi Pineapple + kit no telhado | Sim, pelo Wi-Fi com credenciais roubadas | Acesso ao Confluence interno |
| Austrália | 2024 | Evil twin | Não | Credenciais de passageiros |

---

## 6. O que os casos ensinam

1. **Wi-Fi fraco é uma porta para a rede cabeada.** Em TJX e Lowe's, o problema não era "só o Wi-Fi": era a rede inteira por trás dele.
2. **Portas de rede ativas em áreas públicas são perigosas.** DarkVishnya mostrou que basta entrar no prédio e achar uma tomada.
3. **Inventário de dispositivos é obrigatório.** A NASA não sabia que o Raspberry Pi existia.
4. **Rede plana facilita o movimento lateral.** Em Lowe's e na NASA, uma vez dentro, o atacante chegou longe.
5. **Senha sozinha não basta no Wi-Fi corporativo.** O Nearest Neighbor Attack e o caso dos drones começaram com credenciais roubadas.
6. **O alcance do sinal é um risco físico.** Estacionamentos, prédios vizinhos e telhados fazem parte da superfície de ataque.
7. **Anomalias revelam o invasor.** O MAC "em dois lugares ao mesmo tempo" denunciou os drones.

---

## 7. Como detectar

### Pelo lado sem fio

| Método | Como funciona |
| --- | --- |
| **WIPS / WIDS** | Sensores que monitoram o ar continuamente e alertam sobre APs e clientes desconhecidos |
| **Detecção de rogue no controlador (WLC)** | Os próprios APs da empresa escutam os canais e reportam APs estranhos. A Cisco classifica os APs como *friendly*, *malicious* ou *unclassified*. |
| **Varreduras periódicas** | Andar pelo prédio com um analisador Wi-Fi (por exemplo, inSSIDer, Kismet ou Ekahau) |
| **SSIDs iguais aos da empresa** | Um AP com o SSID corporativo que não está na lista oficial é forte sinal de **evil twin** |

### Pelo lado cabeado

| Método | Como funciona |
| --- | --- |
| **Correlação de MAC** | Compara os MACs vistos no ar com as tabelas de MAC dos switches. Se o mesmo equipamento aparece nos dois lados, o rogue está **ligado na rede**. A Cisco tem o **RLDP** (*Rogue Location Discovery Protocol*), que tenta se conectar ao AP suspeito para confirmar. |
| **Fabricante pelo MAC (OUI)** | Os primeiros 3 bytes do MAC indicam o fabricante. Um MAC de AP doméstico ou de Raspberry Pi em uma porta de usuário é suspeito. |
| **Mais de um MAC por porta** | Um AP ou um switch escondido atrás da porta faz aparecer vários MACs nela |
| **DHCP e NAC** | Novos dispositivos pedindo IP ou falhando no 802.1X geram alertas |
| **Análise de tráfego** | NetFlow, IDS e SIEM procuram tráfego estranho: varreduras, RDP fora do comum, sessões duplicadas |
| **Inspeção física** | Rondas em salas de reunião, recepção e forros, e verificação das tomadas de rede |

---

## 8. Como prevenir e responder

### Prevenção

1. **802.1X em todas as portas cabeadas**, com NAC (por exemplo, Cisco ISE). Um dispositivo não autenticado não entra na rede.
2. **Desligar as portas sem uso** e colocá-las em uma VLAN isolada (*blackhole*).
3. **Port security:** limitar a quantidade de MACs por porta. Um AP ou um switch escondido gera violação.
4. **Wi-Fi corporativo com WPA2/WPA3-Enterprise e EAP-TLS**, de preferência com certificados, não só senha.
5. **Segmentar a rede** (VLANs, ACLs, firewall interno). Se alguém entrar, chega a pouca coisa.
6. **Inventário de ativos** atualizado, com aprovação obrigatória para qualquer novo dispositivo.
7. **Política de redes sem fio** proibindo APs pessoais, com conscientização dos funcionários.
8. **Segurança física:** controle de visitantes, acompanhamento de prestadores de serviço e portas de rede fora das áreas públicas.
9. **Monitorar sinais celulares** em ambientes críticos, quando a lei permitir.

### Resposta a um rogue AP encontrado

1. **Classificar:** é vizinho, de funcionário ou malicioso?
2. **Localizar:** pela força do sinal e pela porta do switch.
3. **Isolar:** desligar a porta do switch (`shutdown`). É a forma mais segura e legal de cortar o acesso.
4. **Preservar evidências:** registrar o MAC, a porta, o horário e o conteúdo do dispositivo, e fotografar antes de remover.
5. **Investigar:** quem instalou e o que foi acessado (logs do switch, do DHCP e do firewall).
6. **Corrigir a causa:** por que a porta estava ativa e sem 802.1X?

> **Atenção à lei:** derrubar clientes de redes de terceiros com pacotes de desautenticação (*containment* do WIPS) pode ser **ilegal**. Em 2014, a FCC (a Anatel dos EUA) multou a rede de hotéis **Marriott em US$ 600 mil** por bloquear os hotspots pessoais dos hóspedes. Use contenção sem fio só contra dispositivos ligados à **sua própria rede**, e com orientação jurídica.

---

## 9. Relação com os labs de Packet Tracer

| Controle | Lab |
| --- | --- |
| Portas sem uso desligadas e na VLAN *blackhole* | Lab 3 |
| Port security (máximo de MACs por porta) | Lab 3 |
| DHCP snooping contra **servidor DHCP falso** (o "rogue DHCP", primo do rogue AP) | Lab 3 |
| BPDU Guard contra switches não autorizados | Lab 3 |
| Segmentação com VLANs | Lab 2 |
| ACLs entre segmentos | Lab 4 |

**Ideia de lab extra:** no Packet Tracer, ligue um **Access Point** (ou um roteador Wi-Fi doméstico) em uma porta do S2 e conecte um notebook nele pelo Wi-Fi. Depois de configurar o port security do Lab 3, veja a porta entrar em violação quando o segundo MAC aparecer.

---

## 10. Resumo rápido

- **Rogue AP** = AP não autorizado **ligado à rede da empresa**. Ele cria uma porta lateral que o firewall não vê.
- **Evil twin** = AP falso que **imita** a rede legítima para roubar credenciais.
- **Drop box com modem celular** contorna todos os controles de rede.
- **Casos reais:** TJX e Lowe's (Wi-Fi fraco), DarkVishnya e NASA JPL (dispositivos plantados), GRU e APT28 (ataques de proximidade ao Wi-Fi), drones no telhado, evil twin em aviões.
- **Defesa:** 802.1X e NAC, portas desligadas, port security, WPA2/WPA3-Enterprise com certificados, segmentação, inventário, WIPS e segurança física.
- **Na resposta:** desligue a **porta do switch** e preserve as evidências.

---

## 11. Vocabulário (inglês → português)

| Inglês | Português |
| --- | --- |
| rogue access point | ponto de acesso não autorizado, clandestino |
| evil twin | gêmeo do mal (AP falso que imita outro) |
| wardriving | busca de redes sem fio de carro |
| drop box / implant | dispositivo plantado |
| close access operation | operação de acesso por proximidade |
| lateral movement | movimento lateral |
| password spraying | tentativa de poucas senhas comuns em muitas contas |
| containment | contenção |
| asset inventory | inventário de ativos |
| shadow IT | TI paralela (sem aprovação da área de TI) |
| perimeter | perímetro |
| exfiltration | exfiltração (retirada de dados) |

---

## 12. Fontes

- **TJX:** [Graham Cluley — TJX hacker sentenced to 20 years](https://grahamcluley.com/tjx-hacker-jail-20-years-stealing-40-million-credit-cards/) · [Techdirt — The story behind the hackers](https://www.techdirt.com/articles/20100521/1053599529.shtml)
- **Lowe's:** [Computerworld — Hacker in Lowe's case sentenced to nine years](https://www.computerworld.com/article/2567456/hacker-in-lowe-s-case-sentenced-to-nine-years.html) · [InformationWeek — Wi-Fi hacker sentenced to nine years](https://www.informationweek.com/cyber-resilience/wi-fi-hacker-sentenced-to-nine-years)
- **DarkVishnya:** [Kaspersky Securelist — DarkVishnya](https://securelist.com/darkvishnya/89169/) · [Schneier on Security](https://www.schneier.com/blog/archives/2018/12/banks_attacked_.html)
- **NASA JPL:** [WeLiveSecurity (ESET)](https://www.welivesecurity.com/2019/06/24/nasa-breach-mars-raspberry-pi/) · [Engadget](https://www.engadget.com/2019-06-20-nasa-jpl-cybersecurity-weaknesses.html)
- **OPCW:** [Al Jazeera — Netherlands disrupted Russian hacking attack against OPCW](https://www.aljazeera.com/news/2018/10/4/netherlands-disrupted-russian-hacking-attack-against-opcw)
- **Nearest Neighbor Attack:** [Help Net Security](https://www.helpnetsecurity.com/?p=317859) · [heise online](https://heise.de/-10130038)
- **Drones:** [The Register — Drone roof attack](https://www.theregister.com/2022/10/12/drone-roof-attack/) · [Dark Reading](https://www.darkreading.com/threat-intelligence/drones-cyber-spy-exploits-in-the-wild)
- **Evil twin na Austrália:** [BleepingComputer](https://www.bleepingcomputer.com/news/security/australian-charged-for-evil-twin-wifi-attack-on-plane) · [Security Affairs — sentença](https://securityaffairs.com/185205/cyber-crime/australian-man-jailed-for-7-years-over-airport-and-in-flight-wi-fi-attacks.html)
