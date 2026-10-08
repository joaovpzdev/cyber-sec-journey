# Network Defense (Cisco) — Módulo 2: Defesa de Sistemas e Redes

> Anotações de estudo do curso **Network Defense** da Cisco Networking Academy.

**Objetivo do módulo:** mostrar como proteger, na prática, cada parte do ambiente: o espaço físico, as aplicações, os serviços de rede, a rede sem fio, os dispositivos IoT e os próprios hosts. É a aplicação concreta da defesa em profundidade vista no Módulo 1.

> A ordem e os nomes das seções podem ser um pouco diferentes no curso. O conteúdo está organizado por tema.

---

## Segurança física

Se o atacante encosta no equipamento, quase todo controle lógico pode ser contornado: ele pode reiniciar o roteador e recuperar a senha, plugar um dispositivo na rede ou simplesmente levar o disco embora.

### Camadas de proteção física

| Camada | Exemplos |
| --- | --- |
| **Perímetro** | Cercas, portões, iluminação, guardas |
| **Prédio** | Catracas, crachás, recepção com registro de visitantes |
| **Sala de equipamentos** | Porta trancada, acesso por cartão ou biometria, racks com chave |
| **Monitoramento** | Câmeras (CFTV), alarmes, registro de quem entrou e quando |
| **Ambiente** | Controle de temperatura e umidade, prevenção de incêndio, nobreak (UPS) |

### Biometria e seus erros

A biometria identifica pela característica física (digital, rosto, íris). Ela pode errar de dois jeitos:

| Erro | Nome | O que acontece | Risco |
| --- | --- | --- | --- |
| **Tipo I** | Falsa rejeição (*False Rejection*) | Uma pessoa autorizada é **barrada** | Incômodo, perda de produtividade |
| **Tipo II** | Falsa aceitação (*False Acceptance*) | Uma pessoa **não autorizada entra** | Grave: é uma falha de segurança |

**Para lembrar:** o tipo II é o perigoso, porque deixa o invasor entrar.

---

## Segurança de aplicações

### Desenvolvimento seguro

- Validar **toda entrada** do usuário, para evitar SQL Injection, XSS e estouro de buffer.
- Tratar erros sem mostrar detalhes internos (versões, caminhos, consultas SQL).
- Aplicar o **menor privilégio**: a aplicação roda só com as permissões de que precisa.
- Testar a segurança antes de publicar (revisão de código, testes de intrusão).

### Integridade com hash

Um **hash** (SHA-256, por exemplo) é uma "impressão digital" do arquivo: qualquer mudança, por menor que seja, gera um hash completamente diferente.

Uso prático: o fabricante publica o hash do instalador. Depois de baixar, você calcula o hash do arquivo e compara. Se for igual, o arquivo **não foi alterado** no caminho.

```bash
sha256sum instalador.iso
```

**Assinatura de código** vai além: prova também **quem** publicou o software.

### Atualizações (*patch management*)

- Manter sistemas e aplicações atualizados fecha vulnerabilidades conhecidas.
- Testar as atualizações antes de aplicar em produção.
- Ter um inventário para saber o que precisa ser atualizado.

---

## Endurecimento da rede: serviços e protocolos

**Endurecimento** (*hardening*) = reduzir a superfície de ataque, deixando ligado só o necessário e protegendo o que fica.

### Regras gerais

- **Desligar serviços que não são usados.** Cada serviço ligado é uma porta a mais para o atacante.
- **Trocar protocolos inseguros por seguros.**
- **Separar o tráfego de gerenciamento** do tráfego dos usuários.

### Protocolos inseguros e seus substitutos

| Inseguro | Problema | Seguro |
| --- | --- | --- |
| Telnet | Usuário, senha e comandos em texto puro | **SSH** |
| HTTP | Tráfego legível por quem captura | **HTTPS** |
| FTP | Credenciais em texto puro | **SFTP** / **FTPS** |
| SNMP v1/v2c | "Senha" (community) em texto puro | **SNMPv3** (autenticação e criptografia) |

