# Bandit 13 → 14 — Chave SSH privada exposta

## Objetivo

Acessar o próximo usuário **sem receber uma senha**. No diretório do usuário atual existe uma chave SSH privada que permite autenticar como o próximo usuário.

## Conceitos

- **Autenticação por chave SSH:** usa um par de chaves. A **pública** fica no servidor (`~/.ssh/authorized_keys`), e a **privada** fica com o usuário. Quem possui a chave privada consegue se autenticar, sem precisar de senha.
- **Permissões de arquivo:** o cliente SSH recusa chaves privadas que outros usuários consigam ler.
- **`scp`:** copia arquivos entre máquinas usando SSH.

## Abordagem

1. Listar o diretório e identificar o arquivo da chave (o cabeçalho `BEGIN OPENSSH PRIVATE KEY` confirma o tipo).
2. Copiar a chave para a máquina local:
   ```bash
   scp -P <porta> usuario@host:<arquivo_da_chave> .
   ```
   > No `scp` a porta é `-P` **maiúsculo**; no `ssh` é `-p` minúsculo.
3. Restringir as permissões da chave, senão o SSH exibe `UNPROTECTED PRIVATE KEY FILE` e se recusa a usá-la:
   ```bash
   chmod 600 <arquivo_da_chave>
   ```
4. Conectar usando a chave:
   ```bash
   ssh -i <arquivo_da_chave> <proximo_usuario>@host -p <porta>
   ```

## A vulnerabilidade

**Credencial sensível armazenada em local acessível a quem não deveria tê-la.**

Uma chave privada equivale a uma senha que **nunca expira** e **não exige interação**. Quem a obtém:

- se autentica como o dono da chave, sem gerar tentativas de login com falha;
- pode continuar entrando mesmo depois que a senha do usuário é trocada;
- consegue fazer **movimento lateral** para qualquer servidor que confie nessa chave.

## No mundo real

- Chaves esquecidas em diretórios home, backups, imagens Docker e repositórios Git.
- Chaves privadas comitadas por engano no GitHub, uma das causas mais comuns de vazamento.
- Em pentests, procurar `id_rsa`, `id_ed25519` e arquivos `*.pem` é um passo padrão de pós-exploração.

**MITRE ATT&CK:** T1552.004 — Unsecured Credentials: Private Keys
**CWE:** CWE-522 — Insufficiently Protected Credentials

## Como corrigir / detectar

- Proteger as chaves com **passphrase**.
- Permissões `600` na chave e `700` no diretório `~/.ssh`.
- Nunca deixar chaves em diretórios compartilhados ou em repositórios. Usar ferramentas como `gitleaks` ou `trufflehog` para varrer o código.
- Fazer rotação de chaves e auditar o `authorized_keys` periodicamente.
- Monitorar logins SSH por chave vindos de origens incomuns.