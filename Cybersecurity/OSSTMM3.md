# OSSTMM 3 — Open Source Security Testing Methodology Manual

> Resumo de estudo baseado no **OSSTMM 3.02**, metodologia de teste de segurança operacional mantida pelo **ISECOM** (Institute for Security and Open Methodologies), autoria original de Pete Herzog. Documento licenciado sob Creative Commons Attribution-NonCommercial-NoDerivs e Open Methodology License 3.0 — este resumo é uma síntese em texto próprio para fins de estudo pessoal, não uma reprodução ou derivação do manual.

## O que é o OSSTMM

Diferente de um checklist de ferramentas, o OSSTMM é uma **metodologia** para medir a segurança operacional (OpSec) de forma factual, repetível e consistente — testando o que **realmente acontece** em um ambiente, e não apenas o que a política ou configuração *diz* que deveria acontecer. Ele cobre um único método aplicado a cinco canais de teste: **Humano, Físico, Wireless, Telecomunicações e Redes de Dados**.

A ideia central é substituir "boas práticas", opiniões e evidências anedóticas por **métricas verificadas**, resumidas na chamada **rav** (attack surface metric) — uma métrica factual de superfície de ataque, sem o viés que métricas de risco tradicionalmente carregam.

---

## 1. Conceitos Fundamentais (Cap. 1–2)

- **Segurança operacional (OpSec)**: o estado real de proteção de um alvo durante sua operação, distinto de conformidade (compliance) — estar em conformidade com uma norma não significa estar operacionalmente seguro.
- **Escopo, ativos e canais**: todo teste precisa definir claramente o que será testado (targets), quais partes serão testadas, e o que **não** será testado — essa transparência é parte da integridade da auditoria.

### Os 6 Tipos de Teste

O OSSTMM classifica os testes conforme o quanto o Analista e o alvo sabem um sobre o outro:

| Tipo | O Analista sabe | O Alvo é avisado | Equivalente comum |
|------|------------------|-------------------|---------------------|
| **Blind** | Nada sobre defesas/ativos | Sim, detalhes completos | Ethical Hacking / War Gaming |
| **Double Blind** | Nada sobre defesas/ativos | Não | Black Box / Penetration Test |
| **Gray Box** | Conhecimento limitado | Sim, detalhes completos | Vulnerability Test (self-assessment) |
| **Double Gray Box** | Conhecimento limitado | Sim, só escopo e prazo | White Box Test |
| **Tandem** | Conhecimento completo | Sim, detalhes completos | In-House Audit / Crystal Box |
| **Reversal** | Conhecimento completo dos processos | Não | Red Team Exercise |

### Regras de Engajamento (Rules of Engagement)

O manual define regras vinculantes organizadas por fase — entre elas: o escopo deve estar definido contratualmente antes do teste; o Analista deve respeitar privacidade, saúde e segurança do público; testes de negação de serviço só podem ocorrer com permissão explícita; achados críticos devem ser reportados assim que encontrados; e relatórios devem ser objetivos, baseados só em métricas quantitativas.

---

## 2. O Processo de Teste (Cap. 2)

### Four Point Process (4PP)

Em vez de depender só do "processo de eco" (interagir e observar a resposta — rápido, mas propenso a erros graves, já que um alvo sem resposta pode ser interpretado erroneamente como seguro), o OSSTMM estrutura o teste em **quatro interações**:

1. **Induction** — levantar verdades sobre o ambiente do alvo (leis, contexto).
2. **Inquest** — investigar emanações e vestígios deixados pelo alvo.
3. **Interaction** — interagir diretamente com o alvo para provocar respostas (inclui o "eco").
4. **Intervention** — alterar as interações de recursos do alvo para entender seus limites operacionais.

### A Trifecta

Aplicar a metodologia deve responder três perguntas centrais:
1. Como as operações funcionam atualmente?
2. Como elas funcionam de forma diferente do que a gestão imagina?
3. Como elas *deveriam* funcionar?

---

## 3. Análise de Segurança e Confiança (Cap. 3 e 5)

- **Pensamento crítico em segurança**: reconhecer o "modelo OpSec", identificar padrões que indicam erro, e caracterizar resultados de forma transparente, evitando conclusões baseadas em intuição não verificada.
- **As Dez Propriedades de Confiança** (Trust Properties) — usadas para transformar confiança em algo mensurável, ao invés de uma decisão subjetiva:

