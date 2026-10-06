# Bandit 15 → 16 — Serviço com SSL/TLS

## Objetivo

Mesma ideia do nível anterior, mas o serviço só aceita conexões **cifradas com SSL/TLS**, então o netcat em texto puro não funciona.

## Conceitos

- **TLS:** protocolo que cifra a comunicação, o mesmo usado pelo HTTPS.
- **Certificado digital:** identifica o servidor. É assinado por uma **autoridade certificadora (CA)** confiável ou pelo próprio servidor (**autoassinado**).
- **`openssl s_client`:** um "netcat com TLS". Abre a conexão cifrada e mostra os detalhes do certificado.

## Abordagem

1. Conectar com o cliente TLS do OpenSSL:
   ```bash
   openssl s_client -connect localhost:<porta>
   ```
2. Analisar a saída: cadeia de certificados, emissor (`issuer`), titular (`subject`), algoritmo e validade.
3. Enviar a senha. Se o cliente interpretar a entrada como comando (aparecendo `RENEGOTIATING` ou `KEYUPDATE`), usar o modo silencioso:
   ```bash
   openssl s_client -connect localhost:<porta> -quiet
   ```

## O que foi observado

O certificado do serviço tinha:

- `verify error: self-signed certificate`
- `subject` igual ao `issuer`, ou seja, assinado por ele mesmo
- um nome genérico de certificado de teste

## A vulnerabilidade

**Certificado autoassinado / validação de certificado fraca.**

A criptografia continua funcionando, mas o cliente **não tem como confirmar a identidade do servidor**. Se usuários e sistemas se acostumam a aceitar certificados inválidos, um atacante pode se colocar no meio da conexão (**man-in-the-middle**), apresentar o próprio certificado e ler ou alterar todo o tráfego.

## No mundo real

- Painéis administrativos internos e appliances com certificados padrão de fábrica.
- Aplicações configuradas para ignorar erros de certificado (`verify=False`, `-k` no curl).
- Usuários treinados a clicar em "Continuar mesmo assim" no navegador.

**CWE:** CWE-295 — Improper Certificate Validation

## Como corrigir / detectar

- Usar certificados emitidos por uma CA confiável (pública ou corporativa interna).
- Nunca desabilitar a verificação de certificado em código de produção.
- Monitorar certificados expirados, autoassinados ou inesperados na rede.