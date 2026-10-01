# Uso do Burp Suite aplicado a XSS e SQL Injection

Guia prático baseado nos labs do PortSwigger Web Security Academy, documentados nos repositórios:
- SQL Injection: https://github.com/joaovpzdev/cyber-sec-journey/tree/main/Labs/SQLinjection
- XSS: https://github.com/joaovpzdev/cyber-sec-journey/tree/main/Labs/XSS

---

## 1. Configuração inicial do Burp Suite

| Passo | Ação | Por quê |
|---|---|---|
| 1 | Abrir o Burp e selecionar "Temporary project" / usar o navegador embutido (Chromium) ou configurar o Firefox com o proxy `127.0.0.1:8080` | O Burp precisa ficar no meio do caminho entre navegador e servidor para interceptar, ler e alterar cada requisição/resposta HTTP |
| 2 | Instalar o certificado CA do Burp (`http://burpsuite` > CA Certificate) | Sem o certificado, o tráfego HTTPS é bloqueado por erro de confiança — o Burp precisa "assinar" o tráfego para poder descriptografá-lo e reconstruí-lo |
| 3 | Conferir na aba **Proxy > HTTP history** se as requisições do alvo aparecem | Confirma que o tráfego está realmente passando pelo proxy antes de iniciar qualquer teste |
| 4 | Navegar manualmente por toda a aplicação (mapear) | Preenche o **Site map**, mostrando todos os parâmetros, formulários e endpoints disponíveis para ataque |

---

## 2. Fluxo de trabalho padrão

1. **Proxy** → intercepta a requisição.
2. **Send to Repeater** → envia a requisição para edição manual e reenvio controlado.
3. **Repeater** → altera parâmetros/payloads e analisa a resposta (reflexo, erro, delay).
4. **Intruder** (quando necessário) → automatiza o teste de múltiplos payloads/parâmetros.
5. **Decoder** → codifica/decodifica payloads (URL, HTML, Base64) para burlar filtros.

O Repeater é o núcleo do processo: ele dá controle total sobre a requisição, permitindo isolar a causa-efeito de cada payload — essencial tanto para XSS quanto para SQLi.

---

## 3. Aplicado a XSS (Cross-Site Scripting)

### Passo a passo

1. **Identificar pontos de reflexão**
   No Repeater, injetar uma string única em cada parâmetro, ex: `xss<>"'&/`.
   *Por quê:* revela se o valor volta sem sanitização na resposta HTML — é o primeiro sinal de que o input não é tratado.

2. **Determinar o contexto de reflexão**
   Observar onde o valor aparece: dentro de uma tag HTML, de um atributo, de uma tag `<script>`, etc.
   *Por quê:* o payload precisa ser montado de acordo com o contexto (ex: fechar aspas de um atributo antes de injetar `<script>`), senão o navegador não interpreta como código.

3. **Testar XSS refletido**
   Enviar payload como `<script>alert(1)</script>` ou variações (`<img src=x onerror=alert(1)>`) via Repeater/URL.
   *Por quê:* confirma execução imediata do código — prova de conceito mais simples e direta.

4. **Testar XSS armazenado (Stored)**
   Submeter o payload em campos persistentes (comentário, perfil, mensagem) e depois recarregar a página onde esse dado é exibido.
   *Por quê:* o impacto é maior — o payload executa para qualquer usuário que visualizar o conteúdo, não só para quem o enviou.

5. **Testar XSS via DOM (DOM-based)**
   Usar o **DOM Invader** (navegador embutido do Burp) para monitorar *sources* (ex: `location.hash`, `document.URL`) e *sinks* (ex: `innerHTML`, `eval`) perigosos.
   *Por quê:* esse tipo de XSS não passa pelo servidor — acontece só no JavaScript do cliente, então o Repeater sozinho não o detecta; é preciso observar a execução no navegador.

6. **Contornar filtros/sanitização**
   Usar o **Decoder** para codificar o payload (URL encode, HTML entities) ou extensões como Hackvertor, e tentar variações de tags/eventos.
   *Por quê:* filtros simples costumam bloquear apenas `<script>` literal; codificar ou usar tags alternativas testa a robustez real da defesa.

---

## 4. Aplicado a SQL Injection

### Passo a passo

1. **Identificar o parâmetro injetável**
   No Repeater, inserir caractere de quebra (`'`, `"`, `--`) em cada parâmetro e comparar a resposta com a original.
   *Por quê:* um erro de sintaxe SQL exposto ou uma mudança de comportamento indica que o input está sendo concatenado diretamente na query.

2. **Confirmar a injeção com lógica booleana**
   Testar pares como `' AND '1'='1` (verdadeiro) e `' AND '1'='2` (falso).
   *Por quê:* se a resposta muda de forma consistente entre verdadeiro/falso, confirma a injeção mesmo sem mensagem de erro visível (SQLi baseada em erro vs. booleana).

3. **Determinar o número de colunas**
   Usar `ORDER BY n--` incrementando `n`, ou `UNION SELECT NULL,NULL,...--`.
   *Por quê:* um ataque `UNION` só funciona se o número de colunas do `SELECT` injetado bater com o da query original.

4. **Extrair dados via UNION**
   Substituir os `NULL` por colunas de texto e consultar tabelas do sistema (ex: `UNION SELECT username, password FROM users--`).
   *Por quê:* permite ler diretamente dados sensíveis do banco através da própria resposta da aplicação.

5. **Testar SQLi cega (Blind)**
   - **Booleana:** comparar respostas com condições verdadeiras/falsas.
   - **Baseada em tempo:** usar `' AND SLEEP(5)--` e medir o delay da resposta no Repeater.
   *Por quê:* quando a aplicação não retorna dados nem erros, o tempo de resposta ou pequenas diferenças de comportamento são o único canal de extração de informação.

6. **Automatizar extração com Intruder**
   Usar o Intruder para iterar sobre nomes de tabelas/colunas ou caracteres (ataque cego caractere a caractere).
   *Por quê:* extrair dado por dado manualmente é inviável; o Intruder automatiza o processo repetitivo de tentativa e comparação de respostas.

---

## 5. Por que o Burp é a ferramenta certa para os dois casos

- **Interceptação total:** permite ver e editar exatamente o que o navegador envia, sem depender da validação client-side.
- **Repeater:** isola cada tentativa, essencial para comparar respostas com precisão (reflexo de XSS, diferença booleana de SQLi).
- **Intruder:** escala testes manuais repetitivos (payloads de XSS, extração cega de SQLi) sem precisar de script externo.
- **Decoder:** contorna codificações e filtros simples em ambos os casos.
- **DOM Invader:** cobre o único cenário (DOM XSS) que o proxy sozinho não enxerga, por acontecer inteiramente no cliente.