### Serviços de rede importantes

| Serviço | Função | Cuidado de segurança |
| --- | --- | --- |
| **DNS** | Traduz nomes em endereços IP | Pode ser envenenado (*DNS spoofing*) ou usado para exfiltrar dados; monitorar consultas |
| **ICMP** | Mensagens de diagnóstico (usado pelo `ping` e pelo `traceroute`) | Útil para o atacante mapear a rede; filtrar o que vem de fora |
| **NTP** | Sincroniza o relógio dos dispositivos | Sem horário certo, os logs não servem para investigar incidentes; usar NTP com autenticação |
| **Syslog** | Centraliza os logs | Enviar para um servidor protegido |
| **Protocolos de roteamento** (OSPF, EIGRP) | Trocam rotas entre roteadores | Ativar **autenticação** para que um roteador falso não injete rotas |

### Gerenciamento fora de banda

| Tipo | Como funciona | Segurança |
| --- | --- | --- |
| **Em banda** (*in-band*) | Gerenciamento pela mesma rede dos usuários | Mais simples, mas exposto: usar SSH e uma VLAN de gerência |
| **Fora de banda** (*out-of-band*, OOB) | Rede separada só para gerenciamento, ou acesso pela porta de console | Mais seguro: o tráfego de gerência não se mistura com o dos usuários |

---

## Segmentação da rede

Dividir a rede em partes menores limita até onde um atacante chega depois de entrar.

| Técnica | Como funciona |
| --- | --- |
| **VLANs** | Separam grupos (usuários, servidores, gerência) dentro dos mesmos switches |
| **ACLs e firewalls** | Controlam o que pode passar de um segmento para outro |
| **DMZ** | Zona intermediária entre a internet e a rede interna |

### DMZ

A **DMZ** (*zona desmilitarizada*) hospeda os servidores que precisam ser acessados pela internet: site, e-mail, DNS público.

```text
Internet ──[Firewall]──┬── DMZ (servidor web, e-mail)
                       └── Rede interna (usuários, bancos de dados)
```

- A internet alcança a DMZ, mas **não** a rede interna.
- Se um servidor da DMZ for invadido, o atacante ainda tem um firewall entre ele e a rede interna.

---

## Redundância e alta disponibilidade

Disponibilidade também é segurança (o "A" da tríade **CIA**: confidencialidade, integridade e disponibilidade).

| Recurso | Protege contra | Como |
| --- | --- | --- |
| **RAID** | Falha de disco | Distribui ou espelha os dados em vários discos |
| **Links e switches redundantes** | Falha de um equipamento ou cabo | Caminhos alternativos na rede |
| **STP** (*Spanning Tree Protocol*) | Loops de camada 2 causados pela redundância | Bloqueia caminhos extras e libera um deles se o principal cair |
| **FHRP** (HSRP, VRRP) | Falha do gateway padrão | Dois roteadores dividem um IP virtual de gateway |
| **Backup** | Perda de dados, ransomware | Cópias regulares, testadas e guardadas fora do ambiente principal |
| **Nobreak (UPS) e gerador** | Falta de energia | Mantêm os equipamentos ligados |

**Sem o STP**, dois cabos entre switches criam um loop: os quadros de broadcast circulam sem parar e derrubam a rede (*broadcast storm*).

---

## Redes sem fio e dispositivos móveis

### Evolução da segurança Wi-Fi

| Padrão | Criptografia | Situação |
| --- | --- | --- |
| **WEP** | RC4 | Quebrado: nunca usar |
| **WPA** | TKIP | Obsoleto |
| **WPA2** | **AES** (CCMP), obrigatório | Padrão mínimo aceitável |
| **WPA3** | AES com SAE | Mais seguro: protege melhor contra ataques de dicionário |

- **Personal (PSK):** uma senha compartilhada, para uso doméstico.
- **Enterprise (802.1X):** cada usuário se autentica com credenciais próprias, verificadas por um servidor RADIUS. É o modelo para empresas.

### Ameaças comuns no Wi-Fi

