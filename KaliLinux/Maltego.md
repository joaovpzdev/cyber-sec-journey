# Maltego — OSINT e análise de vínculos

## O que é

Maltego é uma ferramenta gráfica de mineração de dados e análise de vínculos (link analysis), desenvolvida pela Maltego Technologies (antiga Paterva). Diferente das ferramentas de reconhecimento em linha de comando já documentadas neste repositório, o Maltego representa a informação coletada como um grafo interativo: cada nó ("entidade") representa um objeto do mundo real — uma pessoa, um e-mail, um domínio, um IP, um telefone, uma empresa, um documento, um alias de rede social — e cada linha conectando dois nós representa uma relação descoberta entre eles.

Vem pré-instalado no Kali Linux, na categoria Information Gathering / OSINT Analysis, e é uma das ferramentas de referência para a etapa de OSINT de um pentest ou investigação.

## Conceitos fundamentais

### Entidades (Entities)

Cada nó do grafo representa um tipo específico de objeto. Os tipos mais comuns incluem:

| Entidade | Representa |
|---|---|
| Domain | Um domínio (`exemplo.com`) |
| DNS Name | Um subdomínio ou hostname |
| IPv4 Address | Um endereço IP |
| Email Address | Um endereço de e-mail |
| Person | Um nome de pessoa |
| Alias | Um nome de usuário/apelido usado online |
| Phone Number | Um número de telefone |
| Organization | Uma empresa ou instituição |
| Document | Um arquivo público encontrado (PDF, DOCX, etc.) |
| Website | Uma URL específica |
| Netblock / AS | Uma faixa de rede ou sistema autônomo |
| Location | Uma localização geográfica |

Uma investigação começa com uma ou poucas entidades conhecidas (por exemplo, um domínio) e vai crescendo conforme novas entidades relacionadas são descobertas.

### Transforms

É o mecanismo central da ferramenta: pequenos scripts que recebem uma entidade como entrada, consultam alguma fonte de dados, e devolvem novas entidades relacionadas como saída. Por exemplo: uma entidade Domain, ao rodar o transform "To DNS Name", retorna os subdomínios descobertos; uma entidade Email Address pode retornar em quais redes sociais aquele e-mail está cadastrado.

Os transforms consultam tanto fontes públicas e gratuitas (WHOIS, DNS, buscadores) quanto integrações de terceiros disponíveis na **Transform Hub** — como Shodan, VirusTotal e Have I Been Pwned — algumas delas exigindo chave de API própria, configurada pelo usuário.

### Machines

Sequências predefinidas de transforms, funcionando como uma macro que automatiza um fluxo de reconhecimento em várias etapas com um único clique. Duas das mais citadas:

- **Footprint L1 / L2 / L3**: aplicam um footprinting progressivamente mais profundo sobre um domínio — a mesma lógica do `footprinting.md`, só que automatizada e em camadas de intensidade crescente (L1 mais superficial, L3 mais exaustiva).
- **Company Stalker**: coleta endereços de e-mail associados a um domínio, verifica em quais redes sociais eles aparecem, e extrai metadados de documentos publicados relacionados àquela organização.

## Instalação e primeiro acesso

Já vem pré-instalado no Kali. Para usar, é necessário criar uma conta gratuita (Maltego ID) e vinculá-la à aplicação no primeiro login — a versão gratuita é chamada de **Maltego Graph Community Edition (CE)**.

```bash
maltego
```

## Nível básico

### Criando um grafo e a primeira entidade

- `New Graph`
- Arrastar uma entidade da paleta lateral (por exemplo, `Domain`) para o canvas
- Digitar o valor desejado (ex: `exemplo.com`)

### Rodando um transform manualmente

- Clique direito sobre a entidade → escolher um transform na lista (ex: `To DNS Name [DNS]`)
- O resultado aparece como novos nós, já conectados visualmente à entidade original

### Rodando uma machine automatizada

- Painel `Machines` → `Run Machine` → selecionar, por exemplo, `Footprint L1`
- Informar o domínio-alvo
- O Maltego executa a sequência de transforms automaticamente, populando o grafo sem interação manual a cada passo

## Nível intermediário

### Visualizações do grafo

O Maltego oferece diferentes formas de visualizar o mesmo grafo — a visão principal (nós conectados por linhas), uma visão em bolhas (agrupando por tipo de entidade) e uma lista tabular das entidades — úteis dependendo do que se está tentando enxergar: relações específicas ou volume geral de dados coletados.

### Nós de coleção (collection nodes)

