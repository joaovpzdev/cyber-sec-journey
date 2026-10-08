# Protocolos de Autenticação: 802.1X, EAP, RADIUS e TACACS+

> Anotações de estudo complementares ao curso **Network Defense** da Cisco Networking Academy, com foco nos métodos EAP: **EAP-TLS, PEAP, EAP-TTLS e EAP-FAST**.

**Ideia central:** antes de dar acesso à rede, é preciso provar **quem** está se conectando. Os protocolos de autenticação definem **como** essa prova acontece, **por onde** ela trafega e **quão protegida** ela é contra interceptação e falsificação.

---

## Sumário

1. [Conceitos básicos](#1-conceitos-básicos)
2. [IEEE 802.1X: controle de acesso por porta](#2-ieee-8021x-controle-de-acesso-por-porta)
3. [EAP: o "envelope" da autenticação](#3-eap-o-envelope-da-autenticação)
4. [EAP-TLS](#4-eap-tls)
5. [PEAP](#5-peap)
6. [EAP-TTLS](#6-eap-ttls)
7. [EAP-FAST](#7-eap-fast)
8. [Comparação dos métodos EAP](#8-comparação-dos-métodos-eap)
9. [Métodos legados e inseguros](#9-métodos-legados-e-inseguros)
10. [Protocolos de autenticação de senha: PAP, CHAP e MS-CHAPv2](#10-protocolos-de-autenticação-de-senha-pap-chap-e-ms-chapv2)
11. [RADIUS x TACACS+](#11-radius-x-tacacs)
12. [Onde cada protocolo é usado](#12-onde-cada-protocolo-é-usado)
13. [Ataques comuns e defesas](#13-ataques-comuns-e-defesas)
14. [Boas práticas](#14-boas-práticas)
15. [Resumo rápido](#15-resumo-rápido)
16. [Vocabulário](#16-vocabulário-inglês--português)

---

## 1. Conceitos básicos

### AAA

| Letra | Significado | Pergunta | Exemplo |
| --- | --- | --- | --- |
| **A** | Autenticação (*Authentication*) | Quem é você? | Usuário e senha, certificado, biometria |
| **A** | Autorização (*Authorization*) | O que você pode fazer? | Acesso à VLAN 10, só comandos `show` |
| **A** | Contabilização (*Accounting*) | O que você fez? | Registro de login, logout, comandos e tempo de sessão |

### Fatores de autenticação

| Fator | Tipo | Exemplos |
| --- | --- | --- |
| Algo que você **sabe** | Conhecimento | Senha, PIN |
| Algo que você **tem** | Posse | Certificado digital, token, smartcard, celular |
| Algo que você **é** | Inerência | Digital, rosto, íris |

**MFA** (autenticação multifator) combina fatores **de tipos diferentes**. Duas senhas não são MFA.

### Autenticação mútua

- **Unilateral:** só o cliente prova quem é. O cliente não sabe se está falando com o servidor verdadeiro.
- **Mútua:** cliente e servidor provam suas identidades um ao outro. Isso impede que um atacante se passe pelo servidor (por exemplo, com um AP falso).

---

## 2. IEEE 802.1X: controle de acesso por porta

O **802.1X** é o padrão que controla o acesso a uma porta de switch ou a uma rede Wi-Fi. Enquanto o dispositivo não se autentica, a porta só deixa passar tráfego de autenticação.

### Os três papéis

| Papel | Quem é | Função |
| --- | --- | --- |
| **Suplicante** (*supplicant*) | O cliente: notebook, celular, impressora | Pede acesso e apresenta as credenciais |
| **Autenticador** (*authenticator*) | O switch ou o ponto de acesso (AP/WLC) | Bloqueia a porta e repassa a conversa ao servidor. **Não decide** nada. |
| **Servidor de autenticação** (*authentication server*) | Servidor RADIUS (Cisco ISE, FreeRADIUS, Microsoft NPS) | Verifica as credenciais e decide se libera o acesso |

### Como as mensagens trafegam

```text
[Suplicante] ──── EAPoL ────> [Autenticador] ──── RADIUS ────> [Servidor de autenticação]
  notebook     (camada 2)       switch / AP     (UDP 1812)        ISE / FreeRADIUS / NPS
```

- **EAPoL** (*EAP over LAN*): o EAP é carregado direto em quadros Ethernet ou Wi-Fi, porque o cliente **ainda não tem IP**.
- **RADIUS:** o autenticador coloca as mensagens EAP dentro de pacotes RADIUS (atributo *EAP-Message*) e as envia ao servidor.

### Estados da porta

| Estado | O que passa |
| --- | --- |
| **Não autorizada** (*unauthorized*) | Só EAPoL. Todo o resto é bloqueado. |
| **Autorizada** (*authorized*) | Todo o tráfego, conforme a política (VLAN, ACL) enviada pelo servidor |

### Fluxo simplificado

1. O cliente se conecta. A porta começa **não autorizada**.
2. O autenticador pede a identidade (*EAP-Request/Identity*).
3. O cliente responde com sua identidade (*EAP-Response/Identity*).
4. O servidor escolhe o método EAP (TLS, PEAP...) e os dois negociam pelo autenticador.
5. O servidor responde **Access-Accept** ou **Access-Reject**.
6. Se aceito, a porta vira **autorizada**. No Wi-Fi, o servidor também entrega o material de chave (PMK), e o AP e o cliente fazem o **4-way handshake** para gerar as chaves de criptografia.

### Alternativa para dispositivos sem 802.1X

Impressoras, câmeras e telefones IP às vezes não suportam 802.1X. Nesses casos, usa-se o **MAB** (*MAC Authentication Bypass*): o switch envia o endereço MAC ao RADIUS como identidade. É **fraco**, porque MAC é fácil de falsificar. Deve ser combinado com uma VLAN restrita e perfilamento (*profiling*) do dispositivo.

---

## 3. EAP: o "envelope" da autenticação

O **EAP** (*Extensible Authentication Protocol*, RFC 3748) **não é um método de autenticação**. É uma estrutura que transporta vários métodos diferentes, e por isso se chama "extensível".

Analogia: o EAP é o **envelope**; EAP-TLS, PEAP, EAP-TTLS e EAP-FAST são as **cartas** diferentes que vão dentro dele.

### Mensagens do EAP

| Código | Mensagem | Quem envia |
| --- | --- | --- |
| 1 | **Request** | Autenticador / servidor |
| 2 | **Response** | Suplicante |
| 3 | **Success** | Servidor |
| 4 | **Failure** | Servidor |

### Métodos com túnel

PEAP, EAP-TTLS e EAP-FAST funcionam em **duas fases**:

```text
Fase 1: cria um túnel TLS criptografado (o servidor prova quem é)
          ┌──────────────────────────────────────────┐
Fase 2:   │  autenticação "interna" do usuário        │  ← protegida pelo túnel
          │  (senha, MS-CHAPv2, token...)             │
          └──────────────────────────────────────────┘
```

- **Identidade externa** (*outer identity*): enviada antes do túnel, **sem criptografia**. Pode ser anônima, como `anonymous@empresa.com`.
- **Identidade interna** (*inner identity*): o usuário real, enviado **dentro** do túnel.

Usar uma identidade externa anônima protege a **privacidade**, porque quem captura o tráfego não descobre os nomes dos usuários.

---

## 4. EAP-TLS

**EAP-TLS** (*EAP-Transport Layer Security*, RFC 5216; TLS 1.3 na RFC 9190) é o método **mais seguro** e o padrão de referência.

### Como funciona

- **Servidor e cliente** apresentam **certificados digitais**.
- Cada lado verifica o certificado do outro, usando uma autoridade certificadora (CA) confiável.
- **Não há senha**: a prova de identidade é a posse da chave privada do certificado.

```text
Suplicante                                      Servidor RADIUS
    │ ──────── Identidade ─────────────────────────> │
    │ <─────── Início do EAP-TLS ─────────────────── │
    │ ──────── ClientHello ────────────────────────> │
    │ <─────── ServerHello + certificado do servidor │
    │          + pedido de certificado do cliente    │
    │ ──────── Certificado do cliente + prova ─────> │
    │          (assinatura com a chave privada)      │
    │ <─────── Finished ──────────────────────────── │
    │ <─────── EAP-Success + chaves ──────────────── │
```

### Vantagens

- **Autenticação mútua forte**, com certificados dos dois lados.
- **Imune a roubo de senha e a ataques de dicionário**, porque não existe senha.
- **Resistente a APs falsos**, desde que o cliente valide o certificado do servidor.
- É o método exigido no **WPA3-Enterprise modo 192 bits**.

### Desvantagens

- Exige uma **PKI** (infraestrutura de chaves públicas): emitir, distribuir, renovar e revogar um certificado para **cada dispositivo ou usuário**.
- Implantação e manutenção mais trabalhosas. Normalmente usa-se **MDM** ou política de grupo para distribuir os certificados.
- Na versão com TLS 1.2, o certificado do cliente (que contém o nome do usuário) pode trafegar sem criptografia. O TLS 1.3 resolve isso.

**Quando usar:** empresas com PKI ou MDM, ambientes de alta segurança, dispositivos gerenciados.

---

## 5. PEAP

**PEAP** (*Protected EAP*), criado por Microsoft, Cisco e RSA. É o método mais usado em redes corporativas com Windows e Active Directory.

### Como funciona

- **Só o servidor** precisa de certificado.
- **Fase 1:** o cliente valida o certificado do servidor e cria um **túnel TLS**.
- **Fase 2:** dentro do túnel, o usuário se autentica com **usuário e senha**.

### Versões

| Versão | Método interno | Observação |
| --- | --- | --- |
| **PEAPv0** | **EAP-MSCHAPv2** | A mais comum. Suporte nativo no Windows, macOS, iOS e Android. Integra com o Active Directory. |
| **PEAPv1** | **EAP-GTC** (*Generic Token Card*) | Criada pela Cisco. Permite tokens de senha única (OTP) e bases LDAP. |

### Vantagens

- **Fácil de implantar:** um único certificado, no servidor.
- Os usuários usam as **mesmas credenciais do domínio**.
- Suporte nativo em praticamente todos os sistemas operacionais.

### Desvantagens e riscos

- **Depende totalmente de o cliente validar o certificado do servidor.** Se o cliente aceitar qualquer certificado:
    1. O atacante cria um **AP falso** (*evil twin*) com o mesmo nome da rede.
    2. O cliente cria o túnel com o **servidor RADIUS do atacante**.
    3. O atacante captura o desafio e a resposta do **MS-CHAPv2**.
    4. O MS-CHAPv2 pode ser quebrado offline (por força bruta ou dicionário) e revela a senha do usuário.
- Senhas fracas continuam sendo um ponto de falha.

**Quando usar:** empresas com Active Directory que não têm PKI para os clientes. **Sempre** configurar a validação do certificado do servidor.

---

## 6. EAP-TTLS

**EAP-TTLS** (*EAP-Tunneled TLS*, RFC 5281), criado pela Funk Software e Certicom.

### Como funciona

É parecido com o PEAP: o servidor tem certificado e cria um túnel TLS. A diferença está na **fase 2**: dentro do túnel, o EAP-TTLS aceita **métodos legados que não são EAP**:

| Método interno | Comentário |
| --- | --- |
| **PAP** | Senha "em claro" **dentro do túnel**. Permite validar contra LDAP, bancos de dados ou tokens OTP. |
| **CHAP** | Desafio e resposta com MD5 |
| **MS-CHAP / MS-CHAPv2** | Compatível com bases Microsoft |
| **Métodos EAP** | Qualquer método EAP, como EAP-MSCHAPv2 ou EAP-GTC |

### Vantagens

- **Flexível:** funciona com quase qualquer base de usuários (LDAP, SQL, sistemas de token), graças ao PAP dentro do túnel.
- Protege a identidade com uma identidade externa anônima.
- Muito usado em **universidades e no eduroam**, junto com o PEAP.

### Desvantagens

- Historicamente **não era nativo no Windows**: precisava de um suplicante de terceiros. O Windows passou a suportar a partir do Windows 8.
- Com PAP interno, se o cliente **não validar o certificado**, o atacante recebe a **senha em texto puro**, o que é ainda pior que no PEAP.

**Quando usar:** quando as credenciais estão em LDAP ou em sistemas que não suportam MS-CHAPv2.

---

## 7. EAP-FAST

**EAP-FAST** (*Flexible Authentication via Secure Tunneling*, RFC 4851), criado pela **Cisco** para substituir o LEAP, que tinha sido quebrado.

### Como funciona

Em vez de certificados, usa uma **PAC** (*Protected Access Credential*): uma credencial única para cada usuário, com uma chave secreta compartilhada com o servidor. A PAC cria o túnel sem precisar de PKI.

| Fase | O que acontece |
| --- | --- |
| **Fase 0** | **Entrega da PAC** ao cliente (*provisioning*). É opcional se a PAC já foi instalada manualmente. |
| **Fase 1** | Cria o **túnel TLS** usando a PAC |
| **Fase 2** | Autentica o usuário **dentro do túnel** (por exemplo, com EAP-MSCHAPv2 ou EAP-GTC) |

### Entrega da PAC (fase 0)

| Modo | Como funciona | Segurança |
| --- | --- | --- |
| **Anônimo** | Túnel sem autenticação do servidor (Diffie-Hellman anônimo) | **Vulnerável a homem no meio**: um atacante pode se passar pelo servidor e capturar a troca MS-CHAPv2 |
| **Autenticado** | O cliente valida o certificado do servidor antes de receber a PAC | Seguro. É o recomendado. |
| **Manual** | O administrador instala a PAC no cliente | Seguro, mas trabalhoso |

### EAP-FAST e o EAP chaining

A versão 2 do EAP-FAST suporta **EAP chaining**: autentica a **máquina** e o **usuário** na mesma sessão. Assim, a rede sabe que o usuário certo está em um computador da empresa.

### Vantagens

- Segurança próxima à de túnel TLS **sem precisar de certificado nos clientes**.
- Autenticação rápida e bom suporte a *roaming* em redes Cisco.

### Desvantagens

- Muito ligado ao ecossistema Cisco: pouco suporte nativo fora dele.
- A entrega anônima da PAC é um risco se ficar ativa.
- Foi sendo substituído pelo **TEAP** (*Tunnel EAP*, RFC 7170), o padrão aberto inspirado nele, que também faz EAP chaining.

**Quando usar:** ambientes Cisco legados. Em redes novas, prefira EAP-TLS ou TEAP.

---

## 8. Comparação dos métodos EAP

| Característica | EAP-TLS | PEAP | EAP-TTLS | EAP-FAST |
| --- | --- | --- | --- | --- |
| Criado por | IETF | Microsoft, Cisco, RSA | Funk, Certicom | Cisco |
| Certificado no **servidor** | Sim | Sim | Sim | Não (usa PAC). Opcional na fase 0. |
| Certificado no **cliente** | **Sim** | Não | Não | Não |
| Usa túnel TLS | Não (o próprio TLS é a autenticação) | Sim | Sim | Sim |
| Credencial do usuário | Certificado | Senha (MS-CHAPv2) ou token (GTC) | Senha (PAP, CHAP, MS-CHAPv2) ou EAP | Senha ou token, dentro do túnel |
| Autenticação mútua | **Forte** (certificados dos dois lados) | Sim, se o cliente validar o certificado | Sim, se o cliente validar o certificado | Sim, com PAC ou entrega autenticada |
| Protege a identidade | Só com TLS 1.3 | Sim (identidade externa) | Sim (identidade externa) | Sim |
| Suporte nativo | Amplo | **Muito amplo** | Bom (Windows 8 ou mais novo) | Limitado, principalmente Cisco |
| Dificuldade de implantação | **Alta** (PKI) | Baixa | Média | Média |
| Segurança | **Muito alta** | Boa, se bem configurado | Boa, se bem configurado | Boa, sem entrega anônima |

### Como escolher

```text
Tem PKI ou MDM para dar certificado a cada dispositivo?
   ├── Sim → EAP-TLS
   └── Não → As credenciais estão no Active Directory?
              ├── Sim → PEAP (EAP-MSCHAPv2), validando o certificado do servidor
              └── Não (LDAP, tokens, outras bases) → EAP-TTLS (PAP no túnel)

Ambiente Cisco legado sem certificados → EAP-FAST (sem entrega anônima) ou TEAP
```

---

## 9. Métodos legados e inseguros

| Método | Problema | Situação |
| --- | --- | --- |
| **EAP-MD5** | Sem autenticação mútua, sem geração de chaves e vulnerável a dicionário | Nunca usar em Wi-Fi. Só em redes cabeadas muito simples. |
| **LEAP** (Cisco) | Baseado em MS-CHAP sem túnel; quebrado por ataques de dicionário (ferramenta *asleap*, 2003) | Obsoleto. Foi substituído pelo EAP-FAST. |
| **EAP-MSCHAPv2 sem túnel** | O desafio e a resposta podem ser capturados e quebrados | Usar só dentro de PEAP ou TTLS |

---

## 10. Protocolos de autenticação de senha: PAP, CHAP e MS-CHAPv2

Esses protocolos nasceram para conexões PPP (discadas e links WAN) e hoje aparecem principalmente **dentro dos túneis** do PEAP e do EAP-TTLS.

| Protocolo | Como funciona | Segurança |
| --- | --- | --- |
| **PAP** | Envia usuário e senha **em texto puro** | Inseguro sozinho. Aceitável **só** dentro de um túnel TLS. |
| **CHAP** | O servidor envia um **desafio** aleatório; o cliente responde com um hash MD5 do desafio + senha | A senha não trafega, mas o servidor precisa guardá-la de forma reversível. Vulnerável a dicionário. |
| **MS-CHAPv1** | Versão da Microsoft do CHAP | Quebrado. Não usar. |
| **MS-CHAPv2** | Desafio e resposta com autenticação mútua | A segurança pode ser reduzida à de uma única chave DES. Seguro **apenas** dentro de um túnel. |

---

## 11. RADIUS x TACACS+

Os dois são protocolos **AAA** que ligam os equipamentos de rede a um servidor central de autenticação.

| Característica | RADIUS | TACACS+ |
| --- | --- | --- |
| Padrão | Aberto (RFC 2865 e 2866) | Criado pela Cisco; publicado como RFC 8907 |
| Transporte | **UDP** 1812 (autenticação) e 1813 (contabilização). Portas antigas: 1645/1646. | **TCP** 49 |
| Criptografia | **Só a senha** é ocultada | **Todo o corpo** do pacote é criptografado |
| Separação do AAA | Autenticação e autorização **juntas** | Autenticação, autorização e contabilização **separadas** |
| Autorização de comandos | Limitada | **Comando por comando** (ex.: um técnico só pode usar `show`) |
| Suporte a 802.1X / EAP | **Sim** | Não |
| Uso típico | **Acesso dos usuários à rede**: Wi-Fi, 802.1X, VPN | **Administração dos equipamentos**: login de admins em roteadores e switches |

**Para lembrar:** RADIUS = **usuários entrando na rede**. TACACS+ = **administradores gerenciando os equipamentos**.

Variações modernas:
- **RadSec** (RADIUS sobre TLS, RFC 6614): protege todo o tráfego RADIUS, útil quando ele passa pela internet, como no eduroam.
- **Diameter:** sucessor do RADIUS, usado principalmente em redes de telefonia (4G e 5G).

---

## 12. Onde cada protocolo é usado

| Cenário | Protocolos típicos |
| --- | --- |
| Wi-Fi corporativo (WPA2/WPA3-Enterprise) | 802.1X + EAP (TLS, PEAP, TTLS) + RADIUS |
| Porta de switch cabeada | 802.1X + EAP + RADIUS; MAB para dispositivos sem suporte |
| Login de administradores em roteadores e switches | TACACS+ (ou RADIUS), com usuário local de reserva |
| VPN de acesso remoto | RADIUS, frequentemente com MFA |
| Wi-Fi doméstico (WPA2/WPA3-Personal) | Senha compartilhada (PSK/SAE), **sem** 802.1X |
| Domínio Windows | Kerberos (autenticação no AD) |

---

## 13. Ataques comuns e defesas

| Ataque | Como funciona | Métodos afetados | Defesa |
| --- | --- | --- | --- |
| **Evil twin / RADIUS falso** | AP falso com o mesmo SSID e um servidor RADIUS do atacante | PEAP, EAP-TTLS (quando o cliente não valida o certificado) | Validar o certificado do servidor e fixar o nome do servidor e a CA |
| **Quebra offline do MS-CHAPv2** | O atacante captura o desafio e a resposta e testa senhas | PEAP-MSCHAPv2, LEAP | Túnel bem validado, senhas fortes ou EAP-TLS |
| **Homem no meio na entrega da PAC** | O atacante se passa pelo servidor na fase 0 anônima | EAP-FAST | Desativar a entrega anônima |
| **Falsificação de MAC** | O atacante copia o MAC de uma impressora | MAB | Perfilamento, VLAN restrita, preferir 802.1X |
| **Captura de identidade** | O atacante lê os nomes de usuário enviados antes do túnel | Todos com identidade externa real | Identidade externa anônima |
| **Roubo de certificado** | O atacante copia o certificado e a chave privada de um dispositivo | EAP-TLS | Chave não exportável, TPM, revogação rápida |

---

## 14. Boas práticas

1. **Preferir EAP-TLS** sempre que houver PKI ou MDM.
2. Em PEAP e EAP-TTLS, **sempre validar o certificado do servidor**, definindo:
    - a **CA** confiável;
    - o **nome do servidor** esperado;
    - e **impedindo** que o usuário aceite certificados desconhecidos.
3. Usar **identidade externa anônima**.
4. **Desativar** EAP-MD5, LEAP e a entrega anônima de PAC do EAP-FAST.
5. Usar **WPA3-Enterprise** quando os dispositivos suportarem.
6. Para administração de equipamentos, usar **TACACS+** com autorização de comandos e um **usuário local de reserva** para quando o servidor estiver fora do ar.
7. Ter **pelo menos dois servidores RADIUS/TACACS+**, para evitar ponto único de falha.
8. Gerenciar o **ciclo de vida dos certificados**: renovação antes de vencer e revogação (CRL ou OCSP) quando um dispositivo for perdido.
9. **Registrar e monitorar** as tentativas de autenticação (contabilização e Syslog).

---

## 15. Resumo rápido

- **802.1X** controla o acesso à porta: suplicante → autenticador → servidor.
- **EAP** é o envelope. Os métodos (TLS, PEAP, TTLS, FAST) são o conteúdo.
- **EAP-TLS:** certificados dos dois lados. É o mais seguro e o mais trabalhoso.
- **PEAP:** certificado só no servidor, senha do AD dentro do túnel. É o mais comum.
- **EAP-TTLS:** como o PEAP, mas aceita PAP e outros métodos legados no túnel. Bom para LDAP.
- **EAP-FAST:** usa PAC em vez de certificados. Criado pela Cisco. Desative a entrega anônima.
- **Validar o certificado do servidor** é o que separa um PEAP/TTLS seguro de um inseguro.
- **RADIUS** = acesso dos usuários (UDP, criptografa só a senha). **TACACS+** = administração dos equipamentos (TCP 49, criptografa tudo).

---

## 16. Vocabulário (inglês → português)

| Inglês | Português |
| --- | --- |
| supplicant | suplicante (o cliente) |
| authenticator | autenticador (switch ou AP) |
| authentication server | servidor de autenticação |
| mutual authentication | autenticação mútua |
| certificate authority (CA) | autoridade certificadora |
| public key infrastructure (PKI) | infraestrutura de chaves públicas |
| tunnel | túnel |
| inner / outer identity | identidade interna / externa |
| provisioning | entrega, provisionamento |
| challenge / response | desafio / resposta |
| revocation | revogação |
| rogue / evil twin access point | ponto de acesso falso |
| offline dictionary attack | ataque de dicionário offline |
| accounting | contabilização (registro de atividades) |
