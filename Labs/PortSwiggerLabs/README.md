# Labs - Web Security Academy

Esta pasta reúne writeups práticos dos labs da [PortSwigger Web Security Academy](https://portswigger.net/web-security), resolvidos com **Burp Suite** como parte do meu estudo de segurança ofensiva (pentest/Red Team) e análise de vulnerabilidades web.

Cada writeup documenta o processo real de resolução — incluindo tentativas, erros e correções — com prints do Burp Suite (Proxy, Repeater, Intruder) e explicação técnica de **por que** cada payload funciona, não só o payload em si.

## O que você vai encontrar aqui

### 🔹 SQL Injection
- **Error-based SQL injection**: extração de dados através de mensagens de erro verbosas retornadas pela aplicação (ex: `CAST()` forçando erro de conversão que expõe o valor da subquery).
- **Blind SQL injection (conditional errors)**: extração de dados caractere por caractere usando apenas a presença/ausência de erro HTTP (200 vs 500) como sinal — sem nenhum dado visível na resposta. Inclui uso de **Burp Intruder** para automatizar a extração.

### 🔹 Cross-Site Scripting (XSS)
- **Reflected XSS**: payload refletido na resposta HTTP sem passar pelo banco de dados (em atributos HTML, dentro de strings JavaScript, e via respostas JSON processadas com `eval()`).
- **Stored XSS**: payload persistido no servidor (ex: campo de comentário) e executado para qualquer visitante da página.
- **DOM-based XSS**: vulnerabilidades que existem inteiramente no client-side, onde o JavaScript da própria página lê dados controláveis pelo atacante (`location.search`, `location.hash`) e os insere de forma insegura em *sinks* perigosos (`document.write`, seletores jQuery, atributos `href`, expressões AngularJS).

## Estrutura

```
Labs/
├── SQLinjection/
│   ├── README.md
│   └── images/
├── XSS/
│   ├── README.md
│   └── images/
└── README.md
```

Cada pasta de lab contém:
- Um arquivo `.md` com o passo a passo completo, payloads usados e explicação técnica.
- Uma subpasta `images/` com screenshots do processo (Burp Suite, DevTools, respostas da aplicação).

## Metodologia

Os labs são resolvidos manualmente com o **Burp Suite Community Edition**, priorizando entender a causa raiz de cada vulnerabilidade (não apenas copiar o payload da solução oficial). Quando aplicável, os writeups também registram erros cometidos durante a resolução — como truncamento de payload por limite de caracteres, ou erros de digitação — porque fazem parte do processo real de aprendizado em pentest.

## Próximos labs

Este repositório está em atualização contínua conforme avanço pelas trilhas da Web Security Academy. Categorias previstas para os próximos writeups incluem:
- Authentication
- Access Control
- CSRF
- SSRF
- Business Logic Vulnerabilities
- File Upload Vulnerabilities

---