Quando uma consulta retorna um volume grande de entidades semelhantes, o Maltego pode agrupá-las automaticamente em um "nó de coleção", evitando que o grafo fique poluído visualmente e ajudando a identificar os relacionamentos realmente relevantes em meio ao ruído de resultados.

### Configurando integrações (Transform Hub)

Acessível pelo menu principal, a Transform Hub lista dezenas de integrações disponíveis para instalação — cada uma trazendo seu próprio conjunto de transforms voltados a uma fonte de dados específica. Integrações que dependem de serviços de terceiros normalmente exigem que o usuário configure sua própria chave de API daquele serviço dentro do Maltego.

### Combinando múltiplos transforms manualmente

Em vez de depender só de machines prontas, é possível rodar transforms um a um, escolhendo o caminho de investigação conforme os resultados intermediários — mais lento, mas permite um controle bem mais preciso sobre o que está sendo consultado, e evita gerar ruído desnecessário em investigações mais direcionadas.

## Nível avançado

### Planos do Maltego e limites da versão gratuita (2026)

O Maltego reorganizou sua oferta em uma plataforma mais ampla — Maltego Graph, Maltego Search, Maltego Monitor, Maltego Evidence — distribuída em planos Basic (gratuito), Entry, Professional e Enterprise. A versão gratuita (Maltego Graph CE, incluída no plano Basic) mantém a maior parte da funcionalidade principal, com alguns limites:

- Até 10.000 entidades por grafo
- Até 24 resultados retornados por transform
- 200 créditos/mês para consultar módulos de dados prontos (Data Pass) e conectores de terceiros

Para uso profissional mais intenso — grafos maiores, mais créditos de dados, gestão de casos colaborativa — os planos pagos removem essas limitações.

### Connector Builder

Recurso voltado a integrar fontes de dados próprias ou proprietárias diretamente ao Maltego, permitindo que uma organização conecte seus próprios bancos de dados internos ao mesmo mecanismo de transforms usado para fontes públicas — disponível nos planos pagos.

### Maltego como consolidador de investigação

Na prática, o Maltego funciona bem como camada de consolidação: os achados de ferramentas de linha de comando já documentadas neste repositório (`dnsenum`, `dnsrecon`, `crt.sh`) podem ser inseridos manualmente como entidades no grafo, permitindo visualizar, lado a lado, informações vindas de fontes completamente diferentes sobre o mesmo alvo.

## Fluxo típico de uso

| Ordem | Etapa | Ação no Maltego |
|---|---|---|
| 1 | Definir a entidade inicial | Adicionar Domain/Person/Organization ao grafo |
| 2 | Reconhecimento amplo automatizado | Rodar uma machine (ex: Footprint L1) |
| 3 | Aprofundar manualmente pontos de interesse | Rodar transforms específicos sobre entidades relevantes |
| 4 | Organizar o grafo | Usar nós de coleção e diferentes visualizações |
| 5 | Consolidar com dados de outras ferramentas | Inserir manualmente achados externos como novas entidades |

## Maltego vs ferramentas de linha de comando

Ferramentas como `dnsenum`, `theHarvester` ou `crt.sh` são rápidas, roteirizáveis e focadas em um tipo específico de dado ou fonte. O diferencial do Maltego é justamente o oposto: ele não é o mais rápido em nenhuma consulta individual, mas se destaca em correlacionar visualmente resultados de múltiplos tipos de entidade e múltiplas fontes ao mesmo tempo, revelando conexões que passariam despercebidas ao olhar cada fonte separadamente em um terminal. Na prática, as duas abordagens se complementam: ferramentas de linha de comando para consultas pontuais e rápidas, Maltego para construir a visão consolidada de uma investigação mais longa.

## Considerações éticas e legais

Assim como as demais técnicas de reconhecimento passivo já documentadas, os dados que o Maltego coleta vêm de fontes públicas — mas a capacidade de correlacionar múltiplas fontes rapidamente é justamente o que torna essa ferramenta sensível do ponto de vista de privacidade, especialmente quando o alvo da investigação é uma pessoa física em vez de uma organização. Usar o Maltego para mapear informações sobre indivíduos fora do escopo de uma investigação autorizada (um pentest com escopo definido, uma investigação legítima) pode esbarrar em legislações de proteção de dados pessoais, como a LGPD no Brasil ou o GDPR na União Europeia, mesmo que toda a informação usada seja tecnicamente pública.

## Referências

- Documentação oficial do Maltego (docs.maltego.com)
- Kali Linux Tools — Maltego
- Maltego — comparação de planos (maltego.com/pricing-plans)