| # | Propriedade | O que mede |
|---|---|---|
| 1 | Size | Quantos precisam confiar (um ou muitos) |
| 2 | Symmetry | Se a confiança é uma via (assimétrica) ou mútua (simétrica) |
| 3 | Visibility | Transparência dos processos do alvo |
| 4 | Subjugation | Nível de controle/influência sobre o escopo |
| 5 | Consistency | Histórico de comprometimento do alvo |
| 6 | Integrity | Aviso e prazo de mudanças no alvo |
| 7 | Offsets | Compensação/punição em caso de quebra de confiança |
| 8 | Value | Retorno financeiro que justifica o risco de confiar |
| 9 | Components | Quantos outros elementos fornecem recursos ao alvo |
| 10 | Porosity | Grau de separação entre o alvo e o ambiente externo |

---

## 4. Métricas Operacionais — a Rav (Cap. 4)

O **rav** (risk assessment value / attack surface) é a métrica central do OSSTMM 3: um valor factual da superfície de ataque de um alvo, calculado a partir de três componentes — **segurança operacional**, **controles** existentes e **limitações** encontradas — combinados na **fórmula de Segurança Real (Actual Security)**. Diferente de métricas de risco tradicionais, a rav não carrega opinião ou viés: é puramente derivada de fatos verificados no teste.

---

## 5. Fluxo de Trabalho e Módulos de Teste (Cap. 6)

A execução segue **quatro fases**, que espelham o Four Point Process:

- **A. Induction Phase** — Posture Review (leis, políticas, cultura), Logistics, Active Detection Verification.
- **B. Interaction Phase** — Visibility Audit, Access Verification, Trust Verification (entre outros módulos).
- **C. Inquest Phase** — investigação de emanações e evidências.
- **D. Intervention Phase** — testes de intervenção sobre os recursos do alvo.

Ao todo, o manual organiza os testes em uma sequência de módulos lettrados (A.1, A.2, B.4, B.5...) que cobrem desde revisão de política até verificação de controles — a ideia é que cada Analista percorra os módulos relevantes ao escopo, documentando explicitamente o que **não** foi testado.

---

## 6. Os Cinco Canais de Teste (Cap. 7–11)

| Canal | Classificação | Foco do teste | Popularmente chamado de |
|-------|----------------|----------------|---------------------------|
| **Humano** (Cap. 7) | HUMSEC / PSYOPS | Interação com pessoas em posições de "gatekeeper" de ativos | "Engenharia social" |
| **Físico** (Cap. 8) | PHYSSEC | Barreiras físicas e humanas em espaço 3D | "Invasão" (breaking and entering) |
| **Wireless** (Cap. 9) | SPECSEC (ELSEC/SIGSEC/EMSEC) | Barreiras sobre frequências eletromagnéticas e micro-ondas | "Scanning" |
| **Telecomunicações** (Cap. 10) | COMSEC | Segurança sobre redes de telefonia (digital/analógica) | "Phreaking" |
| **Redes de Dados** (Cap. 11) | COMSEC | Salvaguardas operacionais de redes de computadores | "Pentest" |

Um ponto que o manual reforça em todos os canais: o objetivo de conformidade real do teste **não** é só encontrar a falha (ex: convencer alguém a revelar uma senha, ou entrar fisicamente em um prédio) — é medir o **gap** entre o comportamento observado e o padrão de segurança exigido por política, regulação ou legislação, com considerações éticas e legais específicas para cada canal (ex: testes com pessoas exigem consentimento contratual claro e discrição estatística ao reportar).

---

## 7. Relatório e Conclusão (Cap. 12–15)

- **Compliance (Cap. 12)**: o OSSTMM pode ser mapeado a normas e regulações existentes (PCI-DSS, ISO/IEC 27001/27002/27005, NIST), servindo como base factual para atender a exigências de auditoria.
- **STAR — Security Test Audit Report (Cap. 13)**: o formato de relatório padrão do OSSTMM, focado em métricas quantitativas e no que foi e não foi testado.
- **Möbius Defense (Cap. 14)**: modelo de defesa em profundidade proposto pelo OSSTMM.
- **Open Methodology License — OML 3 (Cap. 15)**: a licença sob a qual a própria metodologia é protegida e distribuída.

---

## Por que isso importa para pentest/security testing

O maior valor do OSSTMM para quem estuda segurança ofensiva/defensiva é o **rigor metodológico**: em vez de rodar ferramentas soltas (Nmap, Hydra, etc.), ele ensina a pensar em **escopo, tipo de teste, regras de engajamento, e métricas verificáveis** — o que se conecta diretamente com a prática de documentar achados de forma factual e reportável, como no seu repositório `cyber-sec-journey`.

## Referências

- ISECOM — https://www.isecom.org
- OSSTMM — https://www.osstmm.org
- Certificações oficiais: OPSA, OPST, OPSE, OWSE — via isecom.org