| Ameaça | O que é | Defesa |
| --- | --- | --- |
| **Rogue AP** | Ponto de acesso não autorizado ligado na rede | Varreduras de RF, port security, 802.1X nas portas |
| **Evil twin** | AP falso com o mesmo nome (SSID) da rede legítima | **Autenticação mútua**: o cliente também verifica o AP |
| **Interceptação** | Captura do tráfego sem fio | Criptografia forte (WPA2/WPA3) |

**Autenticação mútua** = os dois lados provam quem são. Isso impede que um atacante se passe pelo AP ou pelo servidor.

### Dispositivos móveis

- Bloqueio de tela com senha ou biometria.
- Criptografia do armazenamento.
- **MDM** (*Mobile Device Management*) para aplicar políticas e apagar o aparelho remotamente em caso de perda.
- Instalar apps só de lojas oficiais.

---

## Dispositivos IoT

Câmeras, sensores, lâmpadas e impressoras inteligentes costumam vir **inseguros de fábrica**.

Antes de colocar um dispositivo IoT na rede:

1. **Atualizar o firmware.**
2. **Trocar usuário e senha padrão.** Botnets como a Mirai infectaram milhares de câmeras usando senhas de fábrica.
3. **Desligar serviços desnecessários** (Telnet, UPnP, acesso em nuvem que não for usado).
4. **Isolar em uma VLAN própria**, sem acesso direto à rede corporativa.

---

## Segurança dos hosts

Os computadores e servidores são a última camada antes dos dados.

| Controle | Função |
| --- | --- |
| **Antimalware / EDR** | Detecta e bloqueia software malicioso |
| **Firewall do host** | Filtra o tráfego que entra e sai de cada máquina |
| **HIDS / HIPS** | Detecta (ou bloqueia) atividade suspeita no próprio host |
| **Atualizações** | Fecham vulnerabilidades conhecidas |
| **Menor privilégio** | Usuários sem permissão de administrador no dia a dia |
| **Lista de aplicações permitidas** (*allowlist*) | Só roda o que foi aprovado |

---

## Resumo rápido

- **Segurança física** vem primeiro: quem toca no equipamento controla o equipamento.
- **Biometria:** o erro tipo II (falsa aceitação) é o perigoso.
- **Hash** confirma que um arquivo não foi alterado.
- **Hardening:** desligar o que não é usado e trocar protocolos inseguros (Telnet → SSH, SNMPv1 → SNMPv3).
- **Segmentação** (VLANs, DMZ) limita o alcance de um invasor.
- **Redundância** (RAID, STP, FHRP, backup) garante a disponibilidade.
- **Wi-Fi:** WPA2 no mínimo, com AES; autenticação mútua contra APs falsos.
- **IoT:** atualizar, trocar a senha padrão e isolar.

## Relação com os labs de Packet Tracer

| Tema do módulo | Lab |
| --- | --- |
| SSH no lugar de Telnet, senhas, banner | Lab 1 — Acesso seguro |
| Segmentação com VLANs, VLAN de gerência | Lab 2 — VLANs |
| STP, BPDU Guard, portas sem uso desligadas | Lab 3 — Segurança de switches |
| Filtro de tráfego entre segmentos | Lab 4 — ACLs |
| NTP com autenticação e Syslog | Lab 5 — AAA, Syslog e NTP |
| Firewall entre zonas | Lab 6 — Zone-Based Firewall |

## Vocabulário (inglês → português)

| Inglês | Português |
| --- | --- |
| hardening | endurecimento, blindagem |
| attack surface | superfície de ataque |
| false acceptance / false rejection | falsa aceitação / falsa rejeição |
| integrity | integridade |
| patch | atualização de correção |
| out-of-band management | gerenciamento fora de banda |
| redundancy | redundância |
| availability | disponibilidade |
| rogue access point | ponto de acesso clandestino |
| mutual authentication | autenticação mútua |
| firmware | firmware (software embarcado) |
| default credentials | credenciais padrão de fábrica |
