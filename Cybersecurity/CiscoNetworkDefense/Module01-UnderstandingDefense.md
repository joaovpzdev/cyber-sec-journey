# Network Defense (Cisco) — Módulo 1: Entendendo a Defesa

> Anotações de estudo do curso **Network Defense** da Cisco Networking Academy.

**Objetivo do módulo:** explicar como uma organização protege a rede usando a estratégia de **defesa em profundidade** e como **políticas, regulamentações e padrões** sustentam essa defesa.

---

## 1.1 Defesa em profundidade

### Ativos, vulnerabilidades e ameaças

Toda estratégia de defesa começa respondendo três perguntas:

| Conceito | Pergunta | Exemplos |
| --- | --- | --- |
| **Ativo** (*asset*) | O que precisa ser protegido? | Servidores, dados de clientes, propriedade intelectual, estações, dispositivos de rede |
| **Vulnerabilidade** (*vulnerability*) | Onde está a fraqueza? | Software desatualizado, senha fraca, porta aberta sem necessidade, falha de configuração |
| **Ameaça** (*threat*) | Quem ou o que pode causar dano? | Atacantes externos, malware, funcionário mal-intencionado, desastre natural |

**Risco** = a chance de uma ameaça explorar uma vulnerabilidade e afetar um ativo.

#### Identificar ativos

- A organização precisa de um **inventário** de tudo o que tem valor: hardware, software, dados e serviços.
- Com dispositivos móveis, nuvem e BYOD, muitas empresas **não sabem** exatamente quais ativos possuem. Sem inventário, não há como protegê-los.
- Cada ativo deve ter um **dono** e uma **classificação** de importância.

#### Identificar vulnerabilidades

- Inclui falhas técnicas (software, protocolos, configurações) e humanas (falta de treinamento, engenharia social).
- Ferramentas como scanners de vulnerabilidade e testes de intrusão (pentest) ajudam a encontrá-las.
- Cada vulnerabilidade deve receber uma prioridade de correção.

#### Identificar ameaças

- Ameaças podem ser **externas** (cibercriminosos, hacktivistas, Estados-nação) ou **internas** (funcionários, terceiros).
- Fontes de inteligência de ameaças (*threat intelligence*) ajudam a acompanhar as táticas atuais dos atacantes.

### O que é defesa em profundidade

Usar **várias camadas de segurança** em pontos diferentes da rede. Se uma camada falhar, a próxima ainda protege o ativo. O objetivo é **detectar, conter e parar** o ataque antes que ele chegue ao que importa.

Exemplo de camadas em uma rede corporativa:

```text
Internet
   │
[Roteador de borda]   → 1ª linha: filtra tráfego com ACLs
   │
[Firewall]            → 2ª linha: bloqueia conexões iniciadas de fora para dentro
   │
[IPS]                 → analisa o tráfego e bloqueia padrões de ataque conhecidos
   │
[Switches]            → port security, DHCP snooping, VLANs
   │
[Hosts e servidores]  → antivírus/EDR, hardening, patches
   │
[Dados]               → criptografia, backup, controle de acesso
```

Além das camadas técnicas, entram **pessoas** (treinamento, conscientização) e **processos** (políticas, resposta a incidentes).

### Cebola x alcachofra

| Modelo | Ideia | Problema / contexto |
| --- | --- | --- |
| **Cebola** (*security onion*) | O atacante precisa atravessar cada camada, uma de cada vez, de fora para dentro, até chegar ao centro. | Funcionava quando a rede tinha um perímetro bem definido. |
| **Alcachofra** (*security artichoke*) | O atacante pode "arrancar folhas" de qualquer lado e chegar a dados sensíveis sem passar por todas as camadas. | Representa as **redes sem fronteiras** (*borderless networks*): mobilidade, nuvem, BYOD, acesso remoto. |

**Ideia central:** hoje não existe um único perímetro. Cada folha (dispositivo, usuário, aplicação) precisa da sua própria proteção, e é preciso **supor que alguma camada vai falhar**.

---

## 1.2 Políticas de segurança, regulamentações e padrões

### Políticas de negócio

São as regras que a organização define para funcionários e parceiros. As principais:

| Política | O que define |
| --- | --- |
| **Código de conduta** (*code of conduct*) | Comportamento e ética esperados dos funcionários |
| **Política de segurança** (*security policy*) | Requisitos de segurança e regras para proteger pessoas, ativos e dados |
| **Política de RH** (*human resources policy*) | Contratação, desligamento, remuneração, ações disciplinares |

### Política de segurança

Documento que diz **o que** deve ser protegido, **quem** é responsável e **o que é permitido**. Serve também de base para auditorias e para decidir como responder a incidentes.

Componentes comuns:

| Componente | Exemplo |
| --- | --- |
| **Identificação e autenticação** | Quem pode acessar a rede e como prova sua identidade |
| **Senhas** | Tamanho mínimo, complexidade, troca periódica |
| **Uso aceitável** (*AUP — Acceptable Use Policy*) | Quais aplicações e usos da rede são permitidos; o funcionário assina o termo |
| **Acesso remoto** | Como e quem pode acessar a rede de fora (VPN, MFA) |
| **Manutenção de rede** | Atualização de sistemas operacionais e aplicações |
| **Tratamento de incidentes** | Como os incidentes são reportados e tratados |

Pontos importantes sobre a AUP:

- Deve ser **assinada** pelos funcionários.
- Deve ser **atualizada** assim que surgir um novo risco.
- Pode ser reforçada com controles técnicos, como bloqueio de sites.

### Políticas de BYOD

*BYOD (Bring Your Own Device)* = funcionários usam os próprios dispositivos no trabalho. Aumenta a produtividade, mas também a superfície de ataque.

Uma política de BYOD deve definir:

- **Quem** pode usar dispositivos pessoais.
- **Quais dispositivos** e sistemas são suportados.
- **Qual nível de acesso** cada dispositivo recebe.
- **Quais direitos** a equipe de segurança tem sobre o dispositivo (por exemplo, apagar dados remotamente).
- **Quais regulamentações** precisam ser cumpridas.
- **Quais proteções** usar se o dispositivo for comprometido, perdido ou roubado.

Boas práticas de segurança para BYOD:

- Senha ou PIN obrigatório e bloqueio automático de tela.
- Wi-Fi configurado manualmente; evitar redes abertas e desconhecidas.
- Bluetooth desligado quando não estiver em uso.
- Sistema e aplicativos sempre atualizados.
- Backup dos dados e criptografia do dispositivo.
- **MDM** (*Mobile Device Management*) para aplicar e controlar essas regras.

### Conformidade com regulamentações e padrões

Muitas organizações são obrigadas por lei ou por contrato a seguir regras de segurança. Não cumprir pode gerar **multas, processos e danos à reputação**.

| Regulamentação / padrão | Área |
| --- | --- |
| **PCI DSS** | Dados de cartão de pagamento |
| **HIPAA** | Dados de saúde (EUA) |
| **SOX** (*Sarbanes-Oxley*) | Controles financeiros de empresas de capital aberto (EUA) |
| **GDPR** | Proteção de dados pessoais (União Europeia) |
| **LGPD** | Proteção de dados pessoais (Brasil) |
| **ISO/IEC 27001** | Sistema de gestão de segurança da informação |
| **NIST Cybersecurity Framework** | Boas práticas para gerenciar risco de segurança |

> LGPD e ISO 27001 não fazem parte do texto original do módulo; foram incluídas aqui pela relevância no Brasil.

---

## Resumo rápido

- Defesa começa com **ativos, vulnerabilidades e ameaças**.
- **Defesa em profundidade** = várias camadas; se uma falha, outra protege.
- O modelo da **cebola** supõe um perímetro; o da **alcachofra** reflete redes sem fronteiras.
- **Políticas** (segurança, AUP, BYOD) definem as regras; **controles técnicos** as aplicam.
- **Regulamentações e padrões** tornam algumas regras obrigatórias.

## Relação com os labs de Packet Tracer

| Camada | Lab |
| --- | --- |
| Acesso seguro aos dispositivos | Lab 1 — SSH, senhas, banner |
| Segmentação | Lab 2 — VLANs |
| Camada 2 (switches) | Lab 3 — port security, DHCP snooping, BPDU Guard |
| Filtro de tráfego | Lab 4 — ACLs |
| Autenticação central e logs | Lab 5 — AAA, Syslog, NTP |
| Firewall | Lab 6 — Zone-Based Firewall |
| Proteção dos dados em trânsito | Lab 7 — VPN IPsec |

