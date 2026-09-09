# Footprinting (Reconhecimento)

## O que é

Footprinting — também chamado de reconnaissance ou information gathering — é a primeira fase de um teste de intrusão. O objetivo é levantar o máximo de informação possível sobre um alvo antes de qualquer interação mais profunda com sua infraestrutura, mapeando domínio, subdomínios, servidores, tecnologias e pessoas envolvidas. Essas informações orientam as fases seguintes de um pentest, como scanning e enumeration.

O footprinting costuma ser dividido em duas abordagens:

- **Passiva**: coleta de informação sem qualquer interação direta com os sistemas do alvo (ex: bases públicas de WHOIS, logs de Certificate Transparency).
- **Ativa**: envolve algum grau de interação direta com a infraestrutura do alvo (ex: consultas DNS, requisições HTTP direcionadas).

A ordem abaixo organiza os passos indo do inteiramente passivo para o mais ativo, e respeitando dependências naturais entre etapas (por exemplo, nomes e endereços costumam vir do resultado do WHOIS).

## 1. Análise do front-end (navegação e DevTools)

Primeiro passo, e o mais passivo de todos: navegar pelo site como um usuário comum e usar as ferramentas de desenvolvedor do navegador (F12) para inspecionar código-fonte, requisições de rede e scripts carregados. Por ser indistinguível do tráfego de um visitante normal, não chama atenção nos logs do servidor.

O que costuma ser encontrado nessa etapa:

- Comentários deixados por desenvolvedores no HTML ou JavaScript
- Endpoints de API chamados no client-side
- Chaves ou tokens expostos acidentalmente no código-fonte
- Tecnologias e frameworks utilizados, incluindo versões (úteis para cruzar com vulnerabilidades conhecidas)
- Caminhos de diretórios sugeridos por referências no código

## 2. WHOIS

```
whois dominio.com
```

Consulta a base pública de registro de domínios, mantida pelos registradores e coordenada pela ICANN. Retorna data de registro e expiração, servidores de nome (name servers) associados ao domínio e, quando não mascarados por proteção de privacidade, dados de contato do registrante.

## 3. Nomes e endereços

Decorre diretamente do resultado do WHOIS (e pode ser complementado com outras fontes públicas, como redes sociais e o próprio site institucional). Nome do registrante, organização, endereço físico, e-mail e telefone de contato — quando disponíveis — ajudam a entender a estrutura por trás do domínio.

Vale notar que, desde a entrada em vigor de regulamentações como o GDPR, boa parte dos registradores mascara esses dados por padrão, então esse tipo de informação está cada vez mais limitado nas respostas de WHOIS.

## 4. robots.txt

```
dominio.com/robots.txt
```

Arquivo público que instrui crawlers de busca sobre quais caminhos não devem ser indexados. Do ponto de vista de reconhecimento, o interesse está justamente no inverso da sua função: caminhos listados em `Disallow` costumam apontar para áreas que o proprietário não quer ver indexadas — painéis administrativos, diretórios internos, ambientes de staging — e que por isso merecem verificação manual.

## 5. host + domínio

```
host dominio.com
```

Consulta DNS básica que retorna o registro A (IPv4) e, quando existente, AAAA (IPv6) do domínio, além dos registros MX (servidores de e-mail). É o primeiro passo mais "ativo" do processo, já que envolve consulta direta aos servidores DNS do alvo.

## 6. dnsenum

```
dnsenum dominio.com
```

Ferramenta de enumeração DNS que consulta os name servers autoritativos do domínio e executa brute force de subdomínios a partir de uma wordlist. Retorna servidores de nome, registros MX e os subdomínios localizados por tentativa e erro contra o DNS.

## 7. dnsrecon -d

```
dnsrecon -d dominio.com
```

Consulta múltiplos tipos de registro DNS (A, AAAA, MX, NS, TXT, SOA) e retorna todos os IPs associados ao domínio disponíveis por essas consultas — complementar ao dnsenum, com cobertura mais ampla de tipos de registro.

## 8. dnsrecon -d -t brt

```
dnsrecon -d dominio.com -t brt
```

Ativa o módulo de brute force de subdomínios do dnsrecon (`brt`). Testa uma wordlist de possíveis nomes contra o DNS do alvo — tende a demorar mais que o brute force do dnsenum, mas costuma ser mais configurável, permitindo wordlists customizadas e ajuste de threads.

## 9. crt.sh

Ferramenta baseada em Certificate Transparency — sistema público e auditável no qual toda autoridade certificadora é obrigada a registrar os certificados TLS/SSL que emite. Consultar o crt.sh por um domínio revela subdomínios que já receberam certificado, incluindo ambientes de staging, homologação e serviços internos que às vezes escapam ao brute force tradicional. É uma técnica inteiramente passiva: os dados vêm de logs públicos das autoridades certificadoras, sem nenhuma consulta direta ao alvo.

## 10. wafw00f

Disponível na categoria Information Gathering do Kali Linux. Envia requisições HTTP ao alvo e analisa as respostas — cabeçalhos e comportamento diante de payloads de teste — para identificar se há um Web Application Firewall (WAF) na frente da aplicação e, em alguns casos, qual o fabricante. Faz sentido deixar essa etapa por último: com domínio, subdomínios e IPs já mapeados, saber se existe um WAF ajuda a calibrar a abordagem das fases seguintes (scanning e exploitation), evitando requisições que disparem bloqueios ou alertas desnecessários.

## Fluxo resumido

| Ordem | Etapa | Tipo | Retorna |
|---|---|---|---|
| 1 | Front-end / DevTools | Passiva | Código-fonte, endpoints, tecnologias |
| 2 | WHOIS | Passiva | Registro do domínio, name servers |
| 3 | Nomes e endereços | Passiva | Dados do registrante |
| 4 | robots.txt | Passiva | Caminhos não indexados |
| 5 | host | Ativa | IPv4, IPv6, servidores de e-mail |
| 6 | dnsenum | Ativa | Name servers, subdomínios (brute force) |
| 7 | dnsrecon -d | Ativa | IPs associados ao domínio |
| 8 | dnsrecon -d -t brt | Ativa | Subdomínios (brute force mais pesado) |
| 9 | crt.sh | Passiva | Subdomínios via Certificate Transparency |
| 10 | wafw00f | Ativa | Presença e fabricante de WAF |

## Considerações éticas e legais

Todas essas técnicas devem ser aplicadas apenas contra domínios próprios ou com autorização explícita (escopo definido em um contrato de pentest). Mesmo etapas passivas, como WHOIS e crt.sh, servem para mapear um alvo — usar essa informação para acessar sistemas sem autorização é o que configura o problema legal, não a coleta da informação em si.

## Referências

- ICANN — WHOIS
- Certificate Transparency — crt.sh
- Documentação oficial das ferramentas dnsenum, dnsrecon e wafw00f (Kali Linux Tools)
- Robots Exclusion Protocol (especificação do robots.txt)
- OWASP Testing Guide — Information Gathering
- EC-Council CEH — metodologia de footprinting e reconhecimento