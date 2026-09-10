# SSH

> Este documento apresenta o funcionamento do SSH (**Secure Shell**), sua configuração no Linux, autenticação por senha e chaves criptográficas, hardening de servidores, transferência de arquivos, tunelamento e técnicas de diagnóstico.

---

# Sumário

- [1. O que é SSH](#1-o-que-é-ssh)
- [2. Para que serve](#2-para-que-serve)
- [3. Cliente e servidor](#3-cliente-e-servidor)
- [4. Como uma conexão SSH funciona](#4-como-uma-conexão-ssh-funciona)
- [5. A porta 22](#5-a-porta-22)
- [6. Instalação](#6-instalação)
- [7. Iniciando o servidor SSH](#7-iniciando-o-servidor-ssh)
- [8. Arquivos importantes](#8-arquivos-importantes)
- [9. Configuração do sshd](#9-configuração-do-sshd)
- [10. Conectando a um servidor](#10-conectando-a-um-servidor)
- [11. Autenticação por senha](#11-autenticação-por-senha)
- [12. Autenticação por chaves](#12-autenticação-por-chaves)
- [13. Gerando chaves SSH](#13-gerando-chaves-ssh)
- [14. Chave pública e privada](#14-chave-pública-e-privada)
- [15. Copiando a chave pública](#15-copiando-a-chave-pública)
- [16. Permissões corretas](#16-permissões-corretas)
- [17. ssh-agent](#17-ssh-agent)
- [18. known_hosts](#18-known_hosts)
- [19. Host keys](#19-host-keys)
- [20. Configuração do cliente](#20-configuração-do-cliente)
- [21. Alias SSH](#21-alias-ssh)
- [22. Hardening](#22-hardening)
- [23. Desabilitando login root](#23-desabilitando-login-root)
- [24. Desabilitando autenticação por senha](#24-desabilitando-autenticação-por-senha)
- [25. Permitindo usuários específicos](#25-permitindo-usuários-específicos)
- [26. Mudando a porta](#26-mudando-a-porta)
- [27. Firewall](#27-firewall)
- [28. SCP](#28-scp)
- [29. SFTP](#29-sftp)
- [30. Tunelamento SSH](#30-tunelamento-ssh)
- [31. Local Port Forwarding](#31-local-port-forwarding)
- [32. Remote Port Forwarding](#32-remote-port-forwarding)
- [33. Dynamic Port Forwarding](#33-dynamic-port-forwarding)
- [34. Jump Host](#34-jump-host)
- [35. SSH ProxyJump](#35-ssh-proxyjump)
- [36. X11 Forwarding](#36-x11-forwarding)
- [37. Multiplexação de conexões](#37-multiplexação-de-conexões)
- [38. Troubleshooting](#38-troubleshooting)
- [39. Debug com -v](#39-debug-com--v)
- [40. Analisando portas](#40-analisando-portas)
- [41. Analisando logs](#41-analisando-logs)
- [42. Capturando tráfego](#42-capturando-tráfego)
- [43. Boas práticas](#43-boas-práticas)
- [44. Exercícios](#44-exercícios)
- [45. Resumo](#45-resumo)

---

# 1. O que é SSH

SSH significa:

```text
Secure Shell
```

É um protocolo utilizado principalmente para:

- Acessar servidores remotamente.
- Executar comandos.
- Transferir arquivos.
- Criar túneis criptografados.
- Administrar sistemas.
- Encaminhar conexões através de uma máquina intermediária.

Uma conexão SSH protege a comunicação entre:

```text
Cliente SSH
     |
     | comunicação criptografada
     |
     v
Servidor SSH
```

Diferentemente de protocolos antigos como Telnet, o SSH protege a comunicação contra observação direta do conteúdo transmitido.

---

# 2. Para que serve

Um dos usos mais comuns é acessar um servidor:

```bash
ssh usuario@192.168.1.10
```

Após autenticação:

```text
Seu computador
     |
     | SSH
     |
     v
Servidor Linux
```

Você pode executar comandos remotamente:

```bash
hostname
```

```bash
uptime
```

```bash
ip addr
```

```bash
systemctl status ssh
```

---

# 3. Cliente e servidor

Uma comunicação SSH possui dois componentes principais.

## Cliente

O computador que inicia a conexão.

Normalmente utiliza:

```bash
ssh
```

## Servidor

O computador que aceita conexões.

Normalmente executa:

```text
sshd
```

Representação:

```text
CLIENTE                         SERVIDOR

ssh -------------------------> sshd
```

---

# 4. Como uma conexão SSH funciona

Uma visão simplificada:

```text
Cliente
   |
   | TCP SYN
   v
Servidor
   |
   | TCP SYN-ACK
   v
Cliente
   |
   | TCP ACK
   v
Conexão TCP estabelecida
   |
   v
Negociação SSH
   |
   v
Verificação do servidor
   |
   v
Autenticação do usuário
   |
   v
Sessão SSH
```

O SSH normalmente utiliza TCP.

Por padrão:

```text
TCP/22
```

---

# 5. A porta 22

A porta padrão do SSH é:

```text
22/TCP
```

Um servidor pode estar escutando:

```text
0.0.0.0:22
```

ou:

```text
192.168.1.10:22
```

Verifique com:

```bash
ss -tln
```

Ou:

```bash
sudo ss -tlnp
```

Exemplo:

```text
LISTEN 0 128 0.0.0.0:22
```

Isso indica que o serviço está escutando conexões TCP na porta 22.

---

# 6. Instalação

Em distribuições baseadas em Debian:

```bash
sudo apt update
sudo apt install openssh-server
```

Em sistemas baseados em Fedora:

```bash
sudo dnf install openssh-server
```

O cliente geralmente pode ser instalado com:

```bash
sudo apt install openssh-client
```

Em muitos sistemas Linux, o cliente SSH já está instalado.

Verifique:

```bash
ssh -V
```

---

# 7. Iniciando o servidor SSH

Verifique o serviço:

```bash
sudo systemctl status ssh
```

Em algumas distribuições:

```bash
sudo systemctl status sshd
```

Iniciar:

```bash
sudo systemctl start ssh
```

Habilitar no boot:

```bash
sudo systemctl enable ssh
```

Reiniciar:

```bash
sudo systemctl restart ssh
```

Após alterar configurações, prefira validar a sintaxe antes de reiniciar:

```bash
sudo sshd -t
```

Isso ajuda a evitar perder acesso remoto devido a um erro de configuração.

---

# 8. Arquivos importantes

## Configuração do servidor

```text
/etc/ssh/sshd_config
```

Também podem existir arquivos adicionais em diretórios incluídos pela configuração, dependendo da distribuição.

## Configuração do cliente

```text
/etc/ssh/ssh_config
```

## Configuração pessoal do cliente

```text
~/.ssh/config
```

## Chaves do usuário

```text
~/.ssh/
```

## Chaves públicas autorizadas no servidor

```text
~/.ssh/authorized_keys
```

## Hosts conhecidos

```text
~/.ssh/known_hosts
```

---

# 9. Configuração do sshd

O arquivo principal normalmente é:

```text
/etc/ssh/sshd_config
```

Exemplo:

```text
Port 22
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
```

Após alterar:

```bash
sudo sshd -t
```

Depois:

```bash
sudo systemctl reload ssh
```

ou, dependendo da distribuição:

```bash
sudo systemctl reload sshd
```

> Sempre mantenha uma segunda sessão SSH aberta ao testar alterações de acesso. Não encerre a sessão atual até confirmar que uma nova conexão funciona.

---

# 10. Conectando a um servidor

Sintaxe básica:

```bash
ssh usuario@host
```

Exemplo:

```bash
ssh joao@192.168.1.10
```

Especificando uma porta:

```bash
ssh -p 2222 joao@192.168.1.10
```

---

# 11. Autenticação por senha

Fluxo simplificado:

```text
Cliente
   |
   | Solicita conexão
   v
Servidor
   |
   | Solicita autenticação
   v
Cliente
   |
   | Senha protegida pelo canal SSH
   v
Servidor
   |
   | Verifica credenciais
   v
Acesso
```

Apesar de a senha trafegar dentro do canal criptografado, autenticação por senha possui riscos como:

- Senhas fracas.
- Reutilização de senhas.
- Tentativas automatizadas.
- Ataques de força bruta.

Por isso, autenticação por chaves é geralmente preferível para administração de servidores.

---

# 12. Autenticação por chaves

A autenticação utiliza um par:

```text
Chave privada
     +
Chave pública
```

A chave privada permanece no cliente.

A chave pública é instalada no servidor.

```text
CLIENTE                         SERVIDOR

id_ed25519
CHAVE PRIVADA
     |
     | autenticação
     |
     v

                              authorized_keys
                              CHAVE PÚBLICA
```

---

# 13. Gerando chaves SSH

Uma opção moderna comum:

```bash
ssh-keygen -t ed25519
```

Você pode adicionar um comentário:

```bash
ssh-keygen -t ed25519 -C "meu-computador"
```

Arquivos típicos:

```text
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```

---

# 14. Chave pública e privada

## Chave privada

Exemplo:

```text
~/.ssh/id_ed25519
```

Ela deve permanecer privada.

Nunca faça:

```text
Upload público
Commit no GitHub
Enviar em mensagens
Compartilhar em repositórios
```

A chave privada deve ser protegida.

---

## Chave pública

Exemplo:

```text
~/.ssh/id_ed25519.pub
```

Ela pode ser adicionada aos servidores nos quais você deseja autenticar.

---

# 15. Copiando a chave pública

Uma maneira simples:

```bash
ssh-copy-id usuario@192.168.1.10
```

Isso normalmente adiciona a chave pública ao:

```text
~/.ssh/authorized_keys
```

no servidor.

Também é possível copiar manualmente.

No cliente:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copie o conteúdo.

No servidor:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

Depois adicione a chave:

```bash
nano ~/.ssh/authorized_keys
```

E ajuste permissões:

```bash
chmod 600 ~/.ssh/authorized_keys
```

---

# 16. Permissões corretas

Permissões incorretas podem fazer o SSH recusar arquivos por motivos de segurança.

Uma configuração comum:

```bash
chmod 700 ~/.ssh
```

```bash
chmod 600 ~/.ssh/authorized_keys
```

No cliente:

```bash
chmod 600 ~/.ssh/id_ed25519
```

A ideia principal é:

```text
Chave privada
=
Somente o proprietário deve ter acesso.
```

---

# 17. ssh-agent

O `ssh-agent` mantém chaves privadas disponíveis para processos SSH, evitando que você precise informar a senha da chave repetidamente.

Iniciar:

```bash
eval "$(ssh-agent -s)"
```

Adicionar chave:

```bash
ssh-add ~/.ssh/id_ed25519
```

Verificar:

```bash
ssh-add -l
```

---

# 18. known_hosts

Quando você conecta a um servidor pela primeira vez, o cliente registra a identidade criptográfica apresentada pelo servidor.

Isso normalmente é armazenado em:

```text
~/.ssh/known_hosts
```

O objetivo é ajudar a detectar mudanças inesperadas na identidade do servidor.

Na primeira conexão, é comum aparecer algo semelhante a:

```text
The authenticity of host cannot be established.
```

Depois de verificar a identidade do servidor e aceitar sua host key, ela é registrada.

---

# 19. Host keys

O servidor SSH possui suas próprias chaves de host.

Elas representam a identidade criptográfica do servidor.

O cliente utiliza essas chaves para ajudar a responder:

```text
Estou realmente conectando ao mesmo servidor?
```

Se a host key mudar inesperadamente, pode aparecer um alerta.

Exemplo conceitual:

```text
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

Isso pode acontecer por motivos legítimos:

- Servidor reinstalado.
- Máquina substituída.
- Host keys regeneradas.

Mas também pode indicar um problema de segurança.

Portanto:

```text
Não ignore automaticamente esse aviso.
```

Primeiro confirme por um canal confiável se a alteração é esperada.

---

# 20. Configuração do cliente

Arquivo:

```text
~/.ssh/config
```

Exemplo:

```text
Host servidor-estudos
    HostName 192.168.1.10
    User joao
    IdentityFile ~/.ssh/id_ed25519
```

Depois:

```bash
ssh servidor-estudos
```

---

# 21. Alias SSH

Sem configuração:

```bash
ssh -i ~/.ssh/id_ed25519 -p 2222 joao@192.168.1.10
```

Com `~/.ssh/config`:

```text
Host lab
    HostName 192.168.1.10
    User joao
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
```

Conexão:

```bash
ssh lab
```

Isso é especialmente útil quando você administra vários servidores.

---

# 22. Hardening

Hardening significa reduzir a superfície de ataque.

Algumas práticas comuns:

- Usar chaves SSH.
- Desabilitar autenticação por senha quando apropriado.
- Restringir usuários permitidos.
- Desabilitar login remoto direto do root.
- Utilizar firewall.
- Manter o sistema atualizado.
- Revisar logs.
- Remover algoritmos obsoletos conforme compatibilidade.
- Utilizar MFA ou controles adicionais quando o ambiente exigir.

---

# 23. Desabilitando login root

No `sshd_config`:

```text
PermitRootLogin no
```

Isso evita login SSH direto como:

```text
root
```

O fluxo recomendado pode ser:

```text
Usuário normal
      |
      v
SSH
      |
      v
sudo
```

---

# 24. Desabilitando autenticação por senha

Após confirmar que a autenticação por chave funciona:

```text
PasswordAuthentication no
```

Antes de aplicar:

1. Abra uma segunda sessão SSH.
2. Teste o login com chave.
3. Mantenha a sessão atual aberta.
4. Valide a configuração.
5. Recarregue o serviço.
6. Teste novamente.

Nunca desabilite autenticação por senha antes de confirmar que você consegue entrar usando uma chave válida.

---

# 25. Permitindo usuários específicos

É possível restringir usuários autorizados.

Exemplo:

```text
AllowUsers joao admin
```

Assim, o SSH restringe autenticação aos usuários configurados, sujeito às demais regras do sistema.

Também é possível utilizar regras baseadas em grupos, dependendo da política desejada.

---

# 26. Mudando a porta

Exemplo:

```text
Port 2222
```

Depois:

```bash
sudo sshd -t
sudo systemctl reload ssh
```

Conectar:

```bash
ssh -p 2222 usuario@host
```

Importante:

```text
Mudar a porta
≠
substituir autenticação forte.
```

Uma porta não padrão pode reduzir parte do ruído de scanners automatizados, mas não deve ser considerada um controle de segurança principal.

---

# 27. Firewall

Se você usa firewall, a porta SSH precisa estar permitida.

Exemplo conceitual:

```text
Internet
   |
   v
Firewall
   |
   | TCP/22 permitido
   v
Servidor SSH
```

Se mudar a porta:

```text
TCP/2222
```

o firewall também precisa ser ajustado.

Antes de fechar uma sessão remota, teste uma nova conexão.

---

# 28. SCP

SCP permite copiar arquivos utilizando SSH.

Enviar arquivo:

```bash
scp arquivo.txt usuario@192.168.1.10:/home/usuario/
```

Copiar do servidor:

```bash
scp usuario@192.168.1.10:/home/usuario/arquivo.txt .
```

Com porta personalizada:

```bash
scp -P 2222 arquivo.txt usuario@192.168.1.10:/home/usuario/
```

Observe:

```text
ssh usa -p
scp usa -P
```

---

# 29. SFTP

SFTP permite transferência de arquivos através do SSH.

Conectar:

```bash
sftp usuario@192.168.1.10
```

Alguns comandos:

```text
ls
cd
pwd
put
get
mkdir
rm
```

Enviar:

```text
put arquivo.txt
```

Baixar:

```text
get arquivo.txt
```

SFTP não deve ser confundido com FTP.

```text
SFTP
=
Protocolo de transferência sobre SSH
```

---

# 30. Tunelamento SSH

SSH pode transportar conexões através do canal criptografado.

Podemos criar:

```text
Local Port Forwarding
Remote Port Forwarding
Dynamic Port Forwarding
```

Essas técnicas são muito úteis para administração segura e acesso a serviços internos autorizados.

---

# 31. Local Port Forwarding

Formato:

```bash
ssh -L PORTA_LOCAL:DESTINO:PORTA_DESTINO usuario@servidor
```

Exemplo:

```bash
ssh -L 8080:127.0.0.1:80 usuario@servidor
```

Representação:

```text
Seu computador

localhost:8080
      |
      | SSH criptografado
      v
Servidor SSH
      |
      v
127.0.0.1:80
```

Agora, uma conexão local para:

```text
localhost:8080
```

é encaminhada pelo servidor SSH para:

```text
127.0.0.1:80
```

---

# 32. Remote Port Forwarding

Formato:

```bash
ssh -R PORTA_REMOTA:DESTINO:PORTA_DESTINO usuario@servidor
```

Exemplo conceitual:

```bash
ssh -R 8080:localhost:3000 usuario@servidor
```

Fluxo:

```text
Servidor remoto
    |
    | porta 8080
    v
Túnel SSH
    |
    v
Sua máquina
    |
    v
localhost:3000
```

A disponibilidade externa dessa porta depende das configurações do servidor SSH, regras de bind e firewall.

---

# 33. Dynamic Port Forwarding

Formato:

```bash
ssh -D 1080 usuario@servidor
```

O cliente SSH cria um proxy SOCKS local.

Conceitualmente:

```text
Aplicação
    |
    | SOCKS localhost:1080
    v
Cliente SSH
    |
    | túnel criptografado
    v
Servidor SSH
    |
    v
Destino
```

Pode ser útil para encaminhar conexões de aplicações configuradas para utilizar o proxy.

---

# 34. Jump Host

Um Jump Host é uma máquina intermediária utilizada para acessar sistemas internos.

Exemplo:

```text
Seu computador
      |
      v
Jump Host
      |
      v
Servidor interno
```

---

# 35. SSH ProxyJump

Exemplo:

```bash
ssh -J usuario@jump-host usuario@servidor-interno
```

Fluxo:

```text
Cliente
   |
   | SSH
   v
Jump Host
   |
   | SSH
   v
Servidor interno
```

Também pode ser configurado no:

```text
~/.ssh/config
```

Exemplo:

```text
Host jump
    HostName jump.exemplo.local
    User usuario

Host interno
    HostName 10.0.0.10
    User usuario
    ProxyJump jump
```

Depois:

```bash
ssh interno
```

---

# 36. X11 Forwarding

Em ambientes que utilizam X11, SSH pode encaminhar aplicações gráficas.

Exemplo:

```bash
ssh -X usuario@servidor
```

Depois:

```bash
xclock
```

O funcionamento depende da configuração do cliente, servidor e ambiente gráfico.

Em ambientes modernos, esse método pode não ser a melhor escolha para todos os cenários.

---

# 37. Multiplexação de conexões

O OpenSSH pode reutilizar uma conexão já estabelecida para novas sessões.

Exemplo no:

```text
~/.ssh/config
```

```text
Host *
    ControlMaster auto
    ControlPath ~/.ssh/control-%r@%h:%p
    ControlPersist 10m
```

Isso pode reduzir o tempo necessário para abrir várias conexões SSH consecutivas.

Exemplos:

```bash
ssh servidor
```

Depois:

```bash
scp arquivo.txt servidor:/tmp/
```

Dependendo da configuração, as conexões podem reutilizar o canal mestre.

---

# 38. Troubleshooting

Quando SSH não funciona, investigue em ordem.

```text
1. DNS
2. IP
3. Rota
4. Conectividade
5. Porta TCP
6. Firewall
7. sshd
8. Autenticação
```

---

# 39. Debug com -v

SSH possui modos verbosos.

```bash
ssh -v usuario@host
```

Mais detalhes:

```bash
ssh -vv usuario@host
```

Ainda mais:

```bash
ssh -vvv usuario@host
```

Isso ajuda a identificar:

- Problemas de DNS.
- Tentativas de conexão.
- Chaves testadas.
- Métodos de autenticação.
- Falhas de autenticação.
- Problemas de host key.

---

# 40. Analisando portas

No servidor:

```bash
sudo ss -tlnp
```

Procure algo como:

```text
LISTEN ... :22
```

Teste a porta a partir do cliente:

```bash
nc -vz 192.168.1.10 22
```

Se necessário:

```bash
nc -vz 192.168.1.10 2222
```

---

# 41. Analisando logs

Em sistemas com systemd:

```bash
sudo journalctl -u ssh
```

Ou:

```bash
sudo journalctl -u sshd
```

Dependendo da distribuição, logs também podem estar disponíveis em arquivos como:

```text
/var/log/auth.log
```

ou:

```text
/var/log/secure
```

Mensagens úteis podem indicar:

- Usuário inexistente.
- Senha incorreta.
- Chave rejeitada.
- Permissões incorretas.
- Tentativa bloqueada.
- Erro de configuração.

---

# 42. Capturando tráfego

Para verificar conexões SSH:

```bash
sudo tcpdump -i any -n 'tcp port 22'
```

Você pode observar o handshake TCP:

```text
SYN
SYN-ACK
ACK
```

Depois disso, o conteúdo da sessão SSH deve aparecer como tráfego criptografado.

O `tcpdump` pode mostrar:

```text
Cliente -> Servidor
Servidor -> Cliente
```

mas não deve permitir ler diretamente os comandos executados apenas capturando os pacotes criptografados.

---

# 43. Boas práticas

Uma configuração segura geralmente considera:

```text
[ ] Atualizações aplicadas
[ ] Chaves SSH utilizadas
[ ] Chave privada protegida
[ ] Login root direto desabilitado
[ ] Senhas desabilitadas quando possível
[ ] Usuários restritos
[ ] Firewall configurado
[ ] Logs monitorados
[ ] Configuração validada com sshd -t
[ ] Segunda sessão aberta durante mudanças
```

---

# Exemplo de configuração inicial

Um exemplo conceitual de política mais restritiva:

```text
Port 22

PermitRootLogin no

PubkeyAuthentication yes

PasswordAuthentication no

PermitEmptyPasswords no

AllowUsers usuario-admin
```

Antes de utilizar qualquer configuração em produção:

```text
1. Verifique a documentação da sua distribuição.
2. Verifique arquivos incluídos pelo sshd_config.
3. Teste a sintaxe.
4. Mantenha uma sessão SSH ativa.
5. Teste uma nova conexão.
```

---

# 44. Exercícios

## Exercício 1 — Instalação

Verifique se o cliente SSH está instalado:

```bash
ssh -V
```

Verifique se o servidor está ativo:

```bash
systemctl status ssh
```

---

## Exercício 2 — Conexão

Conecte-se a um servidor:

```bash
ssh usuario@IP_DO_SERVIDOR
```

Depois execute:

```bash
hostname
whoami
pwd
```

---

## Exercício 3 — Chaves

Gere uma chave:

```bash
ssh-keygen -t ed25519
```

Liste:

```bash
ls -la ~/.ssh
```

Identifique:

```text
Chave privada
Chave pública
```

---

## Exercício 4 — authorized_keys

Instale sua chave pública no servidor.

Depois teste:

```bash
ssh usuario@servidor
```

Confirme que consegue autenticar sem utilizar a senha da conta, caso sua chave não exija interação adicional.

---

## Exercício 5 — Alias

Crie:

```text
~/.ssh/config
```

Configure:

```text
Host lab
    HostName IP_DO_SERVIDOR
    User usuario
```

Teste:

```bash
ssh lab
```

---

## Exercício 6 — Debug

Execute:

```bash
ssh -vvv usuario@host
```

Observe:

```text
Resolução de nome
Conexão TCP
Host key
Autenticação
```

---

## Exercício 7 — Porta

Verifique portas abertas:

```bash
sudo ss -tlnp
```

Identifique a porta utilizada pelo `sshd`.

---

## Exercício 8 — Captura

Em um terminal:

```bash
sudo tcpdump -i any -n 'tcp port 22'
```

Em outro:

```bash
ssh usuario@host
```

Observe:

```text
SYN
SYN-ACK
ACK
```

---

## Exercício 9 — Local Forwarding

Em um ambiente de laboratório autorizado, execute:

```bash
ssh -L 8080:127.0.0.1:80 usuario@servidor
```

Depois tente acessar:

```text
http://localhost:8080
```

Entenda o caminho:

```text
Browser
   |
   v
localhost:8080
   |
   v
SSH
   |
   v
Servidor
   |
   v
127.0.0.1:80
```

---

## Exercício 10 — Hardening

Faça uma revisão da configuração:

```bash
sudo sshd -T
```

Depois identifique configurações relacionadas a:

```text
root
password
public key
authentication
port
```

> `sshd -T` mostra a configuração efetiva, o que pode ser mais útil do que observar apenas uma linha do arquivo quando existem arquivos incluídos ou valores padrão.

---

# 45. Resumo

SSH é um protocolo essencial para administração Linux.

Fluxo básico:

```text
CLIENTE
   |
   | TCP
   | SSH
   | Criptografia
   v
SERVIDOR
```

Os principais conceitos são:

```text
SSH
│
├── Cliente
│   └── ssh
│
├── Servidor
│   └── sshd
│
├── Autenticação
│   ├── Senha
│   └── Chaves
│       ├── Privada
│       └── Pública
│
├── Segurança
│   ├── PermitRootLogin
│   ├── PasswordAuthentication
│   ├── AllowUsers
│   └── Firewall
│
├── Arquivos
│   ├── sshd_config
│   ├── config
│   ├── authorized_keys
│   └── known_hosts
│
├── Transferência
│   ├── SCP
│   └── SFTP
│
├── Tunelamento
│   ├── -L
│   ├── -R
│   ├── -D
│   └── ProxyJump
│
└── Diagnóstico
    ├── ssh -vvv
    ├── ss
    ├── journalctl
    ├── nc
    └── tcpdump
```

---

# Regra de ouro

Ao configurar SSH remotamente:

```text
ALTEROU A CONFIGURAÇÃO?
        |
        v
VALIDOU COM sshd -t?
        |
        v
MANTEVE A SESSÃO ATUAL ABERTA?
        |
        v
TESTOU UMA NOVA CONEXÃO?
        |
        v
SÓ ENTÃO ENCERRA A SESSÃO ANTIGA
```

> **SSH é uma das ferramentas mais importantes da administração Linux. Entender autenticação por chaves, configuração do `sshd`, host keys, permissões e tunelamento é fundamental para administrar servidores de forma segura e eficiente.**